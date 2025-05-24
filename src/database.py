from functools import lru_cache
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool.impl import NullPool

from src.config import settings

@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(settings.DB_URL)

@lru_cache(maxsize=1)
def get_engine_null_pool() -> AsyncEngine:
    return create_async_engine(settings.DB_URL, poolclass=NullPool)

@lru_cache(maxsize=1)
def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_engine(), expire_on_commit=False)

@lru_cache(maxsize=1)
def get_async_session_maker_null_pool() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_engine_null_pool(), expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Удаляем старые глобальные переменные, если они были
# engine = get_engine() # Нет, вызываем по необходимости
# engine_null_pool = get_engine_null_pool() # Нет, вызываем по необходимости
# async_session_maker = get_async_session_maker() # Нет, вызываем по необходимости
# async_session_maker_null_pool = get_async_session_maker_null_pool() # Нет, вызываем по необходимости
