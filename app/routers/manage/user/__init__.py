# /manage/user
from fastapi import APIRouter, Depends, Request

from app.users import User
from app.core import templates, current_user_admin

user_router = APIRouter(prefix="/user", tags=["manage"])

@user_router.get("")
async def manage_user_root(request: Request, user: User = Depends(current_user_admin)):
    return templates.TemplateResponse("admin/user.html", {"request": request})


@user_router.get("/{user_id}")
async def manage_user_detail(
    request: Request, user: User = Depends(current_user_admin)
):
    return templates.TemplateResponse("admin/user_detail.html", {"request": request})
