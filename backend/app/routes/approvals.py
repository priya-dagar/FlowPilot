from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/approvals")
def list_pending_approvals(db: Session = Depends(get_db)):
    pending = db.query(models.Approval).filter(models.Approval.decision == "pending").all()
    result = []
    for approval in pending:
        req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == approval.request_id).first()
        employee = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()
        result.append({
            "request_id": req.id,
            "employee_name": employee.name,
            "raw_text": req.raw_text,
            "days_requested": req.days_requested,
        })
    return result

class ApprovalDecision(BaseModel):
    decision: str  # "approved" or "rejected"

@router.post("/approvals/{request_id}")
def decide_approval(request_id: int, payload: ApprovalDecision, db: Session = Depends(get_db)):
    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    approval = db.query(models.Approval).filter(models.Approval.request_id == request_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="No pending approval for this request")

    leave_req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave_req:
        raise HTTPException(status_code=404, detail="Request not found")

    # update approval
    approval.decision = payload.decision
    approval.decided_at = datetime.utcnow()

    # audit: human decision
    db.add(models.AuditLog(
        request_id=request_id,
        step="manager_decision",
        detail=f"Manager {payload.decision} the request",
    ))

    if payload.decision == "approved":
        leave_req.status = "approved"
        # mock tool call: deduct balance + "create leave"
        employee = db.query(models.Employee).filter(models.Employee.id == leave_req.employee_id).first()
        employee.leave_balance -= leave_req.days_requested
        db.add(models.AuditLog(
            request_id=request_id,
            step="action_execution",
            detail=f"Mock HR system: leave created, balance reduced by {leave_req.days_requested} days",
        ))
        leave_req.status = "completed"
    else:
        leave_req.status = "rejected"
        db.add(models.AuditLog(
            request_id=request_id,
            step="action_execution",
            detail="No action taken — request rejected",
        ))

    db.commit()

    return {
        "request_id": request_id,
        "final_status": leave_req.status,
    }