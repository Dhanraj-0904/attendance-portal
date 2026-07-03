import sys
from sqlalchemy import create_engine, text

def inspect_logs(url: str):
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            query = "SELECT id, user_id, action, table_name, record_id, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 20"
            res = conn.execute(text(query)).fetchall()
            print("Recent Audit Logs:")
            for row in res:
                print(f"ID: {row[0]} | User: {row[1]} | Action: {row[2]} | Table: {row[3]} | Record: {row[4]} | Time: {row[5]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/inspect_audit_logs.py <postgres_connection_string>")
    else:
        inspect_logs(sys.argv[1])
