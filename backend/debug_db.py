from .database import SessionLocal
from .models import User
import hashlib

def get_hash(password):
    salt = "ngo_auth_salt_9124_secure"
    hasher = hashlib.sha256()
    hasher.update((password + salt).encode('utf-8'))
    return hasher.hexdigest()

db = SessionLocal()
try:
    print("Computed hash for 'admin123':", get_hash("admin123"))
    print("Computed hash for 'teacher123':", get_hash("teacher123"))
    
    users = db.query(User).all()
    print("Registered users in DB:")
    for u in users:
        print(f"User: {u.username}, Role: {u.role}, Hash in DB: {u.hashed_password}")
finally:
    db.close()
