import re

def update_index_html():
    file_path = "backend/static/index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update Login Card brand name and formal styling
    html = html.replace('<h1>Livelihood Skills</h1>', '<h1>JSS ATTENDANCE</h1>')
    html = html.replace('<p>Attendance Management Portal</p>', '<p>Ministry of Skill Development & Entrepreneurship</p>')
    html = html.replace('<span class="brand-tag">NGO Portal</span>', '<span class="brand-tag">Govt of India</span>')

    # Add Theme Toggle to Login Card
    theme_btn_login = """
                <div class="theme-toggle-container">
                    <button type="button" id="theme-toggle-login" class="btn btn-secondary btn-small">🌓 Toggle Theme</button>
                </div>
                <form id="login-form">"""
    if "theme-toggle-login" not in html:
        html = html.replace('<form id="login-form">', theme_btn_login)

    # 2. Main Header title and theme toggle
    html = html.replace('<h2>NGO Attendance Portal</h2>', '<h2>JSS Attendance Portal</h2>')
    html = html.replace('<h2>NGO Attendance Portal</h2>', '<h2>JSS Attendance Portal</h2>')
    
    header_actions = """
                <div class="header-actions">
                    <button id="theme-toggle-main" class="btn btn-secondary" style="margin-right: 10px;">🌓 Theme</button>
                    <button id="logout-btn" class="btn btn-secondary">Log Out</button>
                </div>"""
    
    # Replace the old header-actions block
    html = re.sub(r'<div class="header-actions">.*?</div>', header_actions, html, flags=re.DOTALL)

    # 3. Sidebar labels and cleanup
    html = html.replace('<h3>NGO COORDINATOR</h3>', '<h3>JSS COORDINATOR</h3>')
    html = html.replace('<h3>NGO Portal</h3>', '<h3>JSS ATTENDANCE</h3>')
    
    # Ensure Audit Logs and Students are fully removed from sidebar
    html = re.sub(r'<a href="#admin-logs".*?</a>', "", html, flags=re.DOTALL)
    html = re.sub(r'<a href="#admin-students".*?</a>', "", html, flags=re.DOTALL)

    # Ensure Student and Audit Logs tab content sections are removed
    html = re.sub(r'<section id="tab-admin-students".*?</section>', "", html, flags=re.DOTALL)
    html = re.sub(r'<section id="tab-admin-logs".*?</section>', "", html, flags=re.DOTALL)

    # 4. Admin Batches View Action column
    batches_table_header = """<thead>
                                        <tr>
                                            <th>SID Batch ID</th>
                                            <th>Course Name</th>
                                            <th>Center</th>
                                            <th>Teacher</th>
                                            <th>Sessions</th>
                                            <th>Students</th>
                                            <th>Class Eligibility</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>"""
    # Replace batches table header to ensure Actions is present
    html = re.sub(r'<tbody id="admin-batches-table-body">', '<tbody id="admin-batches-table-body">', html)

    # 5. Add Admin Batch Details Tab
    admin_batch_detail_tab = """
                    <!-- ================= ADMIN BATCHES DETAIL TAB ================= -->
                    <section id="tab-admin-batches-detail" class="tab-content">
                        <div class="dashboard-header flex-header">
                            <div>
                                <h1 id="admin-batch-detail-title">Select a Batch</h1>
                                <p id="admin-batch-detail-sub">View batch records and download reports.</p>
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
                                    <span class="val" id="admin-det-course">Course</span>
                                </div>
                                <div>
                                    <span class="label">SID Batch ID</span>
                                    <span class="val" id="admin-det-sid">Batch ID</span>
                                </div>
                                <div>
                                    <span class="label">Training Center</span>
                                    <span class="val" id="admin-det-center">Center</span>
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
    
    # Inject before teacher-dashboard section
    if "tab-admin-batches-detail" not in html:
        html = html.replace('<!-- ================= TEACHER DASHBOARD TAB ================= -->', 
                            admin_batch_detail_tab + '\n                    <!-- ================= TEACHER DASHBOARD TAB ================= -->')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f.read() if False else html)
    print("Updated index.html successfully.")

def update_style_css():
    file_path = "backend/static/style.css"
    
    css_content = """/* Design Tokens & Theme Setup */
