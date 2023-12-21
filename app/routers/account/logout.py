from typing import Tuple
from fastapi import APIRouter, Depends
from fastapi_users import fastapi_users

from app.users import (
    auth_backend,
    User,
    JWTStrategy
)

logout_router = APIRouter(prefix="/logout", tags=["account"])

@logout_router.get("/")
async def logout(
    user_token: Tuple[User, str] = Depends(
        fastapi_users.authenticator.current_user_token()
    ),
    strategy: JWTStrategy = Depends(auth_backend.get_strategy),
):
    user, token = user_token
    response = await auth_backend.logout(strategy, user, token)
    response.headers["location"] = "/"
    response.status_code = 303
    return response