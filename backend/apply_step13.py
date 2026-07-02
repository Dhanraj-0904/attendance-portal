import re

def apply_sequential_calendar():
    # 1. Update backend/routers/batches.py (add /scheduled-dates endpoint)
    with open("backend/routers/batches.py", "r", encoding="utf-8") as f:
        batches_code = f.read()

    scheduled_dates_route = """

@router.get("/{id}/scheduled-dates")
def get_batch_scheduled_dates(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this batch")

    # Generate dates starting from batch.start_date
    from datetime import timedelta
    working_days = []
    current = batch.start_date
    while len(working_days) < batch.total_sessions:
        if current.weekday() != 6:  # Exclude Sundays (6 = Sunday)
            working_days.append(current)
        current += timedelta(days=1)

    # Get which dates already have attendance uploaded
    uploaded_dates = db.query(AttendanceRecord.session_date).filter(
        AttendanceRecord.batch_id == id
    ).distinct().all()
    uploaded_set = {r[0] for r in uploaded_dates}

    return [
        {
            "date": d.strftime("%Y-%m-%d"),
            "day": d.day,
            "month_name": d.strftime("%b"),
            "has_attendance": d in uploaded_set
        }
        for d in working_days
    ]
"""

    if "/scheduled-dates" not in batches_code:
        batches_code += scheduled_dates_route

    with open("backend/routers/batches.py", "w", encoding="utf-8") as f:
        f.write(batches_code)
    print("Injected /batches/{id}/scheduled-dates endpoint successfully.")

    # 2. Update index.html to simplify visualizer calendar header (remove month selection buttons)
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    old_header_block = """                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Visualizer</h3>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <button class="btn btn-secondary btn-small" id="cal-prev-month" type="button" style="margin: 0;">&lt;</button>
                                        <span id="cal-current-month-year" style="font-size: 14px; font-weight: 600; min-width: 110px; text-align: center;">June 2026</span>
                                        <button class="btn btn-secondary btn-small" id="cal-next-month" type="button" style="margin: 0;">&gt;</button>
                                    </div>
                                </div>"""

    new_header_block = """                                <div class="calendar-header-actions" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h3 style="font-size: 16px; margin: 0;">📅 Attendance Visualizer</h3>
                                </div>"""

    html = html.replace(old_header_block, new_header_block)

    # Bump style and script version numbers
    html = html.replace('style.css?v=9', 'style.css?v=10')
    html = html.replace('app.js?v=9', 'app.js?v=10')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html layout versions successfully.")

    # 3. Update app.js (replace calendar code with sequential scheduled-dates rendering)
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Remove the monthly navigation button click listeners from DOMContentLoaded
    old_nav_listeners = """    // Connect calendar navigation controls
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
    }"""

    js = js.replace(old_nav_listeners, "")

    # Replace calendar helper states & functions at the bottom
    old_helpers_block = """// Interactive Calendar helper states
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
}"""

    new_helpers_block = """// Interactive Calendar helper states
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

    js = js.replace(old_helpers_block, new_helpers_block)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_sequential_calendar()
