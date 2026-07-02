def apply_cache_busting_and_theme_init():
    # 1. Update index.html to add cache-busting version query
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace('/static/style.css', '/static/style.css?v=2.1')
    html = html.replace('/static/app.js', '/static/app.js?v=2.1')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Applied cache-busting to index.html successfully.")

    # 2. Update app.js to call initTheme on DOMContentLoaded
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

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
    print("Injected initTheme call inside app.js successfully.")

if __name__ == "__main__":
    apply_cache_busting_and_theme_init()
