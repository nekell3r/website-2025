from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import uvicorn

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
