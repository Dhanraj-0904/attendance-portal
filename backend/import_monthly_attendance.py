import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Production database URL
DATABASE_URL = "postgresql://jss_postgres_db_user:F7QseAbtfhRBmkLBTy81N7P3VEjbDwhI@dpg-d939qg7avr4c73bmtqp0-a.oregon-postgres.render.com/jss_postgres_db"

monthly_file = r"C:\Users\dhanr\Downloads\export (9).csv"

def get_working_days(start_date, count):
    """
    Returns a list of `count` dates starting from `start_date`, excluding Sundays.
    """
    dates = []
    curr = start_date
    while len(dates) < count:
        # 6 is Sunday in Python's weekday() (0 is Monday, 6 is Sunday)
        if curr.weekday() != 6:
            dates.append(curr)
        curr += timedelta(days=1)
    return dates

def import_monthly():
    if not os.path.exists(monthly_file):
        print(f"Monthly file not found at: {monthly_file}")
        return
        
    print("Reading monthly attendance file...")
    # Load DataFrame
    try:
        df = pd.read_csv(monthly_file, encoding='utf-8-sig')
    except:
        df = pd.read_csv(monthly_file, encoding='latin1')
        
    # Clean column names
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    print(f"Columns: {list(df.columns)}")
    
    # Connect to database
    print("Connecting to PostgreSQL database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    from backend.models import Student, Batch, AttendanceRecord
    
    # Column mapping
    cand_id_col = None
    present_col = None
    working_col = None
    hours_col = None
    
    for col in df.columns:
        col_clean = col.lower()
        if "candidate id" in col_clean or "candidate_id" in col_clean:
            cand_id_col = col
        elif "total days present" in col_clean:
            present_col = col
        elif "total working days" in col_clean:
            working_col = col
        elif "total hours spent" in col_clean:
            hours_col = col
            
    print(f"Mapped columns: cand_id_col={cand_id_col}, present_col={present_col}, working_col={working_col}, hours_col={hours_col}")
    
    if not cand_id_col or not present_col or not working_col:
        print("Error: Could not find required columns in CSV!")
        return
        
    records_to_insert = []
    
    for idx, row in df.iterrows():
        cand_id = str(row.get(cand_id_col)).strip()
        if pd.isna(row.get(cand_id_col)) or not cand_id or cand_id.lower() == "details" or cand_id.lower() == "nan":
            continue
            
        # Find student in database
        student = db.query(Student).filter(Student.sid_student_id == cand_id).first()
        if not student:
            print(f"Student not found in database: {cand_id} ({row.get('Name')})")
            continue
            
        batch = db.query(Batch).filter(Batch.id == student.batch_id).first()
        if not batch:
            print(f"Batch not found for student: {cand_id}")
            continue
            
        try:
            total_working = int(row.get(working_col))
            total_present = int(row.get(present_col))
        except Exception as e:
            print(f"Error parsing working/present days for {cand_id}: {e}")
            continue
            
        # Parse total hours spent (format: "HH:MM:SS" or numeric)
        total_hours = 0.0
        hrs_str = str(row.get(hours_col)).strip() if hours_col else ""
        if hrs_str and ":" in hrs_str:
            try:
                parts = hrs_str.split(":")
                total_hours = float(parts[0]) + float(parts[1])/60.0
            except:
                pass
        else:
            try:
                total_hours = float(row.get(hours_col)) if hours_col else 0.0
            except:
                pass
                
        # Calculate daily duration for present days
        daily_dur = total_hours / total_present if total_present > 0 else 0.0
        
        # Get working days starting from batch start_date
        working_dates = get_working_days(batch.start_date, total_working)
        
        # First total_present days are marked present, the rest are absent
        for d_idx, date_val in enumerate(working_dates):
            status = "present" if d_idx < total_present else "absent"
            hrs_val = daily_dur if status == "present" else 0.0
            
            records_to_insert.append({
                "student_id": student.id,
                "batch_id": batch.id,
                "session_date": date_val,
                "status": status,
                "attended_hours": hrs_val
            })
            
    print(f"Calculated {len(records_to_insert)} attendance records to import.")
    
    if not records_to_insert:
        print("No records to import!")
        return
        
    # Bulk insert logic
    # To prevent duplicates, let's delete existing records for these students and dates
    student_ids = list(set(r["student_id"] for r in records_to_insert))
    dates = list(set(r["session_date"] for r in records_to_insert))
    
    print("Deleting old attendance records to prevent duplicates...")
    db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id.in_(student_ids),
        AttendanceRecord.session_date.in_(dates)
    ).delete(synchronize_session=False)
    db.commit()
    
    print("Inserting new records...")
    for r in records_to_insert:
        db_rec = AttendanceRecord(
            student_id=r["student_id"],
            batch_id=r["batch_id"],
            session_date=r["session_date"],
            status=r["status"],
            attended_hours=r["attended_hours"],
            source="csv_upload"
        )
        db.add(db_rec)
        
    db.commit()
    print("Import completed successfully!")
    db.close()

if __name__ == "__main__":
    import_monthly()
