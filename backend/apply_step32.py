def apply_login_logo_positioning():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Old login logos layout (side-by-side)
    old_login_logos = """            <div class="glass-card login-card">
                <div class="login-logos" style="display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; align-items: center;">
                    <img src="/static/assets/jss_logo.jpg" alt="JSS Logo" style="height: 50px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.15);">
                    <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="height: 50px; border-radius: 8px; border: 1.5px solid rgba(255,255,255,0.15);">
                </div>"""

    # Clean centered single banner layout
    new_login_logos = """            <div class="glass-card login-card">
                <div class="login-logos" style="display: flex; justify-content: center; margin-bottom: 25px;">
                    <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="height: 60px; border-radius: 8px; border: 1.5px solid rgba(255,255,255,0.15); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
                </div>"""

    html = html.replace(old_login_logos, new_login_logos)

    # Bump version
    html = html.replace("app.js?v=29", "app.js?v=30")
    html = html.replace("style.css?v=29", "style.css?v=30")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Cleaned up login logo positioning to center the banner only.")

if __name__ == "__main__":
    apply_login_logo_positioning()
