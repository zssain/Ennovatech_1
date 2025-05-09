# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ─── User & Employee ───────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    password: str
    role: str
    email: Optional[str]

class UserOut(UserBase):
    userID: int
    class Config:
        orm_mode = True

class EmployeeBase(BaseModel):
    fullName: str
    department: Optional[str]
    status: str

class EmployeeOut(EmployeeBase):
    employeeID: int
    userID: int
    user: Optional[UserOut]
    class Config:
        orm_mode = True

# ─── Attendance ─────────────────────────────────────────────────
class AttendanceRecordBase(BaseModel):
    employeeID: int
    att_date: date
    punch_in: Optional[datetime]
    punch_out: Optional[datetime]

class AttendanceRecordOut(AttendanceRecordBase):
    rec_id: int
    class Config:
        orm_mode = True

# ─── Task ───────────────────────────────────────────────────────
class TaskBase(BaseModel):
    title: str
    description: Optional[str]
    due_date: Optional[date]
    status: Optional[str] = "Pending"
    assignee: Optional[int]

class TaskOut(TaskBase):
    task_id: int
    class Config:
        orm_mode = True

# ─── Leave Request ──────────────────────────────────────────────
class LeaveRequestBase(BaseModel):
    employeeID: int
    start_date: date
    end_date: date
    reason: Optional[str]
    status: Optional[str] = "Pending"

class LeaveRequestOut(LeaveRequestBase):
    leave_id: int
    class Config:
        orm_mode = True

# ─── Performance Metric ─────────────────────────────────────────
class PerformanceMetricBase(BaseModel):
    employeeID: int
    metric_date: date
    score: Optional[int]  # or float if needed
    type: Optional[str]

class PerformanceMetricOut(PerformanceMetricBase):
    metric_id: int
    class Config:
        orm_mode = True

# ─── Notification ───────────────────────────────────────────────
class NotificationBase(BaseModel):
    employeeID: int
    message: str

class NotificationOut(NotificationBase):
    note_id: int
    read_flag: Optional[str]
    created_at: Optional[datetime]
    class Config:
        orm_mode = True

# ─── Session Store ──────────────────────────────────────────────
class SessionStoreOut(BaseModel):
    sess_id: int
    userID: int
    token: str
    issued_at: Optional[datetime]
    expires_at: Optional[datetime]
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
