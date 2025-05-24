# Third-party imports
from dotenv import load_dotenv
import pytest
from pydantic_extra_types.phone_numbers import PhoneNumber
from unittest import mock
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

# Импорты из src
from src.config import settings
from src.database import Base, get_engine_null_pool, get_async_session_maker_null_pool
from src.dependencies.db import get_db
from src.main import app
from src.models import *  # noqa: F403
from src.schemas.users import UserAdd
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

# Module-level executable code AFTER all imports
load_dotenv()

print("DEBUG (conftest): Database connection parameters:")
print(f"DB_HOST: {settings.DB_HOST}")
print(f"DB_PORT: {settings.DB_PORT}")
print(f"DB_USER: {settings.DB_USER}")
print(f"DB_NAME: {settings.DB_NAME}")
print(f"Full DB URL: {settings.DB_URL}")


# Патч fastapi_cache после импортов
def early_patch():
    print("DEBUG (conftest): Running early_patch")
    mock.patch(
        "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
    ).start()


early_patch()


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    print("DEBUG (conftest): Starting check_test_mode fixture")
    print(f"DEBUG (conftest): check_test_mode called. settings.MODE = {settings.MODE}")
    assert settings.MODE == "TEST"
    print("DEBUG (conftest): check_test_mode fixture completed")


async def get_db_null_pool_dependency():
    print("DEBUG (conftest): Starting get_db_null_pool_dependency")
    session_maker = get_async_session_maker_null_pool()
    async with DBManager(session_factory=session_maker) as db:
        yield db
    print("DEBUG (conftest): Finished get_db_null_pool_dependency")


@pytest.fixture(scope="function")
async def db():
    print("DEBUG (conftest): Starting db fixture")
    async for session_db in get_db_null_pool_dependency():
        yield session_db
    print("DEBUG (conftest): Finished db fixture")


app.dependency_overrides[get_db] = get_db_null_pool_dependency


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    print("DEBUG (conftest): Starting setup_database fixture")
    engine = get_engine_null_pool()
    print(
        f"DEBUG (conftest - setup_database): Перед engine.begin(). settings.DB_HOST = {settings.DB_HOST}, settings.DB_URL = {settings.DB_URL}"
    )
    async with engine.begin() as conn:
        print("DEBUG (conftest): Dropping all tables")
        await conn.run_sync(Base.metadata.drop_all)
        print("DEBUG (conftest): Creating all tables")
        await conn.run_sync(Base.metadata.create_all)
    print("DEBUG (conftest): setup_database fixture completed")


@pytest.fixture(scope="session", autouse=True)
async def register_user():
    print("DEBUG (conftest): Starting register_user fixture")
    hashed_password = AuthService().hash_password("12345678")
    user_data = UserAdd(
        phone=PhoneNumber("+79282017042"), hashed_password=hashed_password
    )
    session_maker = get_async_session_maker_null_pool()
    async with DBManager(session_factory=session_maker) as db_session:
        print("DEBUG (conftest): Adding test user to database")
        await db_session.users.add(user_data)
        await db_session.commit()
    print("DEBUG (conftest): register_user fixture completed")


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    print("DEBUG (conftest): Starting ac fixture")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac_client:
        yield ac_client
    print("DEBUG (conftest): ac fixture completed")
