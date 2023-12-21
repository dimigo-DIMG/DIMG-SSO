from fastapi import APIRouter, Request

from app.core import templates
from app.routers.service import permission

service_router = APIRouter(prefix="/service", tags=["service"])

@service_router.get("/")
async def service_root(request: Request):
    return templates.TemplateResponse(
        "service/index.html", {"request": request, "location": "서비스"}
    )

service_router.include_router(permission.permission_router)