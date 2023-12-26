# /manage/user
import random
from fastapi import APIRouter, Depends, HTTPException, Request

from app.users import User, UserManager, get_user_manager
from app.core import templates, current_user_admin

user_router = APIRouter(prefix="/user", tags=["manage"])

@user_router.get("")
async def manage_user_root(request: Request, user: User = Depends(current_user_admin)):
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse("admin/user.html", {"request": request, "csrf_token": csrf_token})


@user_router.get("/{user_id}")
async def manage_user_detail(
    request: Request, user: User = Depends(current_user_admin)
):
    return templates.TemplateResponse("admin/user_detail.html", {"request": request})

@user_router.post("/{user_id}/delete")
async def manage_user_delete(
    request: Request, user: User = Depends(current_user_admin), user_manager: UserManager = Depends(get_user_manager)
):
    form = await request.form()
    csrf_token = form.get("csrf_token")
    if csrf_token != request.session["csrf_token"]:
        print (csrf_token, request.session["csrf_token"])
        return {"status": "err_csrftoken"}
    request.session.pop("csrf_token")

    email = form.get("email")
    if email is None:
        return {"status": "err_email"}
    if email == user.email:
        return {"status": "err_self"}
    del_user = await user_manager.get_by_email(email)
    await user_manager.delete(del_user)

    return {"status": "ok"}
    
    
    
