from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_users import exceptions

from app.core import current_user_optional, templates
from app.users import (
    UserManager,
    get_user_manager,
    User,
)

import random

forgot_password_router = APIRouter(prefix="/forgot-password", tags=["account"])


@forgot_password_router.get("/")
async def password(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse(
        "auth/reset_pw.html",
        {"request": request, "failed": failed, "csrf_token": csrf_token, user: user},
    )


@forgot_password_router.post("/")
async def password(
    request: Request,  # type: ignore
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()

    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/forgot-password", status_code=303)
    request.session.pop("csrf_token")
    try:
        user = await user_manager.get_by_email(form.get("email"))
        await user_manager.forgot_password(user)
    except exceptions.UserNotExists:
        request.session["failed"] = 1
        return RedirectResponse("/account/forgot-password", status_code=303)
    return RedirectResponse("/account/login", status_code=303)
