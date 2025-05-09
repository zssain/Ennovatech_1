# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.utils import verify_token
from jose import JWTError
from app.utils.auth import verify_role
from app.database import get_database
from app.models import User
from app.auth import get_current_user
import databases

router = APIRouter(prefix="/admin")
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
    return templates.TemplateResponse("admin-dashboard.html", {"request": request, "user": user})

@router.get("/user-management")
def user_management(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("user-management.html", {"request": request, "user": user})

@router.get("/security-logs")
def security_logs(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("security-logs.html", {"request": request, "user": user})

@router.get("/system-config")
def system_config(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("system-config.html", {"request": request, "user": user})

@router.get("/audit-reports")
def audit_reports(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("audit-reports.html", {"request": request, "user": user})

@router.get("/project-status")
def project_status(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("project-status.html", {"request": request, "user": user})

@router.get("/settings")
def settings(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})

@router.get("/help")
def help_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("help.html", {"request": request, "user": user})

@router.get("/learning-resources", response_class=HTMLResponse)
async def manage_learning_resources(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all learning resources
    resources_query = """
    SELECT lr.*, d.name as department_name
    FROM LEARNING_RESOURCES lr
    JOIN DEPARTMENT d ON lr.dept_id = d.dept_id
    """
    resources = await database.fetch_all(query=resources_query)
    
    # Get all departments for the form
    departments_query = "SELECT * FROM DEPARTMENT"
    departments = await database.fetch_all(query=departments_query)
    
    return templates.TemplateResponse(
        "admin/learning-resources.html",
        {
            "request": request,
            "resources": resources,
            "departments": departments
        }
    )

@router.post("/add-learning-resource")
async def add_learning_resource(
    resource_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Insert new learning resource
    insert_query = """
    INSERT INTO LEARNING_RESOURCES (
        title, description, url, type, 
        duration, rating, dept_id
    ) VALUES (
        :title, :description, :url, :type,
        :duration, :rating, :dept_id
    )
    """
    await database.execute(
        query=insert_query,
        values={
            "title": resource_data["title"],
            "description": resource_data["description"],
            "url": resource_data["url"],
            "type": resource_data["type"],
            "duration": resource_data["duration"],
            "rating": resource_data["rating"],
            "dept_id": resource_data["dept_id"]
        }
    )
    
    return {"status": "success"}

@router.get("/career-levels", response_class=HTMLResponse)
async def manage_career_levels(
    request: Request,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all career levels
    levels_query = """
    SELECT cl.*, d.name as department_name
    FROM CAREER_LEVELS cl
    JOIN DEPARTMENT d ON cl.dept_id = d.dept_id
    ORDER BY cl.level_order
    """
    career_levels = await database.fetch_all(query=levels_query)
    
    # Get all departments for the form
    departments_query = "SELECT * FROM DEPARTMENT"
    departments = await database.fetch_all(query=departments_query)
    
    return templates.TemplateResponse(
        "admin/career-levels.html",
        {
            "request": request,
            "career_levels": career_levels,
            "departments": departments
        }
    )

@router.post("/add-career-level")
async def add_career_level(
    level_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Insert new career level
    insert_query = """
    INSERT INTO CAREER_LEVELS (
        title, dept_id, level_order, description
    ) VALUES (
        :title, :dept_id, :level_order, :description
    )
    """
    await database.execute(
        query=insert_query,
        values={
            "title": level_data["title"],
            "dept_id": level_data["dept_id"],
            "level_order": level_data["level_order"],
            "description": level_data["description"]
        }
    )
    
    return {"status": "success"}

@router.put("/edit-learning-resource/{resource_id}")
async def edit_learning_resource(
    resource_id: int,
    resource_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update learning resource
    update_query = """
    UPDATE LEARNING_RESOURCES
    SET title = :title,
        description = :description,
        url = :url,
        type = :type,
        duration = :duration,
        rating = :rating,
        dept_id = :dept_id
    WHERE id = :id
    """
    await database.execute(
        query=update_query,
        values={
            "id": resource_id,
            "title": resource_data["title"],
            "description": resource_data["description"],
            "url": resource_data["url"],
            "type": resource_data["type"],
            "duration": resource_data["duration"],
            "rating": resource_data["rating"],
            "dept_id": resource_data["dept_id"]
        }
    )
    
    return {"status": "success"}

@router.delete("/delete-learning-resource/{resource_id}")
async def delete_learning_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete learning resource
    delete_query = "DELETE FROM LEARNING_RESOURCES WHERE id = :id"
    await database.execute(query=delete_query, values={"id": resource_id})
    
    return {"status": "success"}

@router.put("/edit-career-level/{level_id}")
async def edit_career_level(
    level_id: int,
    level_data: dict,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update career level
    update_query = """
    UPDATE CAREER_LEVELS
    SET title = :title,
        description = :description,
        level_order = :level_order
    WHERE id = :id
    """
    await database.execute(
        query=update_query,
        values={
            "id": level_id,
            "title": level_data["title"],
            "description": level_data["description"],
            "level_order": level_data["level_order"]
        }
    )
    
    return {"status": "success"}

@router.delete("/delete-career-level/{level_id}")
async def delete_career_level(
    level_id: int,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete career level
    delete_query = "DELETE FROM CAREER_LEVELS WHERE id = :id"
    await database.execute(query=delete_query, values={"id": level_id})
    
    return {"status": "success"}

@router.get("/learning-resources/{resource_id}")
async def get_learning_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get learning resource details
    query = """
    SELECT lr.*, d.name as department_name
    FROM LEARNING_RESOURCES lr
    JOIN DEPARTMENT d ON lr.dept_id = d.dept_id
    WHERE lr.id = :id
    """
    resource = await database.fetch_one(query=query, values={"id": resource_id})
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    return dict(resource)

@router.get("/career-levels/{level_id}")
async def get_career_level(
    level_id: int,
    current_user: User = Depends(get_current_user),
    database: databases.Database = Depends(get_database)
):
    if not await verify_role(current_user.userID, "Admin", database):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get career level details
    query = """
    SELECT cl.*, d.name as department_name
    FROM CAREER_LEVELS cl
    JOIN DEPARTMENT d ON cl.dept_id = d.dept_id
    WHERE cl.id = :id
    """
    level = await database.fetch_one(query=query, values={"id": level_id})
    
    if not level:
        raise HTTPException(status_code=404, detail="Career level not found")
    
    return dict(level)
