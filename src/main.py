import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn


sys.path.append(str(Path(__file__).parent.parent))

from src.api.reviews import router as reviews_router
from src.api.reviews import super_user_router as superuser_reviews_router
from src.api.auth import router as users_router
from src.api.products import router as products_router

app = FastAPI()
app.include_router(products_router)
app.include_router(reviews_router)
app.include_router(superuser_reviews_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
