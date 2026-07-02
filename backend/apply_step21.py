def apply_show_password_feature():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Wrap login password input
    old_login_password = """                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <input type="password" id="login-password" placeholder="••••••••" required>
                    </div>"""

    new_login_password = """                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <div class="password-wrapper">
                            <input type="password" id="login-password" placeholder="••••••••" required>
                            <span class="password-toggle" onclick="togglePasswordVisibility('login-password', this)">👁️</span>
                        </div>
                    </div>"""

    html = html.replace(old_login_password, new_login_password)

    # Wrap register teacher password input
    old_teach_password = """                    <div class="form-group">
                        <label for="teach-password">Password</label>
                        <input type="password" id="teach-password" placeholder="Min 6 characters" required>
                    </div>"""

    new_teach_password = """                    <div class="form-group">
                        <label for="teach-password">Password</label>
                        <div class="password-wrapper">
                            <input type="password" id="teach-password" placeholder="Min 6 characters" required>
                            <span class="password-toggle" onclick="togglePasswordVisibility('teach-password', this)">👁️</span>
                        </div>
                    </div>"""

    html = html.replace(old_teach_password, new_teach_password)

    # Bump version in script/link tags
    html = html.replace("app.js?v=16", "app.js?v=17")
    html = html.replace("style.css?v=16", "style.css?v=17")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrapped password inputs in index.html.")

    # 2. Update style.css
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    password_styles = """
/* ================= PASSWORD TOGGLE SYSTEM ================= */
.password-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
}
.password-wrapper input {
    width: 100%;
    padding-right: 40px !important;
}
.password-toggle {
    position: absolute;
    right: 12px;
    cursor: pointer;
    user-select: none;
    font-size: 16px;
    opacity: 0.7;
    transition: opacity 0.2s ease;
}
.password-toggle:hover {
    opacity: 1;
}
"""
    if ".password-wrapper" not in css:
        css += password_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Appended password toggle styles to style.css.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    toggle_func = """
// Helper to toggle password visibility
function togglePasswordVisibility(inputId, toggleEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === "password") {
        input.type = "text";
        toggleEl.innerText = "🙈";
    } else {
        input.type = "password";
        toggleEl.innerText = "👁️";
    }
}
"""
    if "togglePasswordVisibility" not in js:
        js += toggle_func

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected togglePasswordVisibility function into app.js.")

if __name__ == "__main__":
    apply_show_password_feature()
