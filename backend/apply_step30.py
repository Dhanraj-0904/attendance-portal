def apply_password_restriction_and_refresh():
    # 1. Update index.html (add id to Change Password button)
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    old_btn = '<button onclick="openResetPasswordModal(null, null, true)" class="btn btn-secondary" style="margin-right: 12px;">🔑 Change Password</button>'
    new_btn = '<button id="header-change-password-btn" onclick="openResetPasswordModal(null, null, true)" class="btn btn-secondary" style="margin-right: 12px;">🔑 Change Password</button>'

    html = html.replace(old_btn, new_btn)

    # Bump version to v=28
    html = html.replace("app.js?v=27", "app.js?v=28")
    html = html.replace("style.css?v=27", "style.css?v=28")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Added ID to header change password button in index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Hide/show button inside setupScreenForRole
    old_setup = """    if (state.role === "admin") {
        document.getElementById("nav-admin").classList.remove("hidden");
        switchTab("admin-dashboard");
    }"""

    new_setup = """    const changePassBtn = document.getElementById("header-change-password-btn");
    if (changePassBtn) {
        if (state.role === "admin") {
            changePassBtn.classList.remove("hidden");
        } else {
            changePassBtn.classList.add("hidden");
        }
    }

    if (state.role === "admin") {
        document.getElementById("nav-admin").classList.remove("hidden");
        switchTab("admin-dashboard");
    }"""

    js = js.replace(old_setup, new_setup)

    # Reload active tab data after password change success
    old_success = """                showToast("Password updated successfully");
                closeModal("reset-password-modal");
                resetPasswordForm.reset();"""

    new_success = """                showToast("Password updated successfully");
                closeModal("reset-password-modal");
                resetPasswordForm.reset();
                if (state.currentTab) {
                    loadTabData(state.currentTab);
                }"""

    js = js.replace(old_success, new_success)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected header button visibility rules and table refetch on success in app.js.")

if __name__ == "__main__":
    apply_password_restriction_and_refresh()
