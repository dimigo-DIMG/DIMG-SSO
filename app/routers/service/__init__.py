from fastapi import APIRouter, Request, Depends

from app.core import templates
from app.routers.service import permission
from app.users import User, current_active_user

service_router = APIRouter(prefix="/service", tags=["service"])

@service_router.get("")
async def service_root(request: Request, user=Depends(current_active_user)):
    return templates.TemplateResponse(
        "service/index.html", {"request": request, "location": "서비스", "user": user}
    )

service_router.include_router(permission.permission_router)