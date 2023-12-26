import random
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core import templates, current_user_optional
from app.users import User, current_active_user

from app.routers.account import (
    login,
    logout,
    register,
    forgot_password,
    reset_password,
    verify,
    oauth,
    modify,
    cancel
)

account_router = APIRouter(prefix="/account", tags=["account"])

# user settings page
@account_router.get("")
async def account_root(request: Request, user: User = Depends(current_active_user)):
    google_mail = None
    microsoft_mail = None
    for oauth_account in user.oauth_accounts:
        if oauth_account.provider == "google":
            google_mail = oauth_account.account_email
        elif oauth_account.provider == "microsoft":
            microsoft_mail = oauth_account.account_email

    return templates.TemplateResponse(
        "account/index.html",
        {
            "request": request,
            "user": user,
            "google_mail": google_mail,
            "microsoft_mail": microsoft_mail,
            "location": "설정",
            "menu": 0,
        },
    )

account_router.include_router(login.login_router)
account_router.include_router(logout.logout_router)
account_router.include_router(register.register_router)
account_router.include_router(forgot_password.forgot_password_router)
account_router.include_router(reset_password.reset_password_router)
account_router.include_router(verify.verify_router)
account_router.include_router(oauth.oauth_router)
account_router.include_router(modify.modify_router)
account_router.include_router(cancel.cancel_router)