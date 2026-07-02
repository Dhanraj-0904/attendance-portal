import sqlite3

def run_backfill():
    conn = sqlite3.connect("backend/attendance.db")
    c = conn.cursor()
    c.execute("UPDATE users SET plain_password = 'teacher123' WHERE role = 'teacher' AND plain_password IS NULL")
    c.execute("UPDATE users SET plain_password = 'student123' WHERE role = 'student' AND plain_password IS NULL")
    conn.commit()
    print("Backfilled user rows:", conn.total_changes)
    conn.close()

if __name__ == "__main__":
    run_backfill()
