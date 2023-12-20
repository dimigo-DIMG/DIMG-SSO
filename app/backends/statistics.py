import contextlib
import datetime
import uuid
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import Service, Statistic, User, get_async_session, get_user_db
from fastapi import HTTPException


async def get_statistics(db):
   return Statistic(
          date=datetime.date.today(),
          user_count= (await db.execute(select(func.count()).select_from(select(User).subquery()))).scalar_one(),
          enrolled_user_count= (await db.execute(select(func.count()).select_from(select(User).filter(User.is_dimigo == True).subquery()))).scalar_one(),
          graduated_user_count= (await db.execute(select(func.count()).select_from(select(User).filter(User.is_dimigo == True).filter(User.is_dimigo_updated < datetime.date.today() - datetime.timedelta(days=365)).subquery()))).scalar_one(),
          official_service_count= (await db.execute(select(func.count()).select_from(select(Service).filter(Service.is_official == True).subquery()))).scalar_one(),
          unofficial_service_count= (await db.execute(select(func.count()).select_from(select(Service).filter(Service.is_official == False).subquery()))).scalar_one(),
          login_count=0,
          failed_login_count=0
      )

async def update_statistics():
    get_async_session_ctx = contextlib.asynccontextmanager(get_async_session)
    async with get_async_session_ctx() as db:
        statics = await db.execute(select(Statistic).filter(Statistic.date == datetime.date.today()))
    statics = statics.scalar()
    if statics is None:
      statics = await get_statistics(db)
      db.add(statics)
      await db.commit()
    else:
      new_statics = await get_statistics(db)
      statics.user_count = new_statics.user_count
      statics.enrolled_user_count = new_statics.enrolled_user_count
      statics.graduated_user_count = new_statics.graduated_user_count
      statics.official_service_count = new_statics.official_service_count
      statics.unofficial_service_count = new_statics.unofficial_service_count

      db.add(statics)
      await db.commit()
      await db.refresh(statics)
        

async def get_all_statistics(db: AsyncSession):
    statistics = await db.execute(select(Statistic))
    statistics = statistics.scalars().all()
    return statistics


async def add_login_count(db: AsyncSession):
    statics = await db.execute(select(Statistic).filter(Statistic.date == datetime.date.today()))
    statics = statics.scalar()
    if statics is None:
      statics = await get_statistics(db)
      statics.login_count = 1
      db.add(statics)
      await db.commit()
    else:
      statics.login_count += 1
      db.add(statics)
      await db.commit()
      await db.refresh(statics)
       
async def add_failed_login_count(db: AsyncSession):
    statics = await db.execute(select(Statistic).filter(Statistic.date == datetime.date.today()))
    statics = statics.scalar()
    if statics is None:
      statics = await get_statistics(db)
      statics.failed_login_count = 1
      db.add(statics)
      await db.commit()
    else:
      statics.failed_login_count += 1
      print(statics.failed_login_count)
      db.add(statics)
      await db.commit()
      await db.refresh(statics)
