import re

def apply_brand_and_theme_toggles():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Rebrand title, logo text and tags
    html = html.replace("<title>NGO Attendance Management Portal</title>", "<title>JSS Attendance Portal</title>")
    html = html.replace('<span class="brand-tag">NGO Portal</span>', '<span class="brand-tag">JSS Attendance Portal</span>')
    html = html.replace('<h2>NGO Attendance Portal</h2>', '<h2>JSS Attendance Portal</h2>')
    html = html.replace('<h3>NGO COORDINATOR</h3>', '<h3>JSS COORDINATOR</h3>')

    # Inject login theme toggle button
    login_screen_pattern = r'(<div id="login-screen" class="screen active">)'
    login_toggle_btn = '\n            <button id="theme-toggle-login" class="btn btn-secondary" style="position: absolute; top: 20px; right: 20px; z-index: 1000;">🌓 Theme</button>'
    html = re.sub(login_screen_pattern, r'\1' + login_toggle_btn, html)

    # Inject header theme toggle button
    header_actions_pattern = r'(<div class="header-actions">)'
    header_toggle_btn = '\n                    <button id="theme-toggle-main" class="btn btn-secondary" style="margin-right: 12px;">🌓 Theme</button>'
    html = re.sub(header_actions_pattern, r'\1' + header_toggle_btn, html)

    # Bump version parameters
    html = html.replace('/static/style.css?v=3.2', '/static/style.css?v=4')
    html = html.replace('/static/app.js?v=3.1', '/static/app.js?v=4')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html successfully.")

    # 2. Update style.css
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    # Append Light Theme styles to end of style.css
    light_theme_styles = """

/* ================= LIGHT THEME STYLES ================= */
body.light-theme {
    background: radial-gradient(circle at 50% 50%, #f4f5f7 0%, #e2e8f0 100%);
    color: #1e293b;
    --card-bg: rgba(255, 255, 255, 0.7);
    --card-border: rgba(30, 41, 59, 0.1);
    --text-main: #0f172a;
    --text-muted: #475569;
    --primary-color: #6200ea;
    --secondary-color: #00838f;
}

body.light-theme .main-header {
    background: rgba(248, 250, 252, 0.85);
    border-bottom-color: rgba(30, 41, 59, 0.1);
}

body.light-theme .sidebar {
    background: rgba(248, 250, 252, 0.45);
    border-right-color: rgba(30, 41, 59, 0.1);
}

body.light-theme .nav-item:hover {
    background: rgba(30, 41, 59, 0.04);
    color: #0f172a;
}

body.light-theme .nav-item.active {
    background: rgba(98, 0, 234, 0.1);
    border-color: rgba(98, 0, 234, 0.2);
    color: #6200ea;
}

body.light-theme .data-table th {
    color: #475569;
    border-bottom-color: rgba(30, 41, 59, 0.1);
}

body.light-theme .data-table td {
    border-bottom-color: rgba(30, 41, 59, 0.05);
}

body.light-theme .data-table tbody tr:hover {
    background: rgba(30, 41, 59, 0.02);
}

body.light-theme .form-group input, body.light-theme .form-group select {
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(30, 41, 59, 0.15);
    color: #0f172a;
}

body.light-theme .form-group input:focus, body.light-theme .form-group select:focus {
    border-color: #6200ea;
    box-shadow: 0 0 10px rgba(98, 0, 234, 0.15);
}

body.light-theme .modal {
    background: rgba(15, 23, 42, 0.4);
}

body.light-theme .progress-ring-container {
    background: radial-gradient(circle, #ffffff 60%, transparent 61%), conic-gradient(#6200ea 0%, #cbd5e1 0%);
    box-shadow: 0 0 20px rgba(98,0,234,0.1);
}

body.light-theme .brand-tag {
    background: rgba(98, 0, 234, 0.08);
    color: #6200ea;
}

body.light-theme .drop-zone {
    border-color: rgba(30, 41, 59, 0.2);
    background: rgba(255, 255, 255, 0.5);
}

body.light-theme .drop-zone:hover {
    border-color: #6200ea;
    background: rgba(98, 0, 234, 0.02);
}

body.light-theme .toast {
    background: rgba(255, 255, 255, 0.95);
    color: #0f172a;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}
"""
    if "/* ================= LIGHT THEME STYLES ================= */" not in css:
        css += light_theme_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css successfully.")

    # 3. Update app.js to include theme initialization and listener
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Define initTheme function
    init_theme_js = """
// Theme Management Logic
function initTheme() {
    const currentTheme = localStorage.getItem("theme") || "dark";
    if (currentTheme === "light") {
        document.body.classList.add("light-theme");
    }
    
    const toggleLogin = document.getElementById("theme-toggle-login");
    const toggleMain = document.getElementById("theme-toggle-main");

    const toggleTheme = () => {
        document.body.classList.toggle("light-theme");
        const theme = document.body.classList.contains("light-theme") ? "light" : "dark";
        localStorage.setItem("theme", theme);
    };

    if (toggleLogin) toggleLogin.addEventListener("click", toggleTheme);
    if (toggleMain) toggleMain.addEventListener("click", toggleTheme);
}
"""

    if "function initTheme()" not in js:
        # Prepend to the top of app.js
        js = init_theme_js + "\n" + js

    # Make sure initTheme is called on DOMContentLoaded
    old_dom_listener = """window.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    setupScreenForRole();
});"""

    new_dom_listener = """window.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initNavigation();
    setupScreenForRole();
});"""

    js = js.replace(old_dom_listener, new_dom_listener)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_brand_and_theme_toggles()
