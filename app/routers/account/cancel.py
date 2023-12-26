from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi_users import exceptions

from app.users import (
    current_active_user,
    User,
    UserManager,
    get_user_manager,
)
from app.core import templates, current_user_optional

import random

cancel_router = APIRouter(prefix="/cancel", tags=["account"])

@cancel_router.get("/")
async def account_root(
    request: Request, user: User = Depends(current_user_optional)
):
    google_mail = None
    microsoft_mail = None
    for oauth_account in user.oauth_accounts:
        if oauth_account.provider == "google":
            google_mail = oauth_account.account_email
        elif oauth_account.provider == "microsoft":
            microsoft_mail = oauth_account.account_email

    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    error = None
    if request.session.get("error"):
        error = request.session["error"]
        request.session.pop("error")

    return templates.TemplateResponse(
        "account/index.html",
        {
            "request": request,
            "user": user,
            "google_mail": google_mail,
            "microsoft_mail": microsoft_mail,
            "location": "설정",
            "menu": "cancel",
            "csrf_token": csrf_token,
            "error": error,
        },
    )

@cancel_router.post("/")
async def account_root(
    request: Request, user: User = Depends(current_active_user), user_manager: UserManager = Depends(get_user_manager)
):
    form = await request.form()
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["error"] = 2
        return RedirectResponse("/account/cancel/cancel", status_code=303)
    request.session.pop("csrf_token")

    try:
        await user_manager.delete(user)
    except exceptions.UserNotExists:
        request.session["error"] = 1
        return RedirectResponse("/account/cancel/cancel", status_code=303)
    return RedirectResponse("/account/login", status_code=303)