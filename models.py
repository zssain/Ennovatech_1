from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Text, CHAR
)
from sqlalchemy.orm import relationship
from app.database import Base


# ✅ Added User model
class User(Base):
    __tablename__ = "USER"
    userID   = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    role     = Column(String(20), nullable=False)
    email    = Column(String(100), nullable=True)

    employees = relationship("Employee", back_populates="user")


class Department(Base):
    __tablename__ = "DEPARTMENT"
    dept_id = Column(Integer, primary_key=True, index=True)
    name    = Column(String(50), unique=True, nullable=False)

    employees = relationship("Employee", back_populates="department_rel")


class AttendanceRecord(Base):
    __tablename__ = "ATTENDANCE_RECORD"
    rec_id     = Column(Integer, primary_key=True, index=True)
    employeeID = Column(Integer, ForeignKey("EMPLOYEE.employeeID"), nullable=False)
    att_date   = Column(Date, nullable=False)
    punch_in   = Column(DateTime)
    punch_out  = Column(DateTime)

    employee = relationship("Employee", back_populates="attendance_records")


class Task(Base):
    __tablename__ = "TASK"
    task_id     = Column(Integer, primary_key=True, index=True)
    title       = Column(String(100), nullable=False)
    description = Column(Text)
    due_date    = Column(Date)
    status      = Column(String(20), default="Pending")
    assignee    = Column(Integer, ForeignKey("EMPLOYEE.employeeID"))

    assignee_rel = relationship("Employee", back_populates="tasks")


class LeaveRequest(Base):
    __tablename__ = "LEAVE_REQUEST"
    leave_id    = Column(Integer, primary_key=True, index=True)
    employeeID  = Column(Integer, ForeignKey("EMPLOYEE.employeeID"), nullable=False)
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    reason      = Column(Text)
    status      = Column(String(20), default="Pending")

    employee = relationship("Employee", back_populates="leave_requests")


class PerformanceMetric(Base):
    __tablename__ = "PERFORMANCE_METRIC"
    metric_id   = Column(Integer, primary_key=True, index=True)
    employeeID  = Column(Integer, ForeignKey("EMPLOYEE.employeeID"), nullable=False)
    metric_date = Column(Date, nullable=False)
    score       = Column(Integer)  # or use Numeric(5,2)
    type        = Column(String(50))

    employee = relationship("Employee", back_populates="performance_metrics")


class Notification(Base):
    __tablename__ = "NOTIFICATION"
    note_id    = Column(Integer, primary_key=True, index=True)
    employeeID = Column(Integer, ForeignKey("EMPLOYEE.employeeID"), nullable=False)
    message    = Column(Text, nullable=False)
    read_flag  = Column(CHAR(1), default="N")
    created_at = Column(DateTime)

    employee = relationship("Employee", back_populates="notifications")


class SessionStore(Base):
    __tablename__ = "SESSION_STORE"
    sess_id    = Column(Integer, primary_key=True, index=True)
    userID     = Column(Integer, ForeignKey("USER.userID"), nullable=False)
    token      = Column(Text, nullable=False)
    issued_at  = Column(DateTime)
    expires_at = Column(DateTime)

    user = relationship("User")


class Employee(Base):
    __tablename__ = "EMPLOYEE"
    employeeID = Column(Integer, primary_key=True, index=True)
    userID     = Column(Integer, ForeignKey("USER.userID"), nullable=False)
    fullName   = Column(String(100), nullable=False)
    department = Column(String(50))  # legacy department field
    status     = Column(String(20), nullable=False)

    user                = relationship("User", back_populates="employees")
    department_rel      = relationship("Department", back_populates="employees")
    attendance_records  = relationship("AttendanceRecord", back_populates="employee")
    tasks               = relationship("Task", back_populates="assignee_rel")
    leave_requests      = relationship("LeaveRequest", back_populates="employee")
    performance_metrics = relationship("PerformanceMetric", back_populates="employee")
    notifications       = relationship("Notification", back_populates="employee")
