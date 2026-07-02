import re

def remove_from_index_html():
    file_path = "backend/static/index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove Student Nav Group
    nav_pattern = r'<!-- Student Navigation -->\s*<div id="nav-student" class="nav-group hidden">.*?</div>'
    content = re.sub(nav_pattern, "", content, flags=re.DOTALL)

    # 2. Remove Student Dashboard Section
    tab_pattern = r'<!-- ================= STUDENT DASHBOARD TAB ================= -->\s*<section id="tab-student-dashboard" class="tab-content">.*?</section>'
    content = re.sub(tab_pattern, "", content, flags=re.DOTALL)

    # 3. Remove Student registration modal if they only want CSV import
    # Let's keep the modal just in case, but remove student login help footer
    content = content.replace("or <code>student</code> / <code>student123</code>", "")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed student elements from index.html successfully.")

def remove_from_app_js():
    file_path = "backend/static/app.js"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove student tab loading
    content = content.replace('else if (tabId === "student-dashboard") loadStudentDashboard();', "")
    
    # Remove student routing check
    student_route_pattern = r'\} else if \(state\.role === "student"\) \{\s*document\.getElementById\("nav-student"\)\.classList\.remove\("hidden"\);\s*switchTab\("student-dashboard"\);\s*\}'
    content = re.sub(student_route_pattern, "", content, flags=re.DOTALL)

    # Remove student directory query filtering by student role
    student_query_pattern = r'elif current_user\.role == "student":.*?query = query\.filter\(Student\.user_id == current_user\.id\)'
    # (Since this is in backend, let's keep it in python but remove student dashboard JS logic)
    
    # Remove entire loadStudentDashboard function in JS
    js_func_pattern = r'// ================= STUDENT LOGIC =================.*?window\.addEventListener\("DOMContentLoaded"'
    content = re.sub(js_func_pattern, 'window.addEventListener("DOMContentLoaded"', content, flags=re.DOTALL)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed student logic from app.js successfully.")

def remove_from_auth_py():
    file_path = "backend/routers/auth.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove student user creation in seeding
    student_seed_pattern = r'student = User\(.*?role="student",.*?is_active=True\s*\)'
    content = re.sub(student_seed_pattern, "", content, flags=re.DOTALL)
    
    # Clean up add_all statement: remove student reference
    content = content.replace("db.add_all([admin, teacher, student])", "db.add_all([admin, teacher])")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed student seeding from auth.py successfully.")

if __name__ == "__main__":
    remove_from_index_html()
    remove_from_app_js()
    remove_from_auth_py()
