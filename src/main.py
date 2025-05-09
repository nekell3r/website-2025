import sys
from pathlib import Path
from contextlib import asynccontextmanager


from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
from starlette.middleware.cors import CORSMiddleware
import uvicorn


sys.path.append(str(Path(__file__).parent.parent))

from src.api.reviews import router as reviews_router
from src.api.payments import router as purchases_router
from src.api.reviews import super_user_router as superuser_reviews_router
from src.api.auth import (
    router as users_router,
    register as users_register_router,
    reset as users_reset,
)
from src.api.products import router as products_router
from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(superuser_reviews_router)
app.include_router(purchases_router)
app.include_router(users_router)
app.include_router(users_reset)
app.include_router(users_register_router)
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
