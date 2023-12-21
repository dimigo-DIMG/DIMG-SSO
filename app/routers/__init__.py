from fastapi import APIRouter, Depends, Request

from app.users import fastapi_users
from app.core import templates, current_user_optional
from app.db import get_async_session
from app.users import User
from app.backends.services import get_all_services

from app.routers import (
    account,
    manage,
    service,
    api
)



root_router = APIRouter(tags=["root"])

@root_router.get("/")
async def root(
    request: Request,
    user: User = Depends(current_user_optional),
    db=Depends(get_async_session),
):
    o_services, u_services = await get_all_services(db, True)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "location": "홈",
            "o_services": o_services,
            "u_services": u_services,
        },
    )


@root_router.get("/contact")
async def contact(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse("contact.html", {"request": request})


@root_router.get("/terms")
async def terms(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse(
        "terms.html", {"request": request, "user": user, "location": "이용약관"}
    )

root_router.include_router(account.account_router)
root_router.include_router(manage.manage_router)
root_router.include_router(service.service_router)
root_router.include_router(api.api_router)