import re

def apply_admin_cleanup():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove NSDC column header from Centers table
    html = html.replace("<th>NSDC Center Code</th>", "")

    # Remove NSDC input from Center Modal Form
    old_nsdc_group = """                    <div class="form-group">
                        <label for="center-code">NSDC Center Code</label>
                        <input type="text" id="center-code" placeholder="e.g. TC325939" required>
                    </div>"""
    html = html.replace(old_nsdc_group, "")

    # Remove SID Batch ID input from Create Batch form
    old_sid_group = """                    <div class="form-group">
                        <label for="batch-sid">SID Batch ID</label>
                        <input type="text" id="batch-sid" placeholder="e.g. BATCH_00921" required>
                    </div>"""
    html = html.replace(old_sid_group, "")

    # Remove End Date input from Create Batch form
    old_date_row = """                    <div class="form-row">
                        <div class="form-group col">
                            <label for="batch-start">Start Date</label>
                            <input type="date" id="batch-start" required>
                        </div>
                        <div class="form-group col">
                            <label for="batch-end">End Date</label>
                            <input type="date" id="batch-end" required>
                        </div>
                    </div>"""

    new_date_row = """                    <div class="form-group">
                        <label for="batch-start">Start Date</label>
                        <input type="date" id="batch-start" required>
                    </div>"""
    html = html.replace(old_date_row, new_date_row)

    # Bump static file versions to refresh cache
    html = html.replace('style.css?v=11', 'style.css?v=12')
    html = html.replace('app.js?v=11', 'app.js?v=12')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Cleaned up index.html fields.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update center form submit handler to omit nsdc_center_code
    old_center_submit = """    const data = {
        name: document.getElementById("center-name").value,
        nsdc_center_code: document.getElementById("center-code").value,
        district: document.getElementById("center-district").value,
        state: document.getElementById("center-state").value
    };"""

    new_center_submit = """    const data = {
        name: document.getElementById("center-name").value,
        district: document.getElementById("center-district").value,
        state: document.getElementById("center-state").value
    };"""
    js = js.replace(old_center_submit, new_center_submit)

    # Update batch form submit handler to omit sid_batch_id and end_date
    old_batch_submit = """    const data = {
        center_id: parseInt(document.getElementById("batch-center").value),
        teacher_id: parseInt(document.getElementById("batch-teacher").value),
        sid_batch_id: document.getElementById("batch-sid").value,
        course_name: document.getElementById("batch-course").value,
        start_date: document.getElementById("batch-start").value,
        end_date: document.getElementById("batch-end").value,
        total_sessions: parseInt(document.getElementById("batch-sessions").value)
    };"""

    new_batch_submit = """    const data = {
        center_id: parseInt(document.getElementById("batch-center").value),
        teacher_id: parseInt(document.getElementById("batch-teacher").value),
        course_name: document.getElementById("batch-course").value,
        start_date: document.getElementById("batch-start").value,
        total_sessions: parseInt(document.getElementById("batch-sessions").value)
    };"""
    js = js.replace(old_batch_submit, new_batch_submit)

    # Remove NSDC column cell from loadAdminCenters
    js = js.replace("<td><code>${c.nsdc_center_code}</code></td>", "")
    js = js.replace('colspan="5" class="text-center">No centers registered', 'colspan="4" class="text-center">No centers registered')

    # Improve batch option text in dropdown populators (use center name instead of sid_batch_id)
    js = js.replace('batches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("")',
                    'batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || \'Center\'})</option>`).join("")')

    js = js.replace('state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("")',
                    'state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || \'Center\'})</option>`).join("")')

    js = js.replace('teacherBatches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("")',
                    'teacherBatches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || \'Center\'})</option>`).join("")')

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Cleaned up app.js fields.")

if __name__ == "__main__":
    apply_admin_cleanup()
