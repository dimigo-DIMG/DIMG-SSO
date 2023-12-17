import datetime
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, status, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, schemas
from fastapi_users.router import oauth as oauth_router
from fastapi_users.authentication import JWTStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict, Optional, Tuple, Annotated

from sqlalchemy import select

from app.db import Service, ServiceConnection, User, create_db_and_tables, get_async_session, get_user_db
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

from app.backends.services import create_service, delete_service, generate_access_token, get_all_services, get_service_by_id, get_service_connection, update_service

app = FastAPI()

# session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

current_user_optional = fastapi_users.current_user(optional=True)
current_user_admin = fastapi_users.current_user(active=True, superuser=True)


@app.get("/")
async def root(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user, "location": "홈"}
    )


@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/terms")
async def terms(request: Request, user: User = Depends(current_user_optional)):
    return templates.TemplateResponse(
        "terms.html", {"request": request, "user": user, "location": "이용약관"}
    )


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
        # redirect tp get
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
        await user_manager.request_verify(user)

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
@app.get("account/verify")
async def verify(request: Request, user: User = Depends(current_user_optional), user_manager: UserManager = Depends(get_user_manager)):
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
    
    
@app.get("/account/forgot-password")
async def password(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    failed = request.session.get("failed")
    if failed:
        request.session.pop("failed")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse("auth/reset_pw.html", {"request": request, "failed": failed, "csrf_token": csrf_token})

@app.post("/account/forgot-password")
async def password(
    request: Request,  # type: ignore
    user_manager: UserManager = Depends(get_user_manager),
):
    form = await request.form()

    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/forgot-password", status_code=303)
    request.session.pop("csrf_token")
    try:
        user = await user_manager.get_by_email(form.get("email"))
        await user_manager.forgot_password(user)
    except exceptions.UserNotExists:
        request.session["failed"] = 1
        return RedirectResponse("/account/forgot-password", status_code=303)
    return RedirectResponse("/account/login", status_code=303)

@app.get("/account/reset-password")
async def reset_password(request: Request, user: User = Depends(current_user_optional)):
    if user:
        return RedirectResponse("/")
    
    token = request.query_params.get("token")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset password token",
        )
    return templates.TemplateResponse("auth/reset_pw_next.html", {"request": request, "token": token, "csrf_token": csrf_token})

