from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'teacher', 'student'
    phone = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    plain_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    batches = relationship("Batch", back_populates="teacher")
    student_profile = relationship("Student", uselist=False, back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Center(Base):
    __tablename__ = "centers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    nsdc_center_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    batches = relationship("Batch", back_populates="center", cascade="all, delete-orphan")

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sid_batch_id = Column(String, unique=True, index=True, nullable=False)
    course_name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    total_hours = Column(Integer, default=330, nullable=False)
    daily_duration = Column(Float, default=8.25, nullable=False)
    status = Column(String, default="active")  # 'active', 'completed'

    # Relationships
    center = relationship("Center", back_populates="batches")
    teacher = relationship("User", back_populates="batches")
    students = relationship("Student", back_populates="batch", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="batch", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # link to user login if created
    aadhaar_hash = Column(String, nullable=False)  # SHA-256 hash of Aadhaar number
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    sid_student_id = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    batch = relationship("Batch", back_populates="students")
    user = relationship("User", back_populates="student_profile")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # 'present', 'absent'
    attended_hours = Column(Float, default=0.0)
    source = Column(String, default="csv_upload")  # 'csv_upload', 'manual'
    synced_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    batch = relationship("Batch", back_populates="attendance_records")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # e.g., 'login', 'upload_csv', 'create_user'
    table_name = Column(String, nullable=True)
    record_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher = relationship("User", backref="leave_requests")
