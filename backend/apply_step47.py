def apply_bulletproof_edit_modal():
    # 1. Update index.html - bump version to v=44 to break browser cache
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("app.js?v=43", "app.js?v=44")
    html = html.replace("style.css?v=43", "style.css?v=44")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Bumped version to v=44 in index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_open_edit_student = """// Helper to open Edit Student modal
function openEditStudent(studentId, name, phone) {
    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    document.getElementById("edit-student-phone").value = phone || "";
    openModal("edit-student-modal");
}"""

    new_open_edit_student = """// Helper to open Edit Student modal
function openEditStudent(studentId, name, phone) {
    // Inject edit modal dynamically if it doesn't exist in DOM (safeguard against caching)
    if (!document.getElementById("edit-student-modal")) {
        const modalDiv = document.createElement("div");
        modalDiv.id = "edit-student-modal";
        modalDiv.className = "modal";
        modalDiv.innerHTML = `
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
        `;
        document.body.appendChild(modalDiv);

        // Wire up the submit listener for the dynamically generated form
        const form = document.getElementById("edit-student-form");
        if (form) {
            form.addEventListener("submit", async (e) => {
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
                    
                    // Refresh current view depending on role
                    const activeBatchId = document.getElementById("admin-student-upload-batch-id") ? document.getElementById("admin-student-upload-batch-id").value : null;
                    if (activeBatchId) {
                        viewAdminBatchDetails(activeBatchId);
                    }
                    if (state.selectedBatchId) {
                        viewTeacherBatchDetails(state.selectedBatchId);
                    }
                    loadAdminStudents();
                } catch (err) {
                    showToast(err.message, "error");
                }
            });
        }
    }

    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    document.getElementById("edit-student-phone").value = phone || "";
    openModal("edit-student-modal");
}"""

    js = js.replace(old_open_edit_student, new_open_edit_student)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected bulletproof dynamic modal creator to openEditStudent in app.js.")

if __name__ == "__main__":
    apply_bulletproof_edit_modal()
