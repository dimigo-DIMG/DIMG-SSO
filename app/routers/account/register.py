from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_users import exceptions, schemas
import random

from app.core import current_user_optional, templates
from app.users import (
    UserManager,
    get_user_manager,
    User
)
from app.schemas import UserCreate, UserRead
from app.backends.statistics import update_statistics

register_router = APIRouter(prefix="/register", tags=["account"])

@register_router.get("/")
async def register(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")

    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse(
        "auth/signup.html",
        {
            "request": request,
            "failed": failed,
            "csrf_token": csrf_token,
            "location": "회원가입",
        },
    )


@register_router.post("/account/register")
async def register(
    request: Request,  # type: ignore
    user_manager: UserManager = Depends(get_user_manager),
):
    print("registering...")
    form = await request.form()

    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/register", status_code=303)
    request.session.pop("csrf_token")
    try:
        user_create = UserCreate(email=form.get("email"), password=form.get("password"))
        user = await user_manager.create(user_create, safe=True, request=request)
        await user_manager.request_verify(user)

    except exceptions.UserAlreadyExists:
        request.session["failed"] = 1
        return RedirectResponse("/account/register", status_code=303)
    except exceptions.InvalidPasswordException:
        request.session["failed"] = 3
        return RedirectResponse("/account/register", status_code=303)

    request.session["reg_success"] = 1
    res = schemas.model_validate(UserRead, user)
    response = RedirectResponse("/account/login", status_code=303)
    await update_statistics()
    return response