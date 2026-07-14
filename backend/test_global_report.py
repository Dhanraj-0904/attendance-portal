import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://neondb_owner:npg_vK7dm4PJTCeh@ep-dark-thunder-ao3nxv7j.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def test_report():
    print("Testing get_global_admin_stats logic on Neon data...")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    from backend.routers.reports import get_global_admin_stats
    try:
        # Mock current_user admin
        from backend.models import User
        admin_user = db.query(User).filter(User.role == "admin").first()
        print(f"Using admin user: {admin_user.username} (ID: {admin_user.id})")
        
        stats = get_global_admin_stats(db, admin_user)
        print("Stats returned successfully:")
        print(stats)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report()
