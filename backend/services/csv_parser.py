import io
import re
import pandas as pd
from datetime import datetime, timedelta

def clean_cell_value(val):
    """
    Cleans cell values, especially Excel formatting like =\"\"\"12345\" or leading/trailing spaces.
    """
    if pd.isna(val):
        return ""
    val_str = str(val).strip()
    # Remove Excel formula format: ="12345" or ="""12345"
    if val_str.startswith('="') and val_str.endswith('"'):
        val_str = val_str[2:-1]
    val_str = val_str.replace('"', '').strip()
    return val_str

def parse_name_and_code(name_str):
    """
    Extracts student name and candidate code (e.g. CAN_40343428) from name string.
    Example: "Aarti Baghel (CAN_40343428)" -> ("Aarti Baghel", "CAN_40343428")
    """
    if not name_str:
        return "", ""
    name_str = clean_cell_value(name_str)
    match = re.search(r'\((CAN_[0-9]+)\)', name_str)
    if match:
        candidate_code = match.group(1)
        # Remove the parenthetical code from the name
        clean_name = re.sub(r'\s*\(CAN_[0-9]+\)\s*', '', name_str).strip()
        return clean_name, candidate_code
    return name_str, ""

def parse_attendance_csv(csv_content: bytes):
    """
    Parses AadhaarBAS CSV upload content.
    Returns:
        dict: {
            "date_range": (start_date_str, end_date_str),
            "batch_info": {
                "org_name": str,
                "division": str,
                "location": str
            },
            "students": [
                {
                    "biometric_id": str,
                    "name": str,
                    "sid_id": str,
                    "total_days": int,
                    "present_days": int
                },
                ...
            ]
        }
    """
    # Decode bytes to string
    try:
        content_str = csv_content.decode("utf-8")
    except UnicodeDecodeError:
        content_str = csv_content.decode("latin1")

    lines = content_str.splitlines()
    
    # 1. Detect format and metadata (like Date Range)
    date_range = (None, None)
    org_name = "Unknown Center"
    division = "Unknown Course"
    location = "Unknown Location"
    header_line_idx = 0

    # Look for headers in the first 5 lines
    for idx, line in enumerate(lines[:5]):
        # Check for date range: e.g. "Date Range: 06/15/2026 - 06/20/2026"
        date_match = re.search(r'Date Range:\s*([0-9/.-]+)\s*-\s*([0-9/.-]+)', line, re.IGNORECASE)
        if date_match:
            date_range = (date_match.group(1), date_match.group(2))
        
        # Check for Center name: e.g. "Attendance Report for  JSS Sub Center -TC325939"
        center_match = re.search(r'Attendance Report for\s+([^,\n\r]+)', line, re.IGNORECASE)
        if center_match:
            org_name = center_match.group(1).strip()
            
        # Check for location and division: e.g. "Location :- Shalu Beauty..."
        loc_div_match = re.search(r'Location\s*:-\s*(.+?)\s+Division\s*:-\s*(.+)', line, re.IGNORECASE)
        if loc_div_match:
            location = loc_div_match.group(1).strip()
            division = loc_div_match.group(2).strip()

        # Check if this line is the actual column headers
        if "Emp Id" in line or "Attendance Id" in line or "Name" in line:
            header_line_idx = idx

    # Remove headers before reading csv with pandas
    csv_data_io = io.StringIO("\n".join(lines[header_line_idx:]))
    df = pd.read_csv(csv_data_io)
    
    # Clean column names (strip quotes and spaces)
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    
    # Map columns based on synonyms
    id_col = None
    name_col = None
    working_days_col = None
    present_days_col = None
    org_col = None
    division_col = None
    location_col = None

    for col in df.columns:
        col_clean = col.lower()
        if "emp id" in col_clean or "attendance id" in col_clean:
            id_col = col
        elif "name" in col_clean and name_col is None:
            name_col = col
        elif "working days" in col_clean or "working" in col_clean:
            working_days_col = col
        elif "present" in col_clean:
            present_days_col = col
        elif "org name" in col_clean:
            org_col = col
        elif "division" in col_clean:
            division_col = col
        elif "location" in col_clean:
            location_col = col

    if not name_col or not present_days_col:
        raise ValueError("Could not find Name or Present Days columns in CSV.")

    students_list = []
    for _, row in df.iterrows():
        # Skip empty rows or "Details" rows that pandas might import due to linebreaks
        name_val = clean_cell_value(row.get(name_col))
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue
            
        biometric_id = clean_cell_value(row.get(id_col)) if id_col else ""
        clean_name, sid_id = parse_name_and_code(name_val)
        
        # If sid_id was not in Name, use biometric_id as sid_id
        if not sid_id:
            sid_id = f"CAN_{biometric_id}" if biometric_id else f"CAN_{hash(clean_name) % 100000000}"
            
        total_days = int(row.get(working_days_col, 0)) if working_days_col else 0
        present_days = int(row.get(present_days_col, 0))
        
        students_list.append({
            "biometric_id": biometric_id,
            "name": clean_name,
            "sid_id": sid_id,
            "total_days": total_days,
            "present_days": present_days
        })

    # Update batch info from row 1 if available
    if len(df) > 0:
        if org_col and org_name == "Unknown Center":
            org_name = clean_cell_value(df.iloc[0].get(org_col))
        if division_col and division == "Unknown Course":
            division = clean_cell_value(df.iloc[0].get(division_col))
        if location_col and location == "Unknown Location":
            location = clean_cell_value(df.iloc[0].get(location_col))

    return {
        "date_range": date_range,
        "batch_info": {
            "org_name": org_name,
            "division": division,
            "location": location
        },
        "students": students_list
    }

def generate_simulated_dates(start_date_str, end_date_str, total_days, present_days):
    """
    Generates a list of (date, status) pairs within the date range.
    Filters out Sundays to match realistic working schedules.
    Marks present/absent sequentially to represent the summary statistics correctly.
    """
    try:
        start_date = datetime.strptime(start_date_str, "%m/%d/%Y").date()
        end_date = datetime.strptime(end_date_str, "%m/%d/%Y").date()
    except (ValueError, TypeError):
        # Fallback to current date range if parsing fails
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=max(30, total_days))

    # Collect working days (excluding Sundays)
    working_days = []
    current = start_date
    while current <= end_date:
        if current.weekday() != 6:  # 6 = Sunday
            working_days.append(current)
        current += timedelta(days=1)

    # Trim or extend working days to match total_days count
    if len(working_days) > total_days:
        working_days = working_days[:total_days]
    elif len(working_days) < total_days:
        # Extend backwards if we don't have enough working days in the range
        needed = total_days - len(working_days)
        ext_date = start_date
        while needed > 0:
            ext_date -= timedelta(days=1)
            if ext_date.weekday() != 6:
                working_days.insert(0, ext_date)
                needed -= 1

    records = []
    # Distribute present days. We can make it look realistic by placing presents first, then absents,
    # or alternating. Let's place present days first.
    for i, date in enumerate(working_days):
        status = "present" if i < present_days else "absent"
        records.append((date, status))
        
    return records


def parse_date_wise_attendance_csv(csv_content: bytes):
    """
    Parses a date-wise attendance CSV sheet containing columns:
    Emp Id, Name, Emp Department, Duration, Location.
    """
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

    csv_data_io = io.StringIO("\n".join(lines[header_line_idx:]))
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
    """
    Parses a master list of students for a batch:
    Contains fields: Emp_ID, Employee_Name, Emp_Code, Emp_Department, Emp_Location.
    """
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

    csv_data_io = io.StringIO("\n".join(lines[header_line_idx:]))
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
