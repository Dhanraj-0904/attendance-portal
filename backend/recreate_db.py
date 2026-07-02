import os
import sys

def recreate_and_seed():
    # Make sure workspace root is in path
    sys.path.append('.')
    
    from backend.database import Base, engine, DB_FILE
    
    # 1. Delete existing database file to force schema refresh
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Deleted old database file at {DB_FILE}.")
        except Exception as e:
            print(f"Could not delete database file: {e}")
            
    # 2. Import models so they are registered with Base metadata
    from backend.models import User, Student, Batch, AttendanceRecord, LeaveRequest, AuditLog
    
    # 3. Create tables using SQLAlchemy Metadata
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables recreated fresh with new schema columns!")
    except Exception as e:
        print(f"Error during metadata create_all: {e}")
        return

    # 4. Seed the tables
    try:
        from backend.populate_mock_data import populate
        populate()
        print("Mock data seeded successfully into the new schema!")
    except Exception as e:
        print(f"Error during database seeding: {e}")

if __name__ == "__main__":
    recreate_and_seed()
