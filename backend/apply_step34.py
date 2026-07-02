def revert_and_increase_logo_size():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Current login logos layout (white badge box)
    old_login_logos = """            <div class="glass-card login-card">
                <div class="login-logo-container" style="background: #ffffff; padding: 12px 24px; border-radius: 12px; display: flex; align-items: center; justify-content: center; gap: 15px; margin: 0 auto 25px auto; width: fit-content; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
                    <img src="/static/assets/jss_logo.jpg" alt="JSS Logo" style="height: 42px; width: 42px; border-radius: 50%; display: block;">
                    <div style="width: 1px; height: 32px; background: rgba(0, 0, 0, 0.15);"></div>
                    <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="height: 42px; border-radius: 4px; display: block;">
                </div>"""

    # Side-by-side layout (first version) but with size increased to 65px height
    new_login_logos = """            <div class="glass-card login-card">
                <div class="login-logos" style="display: flex; justify-content: center; gap: 18px; margin-bottom: 25px; align-items: center;">
                    <img src="/static/assets/jss_logo.jpg" alt="JSS Logo" style="height: 65px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.15);">
                    <img src="/static/assets/jss_banner.jpg" alt="JSS Banner" style="height: 65px; border-radius: 8px; border: 1.5px solid rgba(255,255,255,0.15);">
                </div>"""

    html = html.replace(old_login_logos, new_login_logos)

    # Bump version
    html = html.replace("app.js?v=31", "app.js?v=32")
    html = html.replace("style.css?v=31", "style.css?v=32")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Reverted to larger side-by-side logo layout on the login card.")

if __name__ == "__main__":
    revert_and_increase_logo_size()
