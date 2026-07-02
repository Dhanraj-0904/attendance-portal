import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Batch, Student, AttendanceRecord
from .auth import get_current_user, require_role, log_action
from ..services.csv_parser import parse_attendance_csv, generate_simulated_dates


def find_best_batch_match(db, batches, dept, location):
    if not dept:
        return None
    
    dept_clean = dept.strip().lower()
    loc_clean = location.strip().lower() if location else ""
    
    # Phase 1: Try to match both course name and center name
    for b in batches:
        center = b.center
        c_name_clean = center.name.lower() if center else ""
        course_clean = b.course_name.lower()
        
        course_matches = (course_clean in dept_clean) or (dept_clean in course_clean)
        center_matches = False
        if c_name_clean:
            center_matches = (c_name_clean in dept_clean) or (c_name_clean in loc_clean) or (dept_clean in c_name_clean)
            
        if course_matches and center_matches:
            return b
            
    # Phase 2: Fallback to matching course name only
    for b in batches:
        course_clean = b.course_name.lower()
        if (course_clean in dept_clean) or (dept_clean in course_clean):
            return b
            
    return None

router = APIRouter(prefix="/sync", tags=["Sync"])

SALT = "ngo_aadhaar_salt_key_1298471"

def hash_string(val: str) -> str:
    """
    Generates SHA-256 hash with salt for secure identifier storage.
    """
    hasher = hashlib.sha256()
    hasher.update((val + SALT).encode('utf-8'))
    return hasher.hexdigest()

def parse_duration_to_hours(duration_str: str) -> float:
    try:
        if not duration_str:
            return 0.0
        parts = duration_str.strip().split(':')
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            return h + m/60.0 + s/3600.0
        elif len(parts) == 2:
            h, m = int(parts[0]), int(parts[1])
            return h + m/60.0
        return float(duration_str)
    except Exception:
        return 0.0

@router.post("/upload")
async def upload_attendance_csv(
    batch_id: int = Form(...),
    date: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime
    # Parse target date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Prevent future date uploads
    from datetime import date as dt_date
    if target_date > dt_date.today():
        raise HTTPException(status_code=400, detail="Error: You cannot upload attendance for a future date.")

    contents = await file.read()

    try:
        from ..services.csv_parser import parse_date_wise_attendance_csv
        parsed_rows = parse_date_wise_attendance_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Get allowed batches
    if current_user.role == "teacher":
        allowed_batches = db.query(Batch).filter(Batch.teacher_id == current_user.id).all()
    else:
        allowed_batches = db.query(Batch).all()

    allowed_batch_ids = [b.id for b in allowed_batches]

    if batch_id not in allowed_batch_ids:
        raise HTTPException(status_code=403, detail="You do not have permission to sync data for this batch")

    # Group CSV students that match active students in our database
    present_student_ids = set()
    all_processed_student_ids = set()
    student_hours = {}

    for row in parsed_rows:
        emp_id = row["emp_id"]
        raw_emp_id = row["raw_emp_id"]
        duration = row["duration"].strip()

        # Find student by candidate code OR raw emp_id
        student = db.query(Student).filter(
            (Student.sid_student_id == emp_id) | 
            (Student.sid_student_id == f"CAN_{raw_emp_id}")
        ).first()

        if student and student.batch_id in allowed_batch_ids:
            all_processed_student_ids.add(student.id)
            hrs = parse_duration_to_hours(duration)
            student_hours[student.id] = hrs
            if hrs > 0:
                present_student_ids.add(student.id)

    # We will update attendance for the selected batch, and ANY other batch that has students listed in the CSV
    batches_to_update = {batch_id}
    for s_id in all_processed_student_ids:
        s_profile = db.query(Student).filter(Student.id == s_id).first()
        if s_profile:
            batches_to_update.add(s_profile.batch_id)

    total_present = 0
    total_absent = 0

    for b_id in batches_to_update:
        # Get all students enrolled in this batch
        students_in_batch = db.query(Student).filter(Student.batch_id == b_id).all()
        
        for student in students_in_batch:
            # Check status
            if student.id in present_student_ids:
                status_val = "present"
                total_present += 1
                hrs_val = student_hours.get(student.id, 0.0)
            else:
                status_val = "absent"
                total_absent += 1
                hrs_val = 0.0

            # Upsert record
            existing_rec = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student.id,
                AttendanceRecord.batch_id == b_id,
                AttendanceRecord.session_date == target_date
            ).first()

            if existing_rec:
                existing_rec.status = status_val
                existing_rec.attended_hours = hrs_val
                existing_rec.source = "csv_upload"
                existing_rec.synced_at = datetime.utcnow()
            else:
                new_rec = AttendanceRecord(
                    student_id=student.id,
                    batch_id=b_id,
                    session_date=target_date,
                    status=status_val,
                    attended_hours=hrs_val,
                    source="csv_upload",
                    synced_at=datetime.utcnow()
                )
                db.add(new_rec)

    db.commit()

    log_action(db, current_user.id, "upload_csv", "batches", batch_id)

    return {
        "message": f"Attendance synced successfully for {target_date.strftime('%Y-%m-%d')}.",
        "batches_updated": list(batches_to_update),
        "students_present": total_present,
        "students_absent": total_absent
    }


