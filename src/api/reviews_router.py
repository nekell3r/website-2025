import sys

from fastapi import APIRouter, Path

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
async def read_reviews():
    return {"message": "Read reviews"}
