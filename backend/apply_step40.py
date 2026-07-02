def fix_calendar_placeholder_bug():
    # 1. Update index.html to bump version to v=37
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("app.js?v=36", "app.js?v=37")
    html = html.replace("style.css?v=36", "style.css?v=37")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Bumped asset version to v=37 in index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update loadTeacherUploadOptions to call loadSyncAttendanceCalendar
    old_load_options = """    const undoSelect = document.getElementById("undo-batch-select");
    if (undoSelect) {
        undoSelect.innerHTML = `<option value="">-- Choose Batch --</option>` + 
            state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || 'Center'})</option>`).join("");
    }
}"""

    new_load_options = """    const undoSelect = document.getElementById("undo-batch-select");
    if (undoSelect) {
        undoSelect.innerHTML = `<option value="">-- Choose Batch --</option>` + 
            state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || 'Center'})</option>`).join("");
    }
    
    // Initialize the calendar visualizer placeholder message
    loadSyncAttendanceCalendar();
}"""

    js = js.replace(old_load_options, new_load_options)

    # Update renderSyncCalendar to return placeholder if batchId is empty
    old_render_calendar = """function renderSyncCalendar() {
    const grid = document.getElementById("teacher-sync-calendar-grid");
    const monthYearLabel = document.getElementById("cal-current-month-year");
    if (!grid || !monthYearLabel) return;

    const dateInput = document.getElementById("upload-date-input");"""

    new_render_calendar = """function renderSyncCalendar() {
    const grid = document.getElementById("teacher-sync-calendar-grid");
    const monthYearLabel = document.getElementById("cal-current-month-year");
    if (!grid || !monthYearLabel) return;

    const batchSelect = document.getElementById("upload-batch-select");
    const batchId = batchSelect ? batchSelect.value : "";
    if (!batchId) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">Please select a batch to view attendance visualizer</div>`;
        return;
    }

    const dateInput = document.getElementById("upload-date-input");"""

    js = js.replace(old_render_calendar, new_render_calendar)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Fixed calendar rendering check in app.js.")

if __name__ == "__main__":
    fix_calendar_placeholder_bug()
