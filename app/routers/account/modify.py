from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions

from app.users import (
    current_active_user,
    User,
    UserManager,
    get_user_manager,
)
from app.core import templates, current_user_optional

import random
import datetime

modify_router = APIRouter(prefix="/modify", tags=["account"])


@modify_router.get("/{menu}")
async def account_profile(
    request: Request, menu, user: User = Depends(current_user_optional)
):
    google_mail = None
    microsoft_mail = None
    for oauth_account in user.oauth_accounts:
        if oauth_account.oauth_name == "google":
            google_mail = oauth_account.account_email
        elif oauth_account.oauth_name == "microsoft":
            microsoft_mail = oauth_account.account_email

    # chk menu is int
    if not menu.isdigit():
        raise HTTPException(status_code=404, detail="Page not found")

    menu = int(menu)
    if menu not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="Page not found")

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
            "menu": menu,
            "csrf_token": csrf_token,
            "error": error,
        },
    )


@modify_router.post("/profile")
async def account_profile(
    request: Request,
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    new_nick = form.get("nickname")
    new_birth = form.get("birthday")
    new_gender = form.get("gender")
    print(new_nick, new_birth, new_gender)

    update_dict = {}
    if new_nick:
        update_dict["nickname"] = new_nick
    if new_birth:
        update_dict["birthday"] = datetime.datetime.strptime(
            new_birth, "%Y-%m-%d"
        ).date()
    else:
        update_dict["birthday"] = None
    if new_gender:
        update_dict["gender"] = new_gender if new_gender != "no" else None

    await user_manager.user_db.update(user, update_dict)
    return RedirectResponse("/account", status_code=303)


@modify_router.post("/email")
async def account_email(
    request: Request,
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        return templates.TemplateResponse(
            "account/index.html",
            {
                "request": request,
                "user": user,
                "result": 2,
                "location": "설정",
                "menu": 2,
            },
        )
    request.session.pop("csrf_token")

    new_email = form.get("email")
    pw_auth = form.get("password")

    if not new_email or not pw_auth:
        request.session["error"] = "all"
        return RedirectResponse("/account/modify/2", status_code=303)
    try:
        credentials = OAuth2PasswordRequestForm(
            username=user.email, password=pw_auth, scope=""
        )
        if not await user_manager.authenticate(credentials):
            raise Exception("Invalid password")

    except Exception as e:
        request.session["error"] = "password"
        return RedirectResponse("/account/modify/2", status_code=303)

    changed_info = {"email": new_email, "is_verified": False}
    # check if email exists
    try:
        await user_manager.get_by_email(new_email)
        print("email exists")
        request.session["error"] = "email"
        return RedirectResponse("/account/modify/2", status_code=303)

    except exceptions.UserNotExists:
        await user_manager.user_db.update(user, changed_info)
        await user_manager.request_verify(user)
        return templates.TemplateResponse(
            "account/index.html",
            {
                "request": request,
                "user": user,
                "result": 1,
                "location": "설정",
                "menu": 2,
            },
        )


@modify_router.post("/password")
async def account_password(
    request: Request,
    user: User = Depends(current_active_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        return templates.TemplateResponse(
            "account/index.html",
            {
                "request": request,
                "user": user,
                "result": 3,
                "location": "설정",
                "menu": 3,
            },
        )
    request.session.pop("csrf_token")

    pw_auth = form.get("old-password")
    new_pw = form.get("new-password1")
    new_pw2 = form.get("new-password2")

    if not pw_auth or not new_pw or not new_pw2:
        request.session["error"] = "all"
        return RedirectResponse("/account/modify/3", status_code=303)

    try:
        credentials = OAuth2PasswordRequestForm(
            username=user.email, password=pw_auth, scope=""
        )
        if not await user_manager.authenticate(credentials):
            raise Exception("Invalid password")
    except Exception as e:
        request.session["error"] = "password"
        return RedirectResponse("/account/modify/3", status_code=303)

    if new_pw != new_pw2:
        request.session["error"] = "different"
        return RedirectResponse("/account/modify/3", status_code=303)

    try:
        new_user_data = {"hashed_password": user_manager.password_helper.hash(new_pw)}
        await user_manager.user_db.update(user, new_user_data)
        return templates.TemplateResponse(
            "account/index.html",
            {
                "request": request,
                "user": user,
                "result": 1,
                "location": "설정",
                "menu": 3,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "account/index.html",
            {
                "request": request,
                "user": user,
                "result": 3,
                "location": "설정",
                "menu": 3,
            },
        )
