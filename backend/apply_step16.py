import re

def apply_teacher_csv_upload():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Add Actions column header to Teachers table
    old_table_header = """                                    <thead>
                                        <tr>
                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                            <th>Status</th>
                                            <th>Created At</th>
                                        </tr>
                                    </thead>"""

    new_table_header = """                                    <thead>
                                        <tr>
                                            <th>Username</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                            <th>Status</th>
                                            <th>Created At</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>"""
    html = html.replace(old_table_header, new_table_header)

    # Append the teacher-student-upload-modal to the bottom of the body (before final scripts)
    modal_content = """
        <!-- Teacher Student CSV Upload Modal -->
        <div id="teacher-student-upload-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2 id="teacher-upload-modal-title" style="font-size: 18px;">Upload Students for Teacher</h2>
                    <span class="close-btn" onclick="closeModal('teacher-student-upload-modal')">&times;</span>
                </div>
                <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px; line-height: 1.4;">
                    Upload the master student list CSV. Students will be automatically grouped and allocated to their respective batches matching their course department.
                </p>
                <form id="teacher-student-upload-form">
                    <input type="hidden" id="teacher-upload-teacher-id">
                    <div class="form-group">
                        <label for="teacher-student-file-input">Select Master CSV File</label>
                        <input type="file" id="teacher-student-file-input" accept=".csv" required style="padding: 8px; border: 1px solid var(--card-border); border-radius: 8px; width: 100%; background: rgba(255,255,255,0.03); color: var(--text-main);">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">⚡ Sync Teacher's Students</button>
                </form>
            </div>
        </div>
"""

    if "teacher-student-upload-modal" not in html:
        # Insert before </body>
        html = html.replace("    <script src=\"/static/app.js?v=12\"></script>", modal_content + "\n    <script src=\"/static/app.js?v=13\"></script>")
        # Bump stylesheet version
        html = html.replace("style.css?v=12", "style.css?v=13")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html modal markup.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update loadAdminTeachers to output Actions buttons cell
    old_row_map = """        const body = document.getElementById("admin-teachers-table-body");
        body.innerHTML = data.teachers.map(t => `
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
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    js = js.replace(old_row_map, new_row_map)

    # Inject DOMContentLoaded listener for teacher-student-upload-form
    form_submit_js = """
    // Teacher Student List CSV Upload Form Handler
    const teacherStudentUploadForm = document.getElementById("teacher-student-upload-form");
    if (teacherStudentUploadForm) {
        teacherStudentUploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const teacherId = document.getElementById("teacher-upload-teacher-id").value;
            const fileInput = document.getElementById("teacher-student-file-input");

            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please choose a CSV file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("teacher_id", teacherId);
            formData.append("file", fileInput.files[0]);

            try {
                showToast("Uploading and syncing students for teacher...", "info");
                const res = await fetch(`${API_URL}/sync/teacher-admin-upload`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${state.token}`
                    },
                    body: formData
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Upload failed");
                }

                const data = await res.json();
                showToast(data.message);
                
                teacherStudentUploadForm.reset();
                closeModal("teacher-student-upload-modal");
                loadAdminStudents();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
"""

    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + form_submit_js)

    # Add openUploadCSVForTeacher controller at the bottom of the file
    controller_js = """
// Helper to open Teacher Student CSV upload modal
function openUploadCSVForTeacher(teacherId, teacherName) {
    document.getElementById("teacher-upload-teacher-id").value = teacherId;
    document.getElementById("teacher-upload-modal-title").innerText = `Upload Students for ${teacherName}`;
    openModal("teacher-student-upload-modal");
}
"""
    js += controller_js

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected app.js controller and form handlers.")

if __name__ == "__main__":
    apply_teacher_csv_upload()
