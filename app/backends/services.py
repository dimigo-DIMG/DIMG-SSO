import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import Service, ServiceConnection, AccessToken
from fastapi import HTTPException


async def get_all_services(db: AsyncSession, seperate_official: bool = False):
    if not seperate_official:
        services = await db.execute(select(Service))
        services = services.scalars().all()
        return services
    else:
        official_services = await db.execute(select(Service).filter(Service.is_official == True))
        official_services = official_services.scalars().all()
        unofficial_services = await db.execute(select(Service).filter(Service.is_official == False))
        unofficial_services = unofficial_services.scalars().all()
       
        return official_services, unofficial_services

async def get_service_by_id(db: AsyncSession, service_id: str):
    service: Service = await db.execute(
        select(Service).filter(Service.client_id == service_id)
    )
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    service = service.scalar()
    return service


async def create_service(db: AsyncSession, service: Service):
    db.add(service)
    await db.commit()
    return service


async def update_service(db: AsyncSession, id: str, service: Service):
    db.query(Service).filter(Service.client_id == id).update(service)
    await db.commit()
    return service


async def delete_service(db: AsyncSession, service_id: str):
    service: Service = await db.execute(
        select(Service).filter(Service.client_id == service_id)
    )
    service = service.scalar()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
    await db.commit()
    return None


async def update_service(db: AsyncSession, service: Service):
    target_service = await db.execute(
        select(Service).filter(Service.client_id == service.client_id)
    )
    task = target_service.scalar()
    if task is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def get_service_connection(db: AsyncSession, user_id: str, service_id: str):
    service_connection = await db.execute(
        select(ServiceConnection).filter(
            ServiceConnection.user_id == user_id,
            ServiceConnection.service_id == service_id,
        )
    )
    service_connection = service_connection.scalar()
    return service_connection


async def generate_access_token(
    db: AsyncSession, user_id: str, service_id: str, expire: datetime
):
    # check if already exists
    access_token = await db.execute(
        select(AccessToken).filter(
            AccessToken.user_id == user_id, AccessToken.service_id == service_id
        )
    )
    access_token = access_token.scalar()
    if access_token is not None:
        if access_token.expire < datetime.date.today():
            await db.delete(access_token)
            await db.commit()
        else:
            return access_token

    token = str(uuid.uuid4())
    access_token = AccessToken(
        token=token, expire=expire, user_id=user_id, service_id=service_id
    )
    db.add(access_token)
    await db.commit()
    return access_token
