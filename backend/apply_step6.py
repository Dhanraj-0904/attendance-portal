import re

def apply_undo_sync_feature():
    # 1. Update backend/routers/sync.py
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync_code = f.read()

    undo_route = """

@router.post("/undo/{batch_id}")
def undo_last_sync(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Authorize: Only admin or the teacher of this batch can undo
    if current_user.role == "teacher" and batch.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to undo sync for this batch"
        )

    # Find the latest synced record for this batch
    latest_rec = db.query(AttendanceRecord).filter(
        AttendanceRecord.batch_id == batch_id,
        AttendanceRecord.source == "csv_upload"
    ).order_by(AttendanceRecord.synced_at.desc()).first()

    if not latest_rec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No CSV upload records found to undo for this batch"
        )

    # Group records synced within a 15-second window of the latest record
    latest_time = latest_rec.synced_at
    margin = timedelta(seconds=15)
    time_start = latest_time - margin
    time_end = latest_time + margin

    records_to_delete = db.query(AttendanceRecord).filter(
        AttendanceRecord.batch_id == batch_id,
        AttendanceRecord.source == "csv_upload",
        AttendanceRecord.synced_at >= time_start,
        AttendanceRecord.synced_at <= time_end
    ).all()

    num_deleted = len(records_to_delete)
    if num_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No matching records found to undo"
        )

    # Delete records
    for r in records_to_delete:
        db.delete(r)

    db.commit()

    # Log action
    log_action(db, current_user.id, "undo_upload_csv", "batches", batch_id)

    return {
        "message": f"Successfully undone last sync. Removed {num_deleted} attendance records.",
        "records_removed": num_deleted
    }
"""

    if "/undo/{batch_id}" not in sync_code:
        sync_code += undo_route

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync_code)
    print("Injected /sync/undo/{batch_id} endpoint successfully.")

    # 2. Update index.html to add Undo Sync section
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    undo_html = """
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
                                    <button type="submit" class="btn btn-secondary btn-block" style="border-color: var(--status-impossible); color: var(--status-impossible);">
                                        Revert Last Import
                                    </button>
                                </form>
                            </div>
                        </div>"""

    # Replace end of upload-csv-form container
    html = html.replace('</form>\n                        </div>', undo_html)

    # Bump version tags
    html = html.replace('style.css?v=5.1', 'style.css?v=7') # in case
    html = html.replace('app.js?v=6', 'app.js?v=7')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html with Undo Sync section successfully.")

    # 3. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Update loadTeacherUploadOptions dropdown population
    old_dropdown_code = """function loadTeacherUploadOptions() {
    // Load instructor's assigned batches into dropdown selection
    const select = document.getElementById("upload-batch-select");
    select.innerHTML = `<option value="">-- Choose Batch --</option>` + 
        state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("");
}"""

    new_dropdown_code = """function loadTeacherUploadOptions() {
    // Load instructor's assigned batches into dropdown selection
    const select = document.getElementById("upload-batch-select");
    select.innerHTML = `<option value="">-- Choose Batch --</option>` + 
        state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("");

    const undoSelect = document.getElementById("undo-batch-select");
    if (undoSelect) {
        undoSelect.innerHTML = `<option value="">-- Choose Batch --</option>` + 
            state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.sid_batch_id})</option>`).join("");
    }
}"""

    js = js.replace(old_dropdown_code, new_dropdown_code)

    # Add submit listener for undo Form at bottom of DOMContentLoaded or next to other listeners
    undo_form_js = """
    // Revert/Undo CSV Sync Form Handler
    const undoForm = document.getElementById("undo-sync-form");
    if (undoForm) {
        undoForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const batchId = document.getElementById("undo-batch-select").value;
            if (!batchId) return;

            if (!confirm("Are you sure you want to delete all attendance records imported in the last CSV upload for this batch? This action cannot be reverted.")) {
                return;
            }

            try {
                showToast("Reverting last upload...", "info");
                const res = await fetch(`${API_URL}/sync/undo/${batchId}`, {
                    method: "POST",
                    headers: getHeaders()
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Undo failed");
                }

                const data = await res.json();
                showToast(data.message);
                switchTab("teacher-dashboard");
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }
"""

    # Inject inside DOMContentLoaded or at end of file
    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + undo_form_js)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js with Undo Sync form listener successfully.")

if __name__ == "__main__":
    apply_sync_undo_feature = apply_undo_sync_feature()
