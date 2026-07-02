def apply_frontend_password_displays():
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # 1. Update loadAdminTeachers
    old_teachers_mapping = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>"""

    new_teachers_mapping = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>"""

    js = js.replace(old_teachers_mapping, new_teachers_mapping)

    # 2. Update viewAdminBatchDetails
    old_admin_batch_students = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>"""

    new_admin_batch_students = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>"""

    js = js.replace(old_admin_batch_students, new_admin_batch_students)

    # 3. Update loadAdminStudents
    old_admin_students = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>"""

    new_admin_students = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>"""

    js = js.replace(old_admin_students, new_admin_students)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected plain password sub-labels in app.js tables.")

    # 4. Bump version in index.html to v=27
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("app.js?v=26", "app.js?v=27")
    html = html.replace("style.css?v=26", "style.css?v=27")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Bumped version to v=27 in index.html.")

if __name__ == "__main__":
    apply_frontend_password_displays()
