def apply_delete_teacher_students():
    # 1. Update backend/routers/sync.py (append DELETE endpoint)
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync_code = f.read()

    delete_endpoint = """

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
"""

    if "/teacher-delete-students" not in sync_code:
        sync_code += delete_endpoint

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync_code)
    print("Injected delete endpoint into sync.py successfully.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Add Delete Students button to Teachers table mapping
    old_row_map = """        const body = document.getElementById("admin-teachers-table-body");
        body.innerHTML = data.teachers.map(t => `
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
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    new_row_map = """        const body = document.getElementById("admin-teachers-table-body");
        body.innerHTML = data.teachers.map(t => `
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

    js = js.replace(old_row_map, new_row_map)

    # Append controller at the bottom of the file
    controller_js = """
// Helper to delete all students from a teacher
async function deleteTeacherStudents(teacherId, teacherName) {
    if (!confirm(`WARNING: Are you sure you want to delete all students assigned to teacher "${teacherName}"? This will also remove their student login accounts and attendance records!`)) {
        return;
    }
    
    try {
        showToast("Deleting students...", "info");
        const res = await fetch(`${API_URL}/sync/teacher-delete-students/${teacherId}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        
        const data = await res.json();
        showToast(data.message);
        loadAdminStudents();
    } catch (err) {
        showToast(err.message, "error");
    }
}
"""
    if "deleteTeacherStudents" not in js:
        js += controller_js

    # Bump js version in index.html to reload cache
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("app.js?v=13", "app.js?v=14")
    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected app.js buttons and delete controller successfully.")

if __name__ == "__main__":
    apply_delete_teacher_students()
