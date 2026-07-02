def apply_batch_table_refactoring():
    # 1. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Remove SID Batch ID header
    old_headers = """                                            <th>SID Batch ID</th>
                                            <th>Course Name</th>
                                            <th>Center</th>"""

    new_headers = """                                            <th>Course Name</th>
                                            <th>Center</th>"""

    html = html.replace(old_headers, new_headers)

    # Bump version
    html = html.replace("app.js?v=21", "app.js?v=22")
    html = html.replace("style.css?v=21", "style.css?v=22")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Removed SID Batch ID column header from index.html.")

    # 2. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Replace loadAdminBatches row mapping to exclude SID Batch ID and fix status comparison
    old_load_batches = """async function loadAdminBatches() {
    try {
        const res = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load batches");
        const batches = await res.json();

        const body = document.getElementById("admin-batches-table-body");
        body.innerHTML = batches.map(b => {
            const status_badge = b.is_active ? `<span class="badge badge-success">Running</span>` : `<span class="badge badge-danger">Closed</span>`;
            const class_elig_badge = b.class_status === "ELIGIBLE" ? "badge-success" : (b.class_status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code title="${b.sid_batch_id}">${b.sid_batch_id}</code></td>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name || 'Unassigned'}</td>
                    <td>${b.total_sessions} sessions</td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status}</span></td>
                    <td>${status_badge}</td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})">🔍 View</button>
                            <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="9" class="text-center">No batches created</td></tr>`;"""

    new_load_batches = """async function loadAdminBatches() {
    try {
        const res = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load batches");
        const batches = await res.json();

        const body = document.getElementById("admin-batches-table-body");
        body.innerHTML = batches.map(b => {
            const status_badge = b.status === "active" ? `<span class="badge badge-success">Running</span>` : `<span class="badge badge-danger">Closed</span>`;
            const class_elig_badge = b.class_status === "ELIGIBLE" ? "badge-success" : (b.class_status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name || 'Unassigned'}</td>
                    <td>${b.total_sessions} sessions</td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status}</span></td>
                    <td>${status_badge}</td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})">🔍 View</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="8" class="text-center">No batches created</td></tr>`;"""

    js = js.replace(old_load_batches, new_load_batches)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js columns and fixed status matching.")

if __name__ == "__main__":
    apply_batch_table_refactoring()
