import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn


sys.path.append(str(Path(__file__).parent.parent))

from src.api.reviews_router import router as reviews_router
from src.api.users_router import router as users_router

app = FastAPI()
app.include_router(reviews_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
