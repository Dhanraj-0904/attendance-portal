def apply_calendar_and_future_date_fix():
    # 1. Update index.html (fix calendar grid header class)
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace('class="calendar-days-header"', 'class="calendar-grid-header"')

    # Bump version
    html = html.replace("app.js?v=22", "app.js?v=23")
    html = html.replace("style.css?v=22", "style.css?v=23")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed calendar days header class in index.html.")

    # 2. Update app.js (validate date and append to payload)
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_upload_form_submit = """const uploadForm = document.getElementById("upload-csv-form");
if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const batchId = document.getElementById("upload-batch-select").value;
        const file = fileInput.files[0];

        if (!batchId || !file) {
            showToast("Please select a batch and upload a file", "error");
            return;
        }

        const formData = new FormData();
        formData.append("batch_id", batchId);
        formData.append("file", file);"""

    new_upload_form_submit = """const uploadForm = document.getElementById("upload-csv-form");
if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const batchId = document.getElementById("upload-batch-select").value;
        const dateInput = document.getElementById("upload-date-input");
        const dateVal = dateInput ? dateInput.value : "";
        const file = fileInput.files[0];

        if (!batchId || !file || !dateVal) {
            showToast("Please select a batch, date, and upload a file", "error");
            return;
        }

        // Validate future date
        const selectedDate = new Date(dateVal);
        const today = new Date();
        selectedDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate > today) {
            showToast("Error: You cannot upload attendance for a future date.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("batch_id", batchId);
        formData.append("date", dateVal);
        formData.append("file", file);"""

    js = js.replace(old_upload_form_submit, new_upload_form_submit)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected future date validation and date param appending in app.js.")

    # 3. Update backend/routers/sync.py (backend future date validation)
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync_code = f.read()

    old_parse_date = """    # Parse target date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")"""

    new_parse_date = """    # Parse target date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Prevent future date uploads
    from datetime import date as dt_date
    if target_date > dt_date.today():
        raise HTTPException(status_code=400, detail="Error: You cannot upload attendance for a future date.")"""

    if "dt_date.today()" not in sync_code:
        sync_code = sync_code.replace(old_parse_date, new_parse_date)
        with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
            f.write(sync_code)
        print("Added backend future date validation in sync.py.")

if __name__ == "__main__":
    apply_calendar_and_future_date_fix()
