from fastapi import APIRouter, Depends, Request

from app.users import User
from app.core import templates, current_user_admin
from app.routers.manage import (
    service,
    user
)

manage_router = APIRouter(prefix="/manage", tags=["manage"])

@manage_router.get("/")
async def manage(request: Request, user: User = Depends(current_user_admin)):
    return templates.TemplateResponse(
        "admin/index.html", {"request": request, "user": user}
    )

@manage_router.get("/dashboard")
async def manage_dashboard(request: Request, user: User = Depends(current_user_admin)):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

manage_router.include_router(service.service_router)
manage_router.include_router(user.user_router)