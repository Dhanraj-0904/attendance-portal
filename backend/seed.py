from datetime import datetime, date, timedelta
from .database import SessionLocal, engine, Base
from .models import User, Center, Batch, Student, AttendanceRecord, AuditLog
from .routers.auth import get_password_hash
from .routers.sync import hash_string

def seed_database():
    """
    Seeds the local database with rich, realistic demo data so the dashboards,
    rankings, calendars, and PDF exports work out-of-the-box.
    """
    db = SessionLocal()
    try:
        # Check if centers exist, if so database is already seeded
        if db.query(Center).count() > 0:
            print("Database already contains seed data.")
            return

        print("Seeding database with demo data...")

        # 1. Create Users
        admin_pwd = get_password_hash("admin123")
        teacher_pwd = get_password_hash("teacher123")
        student_pwd = get_password_hash("student123")

        admin_user = User(
            username="admin",
            email="coordinator@ngo.org",
            hashed_password=admin_pwd,
            role="admin",
            phone="9999999999",
            plain_password="admin123",
            is_active=True
        )
        
        teacher_user = User(
            username="teacher",
            email="teacher@ngo.org",
            hashed_password=teacher_pwd,
            role="teacher",
            phone="8888888888",
            plain_password="teacher123",
            is_active=True
        )

        student_user = User(
            username="student",
            email="student@ngo.org",
            hashed_password=student_pwd,
            role="student",
            phone="7777777777",
            plain_password="student123",
            is_active=True
        )

        db.add_all([admin_user, teacher_user, student_user])
        db.commit()
        db.refresh(teacher_user)
        db.refresh(student_user)

        # 2. Create Centers
        center1 = Center(
            name="Shalu Beauty Center",
            nsdc_center_code="TC325939",
            district="Raipur",
            state="Chhattisgarh"
        )
        center2 = Center(
            name="Jal Vihar Training Center",
            nsdc_center_code="TC492941",
            district="Bhilai",
            state="Chhattisgarh"
        )
        db.add_all([center1, center2])
        db.commit()
        db.refresh(center1)
        db.refresh(center2)

        # 3. Create Batches
        today = datetime.now().date()
        start_date = today - timedelta(days=20)
        end_date = today + timedelta(days=20)

        batch1 = Batch(
            center_id=center1.id,
            teacher_id=teacher_user.id,
            sid_batch_id="CAN_378748",
            course_name="Beauty Care Assistant Shyam Nagar",
            start_date=start_date,
            end_date=end_date,
            total_sessions=30,
            status="active"
        )
        
        batch2 = Batch(
            center_id=center2.id,
            teacher_id=teacher_user.id,
            sid_batch_id="CAN_383103",
            course_name="Beauty Care Assistant Jal Vihar",
            start_date=start_date,
            end_date=end_date,
            total_sessions=30,
            status="active"
        )
        
        db.add_all([batch1, batch2])
        db.commit()
        db.refresh(batch1)
        db.refresh(batch2)

        # 4. Create Students (5 per batch)
        # Batch 1 Students
        s1 = Student(
            batch_id=batch1.id,
            user_id=student_user.id, # Link default student login to this profile
            aadhaar_hash=hash_string("CAN_40343428"),
            name="Aarti Baghel",
            phone="9988776655",
            sid_student_id="CAN_40343428",
            is_active=True
        )
        s2 = Student(
            batch_id=batch1.id,
            aadhaar_hash=hash_string("CAN_40330680"),
            name="Alfiya Parveen",
            phone="9988776654",
            sid_student_id="CAN_40330680",
            is_active=True
        )
        s3 = Student(
            batch_id=batch1.id,
            aadhaar_hash=hash_string("CAN_37697505"),
            name="Anjani Bora",
            phone="9988776653",
            sid_student_id="CAN_37697505",
            is_active=True
        )
        s4 = Student(
            batch_id=batch1.id,
            aadhaar_hash=hash_string("CAN_40265769"),
            name="Anushka Jogi",
            phone="9988776652",
            sid_student_id="CAN_40265769",
            is_active=True
        )
        s5 = Student(
            batch_id=batch1.id,
            aadhaar_hash=hash_string("CAN_38310368"),
            name="Arpita Sahu",
            phone="9988776651",
            sid_student_id="CAN_38310368",
            is_active=True
        )

        # Batch 2 Students
        s6 = Student(
            batch_id=batch2.id,
            aadhaar_hash=hash_string("CAN_40265722"),
            name="Barkha Masih",
            phone="9988776650",
            sid_student_id="CAN_40265722",
            is_active=True
        )
        s7 = Student(
            batch_id=batch2.id,
            aadhaar_hash=hash_string("CAN_40241776"),
            name="Basanti Mandle",
            phone="9988776649",
            sid_student_id="CAN_40241776",
            is_active=True
        )

        students_list = [s1, s2, s3, s4, s5, s6, s7]
        db.add_all(students_list)
        db.commit()
        for s in students_list:
            db.refresh(s)

        # 5. Create Attendance Records (15 sessions elapsed)
        # We will seed attendance for s1 to s7.
        # Let's seed different attendance levels:
        # s1: Aarti (Present 13/15 = 86.6%) -> ELIGIBLE
        # s2: Alfiya (Present 11/15 = 73.3%) -> AT_RISK (can recover since 15 sessions remaining)
        # s3: Anjani (Present 3/15 = 20.0%) -> IMPOSSIBLE (cannot reach 75% even if attending all remaining 15 sessions: max possible is 18/30 = 60.0%)
        # s4: Anushka (Present 14/15 = 93.3%) -> ELIGIBLE
        # s5: Arpita (Present 12/15 = 80.0%) -> ELIGIBLE
        # s6: Barkha (Present 14/15 = 93.3%) -> ELIGIBLE
        # s7: Basanti (Present 13/15 = 86.6%) -> ELIGIBLE

        attendance_configs = {
            s1.id: 13,
            s2.id: 11,
            s3.id: 3,
            s4.id: 14,
            s5.id: 12,
            s6.id: 14,
            s7.id: 13
        }

        for student_id, present_count in attendance_configs.items():
            stud = db.query(Student).filter(Student.id == student_id).first()
            # Generate 15 working dates (skip Sundays)
            current_date = start_date
            sessions_count = 0
            presents_placed = 0

            while sessions_count < 15:
                if current_date.weekday() != 6: # Not Sunday
                    status = "present" if presents_placed < present_count else "absent"
                    if status == "present":
                        presents_placed += 1
                    
                    rec = AttendanceRecord(
                        student_id=student_id,
                        batch_id=stud.batch_id,
                        session_date=current_date,
                        status=status,
                        source="csv_upload"
                    )
                    db.add(rec)
                    sessions_count += 1
                current_date += timedelta(days=1)

        # 6. Audit Logs
        log = AuditLog(
            user_id=admin_user.id,
            action="seed_database",
            table_name="system",
            record_id=1
        )
        db.add(log)
        db.commit()

        print("Database seeded successfully with 2 centers, 2 batches, 7 students, and 105 attendance records!")

    finally:
        db.close()

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    seed_database()