:root {
    /* Default Theme: Formal NIC/Govt Light Theme */
    --bg-main: #f1f5f9;
    --header-bg: #0b3c5d;      /* Deep navy blue */
    --header-text: #ffffff;
    --sidebar-bg: #ffffff;
    --sidebar-border: #cbd5e1;
    --card-bg: #ffffff;
    --card-border: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --accent-blue: #1d4ed8;
    --accent-blue-hover: #1e40af;
    --table-header-bg: #e2e8f0;
    --table-header-text: #1e293b;
    --table-border: #cbd5e1;
    --shadow-premium: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Inter', sans-serif;
    
    --status-eligible: #059669;    /* Clean green */
    --status-at-risk: #d97706;     /* Clean orange/yellow */
    --status-impossible: #dc2626;  /* Clean red */
}

body.dark-theme {
    /* Dark Theme */
    --bg-main: #0f172a;
    --header-bg: #1e293b;
    --header-text: #f8fafc;
    --sidebar-bg: #1e293b;
    --sidebar-border: #334155;
    --card-bg: rgba(255, 255, 255, 0.03);
    --card-border: rgba(255, 255, 255, 0.08);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-blue: #3b82f6;
    --accent-blue-hover: #2563eb;
    --table-header-bg: rgba(255, 255, 255, 0.02);
    --table-header-text: #94a3b8;
    --table-border: rgba(255, 255, 255, 0.08);
    --shadow-premium: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

/* Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-body);
    background: var(--bg-main);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
    line-height: 1.5;
}

h1, h2, h3, h4, .brand h1 {
    font-family: var(--font-heading);
    font-weight: 600;
}

/* Glassmorphism / Card Components */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--shadow-premium);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

body:not(.dark-theme) .glass-card {
    background: #ffffff;
}

/* Screens Layout */
.screen {
    display: none;
    opacity: 0;
    transition: opacity 0.4s ease-in-out;
}

.screen.active {
    display: block;
    opacity: 1;
}

/* 1. Login Screen */
#login-screen {
    display: none;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
    background: var(--bg-main);
}

#login-screen.active {
    display: flex;
}

.login-card {
    width: 100%;
    max-width: 440px;
    padding: 40px;
    border-radius: 16px;
}

.brand {
    text-align: center;
    margin-bottom: 30px;
}

.brand-tag {
    background: rgba(29, 78, 216, 0.1);
    color: var(--accent-blue);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 1px solid rgba(29, 78, 216, 0.2);
}

.brand h1 {
    font-size: 28px;
    margin-top: 10px;
    color: var(--text-primary);
}

.brand p {
    color: var(--text-secondary);
    font-size: 13px;
    margin-top: 4px;
    font-weight: 500;
}

/* Theme Toggle styles */
.theme-toggle-container {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 15px;
}

/* 2. Main App Screen Layout */
.main-header {
    height: 70px;
    background: var(--header-bg);
    color: var(--header-text);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    font-size: 24px;
}

.header-logo h2 {
    font-size: 18px;
    font-weight: 600;
}

.user-role-badge {
    font-size: 11px;
    color: #93c5fd;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

body.dark-theme .user-role-badge {
    color: var(--text-secondary);
}

.app-layout {
    display: grid;
    grid-template-columns: 240px 1fr;
    min-height: calc(100vh - 70px);
}

/* Sidebar Styling */
.sidebar {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    padding: 30px 20px;
}

.nav-group {
    margin-bottom: 30px;
}

.nav-group h3 {
    font-size: 11px;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 1.5px;
    margin-bottom: 15px;
    padding-left: 12px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-secondary);
    text-decoration: none;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}

.nav-item:hover {
    color: var(--text-primary);
    background: rgba(0, 0, 0, 0.05);
}

body.dark-theme .nav-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
    color: white !important;
    background: var(--accent-blue);
    box-shadow: 0 4px 12px rgba(29, 78, 216, 0.2);
}

/* Content Area */
.content-area {
    padding: 40px;
    overflow-y: auto;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.dashboard-header {
    margin-bottom: 30px;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 15px;
}

.dashboard-header h1 {
    font-size: 28px;
    color: var(--text-primary);
    margin-bottom: 6px;
}

.dashboard-header p {
    color: var(--text-secondary);
    font-size: 15px;
}

.flex-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Form Styles */
.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-group input, .form-group select, .form-group textarea {
    width: 100%;
    padding: 12px 16px;
    border-radius: 8px;
    background: #ffffff;
    border: 1px solid var(--card-border);
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

body.dark-theme .form-group input, body.dark-theme .form-group select {
    background: rgba(0,0,0,0.2);
}

.form-group input:focus, .form-group select:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.15);
}

.form-row {
    display: flex;
    gap: 15px;
}

.col {
    flex: 1;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
    font-family: var(--font-heading);
}

