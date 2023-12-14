from fastapi import Depends, FastAPI, HTTPException, Request, Response, status, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, schemas
from fastapi_users.router import oauth as oauth_router
from fastapi_users.authentication import JWTStrategy

from typing import Dict, Tuple, Annotated

from app.db import Service, User, create_db_and_tables, get_async_session, get_user_db
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import (
    SECRET,
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
    microsoft_oauth_client,
    get_user_manager,
    UserManager,
    init_user
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import random

from app.backends.services import create_service, get_all_services

app = FastAPI()

# session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

current_user_optional = fastapi_users.current_user(optional=True)
current_user_admin = fastapi_users.current_user(active=True, superuser=True)


@app.get("/")
async def root(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/terms")
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/account/login")
async def login(request: Request, user: User = Depends(current_user_optional)):
    redirect_uri = request.query_params.get("next")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")

    reg_success = request.session.get("reg_success")
    if reg_success:
        request.session.pop("reg_success")

    # random string
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    if redirect_uri:
        if not redirect_uri.startswith("/"):
            redirect_uri = None
        request.session["next"] = redirect_uri
    else:
        if request.session.get("next"):
            request.session.pop("next")
    if user:
        return RedirectResponse(redirect_uri or "/")

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "failed": failed,
            "reg_success": reg_success,
        },
    )


@app.post("/account/login")
async def login(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    strategy: JWTStrategy = Depends(auth_backend.get_strategy),
):
    # request form
    form = await request.form()
    # check csrf token
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        #redirect tp get
        return RedirectResponse("/account/login", status_code=303)

    next_url = request.session.get("next")

    if not form.get("email") or not form.get("password"):
        request.session["failed"] = 1
        return RedirectResponse("/account/login", status_code=303)

    try:
        credentials = OAuth2PasswordRequestForm(
            username=form.get("email"), password=form.get("password"), scope=""
        )
        print(await user_manager.get_by_email(credentials.username))
        user = await user_manager.authenticate(credentials)
    except Exception as e:
        request.session["failed"] = 1
        return RedirectResponse("/account/login", status_code=303)

    if user is None or not user.is_active:
        print("user is none")
        request.session["failed"] = 1
        return RedirectResponse("/account/login", status_code=303)

    response = await auth_backend.login(strategy, user)
    if next_url:
        request.session.pop("next")
        response.headers["location"] = next_url
        response.status_code = 303
    else:
        response.headers["location"] = "/"
        response.status_code = 303
    await user_manager.on_after_login(user, request, response)
    return response


@app.get("/account/logout")
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


@app.get("/account/register")
async def register(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")

    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse(
        "auth/signup.html",
        {"request": request, "failed": failed, "csrf_token": csrf_token},
    )


@app.post("/account/register")
async def register(
    request: Request,  # type: ignore
    user_manager: UserManager = Depends(get_user_manager),
):
    print("registering...")
    form = await request.form()

    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/register", status_code=303)
    request.session.pop("csrf_token")
    try:
        user_create = UserCreate(email=form.get("email"), password=form.get("password"))
        user = await user_manager.create(user_create, safe=True, request=request)
        user_manager.request_verify(user)

    except exceptions.UserAlreadyExists:
        request.session["failed"] = 1
        return RedirectResponse("/account/register", status_code=303)
    except exceptions.InvalidPasswordException:
        request.session["failed"] = 3
        return RedirectResponse("/account/register", status_code=303)

    request.session["reg_success"] = 1
    # return RedirectResponse("/account/login", status_code=303)
    res = schemas.model_validate(UserRead, user)
    response = RedirectResponse("/account/login", status_code=303)

    return response
    
@app.get("/account/password")
async def password(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("auth/reset_pw.html", {"request": request})

@app.get("/account/oauth/l/{provider}")
async def oauth_login(request: Request, provider: str):
    callback_route = f"oauth:{provider}.{auth_backend.name}.callback"
    redirect_uri = request.url_for(callback_route)

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

@app.get("/account/oauth/c/{provider}")
async def oauth_connect(request: Request, provider: str, user: User = Depends(current_active_user)):
    callback_route = f"oauth-associate:{provider}.callback"
    redirect_uri = request.url_for(callback_route)

    state_data: Dict[str, str] = {"sub": str(user.id)}
    state = oauth_router.generate_state_token(state_data, SECRET)

    if provider == "google":
        url = await google_oauth_client.get_authorization_url(redirect_uri, state)
    elif provider == "microsoft":
        url = await microsoft_oauth_client.get_authorization_url(redirect_uri, state)
    else:
        raise Exception("Invalid provider")

    # redirect to oauth provider
    return RedirectResponse(url)

@app.get("/manage")
async def manage(request: Request, user: User = Depends(current_user_admin)):
    return templates.TemplateResponse("admin/index.html", {"request": request, "user": user})

@app.get("/manage/services")
async def manage_service(request: Request, user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    services: list[Service] = await get_all_services(db)
    print(services)
    return templates.TemplateResponse("admin/service.html", {"request": request, "user": user, "services": services})

@app.get("/manage/services/create")
async def manage_service(request: Request, user: User = Depends(current_user_admin)):
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse("admin/add_service.html", {"request": request, "user": user, "csrf_token": csrf_token})

@app.post("/manage/services/create")
async def manage_service(request: Request, logo: Annotated[UploadFile, File()], user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    #save to static
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    if logo:
        random_name = "".join([random.choice("0123456789abcdef") for _ in range(32)])
        with open(f"static/icons/{random_name}.png", "wb") as f:
            f.write(await logo.read())
    generated_client_id = "".join([random.choice("0123456789abcdef") for _ in range(6)])

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
    
    #more random include _ and . and - and ! + A-Z + a-z
    generated_client_secret = "".join([random.choice("0123456789_-.!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for _ in range(32)])
    service = Service(
        client_id=generated_client_id,
        client_secret=generated_client_secret,
        name=form.get("name") or "Unnamed Service",
        description=form.get("description") or "No description",
        is_official=form.get("is_official") == "on",
        icon=f"/static/icons/{random_name}.png" if logo else None,
        login_callback=form.get("login_callback"),
        unregister_page=form.get("unregister_url") ,
        main_page=form.get("main_page"),
        scopes=form.get("scopes"),
        register_cooldown=form.get("register_cooldown"),
    )
    
    await create_service(db, service)
    responseJson = {"client_id": generated_client_id, "client_secret": generated_client_secret}
    
    print(responseJson)
    request.session.pop("csrf_token")
    return responseJson

    



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
    prefix="/account/oauth/google/login",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, SECRET),
    prefix="/account/oauth/google/connect",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(microsoft_oauth_client, auth_backend, SECRET),
    prefix="/account/oauth/microsoft/login",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_associate_router(microsoft_oauth_client, UserRead, SECRET),
    prefix="/account/oauth/microsoft/connect",
    tags=["auth"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await init_user()
