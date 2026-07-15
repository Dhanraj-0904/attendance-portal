
from pydantic import BaseModel

class ManualStudentCreate(BaseModel):
    batch_id: int
    sid_student_id: str
    name: str
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, Batch, AttendanceRecord, User
from ..schemas import StudentCreate, StudentResponse, StudentUpdate
from .auth import get_current_user, require_role, log_action
from ..services.eligibility import calculate_student_eligibility

router = APIRouter(prefix="/students", tags=["Students"])

def get_student_with_stats(student: Student, db: Session):
    """
    Helper to calculate attendance statistics for a single student.
    """
    batch = db.query(Batch).filter(Batch.id == student.batch_id).first()
    if not batch:
        return {
            "id": student.id,
            "batch_id": student.batch_id,
            "aadhaar_hash": student.aadhaar_hash,
            "name": student.name,
            "phone": student.phone,
            "sid_student_id": student.sid_student_id,
            "is_active": student.is_active,
            "user_id": student.user_id,
            "plain_password": student.user.plain_password if student.user else None,
            "attendance_pct": 0.0,
            "status": "IMPOSSIBLE",
            "attended_sessions": 0,
            "missed_sessions": 0,
            "remaining_sessions": 0,
            "still_need_to_attend": 0,
            "can_skip": 0,
            "sessions_attended": 0,
            "sessions_missed": 0,
            "sessions_needed_for_75": 0,
            "sessions_remaining": 0,
            "total_hours": 330
        }

    # Count actual attendance records in hours
    from sqlalchemy import func
    attended_hours_sum = db.query(func.sum(AttendanceRecord.attended_hours)).filter(
        AttendanceRecord.student_id == student.id
    ).scalar() or 0.0

    sessions_held = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id
    ).count()

    std_session_len = batch.daily_duration if batch.daily_duration else (batch.total_hours / batch.total_sessions if batch.total_sessions > 0 else 8.25)
    absent_days = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.status == "absent"
    ).count()
    missed_hours = absent_days * std_session_len
    remaining_sessions = max(0, batch.total_sessions - sessions_held)
    remaining_hours = remaining_sessions * std_session_len
    
    elig = calculate_student_eligibility(batch.total_hours, attended_hours_sum, remaining_hours)
    
    return {
        "id": student.id,
        "batch_id": student.batch_id,
        "aadhaar_hash": student.aadhaar_hash,
        "name": student.name,
        "phone": student.phone,
        "sid_student_id": student.sid_student_id,
        "is_active": student.is_active,
        "user_id": student.user_id,
        "plain_password": student.user.plain_password if student.user else None,
        "attendance_pct": elig["current_pct"],
        "status": elig["status"],
        "attended_sessions": attended_hours_sum,
        "missed_sessions": missed_hours,
        "remaining_sessions": remaining_hours,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"],
        "total_hours": batch.total_hours if batch else 330,
        "sessions_attended": attended_hours_sum,
        "sessions_missed": missed_hours,
        "sessions_needed_for_75": elig["still_need_to_attend"],
        "sessions_remaining": remaining_hours
    }

