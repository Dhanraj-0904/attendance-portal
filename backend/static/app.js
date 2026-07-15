

// 2026 Gazetted Holidays in India
const GAZETTED_HOLIDAYS_2026 = [
    "2026-01-26", // Republic Day
    "2026-03-21", // Idu'l Fitr
    "2026-03-31", // Mahavir Jayanti
    "2026-04-03", // Good Friday
    "2026-05-01", // Buddha Purnima
    "2026-05-27", // Idu'l Zuha
    "2026-06-26", // Muharram
    "2026-08-15", // Independence Day
    "2026-09-05", // Prophet Mohammad's Birthday
    "2026-10-02", // Mahatma Gandhi's Birthday
    "2026-10-20", // Dussehra
    "2026-11-08", // Diwali
    "2026-11-24", // Guru Nanak's Birthday
    "2026-12-25"  // Christmas Day
];

// Hours formatting utility to convert float hours (e.g. 44.6) to minutes-based decimals (e.g. 44.36)
function formatHours(hours) {
    if (hours === undefined || hours === null || isNaN(hours)) return "0.00";
    const totalMins = Math.round(hours * 60);
    const h = Math.floor(totalMins / 60);
    const m = totalMins % 60;
    return `${h}.${String(m).padStart(2, '0')}`;
}

// Theme Management Logic
function initTheme() {
    const currentTheme = localStorage.getItem("theme") || "dark";
    if (currentTheme === "light") {
        document.body.classList.add("light-theme");
    }
    
    const toggleLogin = document.getElementById("theme-toggle-login");
    const toggleMain = document.getElementById("theme-toggle-main");

    const toggleTheme = () => {
        document.body.classList.toggle("light-theme");
        const theme = document.body.classList.contains("light-theme") ? "light" : "dark";
        localStorage.setItem("theme", theme);
    };

    if (toggleLogin) toggleLogin.addEventListener("click", toggleTheme);
    if (toggleMain) toggleMain.addEventListener("click", toggleTheme);
}

// ================= TOAST SYSTEM =================
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerText = message;
    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add("active"), 10);

    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove("active");
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// Global JavaScript Error Handler
window.onerror = function(message, source, lineno, colno, error) {
    showToast(`JS Error: ${message} (line ${lineno})`, "error");
    console.error(error);
    return false;
};

// Global Fetch Interceptor to handle session expiration (401 Unauthorized)
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const response = await originalFetch(...args);
    if (response.status === 401 && state.token) {
        state.token = null;
        state.role = null;
        state.username = null;
        localStorage.clear();
        document.getElementById("main-screen").classList.remove("active");
        document.getElementById("login-screen").classList.add("active");
        showToast("Session expired. Please log in again.", "error");
    }
    return response;
};

// State Management
const state = {
    token: localStorage.getItem("token") || null,
    role: localStorage.getItem("role") || null,
    username: localStorage.getItem("username") || null,
    currentTab: "dashboard",
    batches: [],
    selectedBatchId: null
};

// API Base URL
const API_URL = "";

// Helper: Headers with Auth Token
function getHeaders(contentType = "application/json") {
    const headers = {};
    if (contentType) {
        headers["Content-Type"] = contentType;
    }
    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }
    return headers;
}

// ================= TAB NAVIGATION =================
function initNavigation() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update active nav link
    document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
    const activeLink = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    if (activeLink) activeLink.classList.add("active");

    // Auto-close mobile menu on selection
    const activeNavGroup = document.querySelector(".nav-group:not(.hidden)");
    if (activeNavGroup) {
        activeNavGroup.classList.remove("mobile-open");
    }
    // Update active mobile menu label
    if (activeLink) {
        const activeText = document.getElementById("mobile-nav-active-text");
        if (activeText) {
            activeText.innerHTML = activeLink.innerHTML;
        }
    }

    // Hide all tabs, show target tab
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) {
        targetTab.classList.add("active");
        state.currentTab = tabId;
        // Trigger reload of data for this tab
        loadTabData(tabId);
    }
}

function loadTabData(tabId) {
    if (tabId === "admin-dashboard") loadAdminDashboard();
    else if (tabId === "admin-centers") loadAdminCenters();
    else if (tabId === "admin-batches") loadAdminBatches();
    else if (tabId === "admin-teachers") loadAdminTeachers();
    else if (tabId === "admin-students") loadAdminStudents();
    else if (tabId === "teacher-dashboard") loadTeacherDashboard();
    else if (tabId === "teacher-upload") loadTeacherUploadOptions();
    else if (tabId === "student-dashboard") loadStudentDashboard();
    else if (tabId === "admin-leaves") loadAdminLeaves();
    else if (tabId === "teacher-leaves") loadTeacherLeaves();
}

// ================= AUTHENTICATION HANDLERS =================
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("login-username").value;
        const password = document.getElementById("login-password").value;

        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Authentication failed");
            }

            const data = await res.json();
            
            // Set State
            state.token = data.access_token;
            state.role = data.role;
            state.username = data.username;

            localStorage.setItem("token", data.access_token);
            localStorage.setItem("role", data.role);
            localStorage.setItem("username", data.username);

            showToast("Login successful!");
            setupScreenForRole();
        } catch (err) {
            showToast(err.message, "error");
        }
    });
}

document.getElementById("logout-btn").addEventListener("click", () => {
    state.token = null;
    state.role = null;
    state.username = null;
    localStorage.clear();
    
    // Switch to Login screen
    document.getElementById("main-screen").classList.remove("active");
    document.getElementById("login-screen").classList.add("active");
    showToast("Logged out successfully");
});

function setupScreenForRole() {
    if (!state.token) {
        document.getElementById("main-screen").classList.remove("active");
        document.getElementById("login-screen").classList.add("active");
        return;
    }

    // Hide Login, show App Screen
    document.getElementById("login-screen").classList.remove("active");
    document.getElementById("main-screen").classList.add("active");
    
    // Set user metadata display
    document.getElementById("user-display").innerText = `${state.username} (${state.role})`;

    // Toggle navigation panels
    document.getElementById("nav-admin").classList.add("hidden");
    document.getElementById("nav-teacher").classList.add("hidden");
    document.getElementById("nav-student").classList.add("hidden");

    const changePassBtn = document.getElementById("header-change-password-btn");
    if (changePassBtn) {
        if (state.role === "admin") {
            changePassBtn.classList.remove("hidden");
        } else {
            changePassBtn.classList.add("hidden");
        }
    }

    if (state.role === "admin") {
        document.getElementById("nav-admin").classList.remove("hidden");
        switchTab("admin-dashboard");
    } else if (state.role === "teacher") {
        document.getElementById("nav-teacher").classList.remove("hidden");
        switchTab("teacher-dashboard");
    } else if (state.role === "student") {
        document.getElementById("nav-student").classList.remove("hidden");
        switchTab("student-dashboard");
    }
}

