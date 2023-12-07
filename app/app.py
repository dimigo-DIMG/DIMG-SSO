from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.router import oauth as oauth_router
from fastapi_users.authentication import JWTStrategy

from users import get_user_manager, UserManager
from typing import Dict

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import (
    SECRET,
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
    microsoft_oauth_client,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import random

app = FastAPI()

#session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

current_user_optional = fastapi_users.current_user(optional=True)

@app.get("/")
async def root(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/account/login")
async def login(request: Request, user: User = Depends(current_user_optional)):
    redirect_uri = request.query_params.get("next")
    failed = request.session.pop("failed")

    #random string
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token


    if redirect_uri:
        if not redirect_uri.startswith("/"):
            redirect_uri = None
        request.session["next"] = redirect_uri
    if user:
        return RedirectResponse(redirect_uri or "/")
    
    print(request.session.get("next"))
    return templates.TemplateResponse("auth/login.html", {"request": request, "csrf_token": csrf_token , "failed": failed})

@app.post("/account/login")
async def login(request: Request, credentials: OAuth2PasswordRequestForm = Depends(), user_manager: UserManager = Depends(get_user_manager), strategy: JWTStrategy = Depends(auth_backend.get_strategy) ):
    # request form
    form = await request.form()
    # check csrf token
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        return RedirectResponse("/account/login")
    
    
    next_url = request.session.get("next")
    if next_url:
        request.session.pop("next")
        response.headers["location"] = next_url
        response.status_code = 302

    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        request.session["failed"] = 1
        return RedirectResponse("/account/login")
    
    response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, response)
    return response

@app.get("/account/register")
async def register(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@app.get("/account/oauth/r/{provider}")
async def oauth_login(request: Request, provider: str):
    callback_route = f"oauth:{provider}.{auth_backend.name}.callback"
    redirect_uri = request.url_for(callback_route)
    print(redirect_uri)

    state_data: Dict[str, str] = {}
    state = oauth_router.generate_state_token(state_data, SECRET)

    if provider == "google":
        url = await google_oauth_client.get_authorization_url(redirect_uri, state)
    elif provider == "microsoft":
        url = await microsoft_oauth_client.get_authorization_url(redirect_uri, state)
    else:
        raise Exception("Invalid provider")

    # redirect to oauth provider
    return RedirectResponse(url)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/account", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/account",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/account",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/account",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/account/oauth/google",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(microsoft_oauth_client, auth_backend, SECRET),
    prefix="/account/oauth/microsoft",
    tags=["auth"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
