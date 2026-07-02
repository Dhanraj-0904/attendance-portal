from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, AuditLog, Batch, Student, AttendanceRecord
from ..schemas import Token, UserCreate, UserResponse

# Security configuration
SECRET_KEY = "ngo_attendance_secret_key_change_me_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_password_hash(password):
    salt = "ngo_auth_salt_9124_secure"
    hasher = hashlib.sha256()
    hasher.update((password + salt).encode('utf-8'))
    return hasher.hexdigest()

def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def require_role(roles: list):
    """
    Dependency helper to require specific roles.
    """
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return dependency

def log_action(db: Session, user_id: int, action: str, table_name: str = None, record_id: int = None):
    """
    Helper to log user actions in the audit log.
    """
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id
    )
    db.add(log_entry)
    db.commit()

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Auto-seed initial users if they do not exist
    seed_users_if_empty(db)

    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.username) == func.lower(form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    # Audit log entry
    log_action(db, user.id, "login")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Allows Admin to register new users (teachers, students, admins).
    """
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role=user_in.role,
        phone=user_in.phone,
        subject=user_in.subject,
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log action
    log_action(db, current_user.id, "create_user", "users", new_user.id)

    return new_user

def seed_users_if_empty(db: Session):
    """
    Seeds a default Admin, Teacher, and Student if the database is empty.
    """
    user_count = db.query(User).count()
    if user_count == 0:
        admin = User(
            username="admin",
            email="admin@ngo.org",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            phone="9999999999",
            is_active=True,
            plain_password="admin123"
        )
        teacher = User(
            username="teacher",
            email="teacher@ngo.org",
            hashed_password=get_password_hash("teacher123"),
            role="teacher",
            phone="8888888888",
            is_active=True,
            plain_password="teacher123"
        )
        
        db.add_all([admin, teacher])
        db.commit()


class PasswordReset(BaseModel):
    user_id: Optional[int] = None
    new_password: str

@router.post("/change-password")
def change_password(
    data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_user = None
    if data.user_id is not None:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can change other users' passwords.")
        target_user = db.query(User).filter(User.id == data.user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        target_user = current_user

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    target_user.hashed_password = get_password_hash(data.new_password)
    target_user.plain_password = data.new_password
    db.commit()

    log_action(db, current_user.id, "change_password", "users", target_user.id)
    return {"message": f"Password for {target_user.username} updated successfully."}


@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    if current_user.id == teacher_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")

    teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    batches = db.query(Batch).filter(Batch.teacher_id == teacher_id).all()
    for b in batches:
        students = db.query(Student).filter(Student.batch_id == b.id).all()
        for s in students:
            db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.id).delete()
            if s.user_id:
                db.query(AuditLog).filter(AuditLog.user_id == s.user_id).delete()
                db.query(User).filter(User.id == s.user_id).delete()
            db.delete(s)
        db.delete(b)

    from ..models import LeaveRequest
    db.query(LeaveRequest).filter(LeaveRequest.teacher_id == teacher_id).delete()

    db.query(AuditLog).filter(AuditLog.user_id == teacher_id).delete()
    db.delete(teacher)
    db.commit()

    log_action(db, current_user.id, "delete_teacher", "users", teacher_id)
    return {"message": f"Successfully deleted teacher '{teacher.username}' and all associated batches and students."}
