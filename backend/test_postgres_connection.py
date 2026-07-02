import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_conn(url: str):
    print("Connecting to remote database...")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            # Check users count
            res = conn.execute(text("SELECT count(*) FROM users")).fetchone()
            print(f"Users count: {res[0]}")
            
            # Check tables
            res_tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )).fetchall()
            print("Tables found:")
            for t in res_tables:
                print(f" - {t[0]}")
                
            # Print columns of users table
            res_cols = conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'"
            )).fetchall()
            print("Users columns:")
            for c in res_cols:
                print(f" - {c[0]}: {c[1]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/test_postgres_connection.py <postgres_connection_string>")
    else:
        test_conn(sys.argv[1])
