from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Batch, Student, Center, User, AttendanceRecord
from ..schemas import BatchCreate, BatchResponse
from .auth import get_current_user, require_role, log_action
from ..services.eligibility import calculate_student_eligibility, calculate_batch_eligibility

router = APIRouter(prefix="/batches", tags=["Batches"])

def get_batch_with_stats(batch: Batch, db: Session):
    """
    Helper to calculate enrollment and eligibility statistics for a single batch.
    """
    students = db.query(Student).filter(Student.batch_id == batch.id).all()
    student_count = len(students)
    
    from sqlalchemy import func
    student_eligibilities = []
    for s in students:
        attended_hours_sum = db.query(func.sum(AttendanceRecord.attended_hours)).filter(
            AttendanceRecord.student_id == s.id
        ).scalar() or 0.0

        sessions_held = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == s.id
        ).count()

        std_session_len = batch.daily_duration if batch.daily_duration else (batch.total_hours / batch.total_sessions if batch.total_sessions > 0 else 8.25)
        remaining_sessions = max(0, batch.total_sessions - sessions_held)
        remaining_hours = remaining_sessions * std_session_len
        
        elig = calculate_student_eligibility(batch.total_hours, attended_hours_sum, remaining_hours)
        student_eligibilities.append(elig)
        
    batch_stats = calculate_batch_eligibility(student_eligibilities)
    
    center = db.query(Center).filter(Center.id == batch.center_id).first()
    teacher = db.query(User).filter(User.id == batch.teacher_id).first()
    
    return {
        "id": batch.id,
        "center_id": batch.center_id,
        "teacher_id": batch.teacher_id,
        "sid_batch_id": batch.sid_batch_id,
        "course_name": batch.course_name,
        "start_date": batch.start_date,
        "end_date": batch.end_date,
        "total_sessions": batch.total_sessions,
        "total_hours": batch.total_hours,
        "daily_duration": batch.daily_duration,
        "status": batch.status,
        "center_name": center.name if center else "Unknown Center",
        "teacher_name": teacher.username if teacher else "Unknown Teacher",
        "students_count": student_count,
        "class_eligibility_pct": batch_stats["eligible_students_pct"],
        "class_status": batch_stats["status"]
    }

@router.get("/", response_model=List[BatchResponse])
def get_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Admin sees all batches. Teachers see only their own batches.
    """
    if current_user.role == "admin":
        batches = db.query(Batch).all()
    elif current_user.role == "teacher":
        batches = db.query(Batch).filter(Batch.teacher_id == current_user.id).all()
    else:
        # Students shouldn't call this directly, but if they do, filter by their batch
        student_profile = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student_profile:
            batches = db.query(Batch).filter(Batch.id == student_profile.batch_id).all()
        else:
            batches = []

    result = []
    for b in batches:
        result.append(get_batch_with_stats(b, db))
    return result

@router.get("/{id}", response_model=BatchResponse)
def get_batch_by_id(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this batch")
        
    return get_batch_with_stats(batch, db)

@router.post("/", response_model=BatchResponse)
def create_batch(
    batch_in: BatchCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    import time
    from datetime import timedelta
    
    sid_batch_id = batch_in.sid_batch_id
    if not sid_batch_id:
        sid_batch_id = f"BATCH_{batch_in.course_name.replace(' ', '_').upper()}_{int(time.time())}"
        
    end_date = batch_in.end_date or (batch_in.start_date + timedelta(days=365))

    # Check if duplicate SID batch ID
    dup = db.query(Batch).filter(Batch.sid_batch_id == sid_batch_id).first()
    if dup:
        raise HTTPException(status_code=400, detail="SID Batch ID already exists")
        
    # Check if teacher exists and is actually a teacher
    teacher = db.query(User).filter(User.id == batch_in.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Invalid teacher assigned")
        
    # Check if center exists
    center = db.query(Center).filter(Center.id == batch_in.center_id).first()
    if not center:
        raise HTTPException(status_code=400, detail="Invalid center selected")

    new_batch = Batch(
        center_id=batch_in.center_id,
        teacher_id=batch_in.teacher_id,
        sid_batch_id=sid_batch_id,
        course_name=batch_in.course_name,
        start_date=batch_in.start_date,
        end_date=end_date,
        total_sessions=batch_in.total_sessions,
        total_hours=batch_in.total_hours or 330,
        daily_duration=batch_in.daily_duration,
        status=batch_in.status
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    
    log_action(db, current_user.id, "create_batch", "batches", new_batch.id)
    return get_batch_with_stats(new_batch, db)

@router.put("/{id}", response_model=BatchResponse)
def update_batch(
    id: int, 
    batch_in: BatchCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    from datetime import timedelta
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    sid_batch_id = batch_in.sid_batch_id or batch.sid_batch_id
    end_date = batch_in.end_date or (batch_in.start_date + timedelta(days=365))

    batch.center_id = batch_in.center_id
    batch.teacher_id = batch_in.teacher_id
    batch.sid_batch_id = sid_batch_id
    batch.course_name = batch_in.course_name
    batch.start_date = batch_in.start_date
    batch.end_date = end_date
    batch.total_sessions = batch_in.total_sessions
    batch.total_hours = batch_in.total_hours
    batch.daily_duration = batch_in.daily_duration
    batch.status = batch_in.status
    
    db.commit()
    db.refresh(batch)
    
    log_action(db, current_user.id, "update_batch", "batches", batch.id)
    return get_batch_with_stats(batch, db)

@router.delete("/{id}")
def delete_batch(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    db.delete(batch)
    db.commit()
    
    log_action(db, current_user.id, "delete_batch", "batches", id)
    return {"message": f"Batch {id} deleted successfully"}


@router.get("/{id}/attendance-dates")
def get_batch_attendance_dates(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this batch")

    records = db.query(AttendanceRecord.session_date).filter(
        AttendanceRecord.batch_id == id
    ).distinct().all()

    return [r[0].strftime("%Y-%m-%d") for r in records]


@router.get("/{id}/scheduled-dates")
def get_batch_scheduled_dates(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this batch")

    # Generate dates starting from batch.start_date
    from datetime import timedelta
    working_days = []
    current = batch.start_date
    while len(working_days) < batch.total_sessions:
        if current.weekday() != 6:  # Exclude Sundays (6 = Sunday)
            working_days.append(current)
        current += timedelta(days=1)

    # Get which dates already have attendance uploaded
    uploaded_dates = db.query(AttendanceRecord.session_date).filter(
        AttendanceRecord.batch_id == id
    ).distinct().all()
    uploaded_set = {r[0] for r in uploaded_dates}

    return [
        {
            "date": d.strftime("%Y-%m-%d"),
            "day": d.day,
            "month_name": d.strftime("%b"),
            "has_attendance": d in uploaded_set
        }
        for d in working_days
    ]
