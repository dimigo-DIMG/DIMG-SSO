from typing import AsyncGenerator, List

from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy import Column, Integer, String, Boolean, Date

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    nickname = Column(String, nullable=True)

    gender = Column(String, nullable=True)
    birthday = Column(Date, nullable=True)

    is_dimigo = Column(Boolean, nullable=True)
    is_dimigo_updated = Column(Date, nullable=True)
    #dimigo_id = Column(String, nullable=True)

    expire = Column(Date, nullable=True)

class Service(Base):
    __tablename__ = "services"

    """
    SSO Clients pages that are allowed to access the DIMGSSO
    
    clinet_id: OAuth2 client ID ( unique identifier, primary key )
    client_secret: OAuth2 client secret
    name: Friendly name of the service
    description: Description of the service
    is_official: Whether the service is official or not
    icon: URL to the icon of the service
    login_callback: URL to redirect to after login
    unregister_callback: URL to redirect to after unregistering
    scopes: List of scopes that the service is allowed to access
    register_cooldown: Time in Hourss that the service has to wait before re-registering

    """
    client_id = Column(String, primary_key=True, index=True)
    client_secret = Column(String)
    name = Column(String)
    is_official = Column(Boolean)
    description = Column(String)
    icon = Column(String, nullable=True)
    login_callback = Column(String)
    unregister_page = Column(String)
    main_page = Column(String)
    scopes = Column(String)
    register_cooldown = Column(Integer)

    @property
    def icon_url(self):
        if self.icon:
            return self.icon
        else:
            return f"/static/test.png"
        

class ServiceConnection(Base):
    __tablename__ = "service_connections"

    """
    Connection between a user and a service

    cid: Connection ID ( unique identifier, primary key )
    registered: When the user registered the service ( Date )
    """
    cid = Column(Integer, primary_key=True, index=True)
    registered = Column(Date)
    unregistered = Column(Date, nullable=True)
    user = relationship("User", back_populates="service_connections")
    service = relationship("Service", back_populates="service_connections")
    
class AccessToken(Base):
    __tablename__ = "access_tokens"

    """
    Access tokens for services

    token: Access token ( unique identifier, primary key )
    user: User that owns the token
    service: Service that the token is for
    expire: When the token expires ( Date )
    """
    token = Column(String, primary_key=True, index=True)
    expire = Column(Date)
    user = relationship("User", back_populates="access_tokens")
    service = relationship("Service", back_populates="access_tokens")
    
User.service_connections = relationship("ServiceConnection", back_populates="user")
User.access_tokens = relationship("AccessToken", back_populates="user")
Service.service_connections = relationship("ServiceConnection", back_populates="service")
Service.access_tokens = relationship("AccessToken", back_populates="service")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
