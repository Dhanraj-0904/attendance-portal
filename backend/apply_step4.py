import re

def remove_audit_logs():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove Audit Logs sidebar navigation item
    html = re.sub(r'<a href="#admin-logs".*?</a>', "", html, flags=re.DOTALL)

    # Remove the entire Audit Logs Tab (section)
    html = re.sub(r'<!-- ================= ADMIN AUDIT LOGS TAB ================= -->.*?<!-- ================= TEACHER DASHBOARD TAB ================= -->',
                  '<!-- ================= TEACHER DASHBOARD TAB ================= -->', html, flags=re.DOTALL)

    # Bump version tags
    html = html.replace('style.css?v=5.1', 'style.css?v=6')
    html = html.replace('app.js?v=5', 'app.js?v=6')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html by removing Audit Logs tab successfully.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Remove from loadTabData check
    js = js.replace("else if (tabId === \"admin-logs\") loadAdminLogs();\n    ", "")
    
    # Remove loadAdminLogs function definition
    js_func_pattern = r'async function loadAdminLogs\(\).*?\}\s*\}\s*catch \(err\) \{\s*showToast\(err\.message, "error"\);\s*\}\s*\}'
    js = re.sub(js_func_pattern, "", js, flags=re.DOTALL)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js by removing loadAdminLogs function successfully.")

if __name__ == "__main__":
    remove_audit_logs()
