from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.users import User, current_active_user
from app.core import templates
from app.db import get_async_session
from app.db import Service, ServiceConnection
from app.backends.services import (
    get_service_by_id,
    get_service_connection,
)

import datetime
import random

permission_router = APIRouter(prefix="/permission", tags=["service"])


@permission_router.get("/{client_id}")
async def show_connect(
    request: Request,
    client_id: str,
    user: User = Depends(current_active_user),
    db=Depends(get_async_session),
):
    service: Service = await get_service_by_id(db, client_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse(
        "service/permission.html",
        {
            "request": request,
            "user": user,
            "service": service,
            "csrf_token": csrf_token,
        },
    )


@permission_router.post("/{client_id}/allow")
async def allow_permission(
    request: Request,
    client_id: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    service: Service = await get_service_by_id(db, client_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get(
        "csrf_token"
    ):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    # check if serviceconnection exists
    service_connection = await get_service_connection(db, user.id, client_id)
    if service_connection:
        if service_connection.unregistered is None:
            raise HTTPException(status_code=403, detail="Service already connected")
        # chk cooldown
        elif (
            service_connection.unregistered
            + datetime.timedelta(days=service.register_cooldown)
            > datetime.date.today()
        ):
            raise HTTPException(status_code=403, detail="Cooldown not expired")
        else:
            service_connection.unregistered = None
            service_connection.registered = datetime.date.today()
            await db.add(service_connection)
            await db.commit()
            await db.refresh(service_connection)
            return RedirectResponse(
                f"/api/sso/token/get?client_id={client_id}", status_code=303
            )

    # cid : Connection ID ( unique identifier, primary key )
    # generate cid with random int without collision
    cid = random.randint(0, 1000000000)
    tg = await db.execute(select(ServiceConnection).where(ServiceConnection.cid == cid))
    if tg.scalar():
        cid = random.randint(0, 1000000000)

    # create service connection
    service_connection = ServiceConnection(
        cid=cid, user_id=user.id, service_id=client_id, registered=datetime.date.today()
    )
    db.add(service_connection)
    await db.commit()

    # redirect to api/sso/token/get
    return RedirectResponse(f"/api/sso/token/get?client_id={client_id}", status_code=303)
