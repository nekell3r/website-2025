import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
import uvicorn


sys.path.append(str(Path(__file__).parent.parent))

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    init_yookassa(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
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
    uvicorn.run("main:app", host="0.0.0.0" ,reload=True)
