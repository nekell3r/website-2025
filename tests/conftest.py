import pytest
from pydantic_extra_types.phone_numbers import PhoneNumber
from unittest import mock
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from src.config import settings
from src.database import Base, get_engine_null_pool, get_async_session_maker_null_pool
from src.dependencies.db import get_db
from src.main import app
from src.models import *
from src.schemas.users import UserAdd
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    print(f"DEBUG (conftest): check_test_mode called. settings.MODE = {settings.MODE}")
    assert settings.MODE == "TEST"
    # Дополнительная проверка, что и другие тестовые переменные загружены, если нужно
    # Например, assert settings.DB_NAME == "website_test"

async def get_db_null_pool_dependency():
    session_maker = get_async_session_maker_null_pool()
    async with DBManager(session_factory=session_maker) as db:
        yield db

@pytest.fixture(scope="function")
async def db():
    async for session_db in get_db_null_pool_dependency():
        yield session_db

app.dependency_overrides[get_db] = get_db_null_pool_dependency

@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    engine = get_engine_null_pool()
    print(f"DEBUG (conftest - setup_database): Перед engine.begin(). settings.DB_HOST = {settings.DB_HOST}, settings.DB_URL = {settings.DB_URL}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="session", autouse=True)
async def register_user():
    hashed_password = AuthService().hash_password("12345678")
    user_data = UserAdd(phone=PhoneNumber("+79282017042"), hashed_password=hashed_password)
    session_maker = get_async_session_maker_null_pool()
    async with DBManager(session_factory=session_maker) as db_session:
        await db_session.users.add(user_data)
        await db_session.commit()

@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac_client:
        yield ac_client