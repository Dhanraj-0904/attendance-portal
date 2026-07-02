def apply_minimalist_teacher_deletion():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Revert action bar header to clean minimal layout
    old_action_bar = """                            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                                <select id="delete-teacher-select" style="padding: 10px 14px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; min-width: 220px; outline: none; cursor: pointer;">
                                    <option value="">-- Choose Teacher to Delete --</option>
                                </select>
                                <button class="btn btn-destructive" onclick="deleteSelectedTeacher()">🗑️ Delete Teacher</button>
                                <button class="btn btn-primary" onclick="openModal('teacher-modal')">+ Add Teacher</button>
                            </div>"""

    new_action_bar = """                            <div style="display: flex; gap: 10px; align-items: center;">
                                <button id="btn-delete-selected-teachers" class="btn btn-destructive hidden" onclick="deleteSelectedTeachers()" style="margin: 0; padding: 10px 18px; border-radius: 8px;">🗑️ Delete Selected</button>
                                <button class="btn btn-primary" onclick="openModal('teacher-modal')" style="margin: 0;">+ Add Teacher</button>
                            </div>"""

    html = html.replace(old_action_bar, new_action_bar)

    # Insert Checkbox in Table Header
    old_table_header = """                                    <thead>
                                        <tr>
                                            <th>Username</th>
                                            <th>Email</th>"""

    new_table_header = """                                    <thead>
                                        <tr>
                                            <th style="width: 40px; text-align: center;"><input type="checkbox" id="select-all-teachers" onchange="toggleSelectAllTeachers(this)"></th>
                                            <th>Username</th>
                                            <th>Email<th>"""

    # Wait, let's fix double TH tag in my replace to be clean
    new_table_header = """                                    <thead>
                                        <tr>
                                            <th style="width: 40px; text-align: center;"><input type="checkbox" id="select-all-teachers" onchange="toggleSelectAllTeachers(this)"></th>
                                            <th>Username</th>
                                            <th>Email</th>"""

    html = html.replace(old_table_header, new_table_header)

    # Bump version
    html = html.replace("app.js?v=33", "app.js?v=34")
    html = html.replace("style.css?v=33", "style.css?v=34")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html to add checkboxes in teacher table header and clean deletion button.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update loadAdminTeachers body innerHTML mapper to include checkboxes
    old_teachers_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No teachers registered</td></tr>`;

        // Populate delete dropdown selector
        const deleteSelect = document.getElementById("delete-teacher-select");
        if (deleteSelect) {
            deleteSelect.innerHTML = `<option value="">-- Choose Teacher to Delete --</option>` + 
                data.teachers.map(t => `<option value="${t.id}">${t.username} (${t.subject || 'No Subject'})</option>`).join("");
        }"""

    new_teachers_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td style="text-align: center;"><input type="checkbox" class="teacher-select-cb" data-id="${t.id}" data-username="${t.username}" onchange="updateDeleteSelectedButtonState()"></td>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>Today</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="6" class="text-center">No teachers registered</td></tr>`;

        const selectAllCb = document.getElementById("select-all-teachers");
        if (selectAllCb) selectAllCb.checked = false;
        updateDeleteSelectedButtonState();"""

    js = js.replace(old_teachers_renderer, new_teachers_renderer)

    # Replace deleteSelectedTeacher with new bulk functions
    old_delete_func_js = """// Centralized function to delete select teacher and their student records cascadingly
async function deleteSelectedTeacher() {
    const select = document.getElementById("delete-teacher-select");
    if (!select) return;
    const teacherId = select.value;
    if (!teacherId) {
        showToast("Please choose a teacher to delete first", "error");
        return;
    }
    const teacherText = select.options[select.selectedIndex].text;
    
    if (!confirm(`CRITICAL WARNING: Are you sure you want to delete teacher "${teacherText}"? This will permanently delete the teacher account, all their assigned batches, all student profiles in those batches, and all their attendance history! This action CANNOT be undone.`)) {
        return;
    }
    
    try {
        showToast("Deleting teacher and all associated data...", "info");
        const res = await fetch(`${API_URL}/auth/teachers/${teacherId}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        
        const data = await res.json();
        showToast(data.message);
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
}"""

    new_delete_func_js = """// Toggle select-all status for teachers check boxes
function toggleSelectAllTeachers(masterCb) {
    document.querySelectorAll(".teacher-select-cb").forEach(cb => {
        cb.checked = masterCb.checked;
    });
    updateDeleteSelectedButtonState();
}

// Dynamically toggles visibility and label of bulk delete button based on checkbox checklist state
function updateDeleteSelectedButtonState() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    const deleteBtn = document.getElementById("btn-delete-selected-teachers");
    if (!deleteBtn) return;
    
    if (checkedCbs.length > 0) {
        deleteBtn.innerText = `🗑️ Delete Selected (${checkedCbs.length})`;
        deleteBtn.classList.remove("hidden");
    } else {
        deleteBtn.classList.add("hidden");
    }
}

// Bulk delete selected teachers
async function deleteSelectedTeachers() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    if (checkedCbs.length === 0) return;
    
    const teacherIds = Array.from(checkedCbs).map(cb => parseInt(cb.getAttribute("data-id")));
    const teacherNames = Array.from(checkedCbs).map(cb => cb.getAttribute("data-username"));
    
    if (!confirm(`CRITICAL WARNING: Are you sure you want to delete the selected ${teacherIds.length} teacher(s) (${teacherNames.join(", ")})? This will permanently delete their login accounts, all their assigned batches, all student profiles in those batches, and all their attendance history! This action CANNOT be undone.`)) {
        return;
    }
    
    try {
        showToast("Deleting selected teachers and all associated data...", "info");
        
        for (const tId of teacherIds) {
            const res = await fetch(`${API_URL}/auth/teachers/${tId}`, {
                method: "DELETE",
                headers: getHeaders()
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Delete failed");
            }
        }
        
        showToast("Successfully deleted selected teachers and their cascading data.");
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
}"""

    js = js.replace(old_delete_func_js, new_delete_func_js)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected bulk deletion check handlers and checkbox renderings in app.js.")

if __name__ == "__main__":
    apply_minimalist_teacher_deletion()
