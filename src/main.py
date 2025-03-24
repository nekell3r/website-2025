import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import uvicorn

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings as bd_settings
from src.api.reviews_router import router as reviews_router

app = FastAPI()
app.include_router(reviews_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
