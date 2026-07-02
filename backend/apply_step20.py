import re

def remove_delete_dropdown_button():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove the teacher-delete-student-modal modal markup
    old_modal_pattern = r'<!-- Delete a Student Modal \(Dropdown\) -->\s*<div id="teacher-delete-student-modal".*?</form>\s*</div>\s*</div>'
    html = re.sub(old_modal_pattern, '', html, flags=re.DOTALL)

    # Bump cached assets versions
    html = html.replace('style.css?v=15', 'style.css?v=16')
    html = html.replace('app.js?v=15', 'app.js?v=16')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Cleaned up index.html modal markup.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Remove Delete Student (dropdown) button from loadAdminTeachers
    old_teachers_body = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openDeleteStudentDropdownForTeacher(${t.id}, '${t.username}')">🗑️ Delete Student</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    new_teachers_body = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-destructive btn-small" onclick="deleteTeacherStudents(${t.id}, '${t.username}')">🗑️ Delete All Students</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;"""

    js = js.replace(old_teachers_body, new_teachers_body)

    # Add Delete button to viewAdminBatchDetails row mapping
    old_row_render = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\\'")}', '${s.phone || ''}')">✏️ Edit</button>
                        </div>
                    </td>
                </tr>
            `;"""

    new_row_render = """            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\\'")}', '${s.phone || ''}')">✏️ Edit</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;"""

    js = js.replace(old_row_render, new_row_render)

    # Delete teacherDeleteStudentForm submit listener from app.js
    old_submit_form_pattern = r'// Teacher single student delete form submission.*?\n\s*}\s*\n\s*}\s*'
    js = re.sub(old_submit_form_pattern, '', js, flags=re.DOTALL)

    # Delete openDeleteStudentDropdownForTeacher function from app.js
    old_dropdown_func_pattern = r'async function openDeleteStudentDropdownForTeacher.*?^}'
    js = re.sub(old_dropdown_func_pattern, '', js, flags=re.DOTALL | re.MULTILINE)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js delete actions.")

if __name__ == "__main__":
    remove_delete_dropdown_button()
