import sqlite3
import hashlib
from datetime import datetime, date, timedelta
import random

SALT = "ngo_aadhaar_salt_key_1298471"

# JSS 2026 Gazetted Holidays list
GAZETTED_HOLIDAYS_2026 = [
    "2026-01-26", "2026-02-26", "2026-03-05", "2026-03-26", "2026-04-10",
    "2026-05-01", "2026-06-15", "2026-08-15", "2026-09-05", "2026-10-02",
    "2026-10-24", "2026-11-12", "2026-12-25"
]

def hash_string(val: str) -> str:
    hasher = hashlib.sha256()
    hasher.update((val + SALT).encode('utf-8'))
    return hasher.hexdigest()

def get_password_hash(password: str) -> str:
    import hashlib
    salt = "ngo_auth_salt_9124_secure"
    hasher = hashlib.sha256()
    hasher.update((password + salt).encode('utf-8'))
    return hasher.hexdigest()

def get_weekdays(start_date: date, count: int) -> list:
    weekdays = []
    curr = start_date
    while len(weekdays) < count:
        # Check if weekday (0=Mon, 1=Tue, ..., 5=Sat)
        # Note: Sunday is 6 in python date.weekday()
        if curr.weekday() != 6: # Exclude Sunday
            date_str = curr.strftime("%Y-%m-%d")
            if date_str not in GAZETTED_HOLIDAYS_2026:
                weekdays.append(curr)
        curr += timedelta(days=1)
    return weekdays