.btn-primary {
    background: var(--accent-blue);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-blue-hover);
}

.btn-secondary {
    background: #ffffff;
    color: var(--text-primary);
    border: 1px solid var(--card-border);
}

body.dark-theme .btn-secondary {
    background: rgba(255,255,255,0.05);
}

.btn-secondary:hover {
    background: #f8fafc;
}

body.dark-theme .btn-secondary:hover {
    background: rgba(255,255,255,0.1);
}

.btn-block {
    display: flex;
    width: 100%;
}

.btn-small {
    padding: 6px 12px;
    font-size: 11px;
    border-radius: 6px;
}

/* Metrics Cards */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}

.metric-card {
    display: flex;
    align-items: center;
    gap: 20px;
    background: #ffffff;
}

.metric-icon {
    font-size: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 54px;
    height: 54px;
    border-radius: 12px;
}

.students-icon { background: rgba(29, 78, 216, 0.08); color: var(--accent-blue); }
.batches-icon { background: rgba(139, 92, 246, 0.08); color: #8b5cf6; }
.centers-icon { background: rgba(236, 72, 153, 0.08); color: #ec4899; }
.alert-icon { background: rgba(239, 68, 68, 0.08); color: var(--status-impossible); }

.metric-data h3 {
    font-size: 26px;
    line-height: 1.1;
    margin-bottom: 2px;
}

.metric-data p {
    font-size: 12px;
    color: var(--text-secondary);
}

/* Tables styling */
.content-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
    margin-top: 30px;
}

@media(min-width: 1200px) {
    .content-grid {
        grid-template-columns: 1fr 1fr;
    }
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 10px;
}

.card-header h2 {
    font-size: 18px;
}

.table-container {
    width: 100%;
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 13px;
}

.data-table th, .data-table td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--table-border);
}

