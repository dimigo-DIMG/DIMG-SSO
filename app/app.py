from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.users import fastapi_users
from app.db import create_db_and_tables
from app.users import SECRET, init_user
from app.core import templates
from app.backends.statistics import update_statistics
from app import routers

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()

# session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routers.root_router)

'''
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": str(exc.detail), "code": exc.status_code},
    )

# handle 404
@app.exception_handler(404)
async def http_exception_handler(request, exc):
    if str(exc.detail) == "Not Found":
        msg = "페이지를 찾을 수 없어요."
    else:
        msg = str(exc.detail)
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": msg, "code": 404}
    )


# handle internal server error
@app.exception_handler(500)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "서버 내부 오류가 발생했어요. 관리자에게 문의해주세요.", "code": 500},
    )

'''
@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await init_user()
    await update_statistics()


scheduler = AsyncIOScheduler()
# 1시간마다 통계 업데이트
scheduler.add_job(update_statistics, "interval", hours=1)
scheduler.start()
