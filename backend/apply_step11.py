import re

def apply_attendance_redesign():
    # 1. Update style.css (append new styles for split layout & interactive calendar)
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    new_styles = """
/* ================= SYNC ATTENDANCE SPLIT LAYOUT & CALENDAR ================= */
.sync-grid-container {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 24px;
    align-items: start;
}

@media (max-width: 992px) {
    .sync-grid-container {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

.calendar-day.uploaded {
    background: rgba(0, 230, 118, 0.12) !important;
    border-color: var(--status-eligible) !important;
    color: var(--status-eligible) !important;
    font-weight: 700;
}

.calendar-day.selected-date {
    border: 2px solid var(--primary-color) !important;
    background: rgba(124, 77, 255, 0.15) !important;
}

.calendar-day.interactive {
    cursor: pointer;
    transition: all 0.2s ease;
}

.calendar-day.interactive:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-1px);
}

.calendar-header-actions button {
    padding: 6px 12px;
    border-radius: 6px;
}

.select-calendar-card {
    height: 100%;
}
"""
    if "/* ================= SYNC ATTENDANCE SPLIT LAYOUT & CALENDAR ================= */" not in css:
        css += new_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated style.css successfully.")

    # 2. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Rename sidebar links
    html = html.replace('Sync SID CSV', 'Sync Attendance')

    # Replace the teacher upload tab content
    old_section_pattern = r'<!-- ================= TEACHER UPLOAD TAB ================= -->.*?<!-- ================= STUDENT DASHBOARD TAB ================= -->'
    
    new_section_content = """<!-- ================= TEACHER UPLOAD TAB ================= -->
                    <section id="tab-teacher-upload" class="tab-content">
                        <div class="dashboard-header">
                            <h1>Sync Attendance</h1>
                            <p>Select a date and upload the daily attendance CSV file. The portal will automatically record present students and mark the remaining batch students as absent.</p>
                        </div>

                        <div class="sync-grid-container mt-20">
                            <!-- Left Column: Settings & File Drop -->
                            <div class="glass-card">
                                <form id="upload-csv-form">
                                    <div class="form-group">
                                        <label for="upload-batch-select">Select Target Batch</label>
                                        <select id="upload-batch-select" required>
                                            <option value="">-- Choose Batch --</option>
                                        </select>
                                    </div>

                                    <div class="form-group">
                                        <label for="upload-date-input">Select Attendance Date</label>
                                        <input type="date" id="upload-date-input" required>
                                    </div>

                                    <div class="form-group">
                                        <label>Upload Attendance CSV File</label>
                                        <div class="drop-zone" id="csv-drop-zone">
                                            <span class="drop-zone-icon">📥</span>
                                            <p class="drop-zone-text">Drag and drop your attendance CSV here, or click to browse</p>
                                            <input type="file" id="csv-file-input" accept=".csv" class="hidden" required>
                                        </div>
                                        <div id="file-name-display" class="file-display hidden">
                                            Selected: <strong id="selected-file-name">file.csv</strong>
                                        </div>
                                    </div>

                                    <button type="submit" class="btn btn-primary btn-block">⚡ Sync Attendance</button>
                                </form>

                                <hr style="margin: 25px 0; border: 0; border-top: 1px solid var(--card-border);">

                                <div class="undo-sync-section">
                                    <h3 style="font-size: 16px; margin-bottom: 8px;">↩️ Undo Last Upload</h3>
                                    <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px; line-height: 1.4;">
                                        Uploaded the wrong CSV file? Select the batch below and revert the last import.
                                    </p>
                                    <form id="undo-sync-form">
                                        <div class="form-group">
                                            <label for="undo-batch-select">Select Batch to Revert</label>
                                            <select id="undo-batch-select" required>
                                                <option value="">-- Choose Batch --</option>
                                            </select>
                                        </div>
                                        <button type="submit" class="btn btn-destructive btn-block">Revert Last Import</button>
                                    </form>
                                </div>
                            </div>

                            <!-- Right Column: Interactive Calendar Widget -->
                            <div class="glass-card select-calendar-card">
                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Visualizer</h3>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <button class="btn btn-secondary btn-small" id="cal-prev-month" type="button" style="margin: 0;">&lt;</button>
                                        <span id="cal-current-month-year" style="font-size: 14px; font-weight: 600; min-width: 110px; text-align: center;">June 2026</span>
                                        <button class="btn btn-secondary btn-small" id="cal-next-month" type="button" style="margin: 0;">&gt;</button>
                                    </div>
                                </div>
                                <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px;">
                                    Click a date in the calendar below to select the attendance date. Dates highlighted in green have attendance uploaded.
                                </p>
                                <div class="calendar-days-header" style="margin-top: 10px;">
                                    <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
                                </div>
                                <div class="calendar-grid" id="teacher-sync-calendar-grid">
                                    <!-- Populated dynamically by JS -->
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- ================= STUDENT DASHBOARD TAB ================= -->"""

    html = re.sub(old_section_pattern, new_section_content, html, flags=re.DOTALL)

    # Inject Admin Student upload card in tab-admin-batches-detail before the student table card
    old_table_card = '<div class="glass-card mt-20">\n                            <div class="table-container">\n                                <table class="data-table">'
    
    admin_upload_card = """<!-- Master Student List CSV Upload Form -->
                        <div id="admin-batch-student-upload-card" class="glass-card mt-20 hidden">
                            <h3 style="font-size: 16px; margin-bottom: 8px;">📤 Import Student Enrollment List</h3>
                            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px; line-height: 1.4;">
                                Upload the master batch enrollment CSV file (containing 'Emp Id' and 'Name'). This will sync the student profiles in this batch and auto-generate their login accounts.
                            </p>
                            <form id="admin-student-upload-form" style="display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap;">
                                <input type="hidden" id="admin-student-upload-batch-id">
                                <div class="form-group" style="flex: 1; min-width: 250px; margin-bottom: 0;">
                                    <label for="admin-student-file-input">Select Student Master CSV File</label>
                                    <input type="file" id="admin-student-file-input" accept=".csv" required style="padding: 8px; border: 1px solid var(--card-border); border-radius: 8px; width: 100%; background: rgba(255,255,255,0.03); color: var(--text-main);">
                                </div>
                                <button type="submit" class="btn btn-primary" style="margin-bottom: 0;">⚡ Sync Student Enrollment</button>
                            </form>
                        </div>

                        <div class="glass-card mt-20">
                            <div class="table-container">
                                <table class="data-table">"""

    html = html.replace(old_table_card, admin_upload_card)

    # Bump cache-busting style and scripts version
    html = html.replace('style.css?v=8', 'style.css?v=9')
    html = html.replace('app.js?v=8.1', 'app.js?v=9')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html successfully.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Modify upload-csv-form submit handler to accept selected date
    old_upload_form_js = """    // CSV Sync Form Handler
    const uploadForm = document.getElementById("upload-csv-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const batchId = document.getElementById("upload-batch-select").value;
            const fileInput = document.getElementById("csv-file-input");

            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please choose a CSV file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("batch_id", batchId);
            formData.append("file", fileInput.files[0]);

            try {
                showToast("Syncing data in progress...", "info");
                const res = await fetch(`${API_URL}/sync/upload`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${state.token}`
                    },
                    body: formData
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Sync failed");
                }

                const data = await res.json();
                showToast(data.message);
                
                // Clear inputs
                uploadForm.reset();
                document.getElementById("file-name-display").classList.add("hidden");
                
                switchTab("teacher-dashboard");
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }"""

    new_upload_form_js = """    // CSV Sync Form Handler
    const uploadForm = document.getElementById("upload-csv-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const batchId = document.getElementById("upload-batch-select").value;
            const dateVal = document.getElementById("upload-date-input").value;
            const fileInput = document.getElementById("csv-file-input");

            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please choose a CSV file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("batch_id", batchId);
            formData.append("date", dateVal);
            formData.append("file", fileInput.files[0]);

            try {
                showToast("Syncing attendance in progress...", "info");
                const res = await fetch(`${API_URL}/sync/upload`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${state.token}`
                    },
                    body: formData
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Sync failed");
                }

                const data = await res.json();
                showToast(data.message);
                
                // Clear inputs (except batch)
                fileInput.value = "";
                document.getElementById("file-name-display").classList.add("hidden");
                
                // Reload calendar & redirect
                loadSyncAttendanceCalendar();
                switchTab("teacher-dashboard");
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }"""

    js = js.replace(old_upload_form_js, new_upload_form_js)

    # Inject admin student list upload card populate & handlers
    admin_det_card_populate = """        summaryCard.classList.remove("hidden");
        actions.classList.remove("hidden");
        
        // Populate and show Admin student CSV upload card
        const adminUploadCard = document.getElementById("admin-batch-student-upload-card");
        const adminUploadBatchInput = document.getElementById("admin-student-upload-batch-id");
        if (adminUploadCard && adminUploadBatchInput) {
            adminUploadBatchInput.value = batchId;
            adminUploadCard.classList.remove("hidden");
        }"""

    js = js.replace('summaryCard.classList.remove("hidden");\n        actions.classList.remove("hidden");', admin_det_card_populate)

    # Inject DOMContentLoaded handlers for Admin CSV upload form & calendar month navigations
    cal_init_js = """
    // Admin Student List Upload Form Handler
    const adminStudentUploadForm = document.getElementById("admin-student-upload-form");
    if (adminStudentUploadForm) {
        adminStudentUploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const batchId = document.getElementById("admin-student-upload-batch-id").value;
            const fileInput = document.getElementById("admin-student-file-input");
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please choose a CSV file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("batch_id", batchId);
            formData.append("file", fileInput.files[0]);

            try {
                showToast("Uploading student list & generating credentials...", "info");
                const res = await fetch(`${API_URL}/sync/admin-upload`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${state.token}`
                    },
                    body: formData
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Upload failed");
                }

                const data = await res.json();
                showToast(data.message);
                
                adminStudentUploadForm.reset();
                viewAdminBatchDetails(batchId);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // Set default date input value to today for sync screen
    const uploadDateInput = document.getElementById("upload-date-input");
    if (uploadDateInput) {
        uploadDateInput.value = new Date().toISOString().split('T')[0];
        
        // Re-render when date input is manually changed
        uploadDateInput.addEventListener("input", () => {
            renderSyncCalendar();
        });
    }

    // Connect calendar navigation controls
    const prevMonthBtn = document.getElementById("cal-prev-month");
    const nextMonthBtn = document.getElementById("cal-next-month");
    if (prevMonthBtn && nextMonthBtn) {
        prevMonthBtn.addEventListener("click", () => {
            syncCalMonth--;
            if (syncCalMonth < 0) {
                syncCalMonth = 11;
                syncCalYear--;
            }
            renderSyncCalendar();
        });
        nextMonthBtn.addEventListener("click", () => {
            syncCalMonth++;
            if (syncCalMonth > 11) {
                syncCalMonth = 0;
                syncCalYear++;
            }
            renderSyncCalendar();
        });
    }

    // Trigger calendar load when batch selection changes on sync screen
    const uploadBatchSelect = document.getElementById("upload-batch-select");
    if (uploadBatchSelect) {
        uploadBatchSelect.addEventListener("change", () => {
            loadSyncAttendanceCalendar();
        });
    }
"""

    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + cal_init_js)

    # Append helper calendar functions at the bottom of the file
    cal_helpers_js = """
// Interactive Calendar helper states
let syncCalYear = new Date().getFullYear();
let syncCalMonth = new Date().getMonth();
let syncUploadedDates = [];

async function loadSyncAttendanceCalendar() {
    const batchId = document.getElementById("upload-batch-select").value;
    const grid = document.getElementById("teacher-sync-calendar-grid");
    if (!grid) return;

    if (!batchId) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">Please select a batch to view attendance logs</div>`;
        syncUploadedDates = [];
        return;
    }

    try {
        const res = await fetch(`${API_URL}/batches/${batchId}/attendance-dates`, { headers: getHeaders() });
        if (res.ok) {
            syncUploadedDates = await res.json();
        } else {
            syncUploadedDates = [];
        }
    } catch (err) {
        console.error("Failed to load attendance dates:", err);
        syncUploadedDates = [];
    }

    renderSyncCalendar();
}

function renderSyncCalendar() {
    const grid = document.getElementById("teacher-sync-calendar-grid");
    const monthYearLabel = document.getElementById("cal-current-month-year");
    if (!grid || !monthYearLabel) return;

    const dateInput = document.getElementById("upload-date-input");
    const selectedDateStr = dateInput ? dateInput.value : "";

    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    monthYearLabel.innerText = `${months[syncCalMonth]} ${syncCalYear}`;

    const firstDayIdx = new Date(syncCalYear, syncCalMonth, 1).getDay();
    const totalDays = new Date(syncCalYear, syncCalMonth + 1, 0).getDate();

    grid.innerHTML = "";

    // Empty spaces for days before the 1st
    for (let i = 0; i < firstDayIdx; i++) {
        const cell = document.createElement("div");
        cell.className = "calendar-day empty";
        grid.appendChild(cell);
    }

    // Days of the month
    for (let day = 1; day <= totalDays; day++) {
        const cell = document.createElement("div");
        const mStr = String(syncCalMonth + 1).padStart(2, '0');
        const dStr = String(day).padStart(2, '0');
        const dateStr = `${syncCalYear}-${mStr}-${dStr}`;

        cell.className = "calendar-day interactive";
        cell.innerText = day;

        if (syncUploadedDates.includes(dateStr)) {
            cell.classList.add("uploaded");
        }

        if (dateStr === selectedDateStr) {
            cell.classList.add("selected-date");
        }

        cell.addEventListener("click", () => {
            if (dateInput) {
                dateInput.value = dateStr;
                renderSyncCalendar();
            }
        });

        grid.appendChild(cell);
    }
}
"""
    # Append to the end of app.js
    js += cal_helpers_js

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_attendance_redesign()
