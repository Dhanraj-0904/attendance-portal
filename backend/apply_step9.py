import re

def apply_step9_changes():
    # 1. Update backend/routers/sync.py (to delete newly created student profiles on undo sync)
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync_code = f.read()

    # Find the block inside undo_last_sync where we delete records and append student deletion logic
    old_deletion_block = """    # Delete records
    for r in records_to_delete:
        db.delete(r)

    db.commit()

    # Log action
    log_action(db, current_user.id, "undo_upload_csv", "batches", batch_id)

    return {
        "message": f"Successfully undone last sync. Removed {num_deleted} attendance records.",
        "records_removed": num_deleted
    }"""

    new_deletion_block = """    # Delete records
    for r in records_to_delete:
        db.delete(r)
    db.commit()

    # Find and delete students in this batch who have 0 attendance records left in the database
    students_in_batch = db.query(Student).filter(Student.batch_id == batch_id).all()
    students_deleted = 0
    for s in students_in_batch:
        rec_count = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id).count()
        if rec_count == 0:
            db.delete(s)
            students_deleted += 1
    db.commit()

    # Log action
    log_action(db, current_user.id, "undo_upload_csv", "batches", batch_id)

    return {
        "message": f"Successfully undone last sync. Removed {num_deleted} attendance records and {students_deleted} registered student profiles.",
        "records_removed": num_deleted,
        "students_removed": students_deleted
    }"""

    sync_code = sync_code.replace(old_deletion_block, new_deletion_block)

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync_code)
    print("Updated backend/routers/sync.py with student cleanup logic successfully.")

    # 2. Update backend/static/style.css to resolve select option white-on-white text mismatch
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    # Replace color-scheme select styles with solid background selectors
    old_select_styles = """select {
    color-scheme: dark;
}

body.light-theme select {
    color-scheme: light;
}"""

    new_select_styles = """select {
    color-scheme: dark;
}

body.light-theme select {
    color-scheme: light;
}

/* Explicit options coloring to override native browser styling conflicts */
select option {
    background-color: #1a153b !important;
    color: #e2e8f0 !important;
}

body.light-theme select option {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

select option[value=""] {
    color: #718096 !important;
}

body.light-theme select option[value=""] {
    color: #94a3b8 !important;
}"""

    css = css.replace(old_select_styles, new_select_styles)

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css with option overrides successfully.")

    # 3. Update backend/static/index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove "My Batches" navigation link from the teacher sidebar
    old_nav_teacher = """                    <!-- Teacher Navigation -->
                    <div id="nav-teacher" class="nav-group hidden">
                        <h3>INSTRUCTOR</h3>
                        <a href="#teacher-dashboard" class="nav-item active" data-tab="teacher-dashboard">
                            <span class="icon">📈</span> Dashboard
                        </a>
                        <a href="#teacher-batches" class="nav-item" data-tab="teacher-batches">
                            <span class="icon">📅</span> My Batches
                        </a>
                        <a href="#teacher-upload" class="nav-item" data-tab="teacher-upload">
                            <span class="icon">📤</span> Sync SID CSV
                        </a>
                    </div>"""

    new_nav_teacher = """                    <!-- Teacher Navigation -->
                    <div id="nav-teacher" class="nav-group hidden">
                        <h3>INSTRUCTOR</h3>
                        <a href="#teacher-dashboard" class="nav-item active" data-tab="teacher-dashboard">
                            <span class="icon">📈</span> Dashboard
                        </a>
                        <a href="#teacher-upload" class="nav-item" data-tab="teacher-upload">
                            <span class="icon">📤</span> Sync SID CSV
                        </a>
                    </div>"""

    html = html.replace(old_nav_teacher, new_nav_teacher)

    # Update student dashboard labels
    html = html.replace('<span>Sessions Attended:</span>', '<span>Hours Attended:</span>')
    html = html.replace('<span>Sessions Missed:</span>', '<span>Hours Missed:</span>')
    html = html.replace('<span>Remaining Sessions:</span>', '<span>Mandatory Target (75%):</span>')

    # Bump style and script versions
    html = html.replace('style.css?v=7.2', 'style.css?v=8')
    html = html.replace('style.css?v=7.3', 'style.css?v=8')
    html = html.replace('app.js?v=7', 'app.js?v=8')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html successfully.")

    # 4. Update backend/static/app.js to integrate 330 hrs and 75% target Calculations
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Modify viewTeacherBatchDetails(batchId)
    old_teacher_mapping = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended}</td>
                    <td>${s.sessions_missed}</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.sessions_needed_for_75}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;"""

    new_teacher_mapping = """        const totalHrs = 330;
        const reqHrs = 247.5;
        
        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = ((s.sessions_attended / batch.total_sessions) * totalHrs).toFixed(1);
            const missedHrs = ((s.sessions_missed / batch.total_sessions) * totalHrs).toFixed(1);
            const neededHrs = Math.max(0, reqHrs - attendedHrs).toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;"""

    js = js.replace(old_teacher_mapping, new_teacher_mapping)

    # Modify viewAdminBatchDetails(batchId)
    old_admin_mapping = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended}</td>
                    <td>${s.sessions_missed}</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.sessions_needed_for_75}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;"""

    new_admin_mapping = """        const totalHrs = 330;
        const reqHrs = 247.5;

        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = ((s.sessions_attended / batch.total_sessions) * totalHrs).toFixed(1);
            const missedHrs = ((s.sessions_missed / batch.total_sessions) * totalHrs).toFixed(1);
            const neededHrs = Math.max(0, reqHrs - attendedHrs).toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;"""

    js = js.replace(old_admin_mapping, new_admin_mapping)

    # Modify loadStudentDashboard() in app.js
    old_student_dashboard_mapping = """        document.getElementById("student-stat-attended").innerText = data.sessions_attended;
        document.getElementById("student-stat-missed").innerText = data.sessions_missed;
        document.getElementById("student-stat-remaining").innerText = data.sessions_remaining;"""

    new_student_dashboard_mapping = """        // Calculate hours based on total hours 330
        const totalHrs = 330;
        const totalSessions = data.sessions_attended + data.sessions_missed + data.sessions_remaining;
        const attendedHrs = totalSessions > 0 ? ((data.sessions_attended / totalSessions) * totalHrs).toFixed(1) : "0.0";
        const missedHrs = totalSessions > 0 ? ((data.sessions_missed / totalSessions) * totalHrs).toFixed(1) : "0.0";

        document.getElementById("student-stat-attended").innerText = `${attendedHrs} / 330 hrs`;
        document.getElementById("student-stat-missed").innerText = `${missedHrs} hrs`;
        document.getElementById("student-stat-remaining").innerText = `247.5 hrs`;"""

    js = js.replace(old_student_dashboard_mapping, new_student_dashboard_mapping)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_step9_changes()
