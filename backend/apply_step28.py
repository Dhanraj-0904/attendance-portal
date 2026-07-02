def apply_password_reset_system():
    # 1. Update backend/routers/auth.py (Append change-password endpoint)
    with open("backend/routers/auth.py", "r", encoding="utf-8") as f:
        auth_code = f.read()

    password_endpoint = """

class PasswordReset(BaseModel):
    user_id: Optional[int] = None
    new_password: str

@router.post("/change-password")
def change_password(
    data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_user = None
    if data.user_id is not None:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can change other users' passwords.")
        target_user = db.query(User).filter(User.id == data.user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        target_user = current_user

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    target_user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    log_action(db, current_user.id, "change_password", "users", target_user.id)
    return {"message": f"Password for {target_user.username} updated successfully."}
"""

    if "/change-password" not in auth_code:
        auth_code += password_endpoint
        with open("backend/routers/auth.py", "w", encoding="utf-8") as f:
            f.write(auth_code)
        print("Added /change-password endpoint to auth.py.")

    # 2. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Add Change Password button in top header next to Logout
    old_header_actions = """                <div class="header-actions">
                    <button id="theme-toggle-main" class="btn btn-secondary" style="margin-right: 12px;">🌓 Theme</button>
                    <button id="logout-btn" class="btn btn-secondary">Log Out</button>
                </div>"""

    new_header_actions = """                <div class="header-actions">
                    <button id="theme-toggle-main" class="btn btn-secondary" style="margin-right: 12px;">🌓 Theme</button>
                    <button onclick="openResetPasswordModal(null, null, true)" class="btn btn-secondary" style="margin-right: 12px;">🔑 Change Password</button>
                    <button id="logout-btn" class="btn btn-secondary">Log Out</button>
                </div>"""

    html = html.replace(old_header_actions, new_header_actions)

    # Reset Password Modal Markup
    reset_modal = """
        <!-- Reset Password Modal -->
        <div id="reset-password-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2 id="reset-password-title">🔑 Change Password</h2>
                    <span class="close-btn" onclick="closeModal('reset-password-modal')">&times;</span>
                </div>
                <form id="reset-password-form">
                    <input type="hidden" id="reset-password-target-id">
                    <div class="form-group">
                        <label for="reset-new-password">New Password</label>
                        <div class="password-wrapper">
                            <input type="password" id="reset-new-password" placeholder="Min 6 characters" required style="padding: 12px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; width: 100%;">
                            <span class="password-toggle" onclick="togglePasswordVisibility('reset-new-password', this)">SHOW</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="reset-confirm-password">Confirm Password (Double Check)</label>
                        <div class="password-wrapper">
                            <input type="password" id="reset-confirm-password" placeholder="Confirm new password" required style="padding: 12px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; width: 100%;">
                            <span class="password-toggle" onclick="togglePasswordVisibility('reset-confirm-password', this)">SHOW</span>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">⚡ Update Password</button>
                </form>
            </div>
        </div>
"""

    # Insert before </body>
    html = html.replace('<script src="/static/app.js?v=25"></script>', reset_modal + '\n    <script src="/static/app.js?v=26"></script>')
    html = html.replace("app.js?v=25", "app.js?v=26")
    html = html.replace("style.css?v=25", "style.css?v=26")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html headers and modals.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Add Reset Password button in Teacher Actions row mapper
    old_teachers_actions = """                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>"""

    new_teachers_actions = """                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>"""

    js = js.replace(old_teachers_actions, new_teachers_actions)

    # Add Reset Password button in Batch Details Student actions
    old_student_row = """                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\\\\'")}', '${s.phone || ''}')">✏️ Edit</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                        </div>
                    </td>"""

    new_student_row = """                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\\\\'")}', '${s.phone || ''}')">✏️ Edit</button>
                            <button class="btn btn-secondary btn-small" onclick="openResetPasswordModal(${s.user_id}, '${s.sid_student_id}', false)">🔑 Password</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                        </div>
                    </td>"""

    js = js.replace(old_student_row, new_student_row)

    # Reset Password Form Submission listener inside DOMContentLoaded
    reset_form_listener = """
    // Reset Password Form Handler
    const resetPasswordForm = document.getElementById("reset-password-form");
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const targetIdVal = document.getElementById("reset-password-target-id").value;
            const newPassword = document.getElementById("reset-new-password").value;
            const confirmPassword = document.getElementById("reset-confirm-password").value;

            if (newPassword !== confirmPassword) {
                showToast("Error: Passwords do not match! Please double check.", "error");
                return;
            }

            try {
                showToast("Updating password...", "info");
                const res = await fetch(`${API_URL}/auth/change-password`, {
                    method: "POST",
                    headers: getHeaders(),
                    body: JSON.stringify({
                        user_id: targetIdVal ? parseInt(targetIdVal) : null,
                        new_password: newPassword
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Reset failed");
                }

                showToast("Password updated successfully");
                closeModal("reset-password-modal");
                resetPasswordForm.reset();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
"""

    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + reset_form_listener)

    # Append Reset password helpers at the bottom
    helpers_js = """
// Helper to open Reset Password modal
function openResetPasswordModal(userId, username, isSelf = false) {
    const titleEl = document.getElementById("reset-password-title");
    const targetIdInput = document.getElementById("reset-password-target-id");
    
    document.getElementById("reset-new-password").value = "";
    document.getElementById("reset-confirm-password").value = "";
    
    if (isSelf) {
        titleEl.innerText = "🔑 Change My Password";
        targetIdInput.value = "";
    } else {
        titleEl.innerText = `🔑 Reset Password for ${username}`;
        targetIdInput.value = userId;
    }
    
    openModal("reset-password-modal");
}
"""
    js += helpers_js

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected reset password JS helpers and controllers.")

if __name__ == "__main__":
    apply_password_reset_system()
