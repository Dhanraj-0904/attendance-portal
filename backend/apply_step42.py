def remove_duplicate_admin_upload():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Find and delete the batch tab copy of admin-batch-student-upload-card
    old_card_batches = """                        <!-- Master Student List CSV Upload Form -->
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
                        </div>"""

    html = html.replace(old_card_batches, "")

    # Bump version
    html = html.replace("app.js?v=38", "app.js?v=39")
    html = html.replace("style.css?v=38", "style.css?v=39")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Deleted duplicate Import Student Enrollment cards from index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Remove the DOM manipulation in viewAdminBatchDetails
    old_dom_manipulation = """        // Populate and show Admin student CSV upload card
        const adminUploadCard = document.getElementById("admin-batch-student-upload-card");
        const adminUploadBatchInput = document.getElementById("admin-student-upload-batch-id");
        if (adminUploadCard && adminUploadBatchInput) {
            adminUploadBatchInput.value = batchId;
            adminUploadCard.classList.remove("hidden");
        }"""

    js = js.replace(old_dom_manipulation, "")

    # Remove the event listener for admin-student-upload-form
    old_event_listener = """    // Admin Student List Upload Form Handler
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
    }"""

    js = js.replace(old_event_listener, "")

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Cleaned up admin upload form events and details panel linkages in app.js.")

if __name__ == "__main__":
    remove_duplicate_admin_upload()
