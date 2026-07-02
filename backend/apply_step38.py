def apply_dynamic_hours():
    # 1. Run database migration
    import sqlite3
    try:
        conn = sqlite3.connect("ngo_attendance.db")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE batches ADD COLUMN total_hours INTEGER NOT NULL DEFAULT 330;")
        conn.commit()
        print("Database migrated: added total_hours column to batches table.")
    except sqlite3.OperationalError as e:
        print("Migration skipped or column already exists:", e)
    finally:
        conn.close()

    # 2. Update backend/models.py
    with open("backend/models.py", "r", encoding="utf-8") as f:
        models_code = f.read()

    old_batch_model = """    end_date = Column(Date, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    status = Column(String, default="active")  # 'active', 'completed'"""

    new_batch_model = """    end_date = Column(Date, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    total_hours = Column(Integer, default=330, nullable=False)
    status = Column(String, default="active")  # 'active', 'completed'"""

    if "total_hours" not in models_code:
        models_code = models_code.replace(old_batch_model, new_batch_model)
        with open("backend/models.py", "w", encoding="utf-8") as f:
            f.write(models_code)
        print("Updated models.py with total_hours Column in Batch.")

    # 3. Update backend/schemas.py
    with open("backend/schemas.py", "r", encoding="utf-8") as f:
        schemas_code = f.read()

    old_batch_base = """    end_date: Optional[date] = None
    total_sessions: int
    status: Optional[str] = "active\""""

    new_batch_base = """    end_date: Optional[date] = None
    total_sessions: int
    total_hours: Optional[int] = 330
    status: Optional[str] = "active\""""

    if "total_hours" not in schemas_code:
        schemas_code = schemas_code.replace(old_batch_base, new_batch_base)
        with open("backend/schemas.py", "w", encoding="utf-8") as f:
            f.write(schemas_code)
        print("Updated schemas.py with total_hours property in BatchBase.")

    # 4. Update backend/routers/batches.py
    with open("backend/routers/batches.py", "r", encoding="utf-8") as f:
        batches_code = f.read()

    old_new_batch = """    new_batch = Batch(
        center_id=batch_in.center_id,
        teacher_id=batch_in.teacher_id,
        sid_batch_id=sid_batch_id,
        course_name=batch_in.course_name,
        start_date=batch_in.start_date,
        end_date=end_date,
        total_sessions=batch_in.total_sessions,
        status=batch_in.status
    )"""

    new_new_batch = """    new_batch = Batch(
        center_id=batch_in.center_id,
        teacher_id=batch_in.teacher_id,
        sid_batch_id=sid_batch_id,
        course_name=batch_in.course_name,
        start_date=batch_in.start_date,
        end_date=end_date,
        total_sessions=batch_in.total_sessions,
        total_hours=batch_in.total_hours or 330,
        status=batch_in.status
    )"""

    if "total_hours=batch_in.total_hours" not in batches_code:
        batches_code = batches_code.replace(old_new_batch, new_new_batch)
        with open("backend/routers/batches.py", "w", encoding="utf-8") as f:
            f.write(batches_code)
        print("Updated batches.py to map total_hours in create_batch.")

    # 5. Update backend/routers/students.py
    with open("backend/routers/students.py", "r", encoding="utf-8") as f:
        students_code = f.read()

    old_student_stats = """        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"]
    }"""

    new_student_stats = """        "attended_sessions": attended,
        "missed_sessions": missed,
        "remaining_sessions": remaining,
        "still_need_to_attend": elig["still_need_to_attend"],
        "can_skip": elig["can_skip"],
        "total_hours": batch.total_hours if batch else 330
    }"""

    if '"total_hours": batch.total_hours' not in students_code:
        students_code = students_code.replace(old_student_stats, new_student_stats)
        with open("backend/routers/students.py", "w", encoding="utf-8") as f:
            f.write(students_code)
        print("Updated students.py to return total_hours in get_student_with_stats.")

    # 6. Update index.html
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    old_batch_form_sessions = """                    <div class="form-group">
                        <label for="batch-sessions">Total Sessions</label>
                        <input type="number" id="batch-sessions" min="1" value="30" required>
                    </div>"""

    new_batch_form_sessions = """                    <div class="form-group">
                        <label for="batch-sessions">Total Sessions</label>
                        <input type="number" id="batch-sessions" min="1" value="30" required>
                    </div>
                    <div class="form-group">
                        <label for="batch-hours">Total Course Hours</label>
                        <input type="number" id="batch-hours" min="1" value="330" required>
                    </div>"""

    if "batch-hours" not in html:
        html = html.replace(old_batch_form_sessions, new_batch_form_sessions)

    # Bump version
    html = html.replace("app.js?v=35", "app.js?v=36")
    html = html.replace("style.css?v=35", "style.css?v=36")

    with open("backend/static/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html to add Total Course Hours field in batch creation modal form.")

    # 7. Update app.js
    with open("backend/static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    old_js_batch_submit = """        start_date: document.getElementById("batch-start").value,
        total_sessions: parseInt(document.getElementById("batch-sessions").value)
    };"""

    new_js_batch_submit = """        start_date: document.getElementById("batch-start").value,
        total_sessions: parseInt(document.getElementById("batch-sessions").value),
        total_hours: parseInt(document.getElementById("batch-hours").value || 330)
    };"""

    js = js.replace(old_js_batch_submit, new_js_batch_submit)

    old_js_student_stats = """        // Calculate hours based on total hours 330
        const totalHrs = 330;
        const totalSessions = data.sessions_attended + data.sessions_missed + data.sessions_remaining;
        const attendedHrs = totalSessions > 0 ? ((data.sessions_attended / totalSessions) * totalHrs).toFixed(1) : "0.0";
        const missedHrs = totalSessions > 0 ? ((data.sessions_missed / totalSessions) * totalHrs).toFixed(1) : "0.0";

        document.getElementById("student-stat-attended").innerText = `${attendedHrs} / 330 hrs`;
        document.getElementById("student-stat-missed").innerText = `${missedHrs} hrs`;
        document.getElementById("student-stat-remaining").innerText = `247.5 hrs`;

        // Render Action message
        const msgBox = document.getElementById("student-action-msg");
        if (data.status === "ELIGIBLE") {
            msgBox.innerHTML = `<span style="color:var(--status-eligible)">🎉 You are eligible for assessments! Keep attending to maintain it.</span>`;
        } else if (data.status === "AT_RISK") {
            msgBox.innerHTML = `<span style="color:var(--status-at-risk)">⚠️ You need to attend <strong>${data.sessions_needed_for_75}</strong> more sessions to reach eligibility. Contact teacher.</span>`;
        } else {
            msgBox.innerHTML = `<span style="color:var(--status-impossible)">🚨 It is mathematically impossible to reach 75% attendance. Please contact coordinator immediately.</span>`;
        }"""

    new_js_student_stats = """        // Calculate hours based on total hours from backend
        const totalHrs = data.total_hours || 330;
        const totalSessions = data.sessions_attended + data.sessions_missed + data.sessions_remaining;
        const sessionDuration = totalSessions > 0 ? (totalHrs / totalSessions) : 0;
        
        const attendedHrs = (data.sessions_attended * sessionDuration).toFixed(1);
        const missedHrs = (data.sessions_missed * sessionDuration).toFixed(1);
        const neededHrs = (data.sessions_needed_for_75 * sessionDuration).toFixed(1);

        document.getElementById("student-stat-attended").innerText = `${attendedHrs} / ${totalHrs} hrs`;
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
        }"""

    js = js.replace(old_js_student_stats, new_js_student_stats)

    with open("backend/static/app.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("Injected dynamic total hours calculations inside app.js.")

if __name__ == "__main__":
    apply_dynamic_hours()
