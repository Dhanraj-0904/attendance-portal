import re

def apply_student_edit_and_delete_menu():
    # 1. Update backend/routers/students.py (add PUT endpoint & StudentUpdate schema)
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        student_router = f.read()

    new_endpoints = """

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
"""

    if "class StudentUpdate" not in student_router:
        student_router += new_endpoints

    with open("backend/routers/students.py", "w", encoding="utf-8") as f:
        f.write(student_router)
    print("Injected PUT /students/{id} endpoint successfully.")

    # 2. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Add Actions column header to admin batch students table
    html = html.replace('<th>Assessment Status</th>\n                                        </tr>\n                                    </thead>\n                                    <tbody id="admin-batch-students-body">\n                                        <tr><td colspan="7" class="text-center">Loading batch details...</td></tr>',
                        '<th>Assessment Status</th>\n                                            <th>Actions</th>\n                                        </tr>\n                                    </thead>\n                                    <tbody id="admin-batch-students-body">\n                                        <tr><td colspan="8" class="text-center">Loading batch details...</td></tr>')

    # Remove the manual teacher-add-student-modal completely
    # It starts around '<div id="teacher-add-student-modal"' and ends at '</div>\n        </div>'
    old_teacher_modal_pattern = r'<!-- Add Student for Teacher Modal -->\s*<div id="teacher-add-student-modal".*?</form>\s*</div>\s*</div>'
    html = re.sub(old_teacher_modal_pattern, '', html, flags=re.DOTALL)

    # Insert Edit Student Modal and Delete a Student Modal markups
    new_modals = """
        <!-- Edit Student Modal -->
        <div id="edit-student-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>✏️ Edit Student Details</h2>
                    <span class="close-btn" onclick="closeModal('edit-student-modal')">&times;</span>
                </div>
                <form id="edit-student-form">
                    <input type="hidden" id="edit-student-id">
                    <div class="form-group">
                        <label for="edit-student-name">Student Full Name</label>
                        <input type="text" id="edit-student-name" required style="padding: 8px; border: 1px solid var(--card-border); border-radius: 8px; width: 100%; background: rgba(255,255,255,0.03); color: var(--text-main);">
                    </div>
                    <div class="form-group">
                        <label for="edit-student-phone">Phone Number</label>
                        <input type="tel" id="edit-student-phone" style="padding: 8px; border: 1px solid var(--card-border); border-radius: 8px; width: 100%; background: rgba(255,255,255,0.03); color: var(--text-main);">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">⚡ Update Details</button>
                </form>
            </div>
        </div>

        <!-- Delete a Student Modal (Dropdown) -->
        <div id="teacher-delete-student-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2 id="delete-student-modal-title" style="font-size: 18px;">🗑️ Delete a Student</h2>
                    <span class="close-btn" onclick="closeModal('teacher-delete-student-modal')">&times;</span>
                </div>
                <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px;">
                    Select a student assigned to this teacher to delete their profile.
                </p>
                <form id="teacher-delete-student-form">
                    <input type="hidden" id="delete-student-teacher-id">
                    <div class="form-group">
                        <label for="delete-student-select">Choose Student to Delete</label>
                        <select id="delete-student-select" required style="padding: 8px; border: 1px solid var(--card-border); border-radius: 8px; width: 100%; background: var(--bg-card); color: var(--text-main);">
                            <option value="">-- Loading Students... --</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-destructive btn-block">🗑️ Delete Selected Student</button>
                </form>
            </div>
        </div>
"""

    if "edit-student-modal" not in html:
        # Insert before </body>
        html = html.replace('<script src="/static/app.js?v=13"></script>', new_modals + '\n    <script src="/static/app.js?v=15"></script>')
        html = html.replace('app.js?v=14', 'app.js?v=15')
        html = html.replace('style.css?v=13', 'style.css?v=15')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html layouts successfully.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update viewAdminBatchDetails rendering to include edit button
    old_row_render = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;"""

    new_row_render = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\\'")}', '${s.phone || ''}')">✏️ Edit</button>
                        </div>
                    </td>
                </tr>
            `;"""

    js = js.replace(old_row_render, new_row_render)
    js = js.replace('colspan="7" class="text-center">No students registered in this batch.', 'colspan="8" class="text-center">No students registered in this batch.')

    # Update loadAdminTeachers to show actual email/phone inputs and updated action buttons
    old_teachers_body = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.username}@ngo.org</td>
                <td>9876543210</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-primary btn-small" onclick="openAddStudentForTeacher(${t.id}, '${t.username}')">➕ Add Student</button>
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete Students</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    new_teachers_body = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openDeleteStudentDropdownForTeacher(${t.id}, '${t.username}')">🗑️ Delete Student</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    js = js.replace(old_teachers_body, new_teachers_body)

    # Delete the redundant openAddStudentForTeacher function from app.js
    # Starts around 'async function openAddStudentForTeacher' and ends at the next function declaration
    old_add_student_func_pattern = r'async function openAddStudentForTeacher.*?^}'
    js = re.sub(old_add_student_func_pattern, '', js, flags=re.DOTALL | re.MULTILINE)

    # Inject DOMContentLoaded handlers for Edit Student & Delete Student dropdown modals
    new_form_handlers = """
    // Edit Student Form Handler
    const editStudentForm = document.getElementById("edit-student-form");
    if (editStudentForm) {
        editStudentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const studentId = document.getElementById("edit-student-id").value;
            const data = {
                name: document.getElementById("edit-student-name").value,
                phone: document.getElementById("edit-student-phone").value
            };

            try {
                showToast("Updating student details...", "info");
                const res = await fetch(`${API_URL}/students/${studentId}`, {
                    method: "PUT",
                    headers: getHeaders(),
                    body: JSON.stringify(data)
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Update failed");
                }

                showToast("Student details updated successfully");
                closeModal("edit-student-modal");
                
                // Refresh list if batch is currently selected
                const activeBatchId = document.getElementById("admin-student-upload-batch-id") ? document.getElementById("admin-student-upload-batch-id").value : null;
                if (activeBatchId) {
                    viewAdminBatchDetails(activeBatchId);
                }
                loadAdminStudents();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // Teacher single student delete form submission (Dropdown)
    const teacherDeleteStudentForm = document.getElementById("teacher-delete-student-form");
    if (teacherDeleteStudentForm) {
        teacherDeleteStudentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const studentId = document.getElementById("delete-student-select").value;
            
            if (!studentId) {
                showToast("Please select a student first", "error");
                return;
            }

            const select = document.getElementById("delete-student-select");
            const studentName = select.options[select.selectedIndex].text;
            if (!confirm(`Are you sure you want to delete student "${studentName}"? This will permanently remove their profile and login details.`)) {
                return;
            }

            try {
                showToast("Deleting student...", "info");
                const res = await fetch(`${API_URL}/students/${studentId}`, {
                    method: "DELETE",
                    headers: getHeaders()
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Delete failed");
                }

                showToast("Student deleted successfully");
                closeModal("teacher-delete-student-modal");
                
                // Refresh active batch list if viewed
                const activeBatchId = document.getElementById("admin-student-upload-batch-id") ? document.getElementById("admin-student-upload-batch-id").value : null;
                if (activeBatchId) {
                    viewAdminBatchDetails(activeBatchId);
                }
                loadAdminStudents();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
"""

    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + new_form_handlers)

    # Append helper controllers for edit/delete dropdowns at the bottom
    extra_controllers = """
// Helper to open Edit Student modal
function openEditStudent(studentId, name, phone) {
    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    document.getElementById("edit-student-phone").value = phone || "";
    openModal("edit-student-modal");
}

// Helper to open Delete Student dropdown modal for Teacher
async function openDeleteStudentDropdownForTeacher(teacherId, teacherName) {
    document.getElementById("delete-student-teacher-id").value = teacherId;
    document.getElementById("delete-student-modal-title").innerText = `Delete a Student under ${teacherName}`;
    
    const select = document.getElementById("delete-student-select");
    select.innerHTML = `<option value="">-- Loading Students... --</option>`;
    
    try {
        const batchesRes = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        const batches = await batchesRes.json();
        const teacherBatchIds = batches.filter(b => b.teacher_id === teacherId).map(b => b.id);
        
        const studentsRes = await fetch(`${API_URL}/students/`, { headers: getHeaders() });
        const students = await studentsRes.json();
        const teacherStudents = students.filter(s => teacherBatchIds.includes(s.batch_id));
        
        if (teacherStudents.length === 0) {
            select.innerHTML = `<option value="">-- No students enrolled under this teacher --</option>`;
        } else {
            select.innerHTML = `<option value="">-- Choose Student --</option>` + 
                teacherStudents.map(s => `<option value="${s.id}">${s.name} (${s.sid_student_id})</option>`).join("");
        }
    } catch (err) {
        showToast(err.message, "error");
        select.innerHTML = `<option value="">-- Error loading students --</option>`;
    }
    
    openModal("teacher-delete-student-modal");
}
"""
    js += extra_controllers

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js controllers.")

if __name__ == "__main__":
    apply_student_edit_and_delete_menu()
