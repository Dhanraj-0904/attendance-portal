def apply_formal_password_toggle():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("togglePasswordVisibility('login-password', this)\">👁️</span>", "togglePasswordVisibility('login-password', this)\">SHOW</span>")
    html = html.replace("togglePasswordVisibility('teach-password', this)\">👁️</span>", "togglePasswordVisibility('teach-password', this)\">SHOW</span>")

    # Bump version in script/link tags
    html = html.replace("app.js?v=18", "app.js?v=19")
    html = html.replace("style.css?v=18", "style.css?v=19")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html to use formal text.")

    # 2. Update style.css
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    old_toggle_style = """.password-toggle {
    position: absolute;
    right: 14px;
    cursor: pointer;
    user-select: none;
    font-size: 18px;
    opacity: 0.85;
    transition: opacity 0.2s ease;
    z-index: 10;
    color: var(--text-muted);
}"""

    new_toggle_style = """.password-toggle {
    position: absolute;
    right: 14px;
    cursor: pointer;
    user-select: none;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--primary-color);
    opacity: 0.8;
    transition: opacity 0.2s ease;
    z-index: 10;
}"""

    css = css.replace(old_toggle_style, new_toggle_style)

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css for formal text visibility toggle.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_toggle_func = """// Helper to toggle password visibility
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
}"""

    new_toggle_func = """// Helper to toggle password visibility
function togglePasswordVisibility(inputId, toggleEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === "password") {
        input.type = "text";
        toggleEl.innerText = "HIDE";
    } else {
        input.type = "password";
        toggleEl.innerText = "SHOW";
    }
}"""

    js = js.replace(old_toggle_func, new_toggle_func)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js togglePasswordVisibility function.")

if __name__ == "__main__":
    apply_formal_password_toggle()
