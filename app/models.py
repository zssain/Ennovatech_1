from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Text, CHAR, Boolean, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.database import Base

Base = declarative_base()


class User(Base):
    __tablename__ = "USERS"

    userID = Column("USERID", Integer, primary_key=True, index=True)
    username = Column("USERNAME", String(50), unique=True, index=True)
    email = Column("EMAIL", String(100), unique=True, index=True)
    hashed_password = Column("HASHED_PASSWORD", String(100))
    role = Column("ROLE", String(20))  # Admin, Manager, Employee
    is_active = Column("IS_ACTIVE", Boolean, default=True)
    created_at = Column("CREATED_AT", DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="user", uselist=False)


class Department(Base):
    __tablename__ = "DEPARTMENTS"

    dept_id = Column("DEPT_ID", Integer, primary_key=True, index=True)
    name = Column("NAME", String(50), unique=True)
    description = Column("DESCRIPTION", Text)
    
    # Relationships
    employees = relationship("Employee", back_populates="department_rel")
    career_levels = relationship("CareerLevel", back_populates="department")
    learning_resources = relationship("LearningResource", back_populates="department")


class Employee(Base):
    __tablename__ = "EMPLOYEES"

    employeeID = Column("EMPLOYEEID", Integer, primary_key=True, index=True)
    userID = Column("USERID", Integer, ForeignKey("USERS.USERID"))
    firstName = Column("FIRST_NAME", String(50))
    lastName = Column("LAST_NAME", String(50))
    email = Column("EMAIL", String(100))
    position = Column("POSITION", String(50))
    department = Column("DEPARTMENT", Integer, ForeignKey("DEPARTMENTS.DEPT_ID"))
    hire_date = Column("HIRE_DATE", DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="employee")
    department_rel = relationship("Department", back_populates="employees")
    skills = relationship("EmployeeSkill", back_populates="employee")
    courses = relationship("EmployeeCourse", back_populates="employee")
    tasks = relationship("Task", back_populates="assigned_to_rel")


class AttendanceRecord(Base):
    __tablename__ = "ATTENDANCE_RECORDS"

    rec_id = Column("REC_ID", Integer, primary_key=True, index=True)
    employeeID = Column("EMPLOYEEID", Integer, ForeignKey("EMPLOYEES.EMPLOYEEID"))
    att_date = Column("ATT_DATE", Date)
    punch_in = Column("PUNCH_IN", DateTime)
    punch_out = Column("PUNCH_OUT", DateTime)

    employee = relationship("Employee", back_populates="attendance_records")


class Task(Base):
    __tablename__ = "TASKS"

    taskID = Column("TASKID", Integer, primary_key=True, index=True)
    title = Column("TITLE", String(100))
    description = Column("DESCRIPTION", Text)
    assigned_to = Column("ASSIGNED_TO", Integer, ForeignKey("EMPLOYEES.EMPLOYEEID"))
    assigned_by = Column("ASSIGNED_BY", Integer, ForeignKey("EMPLOYEES.EMPLOYEEID"))
    due_date = Column("DUE_DATE", DateTime)
    priority = Column("PRIORITY", String(20))  # low, medium, high
    status = Column("STATUS", String(20))  # pending, in_progress, completed
    created_date = Column("CREATED_DATE", DateTime, default=datetime.utcnow)
    completed_date = Column("COMPLETED_DATE", DateTime)
    
    # Relationships
    assigned_to_rel = relationship("Employee", foreign_keys=[assigned_to], back_populates="tasks")
    assigned_by_rel = relationship("Employee", foreign_keys=[assigned_by])


class LeaveRequest(Base):
    __tablename__ = "LEAVE_REQUESTS"

    leave_id = Column("LEAVE_ID", Integer, primary_key=True, index=True)
    employeeID = Column("EMPLOYEEID", Integer, ForeignKey("EMPLOYEES.EMPLOYEEID"))
    start_date = Column("START_DATE", Date)
    employeeID = Column("EMPLOYEEID", Integer, ForeignKey("EMPLOYEE.EMPLOYEEID"), nullable=False)
    start_date = Column("START_DATE", Date, nullable=False)
    end_date = Column("END_DATE", Date, nullable=False)
    reason = Column("REASON", Text)
    status = Column("STATUS", String(20), default="Pending")

    employee = relationship("Employee", back_populates="leave_requests")


class PerformanceMetric(Base):
    __tablename__ = "PERFORMANCE_METRIC"
    metric_id = Column("METRIC_ID", Integer, primary_key=True, index=True)
    employeeID = Column("EMPLOYEEID", Integer, ForeignKey("EMPLOYEE.EMPLOYEEID"), nullable=False)
    metric_date = Column("METRIC_DATE", Date, nullable=False)
    score = Column("SCORE", Integer)
    type = Column("TYPE", String(50))

    employee = relationship("Employee", back_populates="performance_metrics")


class Notification(Base):
    __tablename__ = "NOTIFICATION"
    note_id = Column("NOTE_ID", Integer, primary_key=True, index=True)
    employeeID = Column("EMPLOYEEID", Integer, ForeignKey("EMPLOYEE.EMPLOYEEID"), nullable=False)
    message = Column("MESSAGE", Text, nullable=False)
    read_flag = Column("READ_FLAG", CHAR(1), default="N")
    created_at = Column("CREATED_AT", DateTime)

    employee = relationship("Employee", back_populates="notifications")


class SessionStore(Base):
    __tablename__ = "SESSION_STORE"
    sess_id = Column("SESS_ID", Integer, primary_key=True, index=True)
    userID = Column("USERID", Integer, ForeignKey("USER.USERID"), nullable=False)
    token = Column("TOKEN", Text, nullable=False)
    issued_at = Column("ISSUED_AT", DateTime)
    expires_at = Column("EXPIRES_AT", DateTime)

    user = relationship("User", back_populates="sessions")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    employeeID = Column(Integer, ForeignKey("employees.employeeID"))
    skillID = Column(Integer, ForeignKey("skills.skill_id"))
    proficiency_level = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")


class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(Text)
    
    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")


class EmployeeCourse(Base):
    __tablename__ = "employee_courses"

    id = Column(Integer, primary_key=True, index=True)
    employeeID = Column(Integer, ForeignKey("employees.employeeID"))
    courseID = Column(Integer, ForeignKey("learning_resources.id"))
    status = Column(String(20))  # pending, in_progress, completed
    progress = Column(Float, default=0)
    start_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee", back_populates="courses")
    course = relationship("LearningResource", back_populates="employee_courses")


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(Text)
    url = Column(String(200))
    type = Column(String(20))  # course, article, video, book
    duration = Column(Float)  # in hours
    rating = Column(Float)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"))
    
    # Relationships
    department = relationship("Department", back_populates="learning_resources")
    employee_courses = relationship("EmployeeCourse", back_populates="course")


class CareerLevel(Base):
    __tablename__ = "career_levels"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    dept_id = Column(Integer, ForeignKey("departments.dept_id"))
    level_order = Column(Integer)
    description = Column(Text)
    
    # Relationships
    department = relationship("Department", back_populates="career_levels")
