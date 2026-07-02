def apply_hours_and_edit_fixes():
    # 1. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Admin Batch Details Table Renderer
    old_admin_renderer = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = ((s.sessions_attended / batch.total_sessions) * totalHrs).toFixed(1);
            const missedHrs = ((s.sessions_missed / batch.total_sessions) * totalHrs).toFixed(1);
            const neededHrs = Math.max(0, reqHrs - attendedHrs).toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>"""

    new_admin_renderer = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = s.sessions_attended.toFixed(1);
            const missedHrs = s.sessions_missed.toFixed(1);
            const neededHrs = s.sessions_needed_for_75.toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${attendedHrs} hrs</td>
                    <td>${missedHrs} hrs</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${neededHrs} hrs</td>"""

    js = js.replace(old_admin_renderer, new_admin_renderer)

    # Teacher Batch Details Table Renderer
    old_teacher_renderer = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = ((s.sessions_attended / batch.total_sessions) * totalHrs).toFixed(1);
            const missedHrs = ((s.sessions_missed / batch.total_sessions) * totalHrs).toFixed(1);
            const neededHrs = Math.max(0, reqHrs - attendedHrs).toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${s.sessions_attended} <small style="color:var(--text-muted)">(${attendedHrs} hrs)</small></td>
                    <td>${s.sessions_missed} <small style="color:var(--text-muted)">(${missedHrs} hrs)</small></td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === "ELIGIBLE" ? "0 <small style='color:var(--text-muted)'>(0.0 hrs)</small>" : `${s.sessions_needed_for_75} <small style='color:var(--text-muted)'>(${neededHrs} hrs)</small>`}</td>"""

    new_teacher_renderer = """        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = s.sessions_attended.toFixed(1);
            const missedHrs = s.sessions_missed.toFixed(1);
            const neededHrs = s.sessions_needed_for_75.toFixed(1);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${attendedHrs} hrs</td>
                    <td>${missedHrs} hrs</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${neededHrs} hrs</td>"""

    js = js.replace(old_teacher_renderer, new_teacher_renderer)

    # Static Edit Form Handler mapping updates
    old_static_handler = """            const data = {
                name: document.getElementById("edit-student-name").value,
                phone: document.getElementById("edit-student-phone").value
            };"""

    new_static_handler = """            const data = {
                name: document.getElementById("edit-student-name").value,
                password: document.getElementById("edit-student-password") ? document.getElementById("edit-student-password").value : ""
            };"""

    js = js.replace(old_static_handler, new_static_handler)

    # Dynamic openEditStudent modal update
    old_dynamic_modal_def = """        modalDiv.innerHTML = `
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>Edit Student Details</h2>
                    <span class="close-btn" onclick="closeModal('edit-student-modal')">&times;</span>
                </div>
                <form id="edit-student-form">
                    <input type="hidden" id="edit-student-id">
                    <div class="form-group">
                        <label for="edit-student-name">Full Name</label>
                        <input type="text" id="edit-student-name" placeholder="e.g. Aarti Baghel" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-student-phone">Phone Number</label>
                        <input type="tel" id="edit-student-phone" placeholder="e.g. 9988776655">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Save Changes</button>
                </form>
            </div>
        `;"""

    new_dynamic_modal_def = """        modalDiv.innerHTML = `
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>Edit Student Details</h2>
                    <span class="close-btn" onclick="closeModal('edit-student-modal')">&times;</span>
                </div>
                <form id="edit-student-form">
                    <input type="hidden" id="edit-student-id">
                    <div class="form-group">
                        <label for="edit-student-name">Full Name</label>
                        <input type="text" id="edit-student-name" placeholder="e.g. Aarti Baghel" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-student-password">Reset Password</label>
                        <input type="password" id="edit-student-password" placeholder="Enter new password (optional)">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Save Changes</button>
                </form>
            </div>
        `;"""

    js = js.replace(old_dynamic_modal_def, new_dynamic_modal_def)

    # Dynamic listener mapping inside openEditStudent
    old_dynamic_listener_mapping = """                const data = {
                    name: document.getElementById("edit-student-name").value,
                    phone: document.getElementById("edit-student-phone").value
                };"""

    new_dynamic_listener_mapping = """                const data = {
                    name: document.getElementById("edit-student-name").value,
                    password: document.getElementById("edit-student-password").value
                };"""

    js = js.replace(old_dynamic_listener_mapping, new_dynamic_listener_mapping)

    # Dynamic opener values mapping
    old_opener_mapping = """    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    document.getElementById("edit-student-phone").value = phone || "";
    openModal("edit-student-modal");"""

    new_opener_mapping = """    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    if (document.getElementById("edit-student-password")) {
        document.getElementById("edit-student-password").value = "";
    }
    openModal("edit-student-modal");"""

    js = js.replace(old_opener_mapping, new_opener_mapping)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated dynamic modal fields, form submit payloads, and layout rendering calculations in app.js.")

if __name__ == "__main__":
    apply_hours_and_edit_fixes()
