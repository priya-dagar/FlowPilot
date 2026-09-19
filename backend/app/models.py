from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    leave_balance = Column(Integer, default=18)  # days

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    raw_text = Column(Text)              # original employee message
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    days_requested = Column(Integer, nullable=True)
    status = Column(String, default="pending_agent")
    # statuses: pending_agent -> pending_approval -> approved/rejected -> completed
    created_at = Column(DateTime, server_default=func.now())

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("leave_requests.id"))
    approver_id = Column(Integer, ForeignKey("employees.id"))
    decision = Column(String, default="pending")  # pending/approved/rejected
    decided_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("leave_requests.id"))
    step = Column(String)        # e.g. "policy_check", "balance_check", "approval_required"
    detail = Column(Text)        # what the agent decided and why
    timestamp = Column(DateTime, server_default=func.now())