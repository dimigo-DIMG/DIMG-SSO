from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import Service
from fastapi import HTTPException

async def get_all_services(db: AsyncSession):
    services = await db.execute(select(Service))
    services = services.scalars().all()
    return services

async def get_service_by_id(db: AsyncSession, service_id: str):
    service: Service = await db.execute(select(Service).filter(Service.client_id == service_id))
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

async def create_service(db: AsyncSession, service: Service):
    db.add(service)
    await db.commit()
    return service

async def update_service(db: AsyncSession, id: str, service: Service):
    db.query(Service).filter(Service.client_id == id).update(service)
    await db.commit()
    return service

async def delete_service(db: AsyncSession, id: str):
    db.query(Service).filter(Service.client_id == id).delete()
    await db.commit()
    return None

