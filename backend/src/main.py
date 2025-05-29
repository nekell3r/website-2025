import sys
from pathlib import Path
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
import asyncpg

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Импорты из src
from src.exceptions.service_exceptions import MadRussianServiceException
from src.exceptions.handlers import mad_russian_service_exception_handler
from src.api.root import router as root_router
from src.api.reviews import router as reviews_router
from src.api.payments import router as purchases_router
from src.api.admin import router as admin_router
from src.api.auth import (
    router as users_router,
    register as users_register_router,
    reset as users_reset,
)
from src.api.personal_info import router as personal_info_router
from src.init import redis_manager, init_yookassa
from src.config import settings


# Инициализация окружения и путей
def early_setup():
    mode = os.environ.get("MODE")

    if mode is None or mode == "LOCAL":
        load_dotenv(dotenv_path=".local_env_example", override=True)
    elif mode == "TEST":
        pass
    else:
        pass

    sys.path.append(str(Path(__file__).parent.parent))


early_setup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # print(f"DEBUG: Attempting to connect to database with URL: {settings.DB_URL}")
    try:
        conn_url = settings.DB_URL.replace("+asyncpg", "")
        conn = await asyncpg.connect(conn_url)
        await conn.execute("SELECT 1")
        await conn.close()
        # print("DEBUG: Database connection successful.")
    except Exception as e:
        print(
            f"CRITICAL: Failed to connect to the database on startup: {e}"
        )  # Оставим CRITICAL

    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    init_yookassa(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(
    MadRussianServiceException, mad_russian_service_exception_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:63342",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
app.include_router(admin_router)
app.include_router(reviews_router)
app.include_router(personal_info_router)
app.include_router(purchases_router)
app.include_router(users_router)
app.include_router(users_reset)
app.include_router(users_register_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
