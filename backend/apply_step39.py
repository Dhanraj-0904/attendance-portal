def run_real_db_migration():
    import sqlite3
    try:
        conn = sqlite3.connect("backend/attendance.db")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE batches ADD COLUMN total_hours INTEGER NOT NULL DEFAULT 330;")
        conn.commit()
        print("Database migrated successfully on backend/attendance.db.")
    except sqlite3.OperationalError as e:
        print("Migration skipped or column already exists on backend/attendance.db:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    run_real_db_migration()
