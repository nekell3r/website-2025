from fastapi import APIRouter

router = APIRouter(prefix="", tags=["корень"])


@router.head("/")
async def get_root():
    return {"status": "Ok"}
