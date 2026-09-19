from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from .. import models
from ..agent.leave_agent import run_leave_agent
from ..agent.gemini_client import GeminiClient

router = APIRouter()
llm = GeminiClient()  # swap for real Gemini client later — one line change

class LeaveRequestIn(BaseModel):
    employee_id: int
    raw_text: str

@router.post("/requests/leave")
def submit_leave_request(payload: LeaveRequestIn, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # run agent
    result = run_leave_agent(payload.raw_text, employee.leave_balance, llm)

    # save the request
    leave_req = models.LeaveRequest(
        employee_id=employee.id,
        raw_text=payload.raw_text,
        days_requested=result["parsed"].get("days_requested"),
        status=result["status"],
    )
    db.add(leave_req)
    db.commit()
    db.refresh(leave_req)

    # save audit trail
    for step in result["trace"]:
        db.add(models.AuditLog(
            request_id=leave_req.id,
            step=step["step"],
            detail=step["detail"],
        ))

        # if approval needed, create an Approval row
    if result["status"] == "pending_approval":
        db.add(models.Approval(
            request_id=leave_req.id,
            approver_id=employee.manager_id,
            decision="pending",
        ))
    elif result["status"] == "approved":
        # auto-approved: execute the action immediately
        employee.leave_balance -= leave_req.days_requested
        db.add(models.AuditLog(
            request_id=leave_req.id,
            step="action_execution",
            detail=f"Mock HR system: leave auto-approved, balance reduced by {leave_req.days_requested} days",
        ))
        leave_req.status = "completed"

    db.commit()

    return {
        "request_id": leave_req.id,
        "status": leave_req.status,
        "trace": result["trace"],
    }

@router.get("/requests/{request_id}")
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    audit = db.query(models.AuditLog).filter(models.AuditLog.request_id == request_id).all()
    return {
        "request": {
            "id": req.id,
            "employee_id": req.employee_id,
            "raw_text": req.raw_text,
            "days_requested": req.days_requested,
            "status": req.status,
        },
        "audit_trail": [{"step": a.step, "detail": a.detail} for a in audit],
    }

@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db)):
    all_requests = db.query(models.LeaveRequest).order_by(models.LeaveRequest.created_at.desc()).all()
    total = len(all_requests)
    pending = sum(1 for r in all_requests if r.status == "pending_approval")
    completed = sum(1 for r in all_requests if r.status == "completed")

    recent = []
    for r in all_requests[:5]:
        employee = db.query(models.Employee).filter(models.Employee.id == r.employee_id).first()
        recent.append({
            "id": r.id,
            "employee_name": employee.name if employee else "Unknown",
            "request": r.raw_text,
            "days_requested": r.days_requested,
            "status": r.status,
        })

    return {
        "total": total,
        "pending": pending,
        "completed": completed,
        "recent": recent,
    }