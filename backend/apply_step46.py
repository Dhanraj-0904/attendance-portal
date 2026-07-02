def apply_glitch_fixes():
    # 1. Update index.html - add Edit Student Modal and bump version to v=43
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    edit_student_modal_html = """        <!-- Edit Student Modal -->
        <div id="edit-student-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>Edit Student Details</h2>
                    <span class="close-btn" onclick="closeModal('edit-student-modal')">&times;</span>
                </div>
                <form id="edit-student-form">
                    <input type="hidden" id="edit-student-id">
                    <div class="form-group">
                        <label for="edit-student-name">Full Name</label>
                        <input type="text" id="edit-student-name" placeholder="e.g. Aarti Baghel" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-student-phone">Phone Number</label>
                        <input type="tel" id="edit-student-phone" placeholder="e.g. 9988776655">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Save Changes</button>
                </form>
            </div>
        </div>

    <script src="/static/app.js?v=42"></script>"""

    # Replace end scripts loader to inject the modal
    new_script_loader = edit_student_modal_html.replace("app.js?v=42", "app.js?v=43")
    html = html.replace("""    <script src="/static/app.js?v=42"></script>""", new_script_loader)
    html = html.replace("style.css?v=42", "style.css?v=43")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Added edit-student-modal and bumped asset versions to v=43 in index.html.")

    # 2. Update schemas.py
    with open("backend/schemas.py", "r", encoding="utf-8") as f:
        schemas = f.read()

    old_schema_definition = """class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    plain_password: Optional[str] = None
    attendance_pct: Optional[float] = 0.0
    status: Optional[str] = "ELIGIBLE"
    attended_sessions: Optional[int] = 0
    missed_sessions: Optional[int] = 0
    remaining_sessions: Optional[int] = 0
    still_need_to_attend: Optional[int] = 0
    can_skip: Optional[int] = 0

    class Config:
        from_attributes = True"""

    new_schema_definition = """class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    plain_password: Optional[str] = None
    attendance_pct: Optional[float] = 0.0
    status: Optional[str] = "ELIGIBLE"
    attended_sessions: Optional[int] = 0
    missed_sessions: Optional[int] = 0
    remaining_sessions: Optional[int] = 0
    still_need_to_attend: Optional[int] = 0
    can_skip: Optional[int] = 0

    # Frontend compatibility fields
    sessions_attended: Optional[int] = 0
    sessions_missed: Optional[int] = 0
    sessions_needed_for_75: Optional[int] = 0
    sessions_remaining: Optional[int] = 0
    total_hours: Optional[int] = 330

    class Config:
        from_attributes = True"""

    schemas = schemas.replace(old_schema_definition, new_schema_definition)
    with open("backend/schemas.py", "w", encoding="utf-8") as f:
        f.write(schemas)
    print("Updated StudentResponse model in schemas.py to include compatibility fields.")

    # 3. Update students.py
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        students_router = f.read()

    # We will modify get_student_with_stats
    old_fallback_dict = """        return {
            "id": student.id,
            "batch_id": student.batch_id,
            "aadhaar_hash": student.aadhaar_hash,
            "name": student.name,
            "phone": student.phone,
            "sid_student_id": student.sid_student_id,
            "is_active": student.is_active,
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

    new_fallback_dict = """        return {
            "id": student.id,
            "batch_id": student.batch_id,
            "aadhaar_hash": student.aadhaar_hash,
            "name": student.name,
            "phone": student.phone,
            "sid_student_id": student.sid_student_id,
            "is_active": student.is_active,
            "user_id": student.user_id,
            "plain_password": student.user.plain_password if student.user else None,
            "attendance_pct": 0.0,
            "status": "IMPOSSIBLE",
            "attended_sessions": 0,
            "missed_sessions": 0,
            "remaining_sessions": 0,
            "still_need_to_attend": 0,
            "can_skip": 0,
            "sessions_attended": 0,
            "sessions_missed": 0,
            "sessions_needed_for_75": 0,
            "sessions_remaining": 0,
            "total_hours": 330
        }"""

    old_success_dict = """    return {
        "id": student.id,
        "batch_id": student.batch_id,
        "aadhaar_hash": student.aadhaar_hash,
        "name": student.name,
        "phone": student.phone,
        "sid_student_id": student.sid_student_id,
        "is_active": student.is_active,
        "user_id": student.user_id,
        "plain_password": student.user.plain_password if student.user else None,
        "attendance_pct": elig["current_pct"],
        "status": elig["status"],
        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"],
        "total_hours": batch.total_hours if batch else 330
    }"""

    new_success_dict = """    return {
        "id": student.id,
        "batch_id": student.batch_id,
        "aadhaar_hash": student.aadhaar_hash,
        "name": student.name,
        "phone": student.phone,
        "sid_student_id": student.sid_student_id,
        "is_active": student.is_active,
        "user_id": student.user_id,
        "plain_password": student.user.plain_password if student.user else None,
        "attendance_pct": elig["current_pct"],
        "status": elig["status"],
        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"],
        "total_hours": batch.total_hours if batch else 330,
        "sessions_attended": attended,
        "sessions_missed": missed,
        "sessions_needed_for_75": elig["still_need_to_attend"],
        "sessions_remaining": remaining
    }"""

    students_router = students_router.replace(old_fallback_dict, new_fallback_dict)
    students_router = students_router.replace(old_success_dict, new_success_dict)

    with open("backend/routers/students.py", "w", encoding="utf-8") as f:
        f.write(students_router)
    print("Updated get_student_with_stats dictionary keys in students.py.")

if __name__ == "__main__":
    apply_glitch_fixes()
