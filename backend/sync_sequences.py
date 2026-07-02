import sys
from sqlalchemy import create_engine, text

def sync_sequences(url: str):
    print("Connecting to remote database to sync sequences...")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    
    tables = ["users", "centers", "batches", "students", "attendance_records", "leave_requests", "audit_logs"]
    
    try:
        with engine.connect() as conn:
            for table in tables:
                seq_name = f"{table}_id_seq"
                # Check if sequence exists first
                res = conn.execute(text(
                    f"SELECT EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = '{seq_name}')"
                )).fetchone()
                
                if res[0]:
                    # Get max ID
                    max_id_res = conn.execute(text(f"SELECT MAX(id) FROM {table}")).fetchone()
                    max_id = max_id_res[0] if max_id_res[0] is not None else 0
                    next_val = max(1, max_id + 1)
                    
                    # Update sequence setval
                    conn.execute(text(f"SELECT setval('{seq_name}', {next_val}, false)"))
                    print(f"Synced sequence '{seq_name}' to start at {next_val}.")
                else:
                    print(f"Sequence '{seq_name}' does not exist, skipping.")
            conn.commit()
            print("🎉 All database sequences synced successfully!")
    except Exception as e:
        print(f"Error syncing sequences: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/sync_sequences.py <postgres_connection_string>")
    else:
        sync_sequences(sys.argv[1])
