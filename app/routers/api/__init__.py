from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core import current_user_admin
from app.users import User, current_active_user
from app.db import Service, ServiceConnection, get_async_session
from app.backends.services import (
    generate_access_token,
    get_all_services,
    get_service_by_id,
    get_service_connection,
)
from app.backends.statistics import get_all_statistics

import datetime

api_router = APIRouter(prefix="/api", tags=["api"])

@api_router.get("/sso/token/get")
async def get_token(
    request: Request,
    user: User = Depends(current_active_user),
    db=Depends(get_async_session),
):
    client_id = request.query_params.get("client_id")
    state = request.query_params.get("state") or request.session.get("state")
    if request.session.get("state"):
        request.session.pop("state")

    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    if not state:
        raise HTTPException(status_code=400, detail="state is required")

    # check if service exists
    service: Service = await get_service_by_id(db, client_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # check if serviceconnection exists
    service_connection = await get_service_connection(db, user.id, client_id)
    if not service_connection:
        # redirect to permission page with state
        request.session["state"] = state
        return RedirectResponse(f"/service/permission/{client_id}", status_code=303)

    if service_connection.unregistered:
        # redirect to api/sso/token/get
        return RedirectResponse(f"/service/permission/{client_id}", status_code=303)

    # check if token exists
    generated_token = await generate_access_token(
        db, user.id, client_id, datetime.date.today() + datetime.timedelta(days=1)
    )
    if not generated_token:
        raise HTTPException(status_code=500, detail="Failed to generate access token")

    # redirect to login_callback
    return RedirectResponse(
        f"{service.login_callback}?token={generated_token.token}&state={state}",
        status_code=303,
    )


@api_router.get("/dashboard")
async def api_dashboard(
    db=Depends(get_async_session), user=Depends(current_user_admin)
):
    statistics = await get_all_statistics(db)
    return statistics


@api_router.get("/services")
async def api_service_list(
    request: Request,
    db=Depends(get_async_session),
    user: User=Depends(current_active_user)
):
    service_connections: list[ServiceConnection] = user.service_connections
    services_json = []

    for service_connection in service_connections:
        service = await get_service_by_id(db, service_connection.service_id)
        joined: datetime.date = service_connection.registered


        services_json.append(
            {
                "client_id": service.client_id,
                "name": service.name,
                "description": service.description,
                "is_official": service.is_official,
                "icon": service.icon_url,
                "unregister_page": service.unregister_page,
                "main_page": service.main_page,
                "scopes": service.scopes,
                "register_cooldown": service.register_cooldown,
                "join_date": joined.strftime("%Y. %m. %d"),
            }
        )
    return services_json

