import re

def apply_admin_batch_wise_student_view():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove Students sidebar navigation item
    html = re.sub(r'<a href="#admin-students".*?</a>', "", html, flags=re.DOTALL)

    # Remove the entire Student Directory Tab (section)
    html = re.sub(r'<!-- ================= ADMIN STUDENTS TAB ================= -->.*?<!-- ================= ADMIN AUDIT LOGS TAB ================= -->',
                  '<!-- ================= ADMIN AUDIT LOGS TAB ================= -->', html, flags=re.DOTALL)

    # Inject the Admin Batch Details Tab
    admin_batch_detail_tab = """
                    <!-- ================= ADMIN BATCHES DETAIL TAB ================= -->
                    <section id="tab-admin-batches-detail" class="tab-content">
                        <div class="dashboard-header flex-header">
                            <div>
                                <h1 id="admin-batch-detail-title">Select a Batch</h1>
                                <p id="admin-batch-detail-sub">View list and download reports.</p>
                            </div>
                            <div id="admin-batch-detail-actions" class="hidden">
                                <button id="btn-admin-batch-pdf" class="btn btn-primary">📄 Download PDF Report</button>
                                <button id="btn-admin-batch-excel" class="btn btn-secondary">📊 Export Excel</button>
                            </div>
                        </div>

                        <!-- Class summary widget -->
                        <div id="admin-batch-detail-summary-card" class="glass-card mt-20 hidden">
                            <div class="class-summary-grid">
                                <div>
                                    <span class="label">Course Name</span>
                                    <span class="val" id="admin-det-course">Beauty Care Assistant</span>
                                </div>
                                <div>
                                    <span class="label">SID Batch ID</span>
                                    <span class="val" id="admin-det-sid">TC325939</span>
                                </div>
                                <div>
                                    <span class="label">Training Center</span>
                                    <span class="val" id="admin-det-center">Shyam Nagar Center</span>
                                </div>
                                <div>
                                    <span class="label">Class Eligibility Status</span>
                                    <span class="val" id="admin-det-eligibility">ELIGIBLE</span>
                                </div>
                            </div>
                        </div>

                        <div class="glass-card mt-20">
                            <div class="table-container">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Student SID ID</th>
                                            <th>Name</th>
                                            <th>Attended</th>
                                            <th>Missed</th>
                                            <th>Attendance %</th>
                                            <th>Needed to Reach 75%</th>
                                            <th>Assessment Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="admin-batch-students-body">
                                        <tr><td colspan="7" class="text-center">Loading batch details...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </section>
    """

    if "tab-admin-batches-detail" not in html:
        # Inject it right before <!-- ================= ADMIN AUDIT LOGS TAB ================= -->
        html = html.replace('<!-- ================= ADMIN AUDIT LOGS TAB ================= -->',
                            admin_batch_detail_tab + '\n                    <!-- ================= ADMIN AUDIT LOGS TAB ================= -->')

    # Bump version tags
    html = html.replace('style.css?v=4.1', 'style.css?v=5')
    html = html.replace('app.js?v=4', 'app.js?v=5')

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html with Admin Batch Detail tab successfully.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Modify loadAdminBatches() mapping to add the View button in Actions column
    old_actions = """                    <td>
                        <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                    </td>"""

    new_actions = """                    <td>
                        <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})" style="margin-right: 5px;">🔍 View</button>
                        <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                    </td>"""

    js = js.replace(old_actions, new_actions)

    # Add viewAdminBatchDetails(batchId) function definition
    view_admin_batch_details_fn = """
// Admin View Batch Details (incorporating batch wise student viewing)
async function viewAdminBatchDetails(batchId) {
    switchTab("admin-batches-detail");
    const titleEl = document.getElementById("admin-batch-detail-title");
    const subEl = document.getElementById("admin-batch-detail-sub");
    const courseEl = document.getElementById("admin-det-course");
    const sidEl = document.getElementById("admin-det-sid");
    const centerEl = document.getElementById("admin-det-center");
    const elSpan = document.getElementById("admin-det-eligibility");
    const body = document.getElementById("admin-batch-students-body");
    const actions = document.getElementById("admin-batch-detail-actions");
    const summaryCard = document.getElementById("admin-batch-detail-summary-card");

    body.innerHTML = `<tr><td colspan="7" class="text-center">Loading batch details...</td></tr>`;

    try {
        const res = await fetch(`${API_URL}/batches/${batchId}`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load batch info");
        const batch = await res.json();

        titleEl.innerText = batch.course_name;
        subEl.innerText = `SID ID: ${batch.sid_batch_id} | Total Sessions: ${batch.total_sessions}`;
        
        courseEl.innerText = batch.course_name;
        sidEl.innerText = batch.sid_batch_id;
        centerEl.innerText = batch.center_name;
        
        elSpan.innerText = batch.class_status;
        elSpan.className = "val " + (batch.class_status === "ELIGIBLE" ? "text-success" : (batch.class_status === "AT_RISK" ? "text-warning" : "text-danger"));

        summaryCard.classList.remove("hidden");
        actions.classList.remove("hidden");

        const sRes = await fetch(`${API_URL}/students/?batch_id=${batchId}`, { headers: getHeaders() });
        if (!sRes.ok) throw new Error("Failed to load batch students");
        const students = await sRes.json();

        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.sessions_attended}</td>
                    <td>${s.sessions_missed}</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.sessions_needed_for_75}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;

        document.getElementById("btn-admin-batch-pdf").onclick = () => downloadReport('pdf', batchId);
        document.getElementById("btn-admin-batch-excel").onclick = () => downloadReport('excel', batchId);

    } catch (err) {
        showToast(err.message, "error");
    }
}
"""
    if "async function viewAdminBatchDetails" not in js:
        # Prepend to logic block
        js = js.replace("async function loadAdminDashboard() {", view_admin_batch_details_fn + "\nasync function loadAdminDashboard() {")

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    apply_admin_batch_wise_student_view()
