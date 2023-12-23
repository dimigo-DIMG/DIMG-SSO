
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
from sqlalchemy.future import select

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
        # redirect to connect page with state
        request.session["state"] = state
        return RedirectResponse(f"/service/connect/{client_id}", status_code=303)

    if service_connection.unregistered:
        # redirect to api/sso/token/get
        return RedirectResponse(f"/service/connect/{client_id}", status_code=303)

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

@api_router.get("/manage/users")
async def api_manager_users(
    db=Depends(get_async_session), user=Depends(current_user_admin)
):
    '''
    {
        "email": "string",
        "nickname": "string",
        "tag": "enrol" | "gred" | "guest",
        "join_date": "string"
    }
    '''

    users = await db.execute(select(User))
    users_json = []
    users: list[User] = users.unique().scalars().all()


    for user in users:
        tag = "guest"
        if user.is_dimigo:
            tag = "enrol"
            if user.is_dimigo_updated < datetime.date.today() - datetime.timedelta(days=365):
                tag = "grad"
        users_json.append(
            {
                "email": user.email,
                "name": user.nickname,
                "tag": tag,
                "join_date": user.sign_up_date.strftime("%Y. %m. %d") if user.sign_up_date else "알 수 없음",
            }
        )
    
    return users_json

@api_router.get("/manage/users/{user_id}")
async def api_manager_user(
    user_id: str,
    db=Depends(get_async_session), user=Depends(current_user_admin)
):
    user = await db.execute(select(User).filter(User.email == user_id))
    user = user.unique().scalar()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tag = "guest"
    if user.is_dimigo:
        tag = "enrol"
        if user.is_dimigo_updated < datetime.date.today() - datetime.timedelta(days=365):
            tag = "grad"

    return {
        "email": user.email,
        "name": user.nickname,
        "tag": tag,
        "gender": user.gender,
        "join_date": user.sign_up_date.strftime("%Y. %m. %d") if user.sign_up_date else "알 수 없음",
    }

@api_router.get("/manage/users/{user_id}/services")
async def api_manager_user_services(
    user_id: str,
    db=Depends(get_async_session), user=Depends(current_user_admin)
):
    user = await db.execute(select(User).filter(User.email == user_id))
    user = user.unique().scalar()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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