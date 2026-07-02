from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# ----------------- Auth & User Schemas -----------------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str  # 'admin', 'teacher', 'student'
    phone: Optional[str] = None
    subject: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Center Schemas -----------------
class CenterBase(BaseModel):
    name: str
    district: str
    state: str
    nsdc_center_code: Optional[str] = None

class CenterCreate(CenterBase):
    pass

class CenterResponse(CenterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Batch Schemas -----------------
class BatchBase(BaseModel):
    center_id: int
    teacher_id: int
    sid_batch_id: Optional[str] = None
    course_name: str
    start_date: date
    end_date: Optional[date] = None
    total_sessions: int
    total_hours: Optional[int] = 330
    daily_duration: Optional[float] = 8.25
    status: Optional[str] = "active"

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: int
    center_name: Optional[str] = None
    teacher_name: Optional[str] = None
    students_count: Optional[int] = 0
    class_eligibility_pct: Optional[float] = 0.0
    class_status: Optional[str] = "ELIGIBLE"

    class Config:
        from_attributes = True

# ----------------- Student Schemas -----------------
class StudentBase(BaseModel):
    batch_id: int
    aadhaar_hash: str
    name: str
    phone: Optional[str] = None
    sid_student_id: str
    is_active: Optional[bool] = True

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: str
    password: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    plain_password: Optional[str] = None
    attendance_pct: Optional[float] = 0.0
    status: Optional[str] = "ELIGIBLE"
    attended_sessions: Optional[float] = 0.0
    missed_sessions: Optional[float] = 0.0
    remaining_sessions: Optional[float] = 0.0
    still_need_to_attend: Optional[float] = 0.0
    can_skip: Optional[float] = 0.0

    # Frontend compatibility fields
    sessions_attended: Optional[float] = 0.0
    sessions_missed: Optional[float] = 0.0
    sessions_needed_for_75: Optional[float] = 0.0
    sessions_remaining: Optional[float] = 0.0
    total_hours: Optional[int] = 330

    class Config:
        from_attributes = True

# ----------------- Attendance Schemas -----------------
class AttendanceRecordBase(BaseModel):
    student_id: int
    batch_id: int
    session_date: date
    status: str  # 'present', 'absent'
    source: Optional[str] = "csv_upload"

class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    synced_at: datetime

    class Config:
        from_attributes = True

# ----------------- Audit Log Schemas -----------------
class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    action: str
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True