@app.post("/account/reset-password")
async def reset_password(request: Request, user: User = Depends(current_user_optional), user_manager: UserManager = Depends(get_user_manager)):
    
    form = await request.form()
    if form.get("csrf_token") != request.session.get("csrf_token"):
        request.session["failed"] = 2
        # redirect tp get
        return RedirectResponse("/account/login", status_code=303)
    request.session.pop("csrf_token")
    
    password = form.get("password")
    token = form.get("token")
    if user:
        return RedirectResponse("/")
    token = request.query_params.get("token")
    try:
        await user_manager.reset_password(token, password, request)
    except (
        exceptions.InvalidResetPasswordToken,
        exceptions.UserNotExists,
        exceptions.UserInactive,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset password token",
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )
    return RedirectResponse("/account/login", status_code=303)



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
async def service_list(request: Request, user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    services: list[Service] = await get_all_services(db)
    print(services)
    return templates.TemplateResponse("admin/service.html", {"request": request, "user": user, "services": services})

@app.get("/manage/services/create")
async def service_create(request: Request, user: User = Depends(current_user_admin)):
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse("admin/add_service.html", {"request": request, "user": user, "csrf_token": csrf_token})

@app.post("/manage/services/create")
async def service_create(request: Request, logo: Optional[UploadFile] = File(None), user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    #save to static
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    if logo:
        random_name = "".join([random.choice("0123456789abcdef") for _ in range(32)])
        with open(f"static/icons/{random_name}.png", "wb") as f:
            f.write(await logo.read())
    generated_client_id = "".join([random.choice("0123456789abcdef") for _ in range(12)])

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
    print("is_official: " + form.get("is_official"))
    service = Service(
        client_id=generated_client_id,
        client_secret=generated_client_secret,
        name=form.get("name") or "Unnamed Service",
        description=form.get("description") or "No description",
        is_official=form.get("is_official") == "true",
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

@app.get("/manage/services/{client_id}")
async def service_edit(request: Request, client_id: str, user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    service: Service = await get_service_by_id(db, client_id)
    print(service)
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse("admin/edit_service.html", {"request": request, "user": user, "service": service, "csrf_token": csrf_token})

@app.post("/manage/services/{client_id}/delete")
async def service_delete(request: Request, client_id: str, user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    await delete_service(db, client_id)
    return Response(status_code=204)

@app.post("/manage/services/{client_id}/update")
async def service_update(request: Request, client_id: str, logo: Optional[UploadFile] = File(None), user: User = Depends(current_user_admin), db = Depends(get_async_session)):
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    service: Service = await get_service_by_id(db, client_id)
    if logo:
        random_name = "".join([random.choice("0123456789abcdef") for _ in range(32)])
        with open(f"static/icons/{random_name}.png", "wb") as f:
            f.write(await logo.read())
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
    
    service.name = form.get("name") or "Unnamed Service"
    service.description = form.get("description") or "No description"
    service.is_official = form.get("is_official") == "true"
    service.login_callback = form.get("login_callback")
    service.unregister_page = form.get("unregister_url")
    service.main_page = form.get("main_page")
    service.scopes = form.get("scopes")
    service.register_cooldown = form.get("register_cooldown")
    if logo:
        service.icon = f"/static/icons/{random_name}.png"

    await update_service(db, service)
    return Response(status_code=204)


app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/account",
    tags=["auth"],
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


# user settings page
@app.get("/account")
async def account_root(request: Request, user: User = Depends(current_user_optional)):
    for oauth_account in user.oauth_accounts:
        if oauth_account.provider == "google":
            google_mail = oauth_account.account_email
        elif oauth_account.provider == "microsoft":
            microsoft_mail = oauth_account.account_email
    return templates.TemplateResponse(
        "account/index.html", {"request": request, "user": user, google_mail: google_mail, microsoft_mail: microsoft_mail,"location": "설정"}
    )

@app.get("/api/sso/token/get")
async def get_token(request: Request, user: User = Depends(current_active_user), db = Depends(get_async_session)):
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
    generated_token = await generate_access_token(db, user.id, client_id, datetime.date.today() + datetime.timedelta(days=1))
    if not generated_token:
        raise HTTPException(status_code=500, detail="Failed to generate access token")
    
    # redirect to login_callback
    return RedirectResponse(f"{service.login_callback}?token={generated_token.token}&state={state}", status_code=303)

@app.get("/service/permission/{client_id}")
async def show_permission(request: Request, client_id: str, user: User = Depends(current_active_user), db = Depends(get_async_session)):
    service: Service = await get_service_by_id(db, client_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    csrf_token = "".join([random.choice("0123456789abcdef") for _ in range(32)])
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse("service/permission.html", {"request": request, "user": user, "service": service, "csrf_token": csrf_token})

@app.post("/service/permission/{client_id}/allow")
async def allow_permission(request: Request, client_id: str, user: User = Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    service: Service = await get_service_by_id(db, client_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    form = await request.form()
    if not form.get("csrf_token") or form.get("csrf_token") != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    request.session.pop("csrf_token")

    # check if serviceconnection exists
    service_connection = await get_service_connection(db, user.id, client_id)
    if service_connection:
        if service_connection.unregistered is None:
            raise HTTPException(status_code=403, detail="Service already connected")
        # chk cooldown
        elif service_connection.unregistered + datetime.timedelta(days=service.register_cooldown) > datetime.date.today():
            raise HTTPException(status_code=403, detail="Cooldown not expired")
        else:
            service_connection.unregistered = None
            service_connection.registered = datetime.date.today()
            await db.add(service_connection)
            await db.commit()
            await db.refresh(service_connection)
            return RedirectResponse(f"/api/sso/token/get?client_id={client_id}", status_code=303)        
    
    # cid : Connection ID ( unique identifier, primary key )
    # generate cid with random int without collision
    cid = random.randint(0, 1000000000)
    tg = await db.execute(select(ServiceConnection).where(ServiceConnection.cid == cid))
    if tg.scalar():
        cid = random.randint(0, 1000000000)

    # create service connection
    service_connection = ServiceConnection(
        cid=cid,
        user_id=user.id,
        service_id=client_id,
        registered=datetime.date.today()
    )
    db.add(service_connection)
    await db.commit()

    # redirect to api/sso/token/get
    return RedirectResponse(f"/api/sso/token/get?client_id={client_id}")


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await init_user()
