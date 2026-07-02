import sqlite3
import os

def run_db_migration():
    db_path = "backend/attendance.db"
    if not os.path.exists(db_path):
        print("Database file not found yet.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN subject VARCHAR;")
        conn.commit()
        print("Successfully migrated database table: added 'subject' column to 'users'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Column 'subject' already exists in 'users' table.")
        else:
            print("DB migration operational error:", e)
    finally:
        conn.close()

def apply_teacher_subject_field():
    # Run DB migration first
    run_db_migration()

    # 1. Update backend/models.py
    with open("backend/models.py", "r", encoding="utf-8") as f:
        models_code = f.read()
    
    old_user_fields = """    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)"""
    
    new_user_fields = """    phone = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)"""
    
    if "subject = Column" not in models_code:
        models_code = models_code.replace(old_user_fields, new_user_fields)
        with open("backend/models.py", "w", encoding="utf-8") as f:
            f.write(models_code)
        print("Added subject column to models.py.")

    # 2. Update backend/schemas.py
    with open("backend/schemas.py", "r", encoding="utf-8") as f:
        schemas_code = f.read()

    old_user_base = """class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str  # 'admin', 'teacher', 'student'
    phone: Optional[str] = None
    is_active: Optional[bool] = True"""

    new_user_base = """class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str  # 'admin', 'teacher', 'student'
    phone: Optional[str] = None
    subject: Optional[str] = None
    is_active: Optional[bool] = True"""

    if "subject: Optional[str]" not in schemas_code:
        schemas_code = schemas_code.replace(old_user_base, new_user_base)
        with open("backend/schemas.py", "w", encoding="utf-8") as f:
            f.write(schemas_code)
        print("Added subject property to UserBase schema.")

    # 3. Update backend/routers/auth.py
    with open("backend/routers/auth.py", "r", encoding="utf-8") as f:
        auth_code = f.read()

    old_user_creation = """    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role=user_in.role,
        phone=user_in.phone,
        is_active=user_in.is_active
    )"""

    new_user_creation = """    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role=user_in.role,
        phone=user_in.phone,
        subject=user_in.subject,
        is_active=user_in.is_active
    )"""

    if "subject=user_in.subject" not in auth_code:
        auth_code = auth_code.replace(old_user_creation, new_user_creation)
        with open("backend/routers/auth.py", "w", encoding="utf-8") as f:
            f.write(auth_code)
        print("Associated subject with new User in auth.py registration.")

    # 4. Update backend/routers/reports.py
    with open("backend/routers/reports.py", "r", encoding="utf-8") as f:
        reports_code = f.read()

    old_teacher_stats = """        teacher_stats.append({
            "id": t.id,
            "username": t.username,
            "email": t.email,
            "phone": t.phone,
            "batches_count": len(t_batches),
            "students_count": t_student_count,
            "average_attendance": avg_attendance
        })"""

    new_teacher_stats = """        teacher_stats.append({
            "id": t.id,
            "username": t.username,
            "email": t.email,
            "phone": t.phone,
            "subject": t.subject,
            "batches_count": len(t_batches),
            "students_count": t_student_count,
            "average_attendance": avg_attendance
        })"""

    if '"subject": t.subject' not in reports_code:
        reports_code = reports_code.replace(old_teacher_stats, new_teacher_stats)
        with open("backend/routers/reports.py", "w", encoding="utf-8") as f:
            f.write(reports_code)
        print("Added subject to reports.py global statistics.")

    # 5. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Table Header Subject column
    old_table_header = """                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                            <th>Status</th>"""

    new_table_header = """                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                            <th>Subject</th>
                                            <th>Status</th>"""

    html = html.replace(old_table_header, new_table_header)

    # Add Subject Input field inside Add Teacher Modal
    old_modal_form = """                    <div class="form-group">
                        <label for="teach-phone">Phone Number</label>
                        <input type="tel" id="teach-phone" placeholder="e.g. 9876543210" required>
                    </div>"""

    new_modal_form = """                    <div class="form-group">
                        <label for="teach-phone">Phone Number</label>
                        <input type="tel" id="teach-phone" placeholder="e.g. 9876543210" required>
                    </div>
                    <div class="form-group">
                        <label for="teach-subject">Subject / Course Specialization</label>
                        <input type="text" id="teach-subject" placeholder="e.g. Beauty Care Assistant" required style="padding: 12px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; width: 100%;">
                    </div>"""

    html = html.replace(old_modal_form, new_modal_form)

    # Bump version
    html = html.replace("app.js?v=19", "app.js?v=20")
    html = html.replace("style.css?v=19", "style.css?v=20")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html elements.")

    # 6. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Teachers table row mapping
    old_teacher_row = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>"""

    new_teacher_row = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>"""

    js = js.replace(old_teacher_row, new_teacher_row)

    # Register Teacher Submit payload
    old_submit_payload = """document.getElementById("teacher-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById("teach-username").value,
        email: document.getElementById("teach-email").value,
        password: document.getElementById("teach-password").value,
        role: "teacher"
    };"""

    new_submit_payload = """document.getElementById("teacher-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById("teach-username").value,
        email: document.getElementById("teach-email").value,
        phone: document.getElementById("teach-phone").value,
        subject: document.getElementById("teach-subject").value,
        password: document.getElementById("teach-password").value,
        role: "teacher"
    };"""

    js = js.replace(old_submit_payload, new_submit_payload)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js mapping and submit handler.")

if __name__ == "__main__":
    apply_teacher_subject_field()
