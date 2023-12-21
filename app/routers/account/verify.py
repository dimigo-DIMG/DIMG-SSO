from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users import exceptions

from app.core import current_user_optional
from app.users import (
    UserManager,
    get_user_manager,
    User,
)

verify_router = APIRouter(prefix="/verify", tags=["account"])

@verify_router.get("/account/verify")
async def verify(
    request: Request,
    user: User = Depends(current_user_optional),
    user_manager: UserManager = Depends(get_user_manager),
):
    if user:
        return RedirectResponse("/")
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )
    try:
        user = await user_manager.verify(token, request)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        request.session["failed"] = 110
    except exceptions.UserAlreadyVerified:
        request.session["failed"] = 100
    return RedirectResponse("/account/login", status_code=303)