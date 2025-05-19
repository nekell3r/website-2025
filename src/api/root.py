from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="", tags=["корень"])

@router.head("/")
async def get_root():
    return {"status":"Ok"}