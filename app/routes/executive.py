# app/routes/executive.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.utils import verify_token
from jose import JWTError

router = APIRouter(prefix="/executive")
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
    return templates.TemplateResponse("executive-dashboard.html", {"request": request, "user": user})

@router.get("/kpi-overview")
def kpi_overview(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("kpi-overview.html", {"request": request, "user": user})

@router.get("/financial-performance")
def financial_performance(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("financial-performance.html", {"request": request, "user": user})

@router.get("/department-comparison")
def department_comparison(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("department-comparison.html", {"request": request, "user": user})

@router.get("/strategic-goals")
def strategic_goals(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("strategic-goals.html", {"request": request, "user": user})
