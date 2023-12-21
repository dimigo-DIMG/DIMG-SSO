import random
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core import current_user_optional, templates
from app.users import (
    UserManager,
    get_user_manager,
    auth_backend,
    User,
    JWTStrategy
)
from app.db import get_async_session
from app.backends.statistics import add_failed_login_count, add_login_count

login_router = APIRouter(prefix="/login", tags=["account"])

@login_router.get("/")
async def login(request: Request, user: User = Depends(current_user_optional)):
    redirect_uri = request.query_params.get("next")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")

    reg_success = request.session.get("reg_success")
    if reg_success:
        request.session.pop("reg_success")

    # random string
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    if redirect_uri:
        if not redirect_uri.startswith("/"):
            redirect_uri = None
        request.session["next"] = redirect_uri
    else:
        if request.session.get("next"):
            request.session.pop("next")
    if user:
        return RedirectResponse(redirect_uri or "/")

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "failed": failed,
            "reg_success": reg_success,
            "location": "로그인",
        },
    )


@login_router.post("/")
async def login(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    strategy: JWTStrategy = Depends(auth_backend.get_strategy),
    db=Depends(get_async_session),
):
    # request form
    form = await request.form()
    # check csrf token
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        await add_failed_login_count(db)
        return RedirectResponse("/account/login", status_code=303)

    next_url = request.session.get("next")

    if not form.get("email") or not form.get("password"):
        request.session["failed"] = 1
        await add_failed_login_count(db)
        return RedirectResponse("/account/login", status_code=303)

    try:
        credentials = OAuth2PasswordRequestForm(
            username=form.get("email"), password=form.get("password"), scope=""
        )
        user = await user_manager.authenticate(credentials)
    except Exception as e:
        request.session["failed"] = 1
        await add_failed_login_count(db)
        return RedirectResponse("/account/login", status_code=303)

    if user is None or not user.is_active:
        request.session["failed"] = 1
        await add_failed_login_count(db)
        return RedirectResponse("/account/login", status_code=303)

    response = await auth_backend.login(strategy, user)
    if next_url:
        request.session.pop("next")
        response.headers["location"] = next_url
        response.status_code = 303
    else:
        response.headers["location"] = "/"
        response.status_code = 303
    await user_manager.on_after_login(user, request, response)
    await add_login_count(db)
    return response