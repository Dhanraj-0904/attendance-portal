import sys
from sqlalchemy import create_engine, text

def inspect_batches(url: str):
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            # Query all batches joined with centers and users (teachers)
            query = """
                SELECT 
                    b.id,
                    b.course_name,
                    c.name as center_name,
                    u.username as teacher_name,
                    b.total_hours,
                    b.daily_duration,
                    b.total_sessions
                FROM batches b
                LEFT JOIN centers c ON b.center_id = c.id
                LEFT JOIN users u ON b.teacher_id = u.id
                ORDER BY b.id
            """
            res = conn.execute(text(query)).fetchall()
            print("Current Batches in database:")
            for row in res:
                print(f"ID: {row[0]} | Course: {row[1]} | Center: {row[2]} | Teacher: {row[3]} | Hours: {row[4]} | Duration: {row[5]} | Sessions: {row[6]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/inspect_batches.py <postgres_connection_string>")
    else:
        inspect_batches(sys.argv[1])
