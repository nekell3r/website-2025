# Third-party imports
from dotenv import load_dotenv
import pytest
from pydantic_extra_types.phone_numbers import PhoneNumber
from unittest import mock
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
import sys

# Импорты из src
from src.config import settings
from src.database import Base, get_engine_null_pool, get_async_session_maker_null_pool
from src.dependencies.db import get_db
from src.main import app
from src.models import *  # noqa: F403
from src.schemas.users import UserAdd
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

# Глобальная настройка для всех асинхронных тестов
pytestmark = pytest.mark.asyncio(loop_scope="session")

# Module-level executable code AFTER all imports
load_dotenv()

print("DEBUG (conftest): Starting conftest.py initialization", file=sys.stderr)
print("DEBUG (conftest): Database connection parameters:", file=sys.stderr)
print(f"DB_HOST: {settings.DB_HOST}", file=sys.stderr)
print(f"DB_PORT: {settings.DB_PORT}", file=sys.stderr)
print(f"DB_USER: {settings.DB_USER}", file=sys.stderr)
print(f"DB_NAME: {settings.DB_NAME}", file=sys.stderr)
print(f"Full DB URL: {settings.DB_URL}", file=sys.stderr)


# Патч fastapi_cache после импортов
def early_patch():
    print("DEBUG (conftest): Running early_patch", file=sys.stderr)
    mock.patch(
        "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
    ).start()


early_patch()


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    print("DEBUG (conftest): Starting check_test_mode fixture", file=sys.stderr)
    print(
        f"DEBUG (conftest): check_test_mode called. settings.MODE = {settings.MODE}",
        file=sys.stderr,
    )
    assert settings.MODE == "TEST"
    print("DEBUG (conftest): check_test_mode fixture completed", file=sys.stderr)
    return True


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    print("DEBUG (conftest): Starting setup_database fixture", file=sys.stderr)
    engine = get_engine_null_pool()
    print(
        f"DEBUG (conftest - setup_database): Перед engine.begin(). settings.DB_HOST = {settings.DB_HOST}, settings.DB_URL = {settings.DB_URL}",
        file=sys.stderr,
    )
    try:
        async with engine.begin() as conn:
            print("DEBUG (conftest): Dropping all tables", file=sys.stderr)
            await conn.run_sync(Base.metadata.drop_all)
            print("DEBUG (conftest): Creating all tables", file=sys.stderr)
            await conn.run_sync(Base.metadata.create_all)
        print(
            "DEBUG (conftest): setup_database fixture completed successfully",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"DEBUG (conftest): Error in setup_database: {str(e)}", file=sys.stderr)
        raise


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database):
    print("DEBUG (conftest): Starting register_user fixture", file=sys.stderr)
    try:
        hashed_password = AuthService().hash_password("12345678")
        user_data = UserAdd(
            phone=PhoneNumber("+79282017042"), hashed_password=hashed_password
        )
        session_maker = get_async_session_maker_null_pool()
        async with DBManager(session_factory=session_maker) as db_session:
            print("DEBUG (conftest): Adding test user to database", file=sys.stderr)
            await db_session.users.add(user_data)
            await db_session.commit()
        print(
            "DEBUG (conftest): register_user fixture completed successfully",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"DEBUG (conftest): Error in register_user: {str(e)}", file=sys.stderr)
        raise


async def get_db_null_pool_dependency():
    print("DEBUG (conftest): Starting get_db_null_pool_dependency", file=sys.stderr)
    session_maker = get_async_session_maker_null_pool()
    async with DBManager(session_factory=session_maker) as db:
        yield db
    print("DEBUG (conftest): Finished get_db_null_pool_dependency", file=sys.stderr)


@pytest.fixture(scope="function")
async def db(register_user):
    print("DEBUG (conftest): Starting db fixture", file=sys.stderr)
    async for session_db in get_db_null_pool_dependency():
        yield session_db
    print("DEBUG (conftest): Finished db fixture", file=sys.stderr)


app.dependency_overrides[get_db] = get_db_null_pool_dependency


@pytest.fixture(scope="session")
async def ac(register_user) -> AsyncClient:
    print("DEBUG (conftest): Starting ac fixture", file=sys.stderr)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac_client:
        yield ac_client
    print("DEBUG (conftest): ac fixture completed", file=sys.stderr)
