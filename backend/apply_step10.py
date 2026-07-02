import re

def apply_step10_add_student_feature():
    # 1. Update backend/routers/students.py (inject ManualStudentCreate schema and endpoint)
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        students_code = f.read()

    schema_def = """
from pydantic import BaseModel

class ManualStudentCreate(BaseModel):
    batch_id: int
    sid_student_id: str
    name: str
"""

    route_def = """

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
            role="student"
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
"""

    if "class ManualStudentCreate" not in students_code:
        students_code = schema_def + students_code

    if "/add-manual" not in students_code:
        students_code += route_def

    with open("backend/routers/students.py", "w", encoding="utf-8") as f:
        f.write(students_code)
    print("Injected /students/add-manual endpoint in students.py successfully.")

    # 2. Update index.html to add the modal overlay
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    modal_html = """
        <!-- Add Student for Teacher Modal -->
        <div id="teacher-add-student-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2 style="font-size: 18px;">➕ Add Student under <span id="add-student-teacher-display-name"></span></h2>
                    <span class="close-btn" onclick="closeModal('teacher-add-student-modal')">&times;</span>
                </div>
                <form id="teacher-add-student-form">
                    <input type="hidden" id="add-student-teacher-id">
                    <div class="form-group">
                        <label for="add-student-batch">Select Target Batch</label>
                        <select id="add-student-batch" required>
                            <option value="">-- Choose Batch --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="add-student-sid">Unique Student ID Code (Attendance ID)</label>
                        <input type="text" id="add-student-sid" placeholder="e.g. STD12345" required>
                        <small style="color: var(--text-muted); font-size: 11px;">This unique code will also be their login username and password (default: student123).</small>
                    </div>
                    <div class="form-group">
                        <label for="add-student-name">Student Full Name</label>
                        <input type="text" id="add-student-name" placeholder="e.g. John Doe" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Add Student Profile & Create Account</button>
                </form>
            </div>
        </div>

    </div>"""

    # Replace end of app layout
    html = html.replace('\n    </div>\n    <script src="/static/app.js?v=8"></script>', modal_html + '\n    <script src="/static/app.js?v=8.1"></script>')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Injected teacher-add-student-modal markup in index.html successfully.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Modify loadAdminTeachers() to show the + Add Student link
    old_load_teachers_mapping = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td><strong>${t.username}</strong></td>
                <td>${t.username}@ngo.org</td>
                <td>9876543210</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No teachers registered</td></tr>`;"""

    new_load_teachers_mapping = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                    <br>
                    <a href="#" onclick="openAddStudentForTeacher(${t.id}, '${t.username}'); return false;" style="font-size: 11px; color: var(--primary-color); text-decoration: underline; margin-top: 4px; display: inline-block;">➕ Add Student</a>
                </td>
                <td>${t.username}@ngo.org</td>
                <td>9876543210</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No teachers registered</td></tr>`;"""

    js = js.replace(old_load_teachers_mapping, new_load_teachers_mapping)

    # Append openAddStudentForTeacher helper function at the bottom of the file
    open_helper_js = """
// Helper to open Add Student for Teacher modal
async function openAddStudentForTeacher(teacherId, teacherName) {
    document.getElementById("add-student-teacher-id").value = teacherId;
    document.getElementById("add-student-teacher-display-name").innerText = teacherName;
    
    const batchSelect = document.getElementById("add-student-batch");
    batchSelect.innerHTML = `<option value="">-- Loading Batches... --</option>`;
    
    try {
        const res = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load batches");
        const batches = await res.json();
        
        const teacherBatches = batches.filter(b => b.teacher_id === teacherId);
        
        if (teacherBatches.length === 0) {
            batchSelect.innerHTML = `<option value="">-- No batches assigned to this instructor --</option>`;
        } else {
            batchSelect.innerHTML = `<option value="">-- Choose Batch --</option>` + 
                teacherBatches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("");
        }
    } catch (err) {
        showToast(err.message, "error");
        batchSelect.innerHTML = `<option value="">-- Error loading batches --</option>`;
    }
    
    openModal("teacher-add-student-modal");
}
"""

    # Inject DOMContentLoaded handler for teacher-add-student-form
    form_submit_js = """
    // Add Student for Teacher Form Handler
    const addStudentTeacherForm = document.getElementById("teacher-add-student-form");
    if (addStudentTeacherForm) {
        addStudentTeacherForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const teacherId = document.getElementById("add-student-teacher-id").value;
            const batchId = document.getElementById("add-student-batch").value;
            const sidStudentId = document.getElementById("add-student-sid").value.trim();
            const name = document.getElementById("add-student-name").value.trim();

            if (!batchId) {
                showToast("Please select a target batch", "error");
                return;
            }

            try {
                showToast("Adding student profile & creating account...", "info");
                const res = await fetch(`${API_URL}/students/add-manual`, {
                    method: "POST",
                    headers: getHeaders(),
                    body: JSON.stringify({
                        batch_id: parseInt(batchId),
                        sid_student_id: sidStudentId,
                        name: name
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Failed to add student");
                }

                const data = await res.json();
                showToast(data.message);
                closeModal("teacher-add-student-modal");
                
                if (state.currentTab === "admin-teachers") {
                    loadAdminTeachers();
                }
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
"""

    # Inject inside DOMContentLoaded
    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + form_submit_js)
    
    # Append the helper function
    js += open_helper_js

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js with teacher student registration helper successfully.")

if __name__ == "__main__":
    apply_step10_add_student_feature()
