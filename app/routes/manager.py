# app/routes/manager.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils import verify_token
from app import models
from app.main import manager
from jose import JWTError
from datetime import datetime
import json
from app.utils.auth import verify_role, get_department_employees
from app.database import get_database
from app.models import User
from app.auth import get_current_user
import databases

router = APIRouter(prefix="/manager")
templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = verify_token(token)
        return payload
    except JWTError:
        return None

@router.get("/dashboard")
def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("manager-dashboard.html", {"request": request, "user": user})

@router.get("/team-overview")
def team_overview(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    
    # Get manager's department
    db_user = db.query(models.User).filter(models.User.username == user["sub"]).first()
    manager = db.query(models.Employee).filter(models.Employee.userID == db_user.userID).first()
    
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    # Get all employees in the manager's department
    team_members = db.query(models.Employee).filter(
        models.Employee.department == manager.department,
        models.Employee.employeeID != manager.employeeID  # Exclude the manager
    ).all()
    
    # Get performance metrics for each team member
    team_data = []
    for member in team_members:
        # Get tasks for this team member
        tasks = db.query(models.Task).filter(
            models.Task.assigned_to == member.employeeID
        ).all()
        
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
        
        team_data.append({
            "employee_id": member.employeeID,
            "name": f"{member.firstName} {member.lastName}",
            "position": member.position,
            "email": member.email,
            "performance_score": round(performance_score, 2),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "on_time_tasks": on_time_tasks
        })
    
    # Get department statistics
    department_stats = {
        "total_members": len(team_members),
        "average_performance": sum(m["performance_score"] for m in team_data) / len(team_data) if team_data else 0,
        "total_tasks": sum(m["total_tasks"] for m in team_data),
        "completed_tasks": sum(m["completed_tasks"] for m in team_data),
        "on_time_tasks": sum(m["on_time_tasks"] for m in team_data)
    }
    
    return templates.TemplateResponse(
        "team-overview.html",
        {
            "request": request,
            "user": user,
            "team_members": team_data,
            "department_stats": department_stats,
            "department_name": manager.department
        }
    )

@router.get("/team-performance-data")
def get_team_performance_data(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get manager's department
    db_user = db.query(models.User).filter(models.User.username == user["sub"]).first()
    manager = db.query(models.Employee).filter(models.Employee.userID == db_user.userID).first()
    
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    # Get all employees in the manager's department
    team_members = db.query(models.Employee).filter(
        models.Employee.department == manager.department,
        models.Employee.employeeID != manager.employeeID
    ).all()
    
    # Calculate real-time team performance
    team_performance = []
    for member in team_members:
        tasks = db.query(models.Task).filter(
            models.Task.assigned_to == member.employeeID
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        on_time_tasks = len([t for t in tasks if t.status == "completed" and t.completed_date <= t.due_date])
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            on_time_rate = (on_time_tasks / completed_tasks) * 100 if completed_tasks > 0 else 0
            performance_score = (completion_rate * 0.7) + (on_time_rate * 0.3)
        else:
            performance_score = 0
        
        team_performance.append({
            "employee_id": member.employeeID,
            "name": f"{member.firstName} {member.lastName}",
            "performance_score": round(performance_score, 2),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "on_time_tasks": on_time_tasks
        })
    
    return JSONResponse({
        "team_performance": team_performance,
        "timestamp": datetime.now().isoformat()
    })

@router.get("/task-assignment")
def task_assignment(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("task-assignment.html", {"request": request, "user": user})

@router.get("/reports")
def reports(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("reports.html", {"request": request, "user": user})

@router.get("/performance-team")
def performance_team(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("performance-team.html", {"request": request, "user": user})

@router.get("/deadline")
def deadlines(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("deadline.html", {"request": request, "user": user})

@router.post("/assign-task")
async def assign_task(
    request: Request,
    task_data: dict,
    db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Create new task
    new_task = models.Task(
        title=task_data["title"],
        description=task_data["description"],
        assigned_to=task_data["employee_id"],
        assigned_by=user["sub"],
        due_date=datetime.fromisoformat(task_data["due_date"]),
        priority=task_data["priority"],
        status="pending"
    )
    db.add(new_task)
    db.commit()
    
    # Get employee details
    employee = db.query(models.Employee).filter(models.Employee.employeeID == task_data["employee_id"]).first()
    if employee:
        # Send real-time notification
        notification = {
            "type": "task_assigned",
            "title": "New Task Assigned",
            "message": f"You have been assigned a new task: {task_data['title']}",
            "task_id": new_task.taskID,
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_notification(str(employee.userID), notification)
    
    return JSONResponse(content={"status": "success", "task_id": new_task.taskID})

@router.get("/team-development", response_class=HTMLResponse)
async def team_development(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Manager", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get manager's department
    manager_query = """
    SELECT department FROM EMPLOYEE WHERE employeeID = :employee_id
    """
    manager = await database.fetch_one(
        query=manager_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get team members
    team_members = await get_department_employees(manager["department"], database)
    
    # Get team skills and progress
    team_skills = []
    for member in team_members:
        skills_query = """
        SELECT * FROM EMPLOYEE_SKILLS 
        WHERE employeeID = :employee_id
        """
        skills = await database.fetch_all(
            query=skills_query,
            values={"employee_id": member["employeeID"]}
        )
        
        courses_query = """
        SELECT * FROM EMPLOYEE_COURSES 
        WHERE employeeID = :employee_id
        """
        courses = await database.fetch_all(
            query=courses_query,
            values={"employee_id": member["employeeID"]}
        )
        
        team_skills.append({
            "employee": member,
            "skills": skills,
            "courses": courses
        })
    
    return templates.TemplateResponse(
        "team-development.html",
        {
            "request": request,
            "team_skills": team_skills
        }
    )

@router.post("/assign-development-plan")
async def assign_development_plan(
    plan_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Manager", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Insert development plan
    insert_query = """
    INSERT INTO DEVELOPMENT_PLAN (
        employeeID, title, description, status, 
        progress, target_date, assigned_by
    ) VALUES (
        :employee_id, :title, :description, 'in_progress',
        0, :target_date, :assigned_by
    )
    """
    await database.execute(
        query=insert_query,
        values={
            "employee_id": plan_data["employee_id"],
            "title": plan_data["title"],
            "description": plan_data["description"],
            "target_date": plan_data["target_date"],
            "assigned_by": current_user.userID
        }
    )
    
    return {"status": "success"}

@router.get("/team-performance", response_class=HTMLResponse)
async def team_performance(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Manager", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get manager's department
    manager_query = """
    SELECT department FROM EMPLOYEE WHERE employeeID = :employee_id
    """
    manager = await database.fetch_one(
        query=manager_query,
        values={"employee_id": current_user.userID}
    )
    
    # Get team performance metrics
    performance_query = """
    SELECT 
        e.employeeID,
        e.fullName,
        COUNT(DISTINCT es.skillID) as total_skills,
        AVG(es.proficiency_level) as avg_proficiency,
        COUNT(DISTINCT ec.courseID) as total_courses,
        AVG(ec.progress) as avg_course_progress
    FROM EMPLOYEE e
    LEFT JOIN EMPLOYEE_SKILLS es ON e.employeeID = es.employeeID
    LEFT JOIN EMPLOYEE_COURSES ec ON e.employeeID = ec.employeeID
    WHERE e.department = :department_id
    GROUP BY e.employeeID, e.fullName
    """
    team_performance = await database.fetch_all(
        query=performance_query,
        values={"department_id": manager["department"]}
    )
    
    return templates.TemplateResponse(
        "team-performance.html",
        {
            "request": request,
            "team_performance": team_performance
        }
    )