@router.post("/admin-upload")
async def upload_admin_student_list(
    batch_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    contents = await file.read()

    try:
        from ..services.csv_parser import parse_admin_student_list_csv
        parsed_students = parse_admin_student_list_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    from .auth import get_password_hash
    from .sync import hash_string

    students_synced = 0
    accounts_created = 0

    for s_info in parsed_students:
        emp_id = s_info["emp_id"]
        name = s_info["name"]
        dept = s_info["department"]

        # Dynamic routing: Match student batch by course and location (no mixup)
        all_batches = db.query(Batch).all()
        target_batch = find_best_batch_match(db, all_batches, dept, s_info.get("location"))

        # Fallback to selected batch if no match found
        active_batch_id = target_batch.id if target_batch else batch_id

        # 1. Check duplicate student profile
        student = db.query(Student).filter(Student.sid_student_id == emp_id).first()

        # 2. Check or create User account
        user = db.query(User).filter(User.username == emp_id).first()
        if not user:
            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student",
                plain_password="student123"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            accounts_created += 1

        if not student:
            student = Student(
                batch_id=active_batch_id,
                name=name,
                sid_student_id=emp_id,
                aadhaar_hash=hash_string(emp_id),
                user_id=user.id,
                is_active=True
            )
            db.add(student)
        else:
            student.name = name
            student.batch_id = active_batch_id
            student.user_id = user.id

        students_synced += 1

    db.commit()

    log_action(db, current_user.id, "admin_sync_students", "batches", batch_id)

    return {
        "message": f"Successfully synced {students_synced} students. Created {accounts_created} student login accounts.",
        "students_synced": students_synced,
        "accounts_created": accounts_created
    }



@router.post("/teacher-admin-upload")
async def upload_teacher_student_list(
    teacher_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    contents = await file.read()

    try:
        from ..services.csv_parser import parse_admin_student_list_csv
        parsed_students = parse_admin_student_list_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Get all batches of this teacher
    teacher_batches = db.query(Batch).filter(Batch.teacher_id == teacher_id).all()
    if not teacher_batches:
        raise HTTPException(status_code=400, detail="This teacher has no active batches assigned. Please create a batch first.")

    from .auth import get_password_hash
    from .sync import hash_string

    students_synced = 0
    accounts_created = 0

    for s_info in parsed_students:
        emp_id = s_info["emp_id"]
        name = s_info["name"]
        dept = s_info["department"]

        # Find which of the teacher's batches matches this student's department (subject) and location
        target_batch = find_best_batch_match(db, teacher_batches, dept, s_info.get("location"))

        # Fallback to teacher's first batch if no match
        active_batch_id = target_batch.id if target_batch else teacher_batches[0].id

        # 1. Create or update user login account
        user = db.query(User).filter(User.username == emp_id).first()
        if not user:
            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student",
                plain_password="student123"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            accounts_created += 1

        # 2. Upsert student profile
        student = db.query(Student).filter(Student.sid_student_id == emp_id).first()
        if not student:
            student = Student(
                batch_id=active_batch_id,
                name=name,
                sid_student_id=emp_id,
                aadhaar_hash=hash_string(emp_id),
                user_id=user.id,
                is_active=True
            )
            db.add(student)
        else:
            student.name = name
            student.batch_id = active_batch_id
            student.user_id = user.id

        students_synced += 1

    db.commit()

    log_action(db, current_user.id, "teacher_admin_sync_students", "users", teacher_id)

    return {
        "message": f"Successfully synced {students_synced} students for this teacher. Created {accounts_created} student login accounts.",
        "students_synced": students_synced,
        "accounts_created": accounts_created
    }


@router.post("/undo/{batch_id}")
def undo_last_sync(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Authorize: Only admin or the teacher of this batch can undo
    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to undo sync for this batch"
        )

    # Find the latest synced record for this batch
    latest_rec = db.query(AttendanceRecord).filter(
        AttendanceRecord.batch_id == batch_id,
        AttendanceRecord.source == "csv_upload"
    ).order_by(AttendanceRecord.synced_at.desc()).first()

    if not latest_rec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No CSV upload records found to undo for this batch"
        )

    # Group records synced within a 15-second window of the latest record
    latest_time = latest_rec.synced_at
    margin = timedelta(seconds=15)
    time_start = latest_time - margin
    time_end = latest_time + margin

    records_to_delete = db.query(AttendanceRecord).filter(
        AttendanceRecord.batch_id == batch_id,
        AttendanceRecord.source == "csv_upload",
        AttendanceRecord.synced_at >= time_start,
        AttendanceRecord.synced_at <= time_end
    ).all()

    num_deleted = len(records_to_delete)
    if num_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No matching records found to undo"
        )

    # Delete records
    for r in records_to_delete:
        db.delete(r)
    db.commit()

    # Find and delete students in this batch who have 0 attendance records left in the database
    students_in_batch = db.query(Student).filter(Student.batch_id == batch_id).all()
    students_deleted = 0
    for s in students_in_batch:
        rec_count = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id).count()
        if rec_count == 0:
            db.delete(s)
            students_deleted += 1
    db.commit()

    # Log action
    log_action(db, current_user.id, "undo_upload_csv", "batches", batch_id)

    return {
        "message": f"Successfully undone last sync. Removed {num_deleted} attendance records and {students_deleted} registered student profiles.",
        "records_removed": num_deleted,
        "students_removed": students_deleted
    }


@router.delete("/teacher-delete-students/{teacher_id}")
def delete_teacher_students(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    batches = db.query(Batch).filter(Batch.teacher_id == teacher_id).all()
    batch_ids = [b.id for b in batches]

    if not batch_ids:
        return {"message": f"No active batches for teacher {teacher.username}. No students to delete.", "deleted_count": 0}

    students = db.query(Student).filter(Student.batch_id.in_(batch_ids)).all()
    deleted_count = len(students)

    for s in students:
        if s.user_id:
            user_login = db.query(User).filter(User.id == s.user_id).first()
            if user_login:
                db.delete(user_login)
        db.delete(s)

    db.commit()

    log_action(db, current_user.id, "delete_teacher_students", "users", teacher_id)

    return {
        "message": f"Successfully deleted all {deleted_count} students assigned to teacher {teacher.username}.",
        "deleted_count": deleted_count
    }
