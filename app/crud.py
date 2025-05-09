from sqlalchemy.orm import Session
from app import models, schemas

# ─── USERS ─────────────────────────────────────────────────────────
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ─── EMPLOYEES ─────────────────────────────────────────────────────
def get_all_employees(db: Session):
    return db.query(models.Employee).all()

def get_employee_by_id(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.employeeID == employee_id).first()

# ─── ATTENDANCE ────────────────────────────────────────────────────
def create_attendance(db: Session, record: schemas.AttendanceRecordBase):
    db_record = models.AttendanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_attendance_by_employee(db: Session, emp_id: int):
    return db.query(models.AttendanceRecord).filter(models.AttendanceRecord.employeeID == emp_id).all()

# ─── TASKS ──────────────────────────────────────────────────────────
def create_task(db: Session, task: schemas.TaskBase):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_all_tasks(db: Session):
    return db.query(models.Task).all()

# ─── LEAVE REQUESTS ────────────────────────────────────────────────
def create_leave_request(db: Session, leave: schemas.LeaveRequestBase):
    db_leave = models.LeaveRequest(**leave.dict())
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def get_leaves_by_employee(db: Session, emp_id: int):
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.employeeID == emp_id).all()

# ─── PERFORMANCE METRICS ───────────────────────────────────────────
def create_performance_metric(db: Session, metric: schemas.PerformanceMetricBase):
    db_metric = models.PerformanceMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_metrics_by_employee(db: Session, emp_id: int):
    return db.query(models.PerformanceMetric).filter(models.PerformanceMetric.employeeID == emp_id).all()

# ─── NOTIFICATIONS ─────────────────────────────────────────────────
def create_notification(db: Session, note: schemas.NotificationBase):
    db_note = models.Notification(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notifications_for_employee(db: Session, emp_id: int):
    return db.query(models.Notification).filter(models.Notification.employeeID == emp_id).all()