@router.get("/", response_model=List[StudentResponse])
def get_students(
    batch_id: Optional[int] = None,
    at_risk: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns lists of students. Admin sees all, teachers see their own, and students see only their own record.
    Supports filtering by batch_id and at_risk status.
    """
    query = db.query(Student)

    if current_user.role == "teacher":
        # Get only student profiles belonging to batches taught by this teacher
        teacher_batches = db.query(Batch.id).filter(Batch.teacher_id == current_user.id).all()
        batch_ids = [b[0] for b in teacher_batches]
        query = query.filter(Student.batch_id.in_(batch_ids))
    elif current_user.role == "student":
        # Student sees only their own student record
        query = query.filter(Student.user_id == current_user.id)

    if batch_id:
        query = query.filter(Student.batch_id == batch_id)

    students = query.all()
    results = []
    
    for s in students:
        stats = get_student_with_stats(s, db)
        if at_risk:
            # At risk means status is either AT_RISK or IMPOSSIBLE (i.e. below 75% attendance)
            if stats["status"] in ["AT_RISK", "IMPOSSIBLE"]:
                results.append(stats)
        else:
            results.append(stats)
            
    return results


@router.get("/my-profile")
def get_my_student_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this profile")
        
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    stats = get_student_with_stats(student, db)
    
    # Generate calendar logs
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id
    ).order_by(AttendanceRecord.session_date.asc()).all()
    
    calendar_logs = []
    for i, r in enumerate(records, start=1):
        calendar_logs.append({
            "day_number": i,
            "date": r.session_date.strftime("%Y-%m-%d"),
            "status": "PRESENT" if r.status == "present" else "ABSENT"
        })
        
    stats["calendar_logs"] = calendar_logs
    stats["sessions_attended"] = stats["attended_sessions"]
    stats["sessions_missed"] = stats["missed_sessions"]
    stats["sessions_remaining"] = stats["remaining_sessions"]
    stats["sessions_needed_for_75"] = stats["still_need_to_attend"]
    
    return stats

@router.get("/{id}", response_model=StudentResponse)
def get_student_by_id(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this student")
        
    if current_user.role == "teacher":
        # Check if student is in one of the teacher's batches
        batch = db.query(Batch).filter(Batch.id == student.batch_id, Batch.teacher_id == current_user.id).first()
        if not batch:
            raise HTTPException(status_code=403, detail="You do not have permission to view this student")

    return get_student_with_stats(student, db)

@router.get("/{id}/calendar")
def get_student_calendar(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns date list for rendering on the student calendar.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this calendar")

    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == id
    ).order_by(AttendanceRecord.session_date.asc()).all()

    return [{"date": r.session_date.strftime("%Y-%m-%d"), "status": r.status} for r in records]

@router.post("/", response_model=StudentResponse)
def create_student(
    student_in: StudentCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    # Check if duplicate SID Student ID
    dup = db.query(Student).filter(Student.sid_student_id == student_in.sid_student_id).first()
    if dup:
        raise HTTPException(status_code=400, detail="SID Student ID already registered")

    new_student = Student(
        batch_id=student_in.batch_id,
        aadhaar_hash=student_in.aadhaar_hash,
        name=student_in.name,
        phone=student_in.phone,
        sid_student_id=student_in.sid_student_id,
        is_active=student_in.is_active
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    log_action(db, current_user.id, "create_student", "students", new_student.id)
    return get_student_with_stats(new_student, db)

@router.put("/{id}", response_model=StudentResponse)
def update_student(
    id: int, 
    student_in: StudentUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "teacher"]))
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = student_in.name
    
    if student_in.password and student_in.password.strip():
        if student.user:
            from .auth import get_password_hash
            student.user.hashed_password = get_password_hash(student_in.password)
            student.user.plain_password = student_in.password
    
    db.commit()
    db.refresh(student)
    
    log_action(db, current_user.id, "update_student", "students", student.id)
    return get_student_with_stats(student, db)

@router.delete("/{id}")
def delete_student(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db.delete(student)
    db.commit()
    
    log_action(db, current_user.id, "delete_student", "students", id)
    return {"message": f"Student {id} deleted successfully"}


@router.post("/add-manual")
def add_student_manual(
    student_in: ManualStudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    from .auth import get_password_hash
    from .sync import hash_string

    # 1. Check duplicate student SID
    dup_student = db.query(Student).filter(Student.sid_student_id == student_in.sid_student_id).first()
    if dup_student:
        raise HTTPException(status_code=400, detail=f"Student ID {student_in.sid_student_id} is already registered.")

    # 2. Check or create User
    user = db.query(User).filter(User.username == student_in.sid_student_id).first()
    if not user:
        user = User(
            username=student_in.sid_student_id,
            hashed_password=get_password_hash("student123"),
            role="student",
            plain_password="student123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Create Student profile
    new_student = Student(
        batch_id=student_in.batch_id,
        name=student_in.name,
        sid_student_id=student_in.sid_student_id,
        aadhaar_hash=hash_string(student_in.sid_student_id),
        user_id=user.id,
        is_active=True
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Log action
    log_action(db, current_user.id, "manual_add_student", "students", new_student.id)

    return {
        "message": f"Student '{student_in.name}' added successfully. Login username: '{user.username}', Password: 'student123'",
        "student_id": new_student.id,
        "username": user.username
    }


class StudentUpdate(BaseModel):
    name: str
    phone: Optional[str] = None

@router.put("/{id}")
def update_student(
    id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = student_in.name
    student.phone = student_in.phone
    db.commit()
    db.refresh(student)

    log_action(db, current_user.id, "update_student", "students", id)
    return {"message": "Student updated successfully"}
