import sqlite3
import os

def run_sqlite_migration():
    db_path = "backend/attendance.db"
    if not os.path.exists(db_path):
        print("Database not found yet.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN plain_password VARCHAR;")
        conn.commit()
        print("Successfully added plain_password column to users table.")
    except sqlite3.OperationalError:
        print("plain_password column already exists in users table.")
    
    # Backfill passwords for seeded admin/teacher/student if they are null
    try:
        cursor.execute("UPDATE users SET plain_password = 'admin123' WHERE username = 'admin' AND plain_password IS NULL;")
        cursor.execute("UPDATE users SET plain_password = 'teacher123' WHERE username = 'teacher' AND plain_password IS NULL;")
        cursor.execute("UPDATE users SET plain_password = 'student123' WHERE role = 'student' AND plain_password IS NULL;")
        conn.commit()
        print("Backfilled plain passwords for existing seed accounts.")
    except Exception as e:
        print("Backfill error:", e)
    finally:
        conn.close()

def apply_password_view_features():
    # Run DB migration first
    run_sqlite_migration()

    # 1. Update models.py to define plain_password field
    with open("backend/models.py", "r", encoding="utf-8") as f:
        models_code = f.read()

    old_user_class = """class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'teacher', 'student'
    phone = Column(String, nullable=True)
    subject = Column(String, nullable=True)"""

    new_user_class = """class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'teacher', 'student'
    phone = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    plain_password = Column(String, nullable=True)"""

    if "plain_password = Column(" not in models_code:
        models_code = models_code.replace(old_user_class, new_user_class)
        with open("backend/models.py", "w", encoding="utf-8") as f:
            f.write(models_code)
        print("Updated User model in models.py with plain_password.")

    # 2. Update backend/routers/auth.py
    with open("backend/routers/auth.py", "r", encoding="utf-8") as f:
        auth_code = f.read()

    # Seed users with plain passwords
    old_seed = """        admin = User(
            username="admin",
            email="admin@ngo.org",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            phone="9999999999",
            is_active=True
        )
        teacher = User(
            username="teacher",
            email="teacher@ngo.org",
            hashed_password=get_password_hash("teacher123"),
            role="teacher",
            phone="8888888888",
            is_active=True
        )"""

    new_seed = """        admin = User(
            username="admin",
            email="admin@ngo.org",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            phone="9999999999",
            is_active=True,
            plain_password="admin123"
        )
        teacher = User(
            username="teacher",
            email="teacher@ngo.org",
            hashed_password=get_password_hash("teacher123"),
            role="teacher",
            phone="8888888888",
            is_active=True,
            plain_password="teacher123"
        )"""

    auth_code = auth_code.replace(old_seed, new_seed)

    # Register user with plain password
    old_reg = """        user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            phone=user_in.phone,
            subject=user_in.subject
        )"""

    new_reg = """        user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            phone=user_in.phone,
            subject=user_in.subject,
            plain_password=user_in.password
        )"""

    auth_code = auth_code.replace(old_reg, new_reg)

    # Change password updates plain password
    old_change = """    target_user.hashed_password = get_password_hash(data.new_password)
    db.commit()"""

    new_change = """    target_user.hashed_password = get_password_hash(data.new_password)
    target_user.plain_password = data.new_password
    db.commit()"""

    auth_code = auth_code.replace(old_change, new_change)

    with open("backend/routers/auth.py", "w", encoding="utf-8") as f:
        f.write(auth_code)
    print("Updated auth.py plain_password mappings.")

    # 3. Update backend/routers/sync.py
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync_code = f.read()

    # admin-upload
    old_sync_admin = """            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student"
            )"""

    new_sync_admin = """            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student",
                plain_password="student123"
            )"""

    sync_code = sync_code.replace(old_sync_admin, new_sync_admin)

    # teacher-admin-upload
    old_sync_teacher = """            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student"
            )"""

    new_sync_teacher = """            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student",
                plain_password="student123"
            )"""

    sync_code = sync_code.replace(old_sync_teacher, new_sync_teacher)

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync_code)
    print("Updated sync.py user credentials creator with default plain_passwords.")

    # 4. Update backend/routers/students.py
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        stud_code = f.read()

    # manual add student user creation
    old_stud_add = """        user = User(
            username=student_in.sid_student_id,
            hashed_password=get_password_hash("student123"),
            role="student"
        )"""

    new_stud_add = """        user = User(
            username=student_in.sid_student_id,
            hashed_password=get_password_hash("student123"),
            role="student",
            plain_password="student123"
        )"""

    stud_code = stud_code.replace(old_stud_add, new_stud_add)

    # get_student_with_stats fallback dict return
    old_fallback_dict = """            "is_active": student.is_active,
            "attendance_pct": 0.0,
            "status": "IMPOSSIBLE",
            "attended_sessions": 0,
            "missed_sessions": 0,
            "remaining_sessions": 0,
            "still_need_to_attend": 0,
            "can_skip": 0
        }"""

    new_fallback_dict = """            "is_active": student.is_active,
            "user_id": student.user_id,
            "plain_password": student.user.plain_password if student.user else None,
            "attendance_pct": 0.0,
            "status": "IMPOSSIBLE",
            "attended_sessions": 0,
            "missed_sessions": 0,
            "remaining_sessions": 0,
            "still_need_to_attend": 0,
            "can_skip": 0
        }"""

    stud_code = stud_code.replace(old_fallback_dict, new_fallback_dict)

    # get_student_with_stats normal return dict
    old_normal_dict = """        "is_active": student.is_active,
        "attendance_pct": elig["current_pct"],
        "status": elig["status"],
        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"]
    }"""

    new_normal_dict = """        "is_active": student.is_active,
        "user_id": student.user_id,
        "plain_password": student.user.plain_password if student.user else None,
        "attendance_pct": elig["current_pct"],
        "status": elig["status"],
        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"]
    }"""

    stud_code = stud_code.replace(old_normal_dict, new_normal_dict)

    with open("backend/routers/students.py", "w", encoding="utf-8") as f:
        f.write(stud_code)
    print("Updated students.py to expose user_id and plain_password.")

    # 5. Update backend/routers/reports.py
    with open("backend/routers/reports.py", "r", encoding="utf-8") as f:
        rep_code = f.read()

    old_rep_teacher = """            "phone": t.phone,
            "subject": t.subject,
            "batches_count": len(t_batches),"""

    new_rep_teacher = """            "phone": t.phone,
            "subject": t.subject,
            "plain_password": t.plain_password,
            "batches_count": len(t_batches),"""

    rep_code = rep_code.replace(old_rep_teacher, new_rep_teacher)

    with open("backend/routers/reports.py", "w", encoding="utf-8") as f:
        f.write(rep_code)
    print("Updated reports.py to expose teacher plain_password.")

    # 6. Update seed.py
    with open("backend/seed.py", "r", encoding="utf-8") as f:
        seed_code = f.read()

    seed_code = seed_code.replace('role="admin",\n            phone="9999999999",', 'role="admin",\n            phone="9999999999",\n            plain_password="admin123",')
    seed_code = seed_code.replace('role="teacher",\n            phone="8888888888",', 'role="teacher",\n            phone="8888888888",\n            plain_password="teacher123",')
    seed_code = seed_code.replace('role="student",\n            phone="7777777777",', 'role="student",\n            phone="7777777777",\n            plain_password="student123",')

    with open("backend/seed.py", "w", encoding="utf-8") as f:
        f.write(seed_code)
    print("Updated seed.py seeder values.")

if __name__ == "__main__":
    apply_password_view_features()
