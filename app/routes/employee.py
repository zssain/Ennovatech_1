# app/routes/employee.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils import verify_token
from app import models
from jose import JWTError
from datetime import datetime, timedelta
import json
from app.utils.auth import verify_role, get_employee_department
from app.database import get_database
from app.models import User
from app.auth import get_current_user
import databases

router = APIRouter(prefix="/employee")
templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        payload = verify_token(token)
        return payload
    except JWTError:
        return None

@router.get("/dashboard", response_class=HTMLResponse)
async def employee_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Employee", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get employee's department
    department_id = await get_employee_department(current_user.userID, database)
    
    # Get employee's skills
    skills_query = """
    SELECT * FROM EMPLOYEE_SKILLS 
    WHERE employeeID = :employee_id
    """
    skills = await database.fetch_all(
        query=skills_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get recommended skills based on department
    recommended_skills_query = """
    SELECT * FROM LEARNING_RESOURCES 
    WHERE dept_id = :department_id
    """
    recommended_skills = await database.fetch_all(
        query=recommended_skills_query,
        values={"department_id": department_id}
    )
    
    return templates.TemplateResponse(
        "skills.html",
        {
            "request": request,
            "skills": skills,
            "recommended_skills": recommended_skills,
            "learning_resources": recommended_skills
        }
    )

@router.post("/update-skill-progress")
async def update_skill_progress(
    skill_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Employee", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update skill progress
    update_query = """
    UPDATE EMPLOYEE_SKILLS 
    SET proficiency_level = :proficiency,
        last_updated = CURRENT_TIMESTAMP
    WHERE skillID = :skill_id 
    AND employeeID = :employee_id
    """
    await database.execute(
        query=update_query,
        values={
            "proficiency": skill_data["proficiency"],
            "skill_id": skill_data["skill_id"],
            "employee_id": current_user.userID
        }
    )
    
    return {"status": "success"}

@router.get("/career-path", response_class=HTMLResponse)
async def career_path(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Employee", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get current position
    position_query = """
    SELECT e.*, d.name as department_name
    FROM EMPLOYEE e
    JOIN DEPARTMENT d ON e.department = d.dept_id
    WHERE e.employeeID = :employee_id
    """
    current_position = await database.fetch_one(
        query=position_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get career path levels
    levels_query = """
    SELECT * FROM CAREER_LEVELS
    WHERE dept_id = :department_id
    ORDER BY level_order
    """
    career_path = await database.fetch_all(
        query=levels_query,
        values={"department_id": current_position["department"]}
    )
    
    # Get development plan
    plan_query = """
    SELECT * FROM DEVELOPMENT_PLAN
    WHERE employeeID = :employee_id
    """
    development_plan = await database.fetch_all(
        query=plan_query,
        values={"employee_id": current_user.userID}
    )
    
    return templates.TemplateResponse(
        "career-path.html",
        {
            "request": request,
            "current_position": current_position,
            "career_path": career_path,
            "development_plan": development_plan
        }
    )

@router.get("/learning-hub", response_class=HTMLResponse)
async def learning_hub(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Employee", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get learning statistics
    stats_query = """
    SELECT 
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as courses_completed,
        COUNT(*) as total_courses,
        COUNT(CASE WHEN type = 'certification' THEN 1 END) as certifications,
        SUM(duration) as learning_hours,
        COUNT(DISTINCT skillID) as skills_gained
    FROM EMPLOYEE_COURSES
    WHERE employeeID = :employee_id
    """
    learning_stats = await database.fetch_one(
        query=stats_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get current courses
    courses_query = """
    SELECT * FROM EMPLOYEE_COURSES
    WHERE employeeID = :employee_id
    """
    current_courses = await database.fetch_all(
        query=courses_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get recommended resources
    resources_query = """
    SELECT * FROM LEARNING_RESOURCES
    WHERE dept_id = (
        SELECT department FROM EMPLOYEE WHERE employeeID = :employee_id
    )
    """
    recommended_resources = await database.fetch_all(
        query=resources_query,
        values={"employee_id": current_user.userID}
    )
    
    return templates.TemplateResponse(
        "learning-hub.html",
        {
            "request": request,
            "learning_stats": learning_stats,
            "current_courses": current_courses,
            "recommended_resources": recommended_resources
        }
    )

@router.get("/my-tasks")
def my_tasks(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("my-tasks.html", {"request": request, "user": user})

@router.get("/attendance")
def attendance(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("attendance.html", {"request": request, "user": user})

@router.get("/leave-requests")
def leave_requests(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("leave-requests.html", {"request": request, "user": user})

@router.get("/performance")
def performance(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    
    db_user = db.query(models.User).filter(models.User.username == user["sub"]).first()
    employee = db.query(models.Employee).filter(models.Employee.userID == db_user.userID).first()
    
    # Get performance metrics
    tasks = db.query(models.Task).filter(
        models.Task.assigned_to == employee.employeeID
    ).all()
    
    # Calculate metrics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "completed"])
    on_time_tasks = len([t for t in tasks if t.status == "completed" and t.completed_date <= t.due_date])
    
    # Calculate performance score
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        on_time_rate = (on_time_tasks / completed_tasks) * 100 if completed_tasks > 0 else 0
        performance_score = (completion_rate * 0.7) + (on_time_rate * 0.3)
    else:
        performance_score = 0
    
    # Get monthly performance data
    monthly_data = []
    for i in range(6):  # Last 6 months
        month_start = datetime.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        month_tasks = [t for t in tasks if month_start <= t.created_date <= month_end]
        month_completed = len([t for t in month_tasks if t.status == "completed"])
        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "tasks_completed": month_completed,
            "total_tasks": len(month_tasks)
        })
    
    return templates.TemplateResponse(
        "performance.html",
        {
            "request": request,
            "user": user,
            "employee": employee,
            "performance_score": round(performance_score, 2),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "on_time_tasks": on_time_tasks,
            "monthly_data": json.dumps(monthly_data)
        }
    )

@router.get("/performance-data")
def get_performance_data(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_user = db.query(models.User).filter(models.User.username == user["sub"]).first()
    employee = db.query(models.Employee).filter(models.Employee.userID == db_user.userID).first()
    
    # Get real-time performance data
    tasks = db.query(models.Task).filter(
        models.Task.assigned_to == employee.employeeID
    ).all()
    
    # Calculate current metrics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "completed"])
    on_time_tasks = len([t for t in tasks if t.status == "completed" and t.completed_date <= t.due_date])
    
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        on_time_rate = (on_time_tasks / completed_tasks) * 100 if completed_tasks > 0 else 0
        performance_score = (completion_rate * 0.7) + (on_time_rate * 0.3)
    else:
        performance_score = 0
    
    return JSONResponse({
        "performance_score": round(performance_score, 2),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "on_time_tasks": on_time_tasks,
        "timestamp": datetime.now().isoformat()
    })

@router.get("/notifications")
def notifications(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("notifications.html", {"request": request, "user": user})

@router.get("/profile")
def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    db_user = db.query(models.User).filter(models.User.username == user["sub"]).first()
    employee = db.query(models.Employee).filter(models.Employee.userID == db_user.userID).first()
    return templates.TemplateResponse(
        "employee-profile.html",
        {"request": request, "user": user, "employee": employee}
    )