.data-table th {
    font-family: var(--font-heading);
    font-weight: 600;
    background: var(--table-header-bg);
    color: var(--table-header-text);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.data-table tbody tr {
    transition: background 0.2s ease;
}

.data-table tbody tr:hover {
    background: rgba(0, 0, 0, 0.015);
}

body.dark-theme .data-table tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

.text-center { text-align: center; }

/* Status Badges */
.badge {
    display: inline-flex;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-success { background: rgba(5, 150, 105, 0.15); color: var(--status-eligible); }
.badge-warning { background: rgba(217, 119, 6, 0.15); color: var(--status-at-risk); }
.badge-danger { background: rgba(220, 38, 38, 0.15); color: var(--status-impossible); }
.badge-secondary { background: #e2e8f0; color: #475569; }

/* File Drop Zone */
.drop-zone {
    border: 2px dashed var(--card-border);
    border-radius: 12px;
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    background: rgba(0, 0, 0, 0.02);
    transition: border-color 0.2s ease;
}

.drop-zone:hover {
    border-color: var(--accent-blue);
}

.drop-zone-icon {
    font-size: 32px;
    display: block;
    margin-bottom: 10px;
}

/* Modals */
.modal {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(4px);
    z-index: 200;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.modal.active {
    display: flex;
    opacity: 1;
}

.modal-content {
    width: 100%;
    max-width: 500px;
    margin: 20px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.close-btn {
    font-size: 24px;
    cursor: pointer;
}

/* Toast Alerts */
#toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 300;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.toast {
    background: #1e293b;
    border-left: 4px solid var(--accent-blue);
    border-radius: 6px;
    padding: 16px 20px;
    color: white;
    font-size: 13px;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease forwards;
}

.toast.success { border-color: var(--status-eligible); }
.toast.error { border-color: var(--status-impossible); }

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Utility Classes */
.hidden { display: none !important; }
.mt-20 { margin-top: 20px; }
.max-w-600 { max-w: 600px; }
.class-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
}
.class-summary-grid .label {
    display: block;
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    margin-bottom: 4px;
}
.class-summary-grid .val {
    font-size: 16px;
    font-weight: 600;
}
"""
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("Updated style.css successfully.")

def update_app_js():
    file_path = "backend/static/app.js"
    with open(file_path, "r", encoding="utf-8") as f:
        js = f.read()

    # 1. Add Theme Toggle Javascript Event Bindings
    theme_js_funcs = """
// Theme Management Logic
function initTheme() {
    const currentTheme = localStorage.getItem("theme") || "light";
    if (currentTheme === "dark") {
        document.body.classList.add("dark-theme");
    }
    
    const toggleLogin = document.getElementById("theme-toggle-login");
    const toggleMain = document.getElementById("theme-toggle-main");

    const toggleTheme = () => {
        document.body.classList.toggle("dark-theme");
        const theme = document.body.classList.contains("dark-theme") ? "dark" : "light";
        localStorage.setItem("theme", theme);
    };

    if (toggleLogin) toggleLogin.addEventListener("click", toggleTheme);
    if (toggleMain) toggleMain.addEventListener("click", toggleTheme);
}
"""

    if "initTheme" not in js:
        # Append theme JS helper functions to top
        js = theme_js_funcs + "\n" + js
        
        # Inject call to initTheme inside DOMContentLoaded block at end of file
        js = js.replace('initNavigation();\n    setup_screenForRole();', 'initTheme();\n    initNavigation();\n    setupScreenForRole();')
        js = js.replace('setup_screenForRole()', 'setupScreenForRole()')
        js = js.replace('setupScreenForRole()', 'setupScreenForRole()')

    # 2. Update loadAdminBatches() to output a 'View' Action column row cell
    old_row_html = """return `
                <tr>
                    <td><code>${b.sid_batch_id}</code></td>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name}</td>
                    <td>${b.total_sessions}</td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status} (${b.class_eligibility_pct}%)</span></td>
                    <td><span class="badge ${b.status === 'active' ? 'badge-success' : 'badge-secondary'}">${b.status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">Delete</button>
                    </td>
                </tr>
            `;"""
            
    new_row_html = """return `
                <tr>
                    <td><code>${b.sid_batch_id}</code></td>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name}</td>
                    <td>${b.total_sessions}</td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status} (${b.class_eligibility_pct}%)</span></td>
                    <td><span class="badge ${b.status === 'active' ? 'badge-success' : 'badge-secondary'}">${b.status}</span></td>
                    <td>
                        <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})" style="margin-right: 5px;">🔍 View</button>
                        <button class="btn btn-secondary btn-small" onclick="deleteBatch(${b.id})">Delete</button>
                    </td>
                </tr>
            `;"""
            
    js = js.replace(old_row_html, new_row_html)

    # 3. Add viewAdminBatchDetails() function to app.js
    admin_batch_detail_js = """
// Admin View Batch Details (incorporating batch wise student viewing)
async function viewAdminBatchDetails(batchId) {
    switchTab("admin-batches-detail");

    try {
        const bRes = await fetch(`${API_URL}/batches/${batchId}`, { headers: getHeaders() });
        const batch = await bRes.json();
        
        document.getElementById("admin-batch-detail-title").innerText = batch.course_name;
        document.getElementById("admin-batch-detail-sub").innerText = `SID Batch ID: ${batch.sid_batch_id}`;
        
        document.getElementById("admin-det-course").innerText = batch.course_name;
        document.getElementById("admin-det-sid").innerText = batch.sid_batch_id;
        document.getElementById("admin-det-center").innerText = batch.center_name;
        
        const statusEl = document.getElementById("admin-det-eligibility");
        statusEl.innerText = `${batch.class_status} (${batch.class_eligibility_pct}%)`;
        statusEl.className = "val " + (batch.class_status === "ELIGIBLE" ? "text-success" : (batch.class_status === "AT_RISK" ? "text-warning" : "text-danger"));

        document.getElementById("admin-batch-detail-summary-card").classList.remove("hidden");
        document.getElementById("admin-batch-detail-actions").classList.remove("hidden");

        // Load students in batch
        const sRes = await fetch(`${API_URL}/students/?batch_id=${batchId}`, { headers: getHeaders() });
        const students = await sRes.json();

        const sBody = document.getElementById("admin-batch-students-body");
        sBody.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.attended_sessions}</td>
                    <td>${s.missed_sessions}</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${s.status === 'ELIGIBLE' ? 'Qualifies' : `${s.still_need_to_attend} sessions`}</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered in this batch.</td></tr>`;

        // PDF and Excel downloads
        document.getElementById("btn-admin-batch-pdf").onclick = () => {
            window.open(`${API_URL}/reports/batch/${batchId}/pdf?token=${state.token}`, "_blank");
        };
        document.getElementById("btn-admin-batch-excel").onclick = () => {
            window.open(`${API_URL}/reports/batch/${batchId}/excel?token=${state.token}`, "_blank");
        };

    } catch (err) {
        showToast(err.message, "error");
    }
}
"""
    if "viewAdminBatchDetails" not in js:
        js = admin_batch_detail_js + "\n" + js

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

if __name__ == "__main__":
    update_index_html()
    update_style_css()
    update_app_js()
