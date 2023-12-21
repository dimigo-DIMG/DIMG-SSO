from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File

from app.core import templates, current_user_admin
from app.db import get_async_session, Service
from app.users import User
from app.backends.statistics import update_statistics
from app.backends.services import (
    get_all_services,
    get_service_by_id,
    update_service,
    delete_service,
    create_service,
)

import random

service_router = APIRouter(prefix="/service", tags=["manage"])

@service_router.get("/create")
async def service_create(request: Request, user: User = Depends(current_user_admin)):
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse(
        "admin/add_service.html",
        {"request": request, "user": user, "csrf_token": csrf_token},
    )

@service_router.post("/create")
async def service_create(
    request: Request,
    logo: Optional[UploadFile] = File(None),
    user: User = Depends(current_user_admin),
    db=Depends(get_async_session),
):
    # save to static
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    if logo:
        random_name = "".join([random.choice("0123456789abcdef") for _ in range(32)])
        with open(f"static/icons/{random_name}.png", "wb") as f:
            f.write(await logo.read())
    generated_client_id = "".join(
        [random.choice("0123456789abcdef") for _ in range(12)]
    )

    if not form.get("login_callback"):
        raise HTTPException(status_code=400, detail="Login callback is required")
    if not form.get("unregister_url"):
        raise HTTPException(status_code=400, detail="Unregister callback is required")
    if not form.get("main_page"):
        raise HTTPException(status_code=400, detail="Main page is required")
    if not form.get("scopes"):
        raise HTTPException(status_code=400, detail="Scopes is required")
    if not form.get("register_cooldown"):
        raise HTTPException(status_code=400, detail="Register cooldown is required")

    # more random include _ and . and - and ! + A-Z + a-z
    generated_client_secret = "".join(
        [
            random.choice(
                "0123456789_-.!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            )
            for _ in range(32)
        ]
    )
    print("is_official: " + form.get("is_official"))
    service = Service(
        client_id=generated_client_id,
        client_secret=generated_client_secret,
        name=form.get("name") or "Unnamed Service",
        description=form.get("description") or "No description",
        is_official=form.get("is_official") == "true",
        icon=f"/static/icons/{random_name}.png" if logo else None,
        login_callback=form.get("login_callback"),
        unregister_page=form.get("unregister_url"),
        main_page=form.get("main_page"),
        scopes=form.get("scopes"),
        register_cooldown=form.get("register_cooldown"),
    )

    await create_service(db, service)
    responseJson = {
        "client_id": generated_client_id,
        "client_secret": generated_client_secret,
    }

    print(responseJson)
    request.session.pop("csrf_token")
    await update_statistics()
    return responseJson

@service_router.get("/")
async def service_list(
    request: Request,
    user: User = Depends(current_user_admin),
    db=Depends(get_async_session),
):
    services: list[Service] = await get_all_services(db)
    print(services)
    return templates.TemplateResponse(
        "admin/service.html", {"request": request, "user": user, "services": services}
    )


@service_router.get("/{client_id}")
async def service_edit(
    request: Request,
    client_id: str,
    user: User = Depends(current_user_admin),
    db=Depends(get_async_session),
):
    service: Service = await get_service_by_id(db, client_id)
    print(service)
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse(
        "admin/edit_service.html",
        {
            "request": request,
            "user": user,
            "service": service,
            "csrf_token": csrf_token,
        },
    )

@service_router.post("/{client_id}/delete")
async def service_delete(
    request: Request,
    client_id: str,
    user: User = Depends(current_user_admin),
    db=Depends(get_async_session),
):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    await delete_service(db, client_id)
    await update_statistics()
    return Response(status_code=204)


@service_router.post("/{client_id}/update")
async def service_update(
    request: Request,
    client_id: str,
    logo: Optional[UploadFile] = File(None),
    user: User = Depends(current_user_admin),
    db=Depends(get_async_session),
):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    service: Service = await get_service_by_id(db, client_id)
    if logo:
        random_name = "".join([random.choice("0123456789abcdef") for _ in range(32)])
        with open(f"static/icons/{random_name}.png", "wb") as f:
            f.write(await logo.read())
    if not form.get("login_callback"):
        raise HTTPException(status_code=400, detail="Login callback is required")
    if not form.get("unregister_url"):
        raise HTTPException(status_code=400, detail="Unregister callback is required")
    if not form.get("main_page"):
        raise HTTPException(status_code=400, detail="Main page is required")
    if not form.get("scopes"):
        raise HTTPException(status_code=400, detail="Scopes is required")
    if not form.get("register_cooldown"):
        raise HTTPException(status_code=400, detail="Register cooldown is required")

    service.name = form.get("name") or "Unnamed Service"
    service.description = form.get("description") or "No description"
    service.is_official = form.get("is_official") == "true"
    service.login_callback = form.get("login_callback")
    service.unregister_page = form.get("unregister_url")
    service.main_page = form.get("main_page")
    service.scopes = form.get("scopes")
    service.register_cooldown = form.get("register_cooldown")
    if logo:
        service.icon = f"/static/icons/{random_name}.png"

    await update_service(db, service)
    return Response(status_code=204)

