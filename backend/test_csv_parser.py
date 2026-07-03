import sys
import os
import pandas as pd
import io
from backend.services.csv_parser import clean_cell_value, parse_name_and_code

real_file_path = r"C:\Users\dhanr\Downloads\csv_file (2).csv"

def debug_parse():
    with open(real_file_path, 'rb') as f:
        contents = f.read()
        
    try:
        content_str = contents.decode("utf-8-sig")
    except:
        content_str = contents.decode("latin1")
        
    lines = content_str.splitlines()
    header_line_idx = 0
    for idx, line in enumerate(lines[:10]):
        line_lower = line.lower()
        if any(h in line_lower for h in ["emp_id", "emp id", "employee_", "employee", "name", "student", "candidate", "aadhaar", "aadhar", "s.no", "mobile", "phone"]):
            header_line_idx = idx
            break
            
    print(f"Header index: {header_line_idx}")
    print(f"Header line: {lines[header_line_idx]}")
    
    csv_data_io = io.StringIO("\n".join(lines[header_line_idx:]))
    df = pd.read_csv(csv_data_io)
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    
    cols = [col for col in df.columns if "unnamed" not in col.lower()]
    print(f"Filtered columns: {cols}")
    
    id_col = None
    name_col = None
    dept_col = None
    loc_col = None

    # 1. Match name_col (highest priority first)
    name_candidates = ["employee_name", "employee_", "candidate_name", "student_name", "name", "candidate", "student", "member", "naam", "नाम"]
    for cand in name_candidates:
        for col in cols:
            col_clean = col.lower()
            if cand in col_clean and "verify" not in col_clean and "status" not in col_clean and "id" not in col_clean:
                name_col = col
                break
        if name_col:
            break

    # 2. Match id_col
    id_candidates = ["emp_id", "emp id", "student_id", "candidate_id", "roll", "s.no", "serial", "aadhaar", "aadhar"]
    for cand in id_candidates:
        for col in cols:
            col_clean = col.lower()
            if cand in col_clean and "verify" not in col_clean and "status" not in col_clean:
                id_col = col
                break
        if id_col:
            break

    # 3. Match dept_col
    dept_candidates = ["emp_department", "department", "division", "subject", "course"]
    for cand in dept_candidates:
        for col in cols:
            col_clean = col.lower()
            if cand in col_clean:
                dept_col = col
                break
        if dept_col:
            break

    # 4. Match loc_col
    loc_candidates = ["emp_location", "emp_locat", "location", "office location", "center"]
    for cand in loc_candidates:
        for col in cols:
            col_clean = col.lower()
            if cand in col_clean:
                loc_col = col
                break
        if loc_col:
            break
            
    print(f"Matches: id_col={id_col}, name_col={name_col}, dept_col={dept_col}, loc_col={loc_col}")
    
    students = []
    for row_idx, row in df.iterrows():
        name_val = clean_cell_value(row.get(name_col)) if name_col else ""
        if not name_val or name_val.lower() == "details" or name_val.isnumeric():
            continue
            
        emp_id = clean_cell_value(row.get(id_col)) if id_col else ""
        dept = clean_cell_value(row.get(dept_col)) if dept_col else ""
        location = clean_cell_value(row.get(loc_col)) if loc_col else ""
        
        clean_name, parsed_code = parse_name_and_code(name_val)
        final_code = parsed_code or emp_id or f"CAN_{abs(hash(clean_name)) % 100000000}"
        
        students.append({
            "emp_id": final_code,
            "name": clean_name,
            "department": dept,
            "location": location
        })
        
    print(f"Total parsed: {len(students)}")
    for s in students[:5]:
        print(s)

if __name__ == "__main__":
    debug_parse()
