import datetime
import os
import uuid
from typing import Any, Coroutine, Optional

from fastapi import Depends, Form, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    CookieTransport
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.microsoft import MicrosoftGraphOAuth2

import app.mailer as mailer

from fastapi_users import exceptions, models

from app.db import User, get_async_session, get_user_db
from app.schemas import UserCreate
SECRET = os.getenv("MAIN_SECRET", "")
MAIN_HOST = os.getenv("MAIN_HOST", "")
IS_HTTPS = os.getenv("IS_HTTPS", "false").lower() == "true"
https_prefix = "https" if IS_HTTPS else "http"

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
)

microsoft_oauth_client = MicrosoftGraphOAuth2(
    os.getenv("MICROSOFT_OAUTH_CLIENT_ID", ""),
    os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", ""),
)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None) -> None:
        await mailer.send_email(user.email, "이메일 인증", f"이메일 인증을 완료하려면 다음 링크를 클릭하세요: {https_prefix}://{MAIN_HOST}/account/verify?token={token}")
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None) -> None:
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        await mailer.send_email(user.email, "비밀번호 초기화", f"비밀번호를 초기화하려면 다음 링크를 클릭하세요: {https_prefix}://{MAIN_HOST}/account/password-reset?token={token}")

    
    async def oauth_associate_callback(self: BaseUserManager[models.UOAP, models.ID], user: models.UOAP, oauth_name: str, access_token: str, account_id: str, account_email: str, expires_at: int | None = None, refresh_token: str | None = None, request: Request | None = None) -> models.UOAP:
        #check logined by request
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }
        if account_email.endswith("@dimigo.hs.kr") or account_email.endswith("@dimigoh.goe.go.kr"):
            print("dimigo user chk")
            await self.user_db.update(user, {"is_dimigo": True, "is_dimigo_updated": datetime.date.today()})
        else:
            raise HTTPException(status_code=403, detail="Only dimigo users can use this service")
        
        for existing_oauth_account in user.oauth_accounts:
            if (
                existing_oauth_account.account_email.endswith(account_email.split("@")[1]) 
            ):
                flag = True
                user = await self.user_db.update_oauth_account(
                    user, existing_oauth_account, oauth_account_dict
                )
        
        if not flag:
            await self.user_db.add_oauth_account(user, oauth_account_dict)
        
        return user
    

    async def oauth_callback(
        self: "BaseUserManager[models.UOAP, models.ID]",
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
    ) -> models.UOAP:
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }        
        try:
            user = await self.get_by_oauth_account(oauth_name, account_id)
        except exceptions.UserNotExists:
            raise HTTPException(status_code=403, detail="No user associated with this account")

        # Update oauth
        for existing_oauth_account in user.oauth_accounts:
            if (
                existing_oauth_account.account_id == account_id
                and existing_oauth_account.oauth_name == oauth_name
            ):
                user = await self.user_db.update_oauth_account(
                    user, existing_oauth_account, oauth_account_dict
                )
        
        return user

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)

import contextlib

async def init_user():
    get_async_session_ctx = contextlib.asynccontextmanager(get_async_session)
    get_user_db_ctx = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_ctx = contextlib.asynccontextmanager(get_user_manager)

    async with get_async_session_ctx() as session:
        async with get_user_db_ctx(session) as user_db:
            async with get_user_manager_ctx(user_db) as user_manager:
                admin_email = os.getenv("F_ADMIN_USER", "")
                admin_password = os.getenv("F_ADMIN_PASS", "")
                try:
                    await user_manager.get_by_email(admin_email)
                except exceptions.UserNotExists:
                    await user_manager.create(
                        UserCreate(
                            email=admin_email,
                            password=admin_password,
                            is_superuser=True,
                            is_verified=True
                        )
                    )
                    await mailer.send_email(admin_email, "관리자 계정 생성", f"관리자 계정이 정상적으로 생성되었습니다.")
                    print("Admin user created")
    

