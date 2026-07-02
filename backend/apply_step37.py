def apply_delete_mode_ux():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Update Action Bar
    old_action_bar = """                            <div style="display: flex; gap: 10px; align-items: center;">
                                <button id="btn-delete-selected-teachers" class="btn btn-destructive hidden" onclick="deleteSelectedTeachers()" style="margin: 0; padding: 10px 18px; border-radius: 8px;">🗑️ Delete Selected</button>
                                <button class="btn btn-primary" onclick="openModal('teacher-modal')" style="margin: 0;">+ Add Teacher</button>
                            </div>"""

    new_action_bar = """                            <div style="display: flex; gap: 10px; align-items: center;">
                                <button id="btn-cancel-delete-teachers" class="btn btn-secondary hidden" onclick="exitTeacherDeleteMode()" style="margin: 0; padding: 10px 18px; border-radius: 8px;">Cancel</button>
                                <button id="btn-delete-teachers-mode" class="btn btn-destructive" onclick="enterTeacherDeleteMode()" style="margin: 0; padding: 10px 18px; border-radius: 8px;">🗑️ Delete Teacher</button>
                                <button class="btn btn-primary" onclick="openModal('teacher-modal')" style="margin: 0;">+ Add Teacher</button>
                            </div>"""

    html = html.replace(old_action_bar, new_action_bar)

    # Update Table Header (Remove select-all checkbox, add delete-col-header class)
    old_table_header = """                                    <thead>
                                        <tr>
                                            <th style="width: 40px; text-align: center;"><input type="checkbox" id="select-all-teachers" onchange="toggleSelectAllTeachers(this)"></th>
                                            <th>Username</th>
                                            <th>Email</th>"""

    new_table_header = """                                    <thead>
                                        <tr>
                                            <th class="delete-col-header hidden" style="width: 40px;"></th>
                                            <th>Username</th>
                                            <th>Email</th>"""

    html = html.replace(old_table_header, new_table_header)

    # Bump version
    html = html.replace("app.js?v=34", "app.js?v=35")
    html = html.replace("style.css?v=34", "style.css?v=35")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html templates for Teacher Delete Mode.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update row renderer body mapping to hide checkbox td by default
    old_row_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td style="text-align: center;"><input type="checkbox" class="teacher-select-cb" data-id="${t.id}" data-username="${t.username}" onchange="updateDeleteSelectedButtonState()"></td>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>"""

    new_row_renderer = """        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td class="delete-col-cell hidden" style="text-align: center;"><input type="checkbox" class="teacher-select-cb" data-id="${t.id}" data-username="${t.username}" onchange="updateDeleteSelectedCount()"></td>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>"""

    js = js.replace(old_row_renderer, new_row_renderer)

    # Update reset state calls at the bottom of loadAdminTeachers
    old_reset_calls = """        const selectAllCb = document.getElementById("select-all-teachers");
        if (selectAllCb) selectAllCb.checked = false;
        updateDeleteSelectedButtonState();"""

    new_reset_calls = """        exitTeacherDeleteMode();"""

    js = js.replace(old_reset_calls, new_reset_calls)

    # Update bulk functions block
    old_bulk_funcs = """// Toggle select-all status for teachers check boxes
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

    new_bulk_funcs = """// Teacher Delete Mode state controller
let teacherDeleteModeActive = false;

function enterTeacherDeleteMode() {
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    const cancelBtn = document.getElementById("btn-cancel-delete-teachers");
    if (!modeBtn || !cancelBtn) return;
    
    if (!teacherDeleteModeActive) {
        // Activate Delete Mode: show column and checkboxes
        teacherDeleteModeActive = true;
        modeBtn.innerText = "🗑️ Confirm Delete (0)";
        cancelBtn.classList.remove("hidden");
        
        document.querySelectorAll(".delete-col-header").forEach(el => el.classList.remove("hidden"));
        document.querySelectorAll(".delete-col-cell").forEach(el => el.classList.remove("hidden"));
    } else {
        // Execute bulk deletion of selected items
        deleteSelectedTeachers();
    }
}

function exitTeacherDeleteMode() {
    teacherDeleteModeActive = false;
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    const cancelBtn = document.getElementById("btn-cancel-delete-teachers");
    if (modeBtn) modeBtn.innerText = "🗑️ Delete Teacher";
    if (cancelBtn) cancelBtn.classList.add("hidden");
    
    // Reset check box values
    document.querySelectorAll(".teacher-select-cb").forEach(cb => cb.checked = false);
    
    // Hide column elements
    document.querySelectorAll(".delete-col-header").forEach(el => el.classList.add("hidden"));
    document.querySelectorAll(".delete-col-cell").forEach(el => el.classList.add("hidden"));
}

function updateDeleteSelectedCount() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    if (modeBtn && teacherDeleteModeActive) {
        modeBtn.innerText = `🗑️ Confirm Delete (${checkedCbs.length})`;
    }
}

// Bulk delete selected teachers cascadingly
async function deleteSelectedTeachers() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    if (checkedCbs.length === 0) {
        showToast("No teachers selected to delete", "error");
        return;
    }
    
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

    js = js.replace(old_bulk_funcs, new_bulk_funcs)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected Delete Mode logic and hidden checkbox columns inside app.js.")

if __name__ == "__main__":
    apply_delete_mode_ux()
