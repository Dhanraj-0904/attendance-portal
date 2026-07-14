from sqlalchemy import create_engine, text

db_url = "postgresql://neondb_owner:npg_vK7dm4PJTCeh@ep-dark-thunder-ao3nxv7j.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def check():
    engine = create_engine(db_url)
    tables = ["users", "centers", "batches", "students", "attendance_records", "audit_logs"]
    with engine.connect() as conn:
        for t in tables:
            r = conn.execute(text(f"SELECT COUNT(*) FROM {t}"))
            count = r.scalar()
            print(f"Table '{t}': {count} rows")
            
        print("\nBatches:")
        r_b = conn.execute(text("SELECT id, course_name, center_id FROM batches LIMIT 5"))
        for row in r_b:
            print(f"  ID: {row[0]}, Course Name: {row[1]}, Center ID: {row[2]}")

if __name__ == "__main__":
    check()
