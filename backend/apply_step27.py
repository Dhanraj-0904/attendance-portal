import sqlite3
import os

def run_db_migration():
    db_path = "backend/attendance.db"
    if not os.path.exists(db_path):
        print("Database not found yet.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            leave_date DATE NOT NULL,
            reason TEXT NOT NULL,
            status VARCHAR DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        );
        """)
        conn.commit()
        print("Successfully ran SQLite migration: created 'leave_requests' table.")
    except Exception as e:
        print("Migration error:", e)
    finally:
        conn.close()

def apply_leaves_feature():
    # Run DB migration
    run_db_migration()

    # 1. Update backend/models.py (Append LeaveRequest model)
    with open("backend/models.py", "r", encoding="utf-8") as f:
        models_code = f.read()

    leave_model = """

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher = relationship("User", backref="leave_requests")
"""

    if "class LeaveRequest" not in models_code:
        models_code += leave_model
        with open("backend/models.py", "w", encoding="utf-8") as f:
            f.write(models_code)
        print("Appended LeaveRequest model to models.py.")

    # 2. Create backend/routers/leaves.py
    leaves_router_code = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..models import User, LeaveRequest
from .auth import get_current_user, require_role, log_action
from pydantic import BaseModel

router = APIRouter(prefix="/leaves", tags=["Leaves"])

class LeaveCreate(BaseModel):
    leave_date: date
    reason: str

@router.post("/request")
def request_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["teacher"]))
):
    existing = db.query(LeaveRequest).filter(
        LeaveRequest.teacher_id == current_user.id,
        LeaveRequest.leave_date == leave_in.leave_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a request for this date.")

    new_leave = LeaveRequest(
        teacher_id=current_user.id,
        leave_date=leave_in.leave_date,
        reason=leave_in.reason,
        status="pending"
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    log_action(db, current_user.id, "request_leave", "leave_requests", new_leave.id)
    return {"message": "Leave request submitted successfully"}

@router.get("/", response_model=List[dict])
def get_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        leaves = db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()
    elif current_user.role == "teacher":
        leaves = db.query(LeaveRequest).filter(LeaveRequest.teacher_id == current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    else:
        leaves = []

    result = []
    for l in leaves:
        result.append({
            "id": l.id,
            "teacher_id": l.teacher_id,
            "teacher_name": l.teacher.username if l.teacher else "Unknown Teacher",
            "leave_date": l.leave_date.strftime("%Y-%m-%d"),
            "reason": l.reason,
            "status": l.status,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return result

@router.post("/{id}/approve")
def approve_leave(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "approved"
    db.commit()

    log_action(db, current_user.id, "approve_leave", "leave_requests", id)
    return {"message": "Leave request approved successfully"}

@router.post("/{id}/decline")
def decline_leave(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "declined"
    db.commit()

    log_action(db, current_user.id, "decline_leave", "leave_requests", id)
    return {"message": "Leave request declined successfully"}
"""
    with open("backend/routers/leaves.py", "w", encoding="utf-8") as f:
        f.write(leaves_router_code)
    print("Created backend/routers/leaves.py router.")

    # 3. Update backend/main.py (Include leaves router)
    with open("backend/main.py", "r", encoding="utf-8") as f:
        main_code = f.read()

    main_code = main_code.replace("from .routers import auth, centers, batches, students, sync, reports",
                                  "from .routers import auth, centers, batches, students, sync, reports, leaves")
    main_code = main_code.replace("app.include_router(reports.router)",
                                  "app.include_router(reports.router)\napp.include_router(leaves.router)")

    with open("backend/main.py", "w", encoding="utf-8") as f:
        f.write(main_code)
    print("Registered leaves router in main.py.")

    # 4. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Admin Sidebar Navigation Day Off Link
    admin_nav_link = """                        <a href="#admin-teachers" class="nav-item" data-tab="admin-teachers">
                            <span class="icon">👨‍🏫</span> Teachers
                        </a>"""

    new_admin_nav_link = """                        <a href="#admin-teachers" class="nav-item" data-tab="admin-teachers">
                            <span class="icon">👨‍🏫</span> Teachers
                        </a>
                        <a href="#admin-leaves" class="nav-item" data-tab="admin-leaves">
                            <span class="icon">📅</span> Leave Approvals
                        </a>"""

    html = html.replace(admin_nav_link, new_admin_nav_link)

    # Teacher Sidebar Navigation Request Day Off Link
    teacher_nav_link = """                    <div id="nav-teacher" class="nav-group hidden">
                        <h3>INSTRUCTOR</h3>
                        <a href="#teacher-dashboard" class="nav-item active" data-tab="teacher-dashboard">
                            <span class="icon">📈</span> Dashboard
                        </a>
                        <a href="#teacher-upload" class="nav-item" data-tab="teacher-upload">
                            <span class="icon">📤</span> Sync Attendance
                        </a>"""

    new_teacher_nav_link = """                    <div id="nav-teacher" class="nav-group hidden">
                        <h3>INSTRUCTOR</h3>
                        <a href="#teacher-dashboard" class="nav-item active" data-tab="teacher-dashboard">
                            <span class="icon">📈</span> Dashboard
                        </a>
                        <a href="#teacher-upload" class="nav-item" data-tab="teacher-upload">
                            <span class="icon">📤</span> Sync Attendance
                        </a>
                        <a href="#teacher-leaves" class="nav-item" data-tab="teacher-leaves">
                            <span class="icon">📅</span> Request Leave
                        </a>"""

    html = html.replace(teacher_nav_link, new_teacher_nav_link)

    # Admin Leaves Tab Content
    admin_leaves_tab = """                    <!-- ================= ADMIN LEAVES TAB ================= -->
                    <section id="tab-admin-leaves" class="tab-content">
                        <div class="dashboard-header">
                            <h1>Teacher Leave Approvals</h1>
                            <p>Approve or decline day off permission requests from teachers.</p>
                        </div>
                        <div class="glass-card mt-20">
                            <div class="table-container">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Teacher</th>
                                            <th>Date Requested</th>
                                            <th>Reason</th>
                                            <th>Status</th>
                                            <th>Requested At</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="admin-leaves-table-body">
                                        <tr><td colspan="6" class="text-center">Loading leave requests...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </section>"""

    # Insert admin leaves tab before teacher dashboard tab
    html = html.replace('<!-- ================= TEACHER DASHBOARD TAB ================= -->',
                        admin_leaves_tab + '\n\n                    <!-- ================= TEACHER DASHBOARD TAB ================= -->')

    # Teacher Leaves Tab Content
    teacher_leaves_tab = """                    <!-- ================= TEACHER LEAVES TAB ================= -->
                    <section id="tab-teacher-leaves" class="tab-content">
                        <div class="tab-header-action">
                            <div>
                                <h1>My Day Off Requests</h1>
                                <p>Submit new requests for day off permission and track status.</p>
                            </div>
                            <button class="btn btn-primary" onclick="openModal('request-leave-modal')">+ Request Day Off</button>
                        </div>
                        <div class="glass-card mt-20">
                            <div class="table-container">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Date Requested</th>
                                            <th>Reason</th>
                                            <th>Status</th>
                                            <th>Requested At</th>
                                        </tr>
                                    </thead>
                                    <tbody id="teacher-leaves-table-body">
                                        <tr><td colspan="4" class="text-center">Loading day off logs...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </section>"""

    # Insert teacher leaves tab before student dashboard tab
    html = html.replace('<!-- ================= STUDENT DASHBOARD TAB ================= -->',
                        teacher_leaves_tab + '\n\n                    <!-- ================= STUDENT DASHBOARD TAB ================= -->')

    # Request Leave Modal Markup
    request_leave_modal = """
        <!-- Request Leave Modal -->
        <div id="request-leave-modal" class="modal">
            <div class="modal-content glass-card">
                <div class="modal-header">
                    <h2>Request Day Off</h2>
                    <span class="close-btn" onclick="closeModal('request-leave-modal')">&times;</span>
                </div>
                <form id="request-leave-form">
                    <div class="form-group">
                        <label for="leave-date-input">Select Date</label>
                        <input type="date" id="leave-date-input" required style="padding: 12px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; width: 100%;">
                    </div>
                    <div class="form-group">
                        <label for="leave-reason-input">Reason for Holiday</label>
                        <textarea id="leave-reason-input" placeholder="e.g. Health issue, family function, urgent personal work..." required style="padding: 12px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; width: 100%; height: 100px; resize: none;"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">⚡ Submit Request</button>
                </form>
            </div>
        </div>
"""

    # Insert before </body>
    html = html.replace('<script src="/static/app.js?v=23"></script>', request_leave_modal + '\n    <script src="/static/app.js?v=24"></script>')
    html = html.replace("app.js?v=23", "app.js?v=24")
    html = html.replace("style.css?v=23", "style.css?v=24")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html templates and navigation successfully.")

    # 5. Update style.css (holiday styles)
    with open("backend/static/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    holiday_styles = """
/* ================= CALENDAR HOLIDAY HIGHLIGHTS ================= */
.calendar-day.holiday {
    color: var(--status-impossible) !important;
    background: rgba(255, 23, 68, 0.03) !important;
    border: 1px dashed rgba(255, 23, 68, 0.25) !important;
}
.calendar-day.holiday.uploaded {
    background: rgba(0, 230, 118, 0.12) !important;
    border: 1px dashed var(--status-eligible) !important;
    color: var(--status-eligible) !important;
}
"""
    if ".calendar-day.holiday" not in css:
        css += holiday_styles

    with open("backend/static/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Appended holiday highlighting styles to style.css.")

    # 6. Update app.js (Incorporate holidays and request leaves logic)
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Define holiday array at the top level
    holiday_definition = """
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
"""
    if "GAZETTED_HOLIDAYS_2026" not in js:
        js = js.replace('// Theme Management Logic', holiday_definition + '\n// Theme Management Logic')

    # Add holiday class logic inside renderSyncCalendar()
    old_sync_cal_loop = """        cell.className = "calendar-day interactive";
        cell.innerText = day;

        if (syncUploadedDates.includes(dateStr)) {
            cell.classList.add("uploaded");
        }"""

    new_sync_cal_loop = """        cell.className = "calendar-day interactive";
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
        }"""

    js = js.replace(old_sync_cal_loop, new_sync_cal_loop)

    # Add holiday class logic inside renderStudentCalendar()
    old_stud_cal_loop = """        cell.className = "calendar-day";
        cell.innerText = day;

        // Look up attendance logs for this specific date string"""

    new_stud_cal_loop = """        cell.className = "calendar-day";
        cell.innerText = day;

        const dayOfWeek = new Date(studentCalYear, studentCalMonth, day).getDay();
        const isSunday = dayOfWeek === 0;
        const isGazettedHoliday = GAZETTED_HOLIDAYS_2026.includes(dateStr);
        
        if (isSunday || isGazettedHoliday) {
            cell.classList.add("holiday");
            cell.title = isSunday ? "Sunday Holiday" : "Gazetted Holiday";
        }

        // Look up attendance logs for this specific date string"""

    js = js.replace(old_stud_cal_loop, new_stud_cal_loop)

    # Add leave loader calls in setupScreenForRole()
    old_setup_screen = """    } else if (state.role === "teacher") {
        document.getElementById("nav-teacher").classList.remove("hidden");
        switchTab("teacher-dashboard");
        loadTeacherDashboard();
    }"""

    new_setup_screen = """    } else if (state.role === "teacher") {
        document.getElementById("nav-teacher").classList.remove("hidden");
        switchTab("teacher-dashboard");
        loadTeacherDashboard();
        loadTeacherLeaves();
    }"""

    js = js.replace(old_setup_screen, new_setup_screen)

    old_setup_screen_admin = """    if (state.role === "admin") {
        document.getElementById("nav-admin").classList.remove("hidden");
        switchTab("admin-dashboard");
        loadAdminDashboard();
    }"""

    new_setup_screen_admin = """    if (state.role === "admin") {
        document.getElementById("nav-admin").classList.remove("hidden");
        switchTab("admin-dashboard");
        loadAdminDashboard();
        loadAdminLeaves();
    }"""

    js = js.replace(old_setup_screen_admin, new_setup_screen_admin)

    # Inject leave request submit listener into DOMContentLoaded
    leave_form_listener = """
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
"""
    js = js.replace('window.addEventListener("DOMContentLoaded", () => {', 'window.addEventListener("DOMContentLoaded", () => {\n' + leave_form_listener)

    # Append leaves controllers to the bottom of the file
    leaves_controllers = """
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
                    <td>${l.created_at}</td>
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
"""
    js += leaves_controllers

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected all leaves controllers and handlers successfully in app.js.")

if __name__ == "__main__":
    apply_leaves_feature()
