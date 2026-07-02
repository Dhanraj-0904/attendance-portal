import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

def migrate(postgres_url: str):
    # Make sure workspace root is in path
    sys.path.append('.')
    
    from backend.database import DB_FILE, engine as sqlite_engine
    from backend.models import Base
    
    if not os.path.exists(DB_FILE):
        print(f"Local database file not found at {DB_FILE}!")
        return
        
    print(f"Connecting to remote PostgreSQL database...")
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)
        
    pg_engine = create_engine(postgres_url)
    
    # 1. Recreate tables on Postgres
    print("Creating tables on remote PostgreSQL database...")
    Base.metadata.create_all(bind=pg_engine)
    
    # 2. Open Sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PgSession = sessionmaker(bind=pg_engine)
    
    sqlite_db = SqliteSession()
    pg_db = PgSession()
    
    try:
        # Clear existing tables in pg
        print("Clearing default seeded data from remote database...")
        for table in reversed(Base.metadata.sorted_tables):
            pg_db.execute(table.delete())
        pg_db.commit()
        
        # Copy data for each model in dependency order
        from backend.models import User, Center, Batch, Student, AttendanceRecord, LeaveRequest, AuditLog
        
        models_to_copy = [User, Center, Batch, Student, AttendanceRecord, LeaveRequest, AuditLog]
        
        for model in models_to_copy:
            name = model.__name__
            print(f"Migrating table {name}...")
            records = sqlite_db.query(model).all()
            if not records:
                print(f"Table {name} is empty, skipping.")
                continue
                
            # Detach records from sqlite session and add to pg session
            from sqlalchemy.orm import make_transient
            for r in records:
                sqlite_db.expunge(r)
                make_transient(r)
                pg_db.add(r)
                
            pg_db.commit()
            print(f"Successfully migrated {len(records)} records for {name}.")
            
        print("🎉 Migration completed successfully! Your online website is now fully updated with all your local data!")
        
    except Exception as e:
        pg_db.rollback()
        print(f"Error during migration: {e}")
    finally:
        sqlite_db.close()
        pg_db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/migrate_to_postgres.py <postgres_connection_string>")
    else:
        migrate(sys.argv[1])
