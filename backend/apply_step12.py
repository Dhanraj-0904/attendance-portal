def apply_csv_parsing_upgrades():
    # 1. Update backend/services/csv_parser.py with robust column mapping
    with open("backend/services/csv_parser.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_parsers = """
def parse_date_wise_attendance_csv(csv_content: bytes):
    \"\"\"
    Parses a date-wise attendance CSV sheet containing columns:
    Emp Id, Name, Emp Department, Duration.
    \"\"\"
    try:
        content_str = csv_content.decode("utf-8")
    except UnicodeDecodeError:
        content_str = csv_content.decode("latin1")

    lines = content_str.splitlines()
    
    # Find column headers index
    header_line_idx = 0
    for idx, line in enumerate(lines[:10]):
        if any(h in line for h in ["Emp Id", "Emp ID", "Name", "Division", "Duration"]):
            header_line_idx = idx
            break

    csv_data_io = io.StringIO("\\n".join(lines[header_line_idx:]))
    df = pd.read_csv(csv_data_io)
    df.columns = [col.strip().replace('"', '') for col in df.columns]

    # Map columns
    id_col = None
    name_col = None
    dept_col = None
    dur_col = None

    for col in df.columns:
        col_clean = col.lower()
        if "emp id" in col_clean or "attendance id" in col_clean:
            id_col = col
        elif "name" in col_clean and name_col is None:
            name_col = col
        elif "division/units" in col_clean or "department" in col_clean or "division" in col_clean or "unit" in col_clean:
            dept_col = col
        elif "duration" in col_clean or "hours" in col_clean:
            dur_col = col

    records = []
    for _, row in df.iterrows():
        name_val = clean_cell_value(row.get(name_col)) if name_col else ""
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue

        emp_id = clean_cell_value(row.get(id_col)) if id_col else ""
        dept = clean_cell_value(row.get(dept_col)) if dept_col else ""
        duration = clean_cell_value(row.get(dur_col)) if dur_col else ""

        # Clean name from parenthetical codes
        clean_name, parsed_sid = parse_name_and_code(name_val)
        if not parsed_sid:
            parsed_sid = f"CAN_{emp_id}" if emp_id else f"CAN_{hash(clean_name) % 100000000}"

        records.append({
            "emp_id": parsed_sid,
            "name": clean_name,
            "department": dept,
            "duration": duration,
            "raw_emp_id": emp_id
        })

    return records


def parse_admin_student_list_csv(csv_content: bytes):
    \"\"\"
    Parses a master list of students for a batch:
    Contains fields: Emp_ID, Employee_Name, Emp_Code, Emp_Department.
    \"\"\"
    try:
        content_str = csv_content.decode("utf-8")
    except UnicodeDecodeError:
        content_str = csv_content.decode("latin1")

    lines = content_str.splitlines()
    header_line_idx = 0
    for idx, line in enumerate(lines[:10]):
        if any(h in line for h in ["Emp_ID", "Emp ID", "Employee_Name", "Name"]):
            header_line_idx = idx
            break

    csv_data_io = io.StringIO("\\n".join(lines[header_line_idx:]))
    df = pd.read_csv(csv_data_io)
    df.columns = [col.strip().replace('"', '') for col in df.columns]

    id_col = None
    code_col = None
    name_col = None
    dept_col = None

    for col in df.columns:
        col_clean = col.lower()
        if "emp_code" in col_clean or "emp code" in col_clean:
            code_col = col
        elif "emp_id" in col_clean or "emp id" in col_clean or "student id" in col_clean:
            id_col = col
        elif "employee_name" in col_clean or "name" in col_clean:
            name_col = col
        elif "emp_department" in col_clean or "department" in col_clean or "division" in col_clean:
            dept_col = col

    students = []
    for _, row in df.iterrows():
        name_val = clean_cell_value(row.get(name_col)) if name_col else ""
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue

        emp_id = clean_cell_value(row.get(id_col)) if id_col else ""
        emp_code = clean_cell_value(row.get(code_col)) if code_col else ""
        dept = clean_cell_value(row.get(dept_col)) if dept_col else ""

        # Clean name from parenthetical codes
        clean_name, parsed_code = parse_name_and_code(name_val)
        final_code = parsed_code or emp_code or (f"CAN_{emp_id}" if emp_id else f"CAN_{hash(clean_name) % 100000000}")

        students.append({
            "emp_id": final_code,
            "name": clean_name,
            "department": dept
        })

    return students
"""

    # Replace the previous implementations of parse_date_wise_attendance_csv and parse_admin_student_list_csv
    # We locate def parse_date_wise_attendance_csv and replace everything to the end of the file
    content_parts = content.split("def parse_date_wise_attendance_csv")
    content = content_parts[0] + "def parse_date_wise_attendance_csv" + new_parsers

    # Ensure to replace double escaped newlines back to single newlines
    content = content.replace('\\n', '\n')

    with open("backend/services/csv_parser.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Injected custom headers parsers into csv_parser.py successfully.")

    # 2. Update backend/routers/sync.py to use robust routing, durations and student list enrollment
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync = f.read()

    new_upload_route = """@router.post("/upload")
async def upload_attendance_csv(
    batch_id: int = Form(...),
    date: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime
    # Parse target date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    contents = await file.read()

    try:
        from ..services.csv_parser import parse_date_wise_attendance_csv
        parsed_rows = parse_date_wise_attendance_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Get allowed batches
    if current_user.role == "teacher":
        allowed_batches = db.query(Batch).filter(Batch.teacher_id == current_user.id).all()
    else:
        allowed_batches = db.query(Batch).all()

    allowed_batch_ids = [b.id for b in allowed_batches]

    if batch_id not in allowed_batch_ids:
        raise HTTPException(status_code=403, detail="You do not have permission to sync data for this batch")

    # Group CSV students that match active students in our database
    present_student_ids = set()
    all_processed_student_ids = set()

    for row in parsed_rows:
        emp_id = row["emp_id"]
        raw_emp_id = row["raw_emp_id"]
        duration = row["duration"].strip()

        # Find student by candidate code OR raw emp_id
        student = db.query(Student).filter(
            (Student.sid_student_id == emp_id) | 
            (Student.sid_student_id == f"CAN_{raw_emp_id}")
        ).first()

        if student and student.batch_id in allowed_batch_ids:
            all_processed_student_ids.add(student.id)
            if duration and duration != "00:00" and duration != "0:00":
                present_student_ids.add(student.id)

    # We will update attendance for the selected batch, and ANY other batch that has students listed in the CSV
    batches_to_update = {batch_id}
    for s_id in all_processed_student_ids:
        s_profile = db.query(Student).filter(Student.id == s_id).first()
        if s_profile:
            batches_to_update.add(s_profile.batch_id)

    total_present = 0
    total_absent = 0

    for b_id in batches_to_update:
        # Get all students enrolled in this batch
        students_in_batch = db.query(Student).filter(Student.batch_id == b_id).all()
        
        for student in students_in_batch:
            # Check status
            if student.id in present_student_ids:
                status_val = "present"
                total_present += 1
            else:
                status_val = "absent"
                total_absent += 1

            # Upsert record
            existing_rec = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student.id,
                AttendanceRecord.batch_id == b_id,
                AttendanceRecord.session_date == target_date
            ).first()

            if existing_rec:
                existing_rec.status = status_val
                existing_rec.source = "csv_upload"
                existing_rec.synced_at = datetime.utcnow()
            else:
                new_rec = AttendanceRecord(
                    student_id=student.id,
                    batch_id=b_id,
                    session_date=target_date,
                    status=status_val,
                    source="csv_upload",
                    synced_at=datetime.utcnow()
                )
                db.add(new_rec)

    db.commit()

    log_action(db, current_user.id, "upload_csv", "batches", batch_id)

    return {
        "message": f"Attendance synced successfully for {target_date.strftime('%Y-%m-%d')}.",
        "batches_updated": list(batches_to_update),
        "students_present": total_present,
        "students_absent": total_absent
    }
"""

    new_admin_upload_route = """@router.post("/admin-upload")
async def upload_admin_student_list(
    batch_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    contents = await file.read()

    try:
        from ..services.csv_parser import parse_admin_student_list_csv
        parsed_students = parse_admin_student_list_csv(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    from .auth import get_password_hash
    from .sync import hash_string

    students_synced = 0
    accounts_created = 0

    for s_info in parsed_students:
        emp_id = s_info["emp_id"]
        name = s_info["name"]
        dept = s_info["department"]

        # Dynamic routing: Match student batch by department name (ilike match) if possible
        target_batch = None
        if dept:
            dept_clean = dept.strip()
            target_batch = db.query(Batch).filter(Batch.sid_batch_id == dept_clean).first()
            if not target_batch:
                target_batch = db.query(Batch).filter(Batch.sid_batch_id.ilike(f"%{dept_clean}%")).first()

        # Fallback to selected batch if no match found
        active_batch_id = target_batch.id if target_batch else batch_id

        # 1. Check duplicate student profile
        student = db.query(Student).filter(Student.sid_student_id == emp_id).first()

        # 2. Check or create User account
        user = db.query(User).filter(User.username == emp_id).first()
        if not user:
            user = User(
                username=emp_id,
                hashed_password=get_password_hash("student123"),
                role="student"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            accounts_created += 1

        if not student:
            student = Student(
                batch_id=active_batch_id,
                name=name,
                sid_student_id=emp_id,
                aadhaar_hash=hash_string(emp_id),
                user_id=user.id,
                is_active=True
            )
            db.add(student)
        else:
            student.name = name
            student.batch_id = active_batch_id
            student.user_id = user.id

        students_synced += 1

    db.commit()

    log_action(db, current_user.id, "admin_sync_students", "batches", batch_id)

    return {
        "message": f"Successfully synced {students_synced} students. Created {accounts_created} student login accounts.",
        "students_synced": students_synced,
        "accounts_created": accounts_created
    }
"""

    # Replace old upload endpoint in sync.py
    # Locate from @router.post("/upload") to @router.post("/admin-upload")
    sync_parts = sync.split('@router.post("/upload")')
    pre_content = sync_parts[0]
    post_content = sync_parts[1].split('@router.post("/admin-upload")')[1]
    
    sync = pre_content + new_upload_route + "\n\n" + new_admin_upload_route + "\n\n" + post_content

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync)
    print("Injected date-wise CSV attendance sync router into sync.py successfully.")

if __name__ == "__main__":
    apply_csv_parsing_upgrades()
