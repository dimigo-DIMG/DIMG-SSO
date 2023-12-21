from typing import Dict
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.core import current_active_user
from app.users import (
    auth_backend,
    User,
    SECRET,
    oauth_router,
    google_oauth_client,
    microsoft_oauth_client,
)

oauth_router = APIRouter(prefix="/oauth", tags=["account"])

@oauth_router.get("/l/{provider}")
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


@oauth_router.get("/c/{provider}")
async def oauth_connect(
    request: Request, provider: str, user: User = Depends(current_active_user)
):
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