def apply_branding_logos():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Place logos in Login Card
    old_login_brand = """            <div class="glass-card login-card">
                <div class="brand">"""

    new_login_brand = """            <div class="glass-card login-card">
                <div class="login-logos" style="display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; align-items: center;">
                    <img src="/static/assets/jss_logo.jpg" alt="JSS Logo" style="height: 50px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.15);">
                    <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="height: 50px; border-radius: 8px; border: 1.5px solid rgba(255,255,255,0.15);">
                </div>
                <div class="brand" style="margin-top: 10px;">"""

    html = html.replace(old_login_brand, new_login_brand)

    # Replace emoji 📊 in header-logo with the circular logo
    old_header_logo = """                <div class="header-logo">
                    <span class="logo-icon">📊</span>"""

    new_header_logo = """                <div class="header-logo">
                    <img src="/static/assets/jss_logo.jpg" alt="JSS Logo" style="height: 38px; width: 38px; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.15); margin-right: 8px;">"""

    html = html.replace(old_header_logo, new_header_logo)

    # Place JSS Banner at the top of the sidebar
    old_sidebar_top = """                <!-- Sidebar (Responsive Navigation) -->
                <aside class="sidebar">"""

    new_sidebar_top = """                <!-- Sidebar (Responsive Navigation) -->
                <aside class="sidebar">
                    <div class="sidebar-logo" style="padding: 0 10px 20px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
                        <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="width: 100%; border-radius: 6px; opacity: 0.95; border: 1px solid rgba(255,255,255,0.1);">
                    </div>"""

    html = html.replace(old_sidebar_top, new_sidebar_top)

    # Bump version
    html = html.replace("app.js?v=26", "app.js?v=29")
    html = html.replace("style.css?v=26", "style.css?v=29")
    html = html.replace("app.js?v=28", "app.js?v=29")
    html = html.replace("style.css?v=28", "style.css?v=29")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Injected logo branding layout updates into index.html.")

if __name__ == "__main__":
    apply_branding_logos()
