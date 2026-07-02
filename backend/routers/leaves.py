from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..models import User, LeaveRequest
from .auth import get_current_user, require_role, log_action
from pydantic import BaseModel

router = APIRouter(prefix="/leaves", tags=["Leaves"])

class LeaveCreate(BaseModel):
    leave_date: date
    reason: str

@router.post("/request")
def request_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["teacher"]))
):
    existing = db.query(LeaveRequest).filter(
        LeaveRequest.teacher_id == current_user.id,
        LeaveRequest.leave_date == leave_in.leave_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a request for this date.")

    new_leave = LeaveRequest(
        teacher_id=current_user.id,
        leave_date=leave_in.leave_date,
        reason=leave_in.reason,
        status="pending"
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    log_action(db, current_user.id, "request_leave", "leave_requests", new_leave.id)
    return {"message": "Leave request submitted successfully"}

@router.get("/", response_model=List[dict])
def get_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        leaves = db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()
    elif current_user.role == "teacher":
        leaves = db.query(LeaveRequest).filter(LeaveRequest.teacher_id == current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    else:
        leaves = []

    result = []
    for l in leaves:
        result.append({
            "id": l.id,
            "teacher_id": l.teacher_id,
            "teacher_name": l.teacher.username if l.teacher else "Unknown Teacher",
            "leave_date": l.leave_date.strftime("%Y-%m-%d"),
            "reason": l.reason,
            "status": l.status,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return result

@router.post("/{id}/approve")
def approve_leave(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "approved"
    db.commit()

    log_action(db, current_user.id, "approve_leave", "leave_requests", id)
    return {"message": "Leave request approved successfully"}

@router.post("/{id}/decline")
def decline_leave(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "declined"
    db.commit()

    log_action(db, current_user.id, "decline_leave", "leave_requests", id)
    return {"message": "Leave request declined successfully"}
