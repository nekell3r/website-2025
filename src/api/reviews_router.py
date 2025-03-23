from fastapi import APIRouter

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
async def read_reviews():
    return {"message": "Read reviews"}
