import sys

from fastapi import APIRouter, Body
from pathlib import Path
from sqlalchemy import insert

from src.database import async_session_maker
from src.schemas.schemas import ReviewSchema
from src.models.reviews import ReviewsORM

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/")
async def create_review(schema: ReviewSchema = Body()):
    async with async_session_maker() as session:
        statemant_add_review = insert(ReviewsORM).values(**schema.model_dump())
        await session.execute(statemant_add_review)
        await session.commit()
    return {"status": "OK, Review created"}
