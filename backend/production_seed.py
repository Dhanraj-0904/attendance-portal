import os
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from .models import User, Center, Batch, Student, AttendanceRecord
from .routers.auth import get_password_hash

def seed_production_db(db: Session):
    # Check if database is already seeded (has users)
    if db.query(User).count() > 0:
        print("Database already contains users. Skipping seed.")
        return

    print("Database is empty. Initializing default and mock data...")

    # 1. Create Users
    admin_pwd_hash = get_password_hash("admin123")
    teacher_pwd_hash = get_password_hash("student123")  # teacher credentials
    student_pwd_hash = get_password_hash("student123")

    admin_user = User(
        username="admin",
        email="admin@ngo.org",
        hashed_password=admin_pwd_hash,
        role="admin",
        phone="9999999999",
        plain_password="admin123",
        is_active=True
    )
    
    teacher_user = User(
        username="Umesh_dewangan",
        email="umesh@ngo.org",
        hashed_password=teacher_pwd_hash,
        role="teacher",
        phone="8888888888",
        plain_password="student123",
        is_active=True
    )

    student_user = User(
        username="student",
        email="student@ngo.org",
        hashed_password=student_pwd_hash,
        role="student",
        phone="7777777777",
        plain_password="student123",
        is_active=True
    )

    db.add_all([admin_user, teacher_user, student_user])
    db.commit()
    db.refresh(admin_user)
    db.refresh(teacher_user)
    db.refresh(student_user)

    # 2. Create Center
    center = Center(
        name="Khamtarai Main Road",
        district="Raipur",
        state="Chhattisgarh",
        nsdc_center_code="NSDC_KHM_01"
    )
    db.add(center)
    db.commit()
    db.refresh(center)

    # 3. Create Batch
    today = date.today()
    start_date = today - timedelta(days=20)
    end_date = today + timedelta(days=20)

    batch = Batch(
        center_id=center.id,
        teacher_id=teacher_user.id,
        sid_batch_id="BATCH_OFFICE_ASSISTANCE_1782979585",
        course_name="Office Assistance",
        start_date=start_date,
        end_date=end_date,
        total_sessions=40,
        total_hours=330.0,
        daily_duration=8.25,
        status="active"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # 4. Create Students
    mock_students = [
        ("Akanksha Kushwaha", "CAN_64337548"),
        ("Aradhana Vishwakarma", "CAN_36857901"),
        ("Chanchal Verma", "CAN_52498932"),
        ("Chhaya Varma", "CAN_42856310"),
        ("Deepika Sahu", "CAN_17696800"),
        ("Gouri Sahu", "CAN_26801917"),
        ("Hemlata Manikpuri", "CAN_29663194"),
        ("Himanshi Sahu", "CAN_72619239"),
    ]

    students_list = []
    for idx, (name, sid) in enumerate(mock_students):
        s = Student(
            batch_id=batch.id,
            user_id=student_user.id if idx == 0 else None,
            aadhaar_hash=str(hash(sid)),
            name=name,
            phone=f"900000000{idx}",
            sid_student_id=sid,
            is_active=True
        )
        students_list.append(s)
        db.add(s)

    db.commit()
    for s in students_list:
        db.refresh(s)

    # 5. Seed Attendance Records (10 sessions conducted so far)
    # Give them different levels of attendance
    attendance_pattern = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], # s1
        [1, 1, 1, 1, 1, 0, 1, 0, 1, 0], # s2
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # s3
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # s4
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0], # s5
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], # s6
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1], # s7
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # s8
    ]

    session_dates = []
    curr = start_date
    while len(session_dates) < 10:
        if curr.weekday() != 6: # Skip Sunday
            session_dates.append(curr)
        curr += timedelta(days=1)

    for s_idx, student in enumerate(students_list):
        pattern = attendance_pattern[s_idx]
        for day_idx, session_date in enumerate(session_dates):
            status = "present" if pattern[day_idx] == 1 else "absent"
            # Calculate hours based on daily duration
            attended_hrs = batch.daily_duration if status == "present" else 0.0
            
            # Since daily_duration is 8.25:
            if status == "present" and s_idx == 0 and day_idx == 0:
                attended_hrs = 6.25 # Late check-in
            
            rec = AttendanceRecord(
                student_id=student.id,
                batch_id=batch.id,
                session_date=session_date,
                status=status,
                attended_hours=attended_hrs,
                source="csv_upload"
            )
            db.add(rec)

    db.commit()
    print("Database seeding completed successfully.")
