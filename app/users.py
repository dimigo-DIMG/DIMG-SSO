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

from app.db import User, get_user_db

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
        await mailer.send_email(user.email, "비밀번호 초기화", f"비밀번호를 초기화하려면 다음 링크를 클릭하세요: {https_prefix}://{MAIN_HOST}/account/reset?token={token}")

    
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
        """
        Customized OAuth Handler
        When logined user request oauth callback, add oauth account to user
        When logouted user request oauth callback, 
        1. If user with same email exists, add oauth account to user
        2. If user with same email not exists, raise UserNotExists

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        :param is_verified_by_default: If True, the `is_verified` flag will be
        set to `True` on newly created user. Make sure the OAuth Provider you're
        using does verify the email address before enabling this flag.
        Defaults to False.
        :return: A user.
        """
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
            #check logined by request
            strategy: JWTStrategy = get_jwt_strategy()
            token = request.cookies.get("fastapiusersauth")
            user: User = await strategy.read_token(token, self)

            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_email.endswith(account_email.split("@")[1]) 
                ):
                    raise exceptions.AlreadyExists()
            if account_email.endswith("@dimigo.hs.kr") or account_email.endswith("@dimigoh.goe.go.kr"):
                print("dimigo user")
                #user.is_dimigo = True
                #user.is_dimigo_updated = datetime.date.today()

            print(user)
            if user is None:
                raise exceptions.UserNotExists()
            await self.user_db.add_oauth_account(user, oauth_account_dict)
                
        else:
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