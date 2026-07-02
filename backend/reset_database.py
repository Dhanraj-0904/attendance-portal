import sqlite3

def reset():
    db_path = "backend/attendance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Resetting database...")
    cursor.execute("DELETE FROM attendance_records;")
    cursor.execute("DELETE FROM leave_requests;")
    cursor.execute("DELETE FROM students;")
    cursor.execute("DELETE FROM batches;")
    cursor.execute("DELETE FROM centers;")
    cursor.execute("DELETE FROM audit_logs;")
    cursor.execute("DELETE FROM users WHERE username != 'admin';")

    conn.commit()
    conn.close()
    print("Database reset successfully! Only admin account remains.")

if __name__ == "__main__":
    reset()
