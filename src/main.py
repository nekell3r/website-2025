import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import uvicorn
from src.config import settings as bd_settings

sys.path.append(str(Path(__file__).parent.parent))
app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