def populate():
    db_path = "backend/attendance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print("Cleaning database...")
    cursor.execute("DELETE FROM attendance_records;")
    cursor.execute("DELETE FROM leave_requests;")
    cursor.execute("DELETE FROM students;")
    cursor.execute("DELETE FROM batches;")
    cursor.execute("DELETE FROM centers;")
    cursor.execute("DELETE FROM audit_logs;")
    cursor.execute("DELETE FROM users WHERE username != 'admin';")

    # Ensure admin exists and has valid created_at
    admin_check = cursor.execute("SELECT id FROM users WHERE username = 'admin';").fetchone()
    if not admin_check:
        admin_pwd_hash = get_password_hash("admin123")
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, phone, is_active, plain_password, created_at)
            VALUES ('admin', 'admin@ngo.org', ?, 'admin', '9999999999', 1, 'admin123', ?);
        """, (admin_pwd_hash, now_str))
        admin_id = cursor.lastrowid
        print("Seeded default admin user.")
    else:
        admin_id = admin_check[0]
        cursor.execute("UPDATE users SET created_at = ? WHERE id = ?;", (now_str, admin_id))
        print("Admin user already exists. Updated created_at timestamp.")

    # 1. Seed 2 Training Centers
    cursor.execute("""
        INSERT INTO centers (name, district, state, nsdc_center_code, created_at)
        VALUES ('Shyam Nagar Center', 'Indore', 'Madhya Pradesh', 'NSDC_IND_01', ?);
    """, (now_str,))
    center1_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO centers (name, district, state, nsdc_center_code, created_at)
        VALUES ('Vijay Nagar Center', 'Indore', 'Madhya Pradesh', 'NSDC_IND_02', ?);
    """, (now_str,))
    center2_id = cursor.lastrowid
    print("Seeded 2 Training Centers.")

    # 2. Seed 2 Teachers
    teacher_pwd_hash = get_password_hash("teacher123")
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, role, phone, subject, is_active, plain_password, created_at)
        VALUES ('sunita', 'sunita@jss.org', ?, 'teacher', '9876543210', 'Beauty & Tailoring', 1, 'teacher123', ?);
    """, (teacher_pwd_hash, now_str))
    teacher1_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, role, phone, subject, is_active, plain_password, created_at)
        VALUES ('sandhya', 'sandhya@jss.org', ?, 'teacher', '8765432109', 'Electricals', 1, 'teacher123', ?);
    """, (teacher_pwd_hash, now_str))
    teacher2_id = cursor.lastrowid
    print("Seeded 2 Teachers.")

    # 3. Seed 3 Batches
    # Batch 1: Shyam Nagar Center, Teacher: sunita (total 40 sessions)
    cursor.execute("""
        INSERT INTO batches (center_id, teacher_id, sid_batch_id, course_name, start_date, end_date, total_sessions, total_hours, daily_duration, status)
        VALUES (?, ?, 'BATCH_BEAUTY_01', 'Beauty Care Assistant', '2026-06-01', '2026-09-30', 40, 330, 8.25, 'active');
    """, (center1_id, teacher1_id))
    batch1_id = cursor.lastrowid

    # Batch 2: Shyam Nagar Center, Teacher: sunita (total 40 sessions)
    cursor.execute("""
        INSERT INTO batches (center_id, teacher_id, sid_batch_id, course_name, start_date, end_date, total_sessions, total_hours, daily_duration, status)
        VALUES (?, ?, 'BATCH_SEWING_01', 'Sewing Machine Operator', '2026-06-01', '2026-09-30', 40, 330, 8.25, 'active');
    """, (center1_id, teacher1_id))
    batch2_id = cursor.lastrowid

    # Batch 3: Vijay Nagar Center, Teacher: sandhya (total 45 sessions)
    cursor.execute("""
        INSERT INTO batches (center_id, teacher_id, sid_batch_id, course_name, start_date, end_date, total_sessions, total_hours, daily_duration, status)
        VALUES (?, ?, 'BATCH_ELEC_01', 'Assistant Electrician', '2026-06-01', '2026-09-30', 45, 330, 7.33, 'active');
    """, (center2_id, teacher2_id))
    batch3_id = cursor.lastrowid
    print("Seeded 3 Batches.")

    # 4. Seed Students (20 per batch)
    student_names_b1 = ["Aarti", "Pooja", "Jyoti", "Kiran", "Sita", "Gita", "Maya", "Rani", "Rekha", "Rupa", "Sunita", "Anita", "Divya", "Kajal", "Komal", "Lata", "Nisha", "Preeti", "Radha", "Sapna"]
    student_names_b2 = ["Deepak", "Amit", "Rahul", "Vijay", "Sanjay", "Raju", "Vikram", "Sunil", "Rajesh", "Anil", "Arjun", "Karan", "Gopal", "Ramesh", "Suresh", "Manoj", "Ajay", "Vinod", "Pawan", "Hari"]
    student_names_b3 = ["Rohan", "Mohit", "Aman", "Sahil", "Vivek", "Vishal", "Yash", "Aditya", "Akash", "Sumit", "Ashish", "Sachin", "Nitin", "Rohit", "Gaurav", "Sandeep", "Deepak", "Vikash", "Pradeep", "Alok"]

    student_pwd_hash = get_password_hash("student123")

    def seed_batch_students(batch_id, names, start_idx):
        student_ids = []
        for idx, name in enumerate(names):
            cand_id = f"CAN_{start_idx + idx}"
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, role, phone, is_active, plain_password, created_at)
                VALUES (?, ?, ?, 'student', '9900990099', 1, 'student123', ?);
            """, (cand_id, f"{cand_id.lower()}@jss.org", student_pwd_hash, now_str))
            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO students (batch_id, user_id, aadhaar_hash, name, phone, sid_student_id, is_active)
                VALUES (?, ?, ?, ?, '9900990099', ?, 1);
            """, (batch_id, user_id, hash_string(cand_id), name, cand_id))
            student_ids.append(cursor.lastrowid)
        return student_ids

    print("Seeding students...")
    student_ids_b1 = seed_batch_students(batch1_id, student_names_b1, 1001)
    student_ids_b2 = seed_batch_students(batch2_id, student_names_b2, 1021)
    student_ids_b3 = seed_batch_students(batch3_id, student_names_b3, 1041)
    print("Successfully seeded 60 student profiles.")

    # 5. Generate weekday calendar list starting from June 1, 2026
    start_date = date(2026, 6, 1)
    batch_dates_32 = get_weekdays(start_date, 32) # Generate 32 session dates
    batch_dates_10 = batch_dates_32[:10]          # First 10 session dates for Batch 3

    print("Generating simulated attendance logs with mixed statuses...")

    # ================= BATCH 1 (Beauty Care - ELIGIBLE CLASS) =================
    # We want this batch to be ELIGIBLE.
    # Rule: At least 75% of students (15 out of 20) must be ELIGIBLE (attending >= 30 sessions).
    # - 16 students: Attend 31 sessions (status: ELIGIBLE)
    # - 2 students: Attend 26 sessions (status: AT_RISK, 30 needed, 8 remaining)
    # - 2 students: Attend 20 sessions (status: IMPOSSIBLE, 30 needed, 8 remaining, cannot pass)
    for idx, s_id in enumerate(student_ids_b1):
        if idx < 16:
            # Attend 31 sessions, skip 1
            present_dates = batch_dates_32[:31]
            absent_dates = batch_dates_32[31:]
        elif idx < 18:
            # Attend 26 sessions, skip 6
            present_dates = batch_dates_32[:26]
            absent_dates = batch_dates_32[26:]
        else:
            # Attend 20 sessions, skip 12
            present_dates = batch_dates_32[:20]
            absent_dates = batch_dates_32[20:]

        for d in present_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'present', 8.25, 'manual', ?);
            """, (s_id, batch1_id, d.strftime("%Y-%m-%d"), now_str))
        for d in absent_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'absent', 0.0, 'manual', ?);
            """, (s_id, batch1_id, d.strftime("%Y-%m-%d"), now_str))

    # ================= BATCH 2 (Sewing Machine - AT_RISK CLASS) =================
    # We want this batch to be AT_RISK.
    # - 10 students: Attend 31 sessions (status: ELIGIBLE)
    # - 6 students: Attend 26 sessions (status: AT_RISK)
    # - 4 students: Attend 20 sessions (status: IMPOSSIBLE)
    for idx, s_id in enumerate(student_ids_b2):
        if idx < 10:
            # Attend 31 sessions
            present_dates = batch_dates_32[:31]
            absent_dates = batch_dates_32[31:]
        elif idx < 16:
            # Attend 26 sessions
            present_dates = batch_dates_32[:26]
            absent_dates = batch_dates_32[26:]
        else:
            # Attend 20 sessions
            present_dates = batch_dates_32[:20]
            absent_dates = batch_dates_32[20:]

        for d in present_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'present', 8.25, 'manual', ?);
            """, (s_id, batch2_id, d.strftime("%Y-%m-%d"), now_str))
        for d in absent_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'absent', 0.0, 'manual', ?);
            """, (s_id, batch2_id, d.strftime("%Y-%m-%d"), now_str))

    # ================= BATCH 3 (Electrician - Early stage AT_RISK CLASS) =================
    # This class has only done 10 sessions. All students will show as AT_RISK because they
    # haven't finished enough classes to be ELIGIBLE, but have plenty of sessions left to pass.
    for s_id in student_ids_b3:
        # Randomly assign 7 to 9 sessions attended out of 10
        attended_count = random.randint(7, 9)
        present_dates = batch_dates_10[:attended_count]
        absent_dates = batch_dates_10[attended_count:]

        # Standard session length: 330 / 45 = 7.33 hours
        for d in present_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'present', 7.33, 'manual', ?);
            """, (s_id, batch3_id, d.strftime("%Y-%m-%d"), now_str))
        for d in absent_dates:
            cursor.execute("""
                INSERT INTO attendance_records (student_id, batch_id, session_date, status, attended_hours, source, synced_at)
                VALUES (?, ?, ?, 'absent', 0.0, 'manual', ?);
            """, (s_id, batch3_id, d.strftime("%Y-%m-%d"), now_str))

    # 6. Seed Leave Requests
    cursor.execute("""
        INSERT INTO leave_requests (teacher_id, leave_date, reason, status, created_at)
        VALUES (?, '2026-07-06', 'Family wedding function', 'pending', ?);
    """, (teacher1_id, now_str))

    cursor.execute("""
        INSERT INTO leave_requests (teacher_id, leave_date, reason, status, created_at)
        VALUES (?, '2026-06-25', 'Routine health checkup', 'approved', ?);
    """, (teacher2_id, now_str))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully! All statuses are generated.")

if __name__ == "__main__":
    populate()
