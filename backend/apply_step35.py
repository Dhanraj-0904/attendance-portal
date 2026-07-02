def apply_central_teacher_deletion():
    # 1. Update backend/routers/auth.py
    with open("backend/routers/auth.py", "r", encoding="utf-8") as f:
        auth_code = f.read()

    delete_endpoint = """

@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    if current_user.id == teacher_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")

    teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    batches = db.query(Batch).filter(Batch.teacher_id == teacher_id).all()
    for b in batches:
        students = db.query(Student).filter(Student.batch_id == b.id).all()
        for s in students:
            db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id).delete()
            if s.user_id:
                db.query(User).filter(User.id == s.user_id).delete()
            db.delete(s)
        db.delete(b)

    from ..models import LeaveRequest
    db.query(LeaveRequest).filter(LeaveRequest.teacher_id == teacher_id).delete()

    db.delete(teacher)
    db.commit()

    log_action(db, current_user.id, "delete_teacher", "users", teacher_id)
    return {"message": f"Successfully deleted teacher '{teacher.username}' and all associated batches and students."}
"""

    if "/teachers/{teacher_id}" not in auth_code:
        auth_code += delete_endpoint
        with open("backend/routers/auth.py", "w", encoding="utf-8") as f:
            f.write(auth_code)
        print("Appended delete_teacher endpoint in auth.py.")

    # 2. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    old_action_bar = """                    <!-- ================= ADMIN TEACHERS TAB ================= -->
                    <section id="tab-admin-teachers" class="tab-content">
                        <div class="tab-header-action">
                            <div>
                                <h1>Teacher Management</h1>
                                <p>Create, edit, and manage teacher profiles and login accounts.</p>
                            </div>
                            <button class="btn btn-primary" onclick="openModal('teacher-modal')">+ Add Teacher</button>
                        </div>"""

    new_action_bar = """                    <!-- ================= ADMIN TEACHERS TAB ================= -->
                    <section id="tab-admin-teachers" class="tab-content">
                        <div class="tab-header-action">
                            <div>
                                <h1>Teacher Management</h1>
                                <p>Create, edit, and manage teacher profiles and login accounts.</p>
                            </div>
                            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                                <select id="delete-teacher-select" style="padding: 10px 14px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; min-width: 220px; outline: none; cursor: pointer;">
                                    <option value="">-- Choose Teacher to Delete --</option>
                                </select>
                                <button class="btn btn-destructive" onclick="deleteSelectedTeacher()">🗑️ Delete Teacher</button>
                                <button class="btn btn-primary" onclick="openModal('teacher-modal')">+ Add Teacher</button>
                            </div>
                        </div>"""

    html = html.replace(old_action_bar, new_action_bar)

    # Bump version
    html = html.replace("app.js?v=32", "app.js?v=33")
    html = html.replace("style.css?v=32", "style.css?v=33")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html with header dropdown for deleting teachers.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Change loadAdminTeachers mapper and dropdown populator
    old_teachers_list_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    new_teachers_list_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No teachers registered</td></tr>`;

        // Populate delete dropdown selector
        const deleteSelect = document.getElementById("delete-teacher-select");
        if (deleteSelect) {
            deleteSelect.innerHTML = `<option value="">-- Choose Teacher to Delete --</option>` + 
                data.teachers.map(t => `<option value="${t.id}">${t.username} (${t.subject || 'No Subject'})</option>`).join("");
        }"""

    js = js.replace(old_teachers_list_renderer, new_teachers_list_renderer)

    # Append deleteSelectedTeacher helper at the end
    delete_func_js = """
// Centralized function to delete select teacher and their student records cascadingly
async function deleteSelectedTeacher() {
    const select = document.getElementById("delete-teacher-select");
    if (!select) return;
    const teacherId = select.value;
    if (!teacherId) {
        showToast("Please choose a teacher to delete first", "error");
        return;
    }
    const teacherText = select.options[select.selectedIndex].text;
    
    if (!confirm(`CRITICAL WARNING: Are you sure you want to delete teacher "${teacherText}"? This will permanently delete the teacher account, all their assigned batches, all student profiles in those batches, and all their attendance history! This action CANNOT be undone.`)) {
        return;
    }
    
    try {
        showToast("Deleting teacher and all associated data...", "info");
        const res = await fetch(`${API_URL}/auth/teachers/${teacherId}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        
        const data = await res.json();
        showToast(data.message);
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
}
"""
    js += delete_func_js

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected central deleteSelectedTeacher JS controller and row actions update.")

if __name__ == "__main__":
    apply_central_teacher_deletion()