// ================= MODAL HANDLERS =================
function openModal(id) {
    document.getElementById(id).classList.add("active");
}
function closeModal(id) {
    document.getElementById(id).classList.remove("active");
}

// ================= ADMIN LOGIC =================

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
        subEl.innerText = `SID ID: ${batch.sid_batch_id} | Total Course Hours: ${batch.total_hours} hrs`;
        
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

        const totalHrs = 330;
        const reqHrs = 247.5;
        
        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = formatHours(s.sessions_attended);
            const missedHrs = formatHours(s.sessions_missed);
            const neededHrs = formatHours(s.sessions_needed_for_75);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${attendedHrs} hrs</td>
                    <td>${missedHrs} hrs</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${neededHrs} hrs</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\'")}', '${s.phone || ''}')">✏️ Edit</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="8" class="text-center">No students registered in this batch.</td></tr>`;

        document.getElementById("btn-admin-batch-pdf").onclick = () => downloadReport('pdf', batchId);
        document.getElementById("btn-admin-batch-excel").onclick = () => downloadReport('excel', batchId);

    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadAdminDashboard() {
    try {
        const res = await fetch(`${API_URL}/reports/global`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load dashboard data");
        const data = await res.json();

        // Render Stats
        document.getElementById("admin-stat-students").innerText = data.global.total_students;
        document.getElementById("admin-stat-batches").innerText = data.global.total_batches;
        document.getElementById("admin-stat-centers").innerText = data.global.total_centers;
        document.getElementById("admin-stat-risk").innerText = data.global.at_risk_students_count;

        // Render Center Comparisons
        const cmpBody = document.getElementById("admin-center-comparison-body");
        cmpBody.innerHTML = data.centers.map(c => `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td><code class="brand-tag">${c.nsdc_code}</code></td>
                <td>${c.students_count} students</td>
                <td><strong style="color: ${c.average_attendance >= 75 ? 'var(--status-eligible)' : 'var(--status-at-risk)'}">${c.average_attendance}%</strong></td>
            </tr>
        `).join("") || `<tr><td colspan="4" class="text-center">No centers found</td></tr>`;

        // Render Teacher Rankings
        const rankBody = document.getElementById("admin-teacher-rankings-body");
        rankBody.innerHTML = data.teachers.map(t => `
            <tr>
                <td><strong>${t.username}</strong></td>
                <td>${t.batches_count} batches</td>
                <td>${t.students_count} students</td>
                <td><strong style="color: ${t.average_attendance >= 75 ? 'var(--status-eligible)' : 'var(--status-at-risk)'}">${t.average_attendance}%</strong></td>
            </tr>
        `).join("") || `<tr><td colspan="4" class="text-center">No teachers found</td></tr>`;

    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadAdminCenters() {
    try {
        const res = await fetch(`${API_URL}/centers/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load centers");
        const centers = await res.json();
        
        const body = document.getElementById("admin-centers-table-body");
        body.innerHTML = centers.map(c => `
            <tr>
                <td><strong>${c.name}</strong></td>
                
                <td>${c.district}</td>
                <td>${c.state}</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="deleteCenter(${c.id})">🗑️ Delete</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="4" class="text-center">No centers registered</td></tr>`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadAdminBatches() {
    try {
        const res = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load batches");
        const batches = await res.json();
        
        state.batches = batches;

        const body = document.getElementById("admin-batches-table-body");
        body.innerHTML = batches.map(b => {
            const status_badge = b.status === "active" ? `<span class="badge badge-success">Running</span>` : `<span class="badge badge-danger">Closed</span>`;
            const class_elig_badge = b.class_status === "ELIGIBLE" ? "badge-success" : (b.class_status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><strong>${b.course_name}</strong></td>
                    <td>${b.center_name}</td>
                    <td>${b.teacher_name || 'Unassigned'}</td>
                    <td>${b.total_hours} hours</td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status}</span></td>
                    <td>${status_badge}</td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="viewAdminBatchDetails(${b.id})">🔍 View</button>
                            <button class="btn btn-secondary btn-small" onclick="openEditBatchModal(${b.id})">✏️ Edit</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteBatch(${b.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="8" class="text-center">No batches created</td></tr>`;
        
        // Load options for forms
        loadDropdownOptions();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadDropdownOptions() {
    const centerSelect = document.getElementById("batch-center");
    const teacherSelect = document.getElementById("batch-teacher");
    const batchSelect = document.getElementById("stud-batch");

    try {
        const cRes = await fetch(`${API_URL}/centers/`, { headers: getHeaders() });
        const centers = await cRes.json();
        centerSelect.innerHTML = centers.map(c => `<option value="${c.id}">${c.name}</option>`).join("");

        // Simple user fetch to filter teachers
        const uRes = await fetch(`${API_URL}/reports/global`, { headers: getHeaders() });
        const globalData = await uRes.json();
        teacherSelect.innerHTML = globalData.teachers.map(t => `<option value="${t.id}">${t.username}</option>`).join("");

        const bRes = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        const batches = await bRes.json();
        batchSelect.innerHTML = batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || 'Center'})</option>`).join("");
    } catch(err) {
        console.error("Error loading dropdown options", err);
    }
}

async function loadAdminTeachers() {
    try {
        const usersRes = await fetch(`${API_URL}/reports/global`, { headers: getHeaders() });
        const data = await usersRes.json();
        
        state.teachers = data.teachers || [];

        const body = document.getElementById("admin-teachers-table-body");
        body.innerHTML = data.teachers.map(t => `
            <tr>
                <td class="delete-col-cell hidden" style="text-align: center;"><input type="checkbox" class="teacher-select-cb" data-id="${t.id}" data-username="${t.username}" onchange="updateDeleteSelectedCount()"></td>
                <td>
                    <strong>${t.username}</strong>
                    <br><small style="color:var(--text-muted)">🔑 ${t.plain_password || 'teacher123'}</small>
                </td>
                <td>${t.email || 'N/A'}</td>
                <td>${t.phone || 'N/A'}</td>
                <td>${t.subject || 'N/A'}</td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-secondary btn-small" onclick="openEditTeacherModal(${t.id})">✏️ Edit</button>
                        <button class="btn btn-secondary btn-small" onclick="openUploadCSVForTeacher(${t.id}, '${t.username}')">📤 Upload CSV</button>
                        <button class="btn btn-primary btn-small" onclick="openResetPasswordModal(${t.id}, '${t.username}', false)">🔑 Password</button>
                    </div>
                </td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No teachers registered</td></tr>`;

        exitTeacherDeleteMode();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadAdminStudents() {
    try {
        const res = await fetch(`${API_URL}/students/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load student directory");
        const students = await res.json();
        
        const body = document.getElementById("admin-students-table-body");
        if (!body) return;
        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${s.phone || 'N/A'}</td>
                    <td>${s.batch_name}</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="7" class="text-center">No students registered yet</td></tr>`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadAdminLogs() {
    try {
        const res = await fetch(`${API_URL}/reports/global`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load audit logs");
        const data = await res.json();

        const body = document.getElementById("admin-logs-table-body");
        body.innerHTML = data.audit_logs.map(l => `
            <tr>
                <td><code style="color:var(--text-muted)">${l.timestamp}</code></td>
                <td><strong>${l.username}</strong></td>
                <td><span class="brand-tag">${l.action}</span></td>
                <td><code>${l.table_name || 'N/A'}</code></td>
                <td>${l.record_id || 'N/A'}</td>
            </tr>
        `).join("") || `<tr><td colspan="5" class="text-center">No system logs</td></tr>`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Modal Form Submissions
document.getElementById("center-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById("center-name").value,
        district: document.getElementById("center-district").value,
        state: document.getElementById("center-state").value
    };
    try {
        const res = await fetch(`${API_URL}/centers/`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Failed to register center");
        showToast("Training Center created successfully");
        closeModal("center-modal");
        loadAdminCenters();
    } catch (err) {
        showToast(err.message, "error");
    }
});

document.getElementById("batch-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const hours = parseInt(document.getElementById("batch-hours").value || 330);
    const dailyDuration = parseFloat(document.getElementById("batch-duration").value || 8.25);
    const data = {
        center_id: parseInt(document.getElementById("batch-center").value),
        teacher_id: parseInt(document.getElementById("batch-teacher").value),
        course_name: document.getElementById("batch-course").value,
        start_date: document.getElementById("batch-start").value,
        total_sessions: Math.round(hours / dailyDuration),
        total_hours: hours,
        daily_duration: dailyDuration
    };
    try {
        const res = await fetch(`${API_URL}/batches/`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Failed to create batch");
        showToast("Batch created successfully");
        closeModal("batch-modal");
        loadAdminBatches();
    } catch (err) {
        showToast(err.message, "error");
    }
});

document.getElementById("teacher-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById("teach-username").value,
        email: document.getElementById("teach-email").value,
        phone: document.getElementById("teach-phone").value,
        subject: document.getElementById("teach-subject").value,
        password: document.getElementById("teach-password").value,
        role: "teacher"
    };
    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Failed to register teacher account");
        showToast("Teacher registered successfully");
        closeModal("teacher-modal");
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
});

document.getElementById("student-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        batch_id: parseInt(document.getElementById("stud-batch").value),
        name: document.getElementById("stud-name").value,
        sid_student_id: document.getElementById("stud-sid").value,
        phone: document.getElementById("stud-phone").value,
        aadhaar_hash: document.getElementById("stud-aadhaar").value
    };
    try {
        const res = await fetch(`${API_URL}/students/`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Failed to register student");
        showToast("Student registered successfully");
        closeModal("student-modal");
        loadAdminStudents();
    } catch (err) {
        showToast(err.message, "error");
    }
});

// Delete wrappers
async function deleteCenter(id) {
    if (!confirm("Are you sure you want to delete this center?")) return;
    try {
        const res = await fetch(`${API_URL}/centers/${id}`, { method: "DELETE", headers: getHeaders() });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        showToast("Center deleted");
        loadAdminCenters();
    } catch(err) { showToast(err.message, "error"); }
}
async function deleteBatch(id) {
    if (!confirm("Are you sure? This deletes students and records under this batch.")) return;
    try {
        const res = await fetch(`${API_URL}/batches/${id}`, { method: "DELETE", headers: getHeaders() });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        showToast("Batch deleted");
        loadAdminBatches();
    } catch(err) { showToast(err.message, "error"); }
}
async function deleteStudent(id) {
    if (!confirm("Delete student?")) return;
    try {
        const res = await fetch(`${API_URL}/students/${id}`, { method: "DELETE", headers: getHeaders() });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        showToast("Student deleted");
        loadAdminStudents();
    } catch(err) { showToast(err.message, "error"); }
}

// ================= TEACHER PORTAL LOGIC =================
async function loadTeacherDashboard() {
    try {
        // Load batches
        const bRes = await fetch(`${API_URL}/batches/`, { headers: getHeaders() });
        const batches = await bRes.json();
        state.batches = batches;
        
        document.getElementById("teacher-stat-batches").innerText = batches.length;
        
        let totalStudents = 0;
        batches.forEach(b => totalStudents += b.students_count);
        document.getElementById("teacher-stat-students").innerText = totalStudents;

        // Load at-risk students
        const rRes = await fetch(`${API_URL}/students/?at_risk=true`, { headers: getHeaders() });
        const riskStudents = await rRes.json();
        document.getElementById("teacher-stat-risk").innerText = riskStudents.length;

        // Render My Batches
        const bBody = document.getElementById("teacher-batches-list-body");
        bBody.innerHTML = batches.map(b => {
            const class_elig_badge = b.class_status === "ELIGIBLE" ? "badge-success" : (b.class_status === "AT_RISK" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><strong>${b.course_name}</strong></td>
                    <td><code>${b.sid_batch_id}</code></td>
                    <td>${b.students_count}</td>
                    <td><span class="badge ${class_elig_badge}">${b.class_status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-small" onclick="viewTeacherBatchDetails(${b.id})">🔍 View</button>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="5" class="text-center">No batches assigned to you</td></tr>`;

        // Render At Risk Students
        const rBody = document.getElementById("teacher-risk-students-body");
        rBody.innerHTML = riskStudents.map(s => `
            <tr>
                <td><strong>${s.name}</strong></td>
                <td>Batch #${s.batch_id}</td>
                <td><strong class="text-danger">${s.attendance_pct}%</strong></td>
                <td><span class="badge badge-danger">${s.status}</span></td>
            </tr>
        `).join("") || `<tr><td colspan="4" class="text-center" style="color: var(--status-eligible)">🎉 Hurray! No students are at risk.</td></tr>`;

    } catch (err) {
        showToast(err.message, "error");
    }
}

async function viewTeacherBatchDetails(batchId) {
    state.selectedBatchId = batchId;
    switchTab("teacher-batches");

    try {
        const res = await fetch(`${API_URL}/batches/${batchId}`, { headers: getHeaders() });
        const batch = await res.json();

        // Update details card
        document.getElementById("batch-detail-title").innerText = batch.course_name;
        document.getElementById("batch-detail-sub").innerText = `SID ID: ${batch.sid_batch_id} | Total Course Hours: ${batch.total_hours} hrs`;
        
        document.getElementById("det-course").innerText = batch.course_name;
        document.getElementById("det-sid").innerText = batch.sid_batch_id;
        document.getElementById("det-center").innerText = batch.center_name;
        
        const elSpan = document.getElementById("det-eligibility");
        elSpan.innerText = batch.class_status;
        elSpan.className = "val " + (batch.class_status === "ELIGIBLE" ? "text-success" : (batch.class_status === "AT_RISK" ? "text-warning" : "text-danger"));

        document.getElementById("batch-detail-summary-card").classList.remove("hidden");
        document.getElementById("batch-detail-actions").classList.remove("hidden");

        // Load students in batch
        const sRes = await fetch(`${API_URL}/students/?batch_id=${batchId}`, { headers: getHeaders() });
        const students = await sRes.json();

        const body = document.getElementById("teacher-batch-students-body");
        const totalHrs = 330;
        const reqHrs = 247.5;
        
        body.innerHTML = students.map(s => {
            const status_badge = s.status === "ELIGIBLE" ? "badge-success" : (s.status === "AT_RISK" ? "badge-warning" : "badge-danger");
            const attendedHrs = formatHours(s.sessions_attended);
            const missedHrs = formatHours(s.sessions_missed);
            const neededHrs = formatHours(s.sessions_needed_for_75);

            return `
                <tr>
                    <td><code>${s.sid_student_id}</code></td>
                    <td>
                        <strong>${s.name}</strong>
                        <br><small style="color:var(--text-muted)">🔑 ${s.plain_password || 'student123'}</small>
                    </td>
                    <td>${attendedHrs} hrs</td>
                    <td>${missedHrs} hrs</td>
                    <td><strong>${s.attendance_pct}%</strong></td>
                    <td>${neededHrs} hrs</td>
                    <td><span class="badge ${status_badge}">${s.status}</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-primary btn-small" onclick="openEditStudent(${s.id}, '${s.name.replace("'", "\'")}', '${s.phone || ''}')">✏️ Edit</button>
                            <button class="btn btn-destructive btn-small" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="8" class="text-center">No students registered in this batch.</td></tr>`;

        // Configure Report Downloads Links
        document.getElementById("btn-batch-pdf").onclick = () => downloadReport('pdf', batchId);
        document.getElementById("btn-batch-excel").onclick = () => downloadReport('excel', batchId);

    } catch (err) {
        showToast(err.message, "error");
    }
}

function downloadReport(format, batchId) {
    // Direct link trigger
    const url = `${API_URL}/reports/batch/${batchId}/${format}`;
    const a = document.createElement("a");
    a.href = url;
    // Set Authorization header in cookie or fetch blob
    // For simplicity with fast API download, fetch as blob
    showToast("Generating report...", "info");
    fetch(url, { headers: getHeaders() })
        .then(res => {
            if (!res.ok) throw new Error("Could not download file");
            return res.blob();
        })
        .then(blob => {
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = `Batch_${batchId}_Report.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            showToast("Report downloaded successfully");
        })
        .catch(err => showToast(err.message, "error"));
}

function loadTeacherUploadOptions() {
    // Load instructor's assigned batches into dropdown selection
    const select = document.getElementById("upload-batch-select");
    select.innerHTML = `<option value="">-- Choose Batch --</option>` + 
        state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || 'Center'})</option>`).join("");

    const undoSelect = document.getElementById("undo-batch-select");
    if (undoSelect) {
        undoSelect.innerHTML = `<option value="">-- Choose Batch --</option>` + 
            state.batches.map(b => `<option value="${b.id}">${b.course_name} (${b.center_name || 'Center'})</option>`).join("");
    }
    
    // Initialize the calendar visualizer placeholder message
    loadSyncAttendanceCalendar();
}

// Drag & Drop Setup
const dropZone = document.getElementById("csv-drop-zone");
const fileInput = document.getElementById("csv-file-input");
const fileDisplay = document.getElementById("file-name-display");
const selectedFileName = document.getElementById("selected-file-name");

if (dropZone) {
    dropZone.addEventListener("click", () => fileInput.click());
    
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileName();
        }
    });

    fileInput.addEventListener("change", () => updateFileName());
}

function updateFileName() {
    if (fileInput.files.length) {
        selectedFileName.innerText = fileInput.files[0].name;
        fileDisplay.classList.remove("hidden");
    } else {
        fileDisplay.classList.add("hidden");
    }
}

const uploadForm = document.getElementById("upload-csv-form");
if (uploadForm) {
    // Mode toggles
    const syncModeRadios = document.getElementsByName("sync-mode");
    const singleGroup = document.getElementById("date-single-group");
    const rangeGroup = document.getElementById("date-range-group");
    const singleInput = document.getElementById("upload-date-input");
    const startInput = document.getElementById("upload-start-date");
    const endInput = document.getElementById("upload-end-date");

    if (syncModeRadios.length) {
        syncModeRadios.forEach(radio => {
            radio.addEventListener("change", (e) => {
                if (e.target.value === "one-day") {
                    singleGroup.classList.remove("hidden");
                    rangeGroup.classList.add("hidden");
                    singleInput.required = true;
                    startInput.required = false;
                    endInput.required = false;
                } else {
                    singleGroup.classList.add("hidden");
                    rangeGroup.classList.remove("hidden");
                    singleInput.required = false;
                    startInput.required = true;
                    endInput.required = true;
                }
                renderSyncCalendar();
            });
        });
    }

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const batchId = document.getElementById("upload-batch-select").value;
        const file = fileInput.files[0];
        const mode = document.querySelector('input[name="sync-mode"]:checked').value;

        if (!batchId || !file) {
            showToast("Please select a batch and upload a file", "error");
            return;
        }

        const formData = new FormData();
        formData.append("batch_id", batchId);
        formData.append("file", file);

        let endpointUrl = `${API_URL}/sync/upload`;

        if (mode === "one-day") {
            const dateVal = singleInput.value;
            if (!dateVal) {
                showToast("Please select an attendance date", "error");
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
            
            formData.append("date", dateVal);
        } else {
            const startVal = startInput.value;
            const endVal = endInput.value;
            if (!startVal || !endVal) {
                showToast("Please select both start and end dates", "error");
                return;
            }

            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            const today = new Date();
            startDate.setHours(0, 0, 0, 0);
            endDate.setHours(0, 0, 0, 0);
            today.setHours(0, 0, 0, 0);

            if (startDate > endDate) {
                showToast("Error: Start date must be before or equal to end date.", "error");
                return;
            }
            if (endDate > today) {
                showToast("Error: You cannot upload attendance for a future date.", "error");
                return;
            }

            formData.append("start_date", startVal);
            formData.append("end_date", endVal);
            endpointUrl = `${API_URL}/sync/upload-range`;
        }

        try {
            showToast("Parsing CSV and syncing database... Please wait.", "info");
            const res = await fetch(endpointUrl, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${state.token}`
                },
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Sync failed");
            }
            
            const data = await res.json();
            showToast(data.message || `Sync complete! Processed ${data.records_synced} records.`);
            switchTab("teacher-dashboard");
        } catch (err) {
            showToast(err.message, "error");
        }
    });
}

// ================= STUDENT LOGIC =================
async function loadStudentDashboard() {
    try {
        const res = await fetch(`${API_URL}/students/my-profile`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load student profile");
        const data = await res.json();

        // Update stats
        document.getElementById("student-ring-pct").innerText = `${data.attendance_pct}%`;
        const ring = document.querySelector(".progress-ring-container");
        if (ring) {
            ring.style.background = `radial-gradient(circle, #100d23 60%, transparent 61%), conic-gradient(var(--primary-color) ${data.attendance_pct}%, #171337 ${data.attendance_pct}%)`;
        }

        const statusBadge = document.getElementById("student-status-badge");
        statusBadge.innerText = data.status;
        statusBadge.className = "badge " + (data.status === "ELIGIBLE" ? "badge-success" : (data.status === "AT_RISK" ? "badge-warning" : "badge-danger"));

        // Calculate hours based on total hours from backend
        const totalHrs = data.total_hours || 330;
        
        const attendedHrs = formatHours(data.sessions_attended);
        const missedHrs = formatHours(data.sessions_missed);
        const neededHrs = formatHours(data.sessions_needed_for_75);

        document.getElementById("student-stat-attended").innerText = `${attendedHrs} / ${formatHours(totalHrs)} hrs`;
        document.getElementById("student-stat-missed").innerText = `${missedHrs} hrs`;
        document.getElementById("student-stat-remaining").innerText = `${neededHrs} hrs`;

        // Render Action message
        const msgBox = document.getElementById("student-action-msg");
        if (data.status === "ELIGIBLE") {
            msgBox.innerHTML = `<span style="color:var(--status-eligible)">🎉 You are eligible for assessments! Keep attending to maintain it.</span>`;
        } else if (data.status === "AT_RISK") {
            msgBox.innerHTML = `<span style="color:var(--status-at-risk)">⚠️ You need to attend <strong>${data.sessions_needed_for_75}</strong> more sessions (<strong>${neededHrs} hrs</strong>) to reach 75% attendance.</span>`;
        } else {
            msgBox.innerHTML = `<span style="color:var(--status-impossible)">🚨 It is mathematically impossible to reach 75% attendance. Please contact coordinator immediately.</span>`;
        }

        // Save attendance logs to state & render monthly calendar
        studentAttendanceLogs = data.calendar_logs;
        renderStudentCalendar();

    } catch (err) {
        showToast(err.message, "error");
    }
}

window.addEventListener("DOMContentLoaded", () => {

    // Reset Password Form Handler
    const resetPasswordForm = document.getElementById("reset-password-form");
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const targetIdVal = document.getElementById("reset-password-target-id").value;
            const newPassword = document.getElementById("reset-new-password").value;
            const confirmPassword = document.getElementById("reset-confirm-password").value;

            if (newPassword !== confirmPassword) {
                showToast("Error: Passwords do not match! Please double check.", "error");
                return;
            }

            try {
                showToast("Updating password...", "info");
                const res = await fetch(`${API_URL}/auth/change-password`, {
                    method: "POST",
                    headers: getHeaders(),
                    body: JSON.stringify({
                        user_id: targetIdVal ? parseInt(targetIdVal) : null,
                        new_password: newPassword
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Reset failed");
                }

                showToast("Password updated successfully");
                closeModal("reset-password-modal");
                resetPasswordForm.reset();
                if (state.currentTab) {
                    loadTabData(state.currentTab);
                }
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }


    // Request Leave Form Submit Handler
    const requestLeaveForm = document.getElementById("request-leave-form");
    if (requestLeaveForm) {
        requestLeaveForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const dateVal = document.getElementById("leave-date-input").value;
            const reasonVal = document.getElementById("leave-reason-input").value.trim();
            
            try {
                showToast("Submitting request...", "info");
                const res = await fetch(`${API_URL}/leaves/request`, {
                    method: "POST",
                    headers: getHeaders(),
                    body: JSON.stringify({
                        leave_date: dateVal,
                        reason: reasonVal
                      })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Request failed");
                }

                showToast("Leave request submitted successfully");
                closeModal("request-leave-modal");
                requestLeaveForm.reset();
                loadTeacherLeaves();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }


    // Edit Student Form Handler
    const editStudentForm = document.getElementById("edit-student-form");
    if (editStudentForm) {
        editStudentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const studentId = document.getElementById("edit-student-id").value;
            const data = {
                name: document.getElementById("edit-student-name").value,
                password: document.getElementById("edit-student-password") ? document.getElementById("edit-student-password").value : ""
            };

            try {
                showToast("Updating student details...", "info");
                const res = await fetch(`${API_URL}/students/${studentId}`, {
                    method: "PUT",
                    headers: getHeaders(),
                    body: JSON.stringify(data)
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Update failed");
                }

                showToast("Student details updated successfully");
                closeModal("edit-student-modal");
                
                // Refresh list if batch is currently selected
                const activeBatchId = document.getElementById("admin-student-upload-batch-id") ? document.getElementById("admin-student-upload-batch-id").value : null;
                if (activeBatchId) {
                    viewAdminBatchDetails(activeBatchId);
                }
                loadAdminStudents();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }


    // Teacher Student List CSV Upload Form Handler
    const teacherStudentUploadForm = document.getElementById("teacher-student-upload-form");
    if (teacherStudentUploadForm) {
        teacherStudentUploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const teacherId = document.getElementById("teacher-upload-teacher-id").value;
            const fileInput = document.getElementById("teacher-student-file-input");

            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please choose a CSV file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("teacher_id", teacherId);
            formData.append("file", fileInput.files[0]);

            try {
                showToast("Uploading and syncing students for teacher...", "info");
                const res = await fetch(`${API_URL}/sync/teacher-admin-upload`, {
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
                
                teacherStudentUploadForm.reset();
                closeModal("teacher-student-upload-modal");
                loadAdminStudents();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }


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




    // Set default date input value to today for sync screen
    const uploadDateInput = document.getElementById("upload-date-input");
    if (uploadDateInput) {
        uploadDateInput.value = new Date().toISOString().split('T')[0];
        
        // Re-render when date input is manually changed
        uploadDateInput.addEventListener("input", () => {
            renderSyncCalendar();
        });
    }



    // Trigger calendar load when batch selection changes on sync screen
    const uploadBatchSelect = document.getElementById("upload-batch-select");
    if (uploadBatchSelect) {
        uploadBatchSelect.addEventListener("change", () => {
            loadSyncAttendanceCalendar();
        });
    }


    // Add Student for Teacher Form Handler
    const addStudentTeacherForm = document.getElementById("teacher-add-student-form");
    if (addStudentTeacherForm) {
        addStudentTeacherForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const teacherId = document.getElementById("add-student-teacher-id").value;
            const batchId = document.getElementById("add-student-batch").value;
            const sidStudentId = document.getElementById("add-student-sid").value.trim();
            const name = document.getElementById("add-student-name").value.trim();

            if (!batchId) {
                showToast("Please select a target batch", "error");
                return;
            }

            try {
                showToast("Adding student profile & creating account...", "info");
                const res = await fetch(`${API_URL}/students/add-manual`, {
                    method: "POST",
                    headers: getHeaders(),
                    body: JSON.stringify({
                        batch_id: parseInt(batchId),
                        sid_student_id: sidStudentId,
                        name: name
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Failed to add student");
                }

                const data = await res.json();
                showToast(data.message);
                closeModal("teacher-add-student-modal");
                
                if (state.currentTab === "admin-teachers") {
                    loadAdminTeachers();
                }
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }


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

    initTheme();
    initNavigation();
    setupScreenForRole();
});

// Helper to open Add Student for Teacher modal


// Standard monthly calendar states for both portals
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

    const batchSelect = document.getElementById("upload-batch-select");
    const batchId = batchSelect ? batchSelect.value : "";
    if (!batchId) {
        grid.innerHTML = `<div class="text-center" style="grid-column: span 7; padding: 30px 0; color: var(--text-muted);">Please select a batch to view attendance visualizer</div>`;
        return;
    }

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

        const dayOfWeek = new Date(syncCalYear, syncCalMonth, day).getDay();
        const isSunday = dayOfWeek === 0;
        const isGazettedHoliday = GAZETTED_HOLIDAYS_2026.includes(dateStr);
        
        if (isSunday || isGazettedHoliday) {
            cell.classList.add("holiday");
            cell.title = isSunday ? "Sunday Holiday" : "Gazetted Holiday";
        }

        if (syncUploadedDates.includes(dateStr)) {
            cell.classList.add("uploaded");
        }

        const startInput = document.getElementById("upload-start-date");
        const endInput = document.getElementById("upload-end-date");
        const modeRadio = document.querySelector('input[name="sync-mode"]:checked');
        const mode = modeRadio ? modeRadio.value : "one-day";

        if (mode === "one-day") {
            if (dateStr === selectedDateStr) {
                cell.classList.add("selected-date");
            }
        } else {
            const startVal = startInput ? startInput.value : "";
            const endVal = endInput ? endInput.value : "";
            if (startVal && dateStr === startVal) {
                cell.classList.add("range-start");
            }
            if (endVal && dateStr === endVal) {
                cell.classList.add("range-end");
            }
            if (startVal && endVal && dateStr > startVal && dateStr < endVal) {
                cell.classList.add("range-mid");
            }
        }

        cell.addEventListener("click", () => {
            const currentModeRadio = document.querySelector('input[name="sync-mode"]:checked');
            const currentMode = currentModeRadio ? currentModeRadio.value : "one-day";

            if (currentMode === "one-day") {
                if (dateInput) {
                    dateInput.value = dateStr;
                    renderSyncCalendar();
                }
            } else {
                if (startInput && endInput) {
                    const startVal = startInput.value;
                    const endVal = endInput.value;

                    if (!startVal || (startVal && endVal)) {
                        startInput.value = dateStr;
                        endInput.value = "";
                    } else {
                        if (dateStr >= startVal) {
                            endInput.value = dateStr;
                        } else {
                            startInput.value = dateStr;
                            endInput.value = "";
                        }
                    }
                    renderSyncCalendar();
                }
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

        const dayOfWeek = new Date(studentCalYear, studentCalMonth, day).getDay();
        const isSunday = dayOfWeek === 0;
        const isGazettedHoliday = GAZETTED_HOLIDAYS_2026.includes(dateStr);
        
        if (isSunday || isGazettedHoliday) {
            cell.classList.add("holiday");
            cell.title = isSunday ? "Sunday Holiday" : "Gazetted Holiday";
        }

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
}

// Helper to open Teacher Student CSV upload modal
function openUploadCSVForTeacher(teacherId, teacherName) {
    document.getElementById("teacher-upload-teacher-id").value = teacherId;
    document.getElementById("teacher-upload-modal-title").innerText = `Upload Students for ${teacherName}`;
    openModal("teacher-student-upload-modal");
}

// Helper to open Edit Student modal
function openEditStudent(studentId, name, phone) {
    // Inject edit modal dynamically if it doesn't exist in DOM (safeguard against caching)
    if (!document.getElementById("edit-student-modal")) {
        const modalDiv = document.createElement("div");
        modalDiv.id = "edit-student-modal";
        modalDiv.className = "modal";
        modalDiv.innerHTML = `
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>Edit Student Details</h2>
                    <span class="close-btn" onclick="closeModal('edit-student-modal')">&times;</span>
                </div>
                <form id="edit-student-form">
                    <input type="hidden" id="edit-student-id">
                    <div class="form-group">
                        <label for="edit-student-name">Full Name</label>
                        <input type="text" id="edit-student-name" placeholder="e.g. Aarti Baghel" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-student-password">Reset Password</label>
                        <input type="password" id="edit-student-password" placeholder="Enter new password (optional)">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Save Changes</button>
                </form>
            </div>
        `;
        document.body.appendChild(modalDiv);

        // Wire up the submit listener for the dynamically generated form
        const form = document.getElementById("edit-student-form");
        if (form) {
            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                const studentId = document.getElementById("edit-student-id").value;
                const data = {
                    name: document.getElementById("edit-student-name").value,
                    password: document.getElementById("edit-student-password").value
                };

                try {
                    showToast("Updating student details...", "info");
                    const res = await fetch(`${API_URL}/students/${studentId}`, {
                        method: "PUT",
                        headers: getHeaders(),
                        body: JSON.stringify(data)
                    });

                    if (!res.ok) {
                        const err = await res.json();
                        throw new Error(err.detail || "Update failed");
                    }

                    showToast("Student details updated successfully");
                    closeModal("edit-student-modal");
                    
                    // Refresh current view depending on role
                    const activeBatchId = document.getElementById("admin-student-upload-batch-id") ? document.getElementById("admin-student-upload-batch-id").value : null;
                    if (activeBatchId) {
                        viewAdminBatchDetails(activeBatchId);
                    }
                    if (state.selectedBatchId) {
                        viewTeacherBatchDetails(state.selectedBatchId);
                    }
                    loadAdminStudents();
                } catch (err) {
                    showToast(err.message, "error");
                }
            });
        }
    }

    document.getElementById("edit-student-id").value = studentId;
    document.getElementById("edit-student-name").value = name;
    if (document.getElementById("edit-student-password")) {
        document.getElementById("edit-student-password").value = "";
    }
    openModal("edit-student-modal");
}

// Helper to open Delete Student dropdown modal for Teacher


// Helper to delete all students from a teacher
async function deleteTeacherStudents(teacherId, teacherName) {
    if (!confirm(`WARNING: Are you sure you want to delete all students assigned to teacher "${teacherName}"? This will also remove their student login accounts and attendance records!`)) {
        return;
    }
    
    try {
        showToast("Deleting students...", "info");
        const res = await fetch(`${API_URL}/sync/teacher-delete-students/${teacherId}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Delete failed");
        }
        
        const data = await res.json();
        showToast(data.message);
        loadAdminStudents();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Helper to toggle password visibility
function togglePasswordVisibility(inputId, toggleEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === "password") {
        input.type = "text";
        toggleEl.innerText = "HIDE";
    } else {
        input.type = "password";
        toggleEl.innerText = "SHOW";
    }
}

// Load leaves list for admin approvals tab
async function loadAdminLeaves() {
    try {
        const res = await fetch(`${API_URL}/leaves/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load leaves");
        const leaves = await res.json();
        
        const body = document.getElementById("admin-leaves-table-body");
        if (!body) return;
        
        body.innerHTML = leaves.map(l => {
            let actionsHtml = "";
            if (l.status === "pending") {
                actionsHtml = `
                    <div class="actions-cell">
                        <button class="btn btn-success btn-small" onclick="handleLeaveApproval(${l.id}, 'approve')">✅ Approve</button>
                        <button class="btn btn-destructive btn-small" onclick="handleLeaveApproval(${l.id}, 'decline')">❌ Decline</button>
                    </div>
                `;
            } else {
                actionsHtml = `<span style="color:var(--text-muted)">Closed</span>`;
            }
            const statusBadge = l.status === "approved" ? "badge-success" : (l.status === "pending" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><strong>${l.teacher_name}</strong></td>
                    <td><code>${l.leave_date}</code></td>
                    <td>${l.reason}</td>
                    <td><span class="badge ${statusBadge}">${l.status.toUpperCase()}</span></td>
                    <td>${actionsHtml}</td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="6" class="text-center">No leave requests submitted yet.</td></tr>`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Approve or Decline leaves action handler
async function handleLeaveApproval(id, action) {
    try {
        showToast("Processing request...", "info");
        const res = await fetch(`${API_URL}/leaves/${id}/${action}`, {
            method: "POST",
            headers: getHeaders()
        });
        if (!res.ok) throw new Error("Failed to process leave status");
        showToast(`Request ${action}d successfully`);
        loadAdminLeaves();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Load leaves log for teachers tab
async function loadTeacherLeaves() {
    try {
        const res = await fetch(`${API_URL}/leaves/`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to load leaves");
        const leaves = await res.json();
        
        const body = document.getElementById("teacher-leaves-table-body");
        if (!body) return;
        
        body.innerHTML = leaves.map(l => {
            const statusBadge = l.status === "approved" ? "badge-success" : (l.status === "pending" ? "badge-warning" : "badge-danger");
            return `
                <tr>
                    <td><code>${l.leave_date}</code></td>
                    <td>${l.reason}</td>
                    <td><span class="badge ${statusBadge}">${l.status.toUpperCase()}</span></td>
                    <td>${l.created_at}</td>
                </tr>
            `;
        }).join("") || `<tr><td colspan="4" class="text-center">No leave requests submitted yet.</td></tr>`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Helper to open Reset Password modal
function openResetPasswordModal(userId, username, isSelf = false) {
    const titleEl = document.getElementById("reset-password-title");
    const targetIdInput = document.getElementById("reset-password-target-id");
    
    document.getElementById("reset-new-password").value = "";
    document.getElementById("reset-confirm-password").value = "";
    
    if (isSelf) {
        titleEl.innerText = "🔑 Change My Password";
        targetIdInput.value = "";
    } else {
        titleEl.innerText = `🔑 Reset Password for ${username}`;
        targetIdInput.value = userId;
    }
    
    openModal("reset-password-modal");
}

// Teacher Delete Mode state controller
let teacherDeleteModeActive = false;

function enterTeacherDeleteMode() {
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    const cancelBtn = document.getElementById("btn-cancel-delete-teachers");
    if (!modeBtn || !cancelBtn) return;
    
    if (!teacherDeleteModeActive) {
        // Activate Delete Mode: show column and checkboxes
        teacherDeleteModeActive = true;
        modeBtn.innerText = "🗑️ Confirm Delete (0)";
        cancelBtn.classList.remove("hidden");
        
        document.querySelectorAll(".delete-col-header").forEach(el => el.classList.remove("hidden"));
        document.querySelectorAll(".delete-col-cell").forEach(el => el.classList.remove("hidden"));
    } else {
        // Execute bulk deletion of selected items
        deleteSelectedTeachers();
    }
}

function exitTeacherDeleteMode() {
    teacherDeleteModeActive = false;
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    const cancelBtn = document.getElementById("btn-cancel-delete-teachers");
    if (modeBtn) modeBtn.innerText = "🗑️ Delete Teacher";
    if (cancelBtn) cancelBtn.classList.add("hidden");
    
    // Reset check box values
    document.querySelectorAll(".teacher-select-cb").forEach(cb => cb.checked = false);
    
    // Hide column elements
    document.querySelectorAll(".delete-col-header").forEach(el => el.classList.add("hidden"));
    document.querySelectorAll(".delete-col-cell").forEach(el => el.classList.add("hidden"));
}

function updateDeleteSelectedCount() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    const modeBtn = document.getElementById("btn-delete-teachers-mode");
    if (modeBtn && teacherDeleteModeActive) {
        modeBtn.innerText = `🗑️ Confirm Delete (${checkedCbs.length})`;
    }
}

// Bulk delete selected teachers cascadingly
async function deleteSelectedTeachers() {
    const checkedCbs = document.querySelectorAll(".teacher-select-cb:checked");
    if (checkedCbs.length === 0) {
        showToast("No teachers selected to delete", "error");
        return;
    }
    
    const teacherIds = Array.from(checkedCbs).map(cb => parseInt(cb.getAttribute("data-id")));
    const teacherNames = Array.from(checkedCbs).map(cb => cb.getAttribute("data-username"));
    
    if (!confirm(`CRITICAL WARNING: Are you sure you want to delete the selected ${teacherIds.length} teacher(s) (${teacherNames.join(", ")})? This will permanently delete their login accounts, all their assigned batches, all student profiles in those batches, and all their attendance history! This action CANNOT be undone.`)) {
        return;
    }
    
    try {
        showToast("Deleting selected teachers and all associated data...", "info");
        
        for (const tId of teacherIds) {
            const res = await fetch(`${API_URL}/auth/teachers/${tId}`, {
                method: "DELETE",
                headers: getHeaders()
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Delete failed");
            }
        }
        
        showToast("Successfully deleted selected teachers and their cascading data.");
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function toggleMobileNav() {
    const activeNavGroup = document.querySelector(".nav-group:not(.hidden)");
    if (activeNavGroup) {
        activeNavGroup.classList.toggle("mobile-open");
    }
}
window.toggleMobileNav = toggleMobileNav;

// ----------------- Edit Batch Logic -----------------
async function openEditBatchModal(batchId) {
    const batch = state.batches.find(b => b.id === batchId);
    if (!batch) {
        showToast("Batch data not found", "error");
        return;
    }
    
    document.getElementById("edit-batch-id").value = batch.id;
    document.getElementById("edit-batch-course").value = batch.course_name;
    document.getElementById("edit-batch-start").value = batch.start_date;
    document.getElementById("edit-batch-end").value = batch.end_date || "";
    document.getElementById("edit-batch-hours").value = batch.total_hours;
    document.getElementById("edit-batch-duration").value = batch.daily_duration;
    document.getElementById("edit-batch-status").value = batch.status || "active";
    
    const centerSelect = document.getElementById("edit-batch-center");
    const teacherSelect = document.getElementById("edit-batch-teacher");
    
    try {
        const [cRes, uRes] = await Promise.all([
            fetch(`${API_URL}/centers/`, { headers: getHeaders() }),
            fetch(`${API_URL}/reports/global`, { headers: getHeaders() })
        ]);
        const centers = await cRes.json();
        const globalData = await uRes.json();
        
        centerSelect.innerHTML = centers.map(c => `<option value="${c.id}" ${c.id === batch.center_id ? 'selected' : ''}>${c.name}</option>`).join("");
        teacherSelect.innerHTML = globalData.teachers.map(t => `<option value="${t.id}" ${t.id === batch.teacher_id ? 'selected' : ''}>${t.username}</option>`).join("");
        
        openModal("edit-batch-modal");
    } catch (err) {
        showToast("Failed to load options: " + err.message, "error");
    }
}
window.openEditBatchModal = openEditBatchModal;

document.getElementById("edit-batch-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const batchId = document.getElementById("edit-batch-id").value;
    
    const payload = {
        center_id: parseInt(document.getElementById("edit-batch-center").value),
        teacher_id: parseInt(document.getElementById("edit-batch-teacher").value),
        course_name: document.getElementById("edit-batch-course").value,
        start_date: document.getElementById("edit-batch-start").value,
        end_date: document.getElementById("edit-batch-end").value || null,
        total_sessions: 40,
        total_hours: parseInt(document.getElementById("edit-batch-hours").value),
        daily_duration: parseFloat(document.getElementById("edit-batch-duration").value),
        status: document.getElementById("edit-batch-status").value,
        sid_batch_id: ""
    };
    
    payload.total_sessions = Math.ceil(payload.total_hours / payload.daily_duration);
    
    try {
        const res = await fetch(`${API_URL}/batches/${batchId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to update batch");
        }
        showToast("Batch details updated successfully!");
        closeModal("edit-batch-modal");
        loadAdminBatches();
    } catch (err) {
        showToast(err.message, "error");
    }
});

// ----------------- Edit Teacher Logic -----------------
function openEditTeacherModal(teacherId) {
    const teacher = state.teachers.find(t => t.id === teacherId);
    if (!teacher) {
        showToast("Teacher data not found", "error");
        return;
    }
    
    document.getElementById("edit-teacher-id").value = teacher.id;
    document.getElementById("edit-teach-username").value = teacher.username;
    document.getElementById("edit-teach-email").value = teacher.email || "";
    document.getElementById("edit-teach-phone").value = teacher.phone || "";
    document.getElementById("edit-teach-subject").value = teacher.subject || "";
    document.getElementById("edit-teach-password").value = "";
    document.getElementById("edit-teach-status").value = teacher.is_active === false ? "false" : "true";
    
    openModal("edit-teacher-modal");
}
window.openEditTeacherModal = openEditTeacherModal;

document.getElementById("edit-teacher-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const teacherId = document.getElementById("edit-teacher-id").value;
    
    const payload = {
        username: document.getElementById("edit-teach-username").value,
        email: document.getElementById("edit-teach-email").value,
        phone: document.getElementById("edit-teach-phone").value,
        subject: document.getElementById("edit-teach-subject").value,
        password: document.getElementById("edit-teach-password").value || null,
        is_active: document.getElementById("edit-teach-status").value === "true"
    };
    
    try {
        const res = await fetch(`${API_URL}/auth/teachers/${teacherId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to update teacher");
        }
        showToast("Teacher details updated successfully!");
        closeModal("edit-teacher-modal");
        loadAdminTeachers();
    } catch (err) {
        showToast(err.message, "error");
    }
});
