from datetime import datetime, timezone

from sqlalchemy import Column, String, TIMESTAMP, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator

from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi import Depends


from config import DB_HOST, DB_PASS, DB_NAME, DB_PORT, DB_USER
from auth.models import role, user

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base: DeclarativeMeta = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    password: str = Column(String(length=1024), nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nickname = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey(role.c.id))
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True)
    wallet = Column(String, nullable=False)
    wallet_id = Column(Integer, ForeignKey(user.c.id))
    crypto = Column(String, default=0)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
