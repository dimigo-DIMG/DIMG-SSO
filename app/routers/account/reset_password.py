from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users import exceptions, fastapi_users

from app.core import current_user_optional, templates
from app.users import (
    UserManager,
    get_user_manager,
    User,
)

import random

reset_password_router = APIRouter(prefix="/reset-password", tags=["account"])


@reset_password_router.get("/")
async def reset_password(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")

    token = request.query_params.get("token")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset password token",
        )
    return templates.TemplateResponse(
        "auth/reset_pw_next.html",
        {"request": request, "token": token, "csrf_token": csrf_token},
    )


@reset_password_router.post("/")
async def reset_password(
    request: Request,
    user: User = Depends(current_user_optional),
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/login", status_code=303)
    request.session.pop("csrf_token")

    password = form.get("password")
    token = form.get("token")
    if user:
        return RedirectResponse("/")
    token = request.query_params.get("token")
    try:
        await user_manager.reset_password(token, password, request)
    except (
        exceptions.InvalidResetPasswordToken,
        exceptions.UserNotExists,
        exceptions.UserInactive,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset password token",
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )
    return RedirectResponse("/account/login", status_code=303)
