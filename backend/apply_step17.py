def apply_matching_upgrades():
    # 1. Update backend/services/csv_parser.py to capture locations
    with open("backend/services/csv_parser.py", "r", encoding="utf-8") as f:
        parser_code = f.read()

    # We need to find the parse_date_wise_attendance_csv and parse_admin_student_list_csv functions and modify them to capture location
    # Let's replace the whole block from parse_date_wise_attendance_csv to the end of the file with the new versions that capture location
    new_parsers = """def parse_date_wise_attendance_csv(csv_content: bytes):
    \"\"\"
    Parses a date-wise attendance CSV sheet containing columns:
    Emp Id, Name, Emp Department, Duration, Location.
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
    loc_col = None

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
        elif "location" in col_clean:
            loc_col = col

    records = []
    for _, row in df.iterrows():
        name_val = clean_cell_value(row.get(name_col)) if name_col else ""
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue

        emp_id = clean_cell_value(row.get(id_col)) if id_col else ""
        dept = clean_cell_value(row.get(dept_col)) if dept_col else ""
        duration = clean_cell_value(row.get(dur_col)) if dur_col else ""
        location = clean_cell_value(row.get(loc_col)) if loc_col else ""

        # Clean name from parenthetical codes
        clean_name, parsed_sid = parse_name_and_code(name_val)
        if not parsed_sid:
            parsed_sid = f"CAN_{emp_id}" if emp_id else f"CAN_{hash(clean_name) % 100000000}"

        records.append({
            "emp_id": parsed_sid,
            "name": clean_name,
            "department": dept,
            "duration": duration,
            "raw_emp_id": emp_id,
            "location": location
        })

    return records


def parse_admin_student_list_csv(csv_content: bytes):
    \"\"\"
    Parses a master list of students for a batch:
    Contains fields: Emp_ID, Employee_Name, Emp_Code, Emp_Department, Emp_Location.
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
    loc_col = None

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
        elif "emp_location" in col_clean or "location" in col_clean or "office location" in col_clean:
            loc_col = col

    students = []
    for _, row in df.iterrows():
        name_val = clean_cell_value(row.get(name_col)) if name_col else ""
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue

        emp_id = clean_cell_value(row.get(id_col)) if id_col else ""
        emp_code = clean_cell_value(row.get(code_col)) if code_col else ""
        dept = clean_cell_value(row.get(dept_col)) if dept_col else ""
        location = clean_cell_value(row.get(loc_col)) if loc_col else ""

        # Clean name from parenthetical codes
        clean_name, parsed_code = parse_name_and_code(name_val)
        final_code = parsed_code or emp_code or (f"CAN_{emp_id}" if emp_id else f"CAN_{hash(clean_name) % 100000000}")

        students.append({
            "emp_id": final_code,
            "name": clean_name,
            "department": dept,
            "location": location
        })

    return students
"""

    content_parts = parser_code.split("def parse_date_wise_attendance_csv")
    parser_code = content_parts[0] + new_parsers

    with open("backend/services/csv_parser.py", "w", encoding="utf-8") as f:
        f.write(parser_code)
    print("Updated csv_parser.py to capture locations successfully.")

    # 2. Update backend/routers/sync.py
    with open("backend/routers/sync.py", "r", encoding="utf-8") as f:
        sync = f.read()

    # Define matching helper function in sync.py
    matching_helper = """
def find_best_batch_match(db, batches, dept, location):
    if not dept:
        return None
    
    dept_clean = dept.strip().lower()
    loc_clean = location.strip().lower() if location else ""
    
    # Phase 1: Try to match both course name and center name
    for b in batches:
        center = b.center
        c_name_clean = center.name.lower() if center else ""
        course_clean = b.course_name.lower()
        
        course_matches = (course_clean in dept_clean) or (dept_clean in course_clean)
        center_matches = False
        if c_name_clean:
            center_matches = (c_name_clean in dept_clean) or (c_name_clean in loc_clean) or (dept_clean in c_name_clean)
            
        if course_matches and center_matches:
            return b
            
    # Phase 2: Fallback to matching course name only
    for b in batches:
        course_clean = b.course_name.lower()
        if (course_clean in dept_clean) or (dept_clean in course_clean):
            return b
            
    return None
"""

    if "def find_best_batch_match" not in sync:
        # Inject at the bottom or before first route
        # Let's insert it right after the imports
        import_end_idx = sync.find("router = APIRouter")
        sync = sync[:import_end_idx] + matching_helper + "\n" + sync[import_end_idx:]

    # Update admin-upload route to use find_best_batch_match
    old_admin_upload = """        # Dynamic routing: Match student batch by department name (ilike match) if possible
        target_batch = None
        if dept:
            dept_clean = dept.strip()
            target_batch = db.query(Batch).filter(Batch.sid_batch_id == dept_clean).first()
            if not target_batch:
                target_batch = db.query(Batch).filter(Batch.sid_batch_id.ilike(f"%{dept_clean}%")).first()

        # Fallback to selected batch if no match found
        active_batch_id = target_batch.id if target_batch else batch_id"""

    new_admin_upload = """        # Dynamic routing: Match student batch by course and location (no mixup)
        all_batches = db.query(Batch).all()
        target_batch = find_best_batch_match(db, all_batches, dept, s_info.get("location"))

        # Fallback to selected batch if no match found
        active_batch_id = target_batch.id if target_batch else batch_id"""

    sync = sync.replace(old_admin_upload, new_admin_upload)

    # Update teacher-admin-upload route to use find_best_batch_match
    old_teacher_upload = """        # Find which of the teacher's batches matches this student's department (subject)
        target_batch = None
        if dept:
            dept_clean = dept.strip().lower()
            for b in teacher_batches:
                if b.course_name.lower() in dept_clean or dept_clean in b.course_name.lower():
                    target_batch = b
                    break

        # Fallback to teacher's first batch if no match
        active_batch_id = target_batch.id if target_batch else teacher_batches[0].id"""

    new_teacher_upload = """        # Find which of the teacher's batches matches this student's department (subject) and location
        target_batch = find_best_batch_match(db, teacher_batches, dept, s_info.get("location"))

        # Fallback to teacher's first batch if no match
        active_batch_id = target_batch.id if target_batch else teacher_batches[0].id"""

    sync = sync.replace(old_teacher_upload, new_teacher_upload)

    with open("backend/routers/sync.py", "w", encoding="utf-8") as f:
        f.write(sync)
    print("Updated sync.py matching logic successfully.")

if __name__ == "__main__":
    apply_matching_upgrades()
