import re

def apply_standard_calendars():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Re-insert the Teacher Visualizer calendar header action buttons
    old_teacher_cal_header = """                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Visualizer</h3>
                                </div>"""

    new_teacher_cal_header = """                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Visualizer</h3>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <button class="btn btn-secondary btn-small" id="cal-prev-month" type="button" style="margin: 0;">&lt;</button>
                                        <span id="cal-current-month-year" style="font-size: 14px; font-weight: 600; min-width: 110px; text-align: center;">June 2026</span>
                                        <button class="btn btn-secondary btn-small" id="cal-next-month" type="button" style="margin: 0;">&gt;</button>
                                    </div>
                                </div>"""

    html = html.replace(old_teacher_cal_header, new_teacher_cal_header)

    # Update Student calendar header in index.html to include month selector buttons
    old_student_cal_header = """                            <!-- Attendance Calendar -->
                            <div class="glass-card student-calendar-card">
                                <h3>Attendance Calendar</h3>
                                <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px;">
                                    Green = Present, Red = Absent, Gray = No Session / Rest Day
                                </p>"""

    new_student_cal_header = """                            <!-- Attendance Calendar -->
                            <div class="glass-card student-calendar-card">
                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Calendar</h3>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <button class="btn btn-secondary btn-small" id="student-cal-prev" type="button" style="margin: 0;">&lt;</button>
                                        <span id="student-cal-month-year" style="font-size: 14px; font-weight: 600; min-width: 110px; text-align: center;">June 2026</span>
                                        <button class="btn btn-secondary btn-small" id="student-cal-next" type="button" style="margin: 0;">&gt;</button>
                                    </div>
                                </div>
                                <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px;">
                                    Green = Present, Red = Absent, Gray = No Session / Rest Day
                                </p>"""

    html = html.replace(old_student_cal_header, new_student_cal_header)

    # Change weekday headers order to start on Sunday for both calendars
    old_days_header = """                                <div class="calendar-days-header" style="margin-top: 10px;">
                                    <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
                                </div>"""
    
    # Just to be safe, replace all occurrences of weekday grids to match Sun -> Sat
    html = html.replace('<div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>',
                        '<div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>')

    # Bump style and script cache version keys
    html = html.replace('style.css?v=10', 'style.css?v=11')
    html = html.replace('app.js?v=10', 'app.js?v=11')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html layouts successfully.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Modify student calendar render inside loadStudentDashboard
    old_student_cal_render = """        // Render Calendar
        const cal = document.getElementById("student-calendar-grid");
        cal.innerHTML = "";

        // Fill with days
        data.calendar_logs.forEach(day => {
            const div = document.createElement("div");
            div.className = "calendar-day " + (day.status === "PRESENT" ? "present" : (day.status === "ABSENT" ? "absent" : ""));
            div.innerText = day.day_number;
            div.title = `Session ${day.day_number}: ${day.status || 'No record'}`;
            cal.appendChild(div);
        });"""

    new_student_cal_render = """        // Save attendance logs to state & render monthly calendar
        studentAttendanceLogs = data.calendar_logs;
        renderStudentCalendar();"""

    js = js.replace(old_student_cal_render, new_student_cal_render)

    # Inject prev/next button click handlers inside DOMContentLoaded
    nav_button_listeners = """
    // Connect calendar navigation controls (Teacher Portal)
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

    // Connect calendar navigation controls (Student Portal)
    const studentPrevBtn = document.getElementById("student-cal-prev");
    const studentNextBtn = document.getElementById("student-cal-next");
    if (studentPrevBtn && studentNextBtn) {
        studentPrevBtn.addEventListener("click", () => {
            studentCalMonth--;
            if (studentCalMonth < 0) {
                studentCalMonth = 11;
                studentCalYear--;
            }
            renderStudentCalendar();
        });
        studentNextBtn.addEventListener("click", () => {
            studentCalMonth++;
            if (studentCalMonth > 11) {
                studentCalMonth = 0;
                studentCalYear++;
            }
            renderStudentCalendar();
        });
    }
"""

    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + nav_button_listeners)

    # Replace calendar helpers at the bottom
    old_helpers_block = """// Interactive Calendar helper states
let syncScheduledDates = [];

async function loadSyncAttendanceCalendar() {
    const batchId = document.getElementById("upload-batch-select").value;
    const grid = document.getElementById("teacher-sync-calendar-grid");
    if (!grid) return;

    if (!batchId) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">Please select a batch to view attendance visualizer</div>`;
        syncScheduledDates = [];
        return;
    }

    try {
        const res = await fetch(`${API_URL}/batches/${batchId}/scheduled-dates`, { headers: getHeaders() });
        if (res.ok) {
            syncScheduledDates = await res.json();
        } else {
            syncScheduledDates = [];
        }
    } catch (err) {
        console.error("Failed to load scheduled dates:", err);
        syncScheduledDates = [];
    }

    renderSyncCalendar();
}

function renderSyncCalendar() {
    const grid = document.getElementById("teacher-sync-calendar-grid");
    if (!grid) return;

    const dateInput = document.getElementById("upload-date-input");
    const selectedDateStr = dateInput ? dateInput.value : "";

    grid.innerHTML = "";

    if (syncScheduledDates.length === 0) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">No scheduled sessions found for this batch</div>`;
        return;
    }

    syncScheduledDates.forEach(day => {
        const cell = document.createElement("div");
        cell.className = "calendar-day interactive";
        cell.innerText = day.day;
        cell.title = `Date: ${day.date} (${day.month_name}) | ${day.has_attendance ? 'Attendance uploaded' : 'No records'}`;

        if (day.has_attendance) {
            cell.classList.add("uploaded");
        }

        if (day.date === selectedDateStr) {
            cell.classList.add("selected-date");
        }

        cell.addEventListener("click", () => {
            if (dateInput) {
                dateInput.value = day.date;
                renderSyncCalendar();
            }
        });

        grid.appendChild(cell);
    });
}"""

    new_helpers_block = """// Standard monthly calendar states for both portals
let syncCalYear = new Date().getFullYear();
let syncCalMonth = new Date().getMonth();
let syncUploadedDates = [];

let studentCalYear = new Date().getFullYear();
let studentCalMonth = new Date().getMonth();
let studentAttendanceLogs = [];

async function loadSyncAttendanceCalendar() {
    const batchId = document.getElementById("upload-batch-select").value;
    const grid = document.getElementById("teacher-sync-calendar-grid");
    if (!grid) return;

    if (!batchId) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">Please select a batch to view attendance visualizer</div>`;
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

    const firstDayIdx = new Date(syncCalYear, syncCalMonth, 1).getDay(); // Sunday=0, Monday=1...
    const totalDays = new Date(syncCalYear, syncCalMonth + 1, 0).getDate();

    grid.innerHTML = "";

    // Empty cells for weekday offset
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

// Student Portal standard monthly calendar rendering
function renderStudentCalendar() {
    const grid = document.getElementById("student-calendar-grid");
    const monthYearLabel = document.getElementById("student-cal-month-year");
    if (!grid || !monthYearLabel) return;

    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    monthYearLabel.innerText = `${months[studentCalMonth]} ${studentCalYear}`;

    const firstDayIdx = new Date(studentCalYear, studentCalMonth, 1).getDay();
    const totalDays = new Date(studentCalYear, studentCalMonth + 1, 0).getDate();

    grid.innerHTML = "";

    // Empty cells for weekday offset
    for (let i = 0; i < firstDayIdx; i++) {
        const cell = document.createElement("div");
        cell.className = "calendar-day empty";
        grid.appendChild(cell);
    }

    // Days of the month
    for (let day = 1; day <= totalDays; day++) {
        const cell = document.createElement("div");
        const mStr = String(studentCalMonth + 1).padStart(2, '0');
        const dStr = String(day).padStart(2, '0');
        const dateStr = `${studentCalYear}-${mStr}-${dStr}`;

        cell.className = "calendar-day";
        cell.innerText = day;

        // Look up attendance logs for this specific date string
        const match = studentAttendanceLogs.find(log => log.date === dateStr);
        if (match) {
            if (match.status === "PRESENT") {
                cell.classList.add("present");
            } else if (match.status === "ABSENT") {
                cell.classList.add("absent");
            }
        }

        grid.appendChild(cell);
    }
}"""

    js = js.replace(old_helpers_block, new_helpers_block)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_standard_calendars()
