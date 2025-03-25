import sys

from fastapi import APIRouter, Body
from pathlib import Path
from sqlalchemy import insert, select

from src.database import async_session_maker
from src.schemas.schemas import ReviewSchema
from src.models.reviews import ReviewsORM

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
async def get_reviews():
    async with async_session_maker() as session:
        query = select(ReviewsORM)
        result = await session.execute(query)
        reviews = result.scalars().all()
        return reviews


@router.post("/")
async def create_review(
    schema: ReviewSchema = Body(
        openapi_examples={
            "1": {
                "summary": "Отзыв Павла",
                "value": {
                    "user_id": 3,
                    "name": "Павел",
                    "exam": "ЕГЭ",
                    "result": 100,
                    "review": "Замечательный учитель",
                },
            },
            "2": {
                "summary": "Отзыв Антона",
                "value": {
                    "user_id": 4,
                    "name": "Павел",
                    "exam": "ЕГЭ",
                    "result": 80,
                    "review": "кайфово было вообще блин",
                },
            },
        }
    )
):
    async with async_session_maker() as session:
        statemant_add_review = insert(ReviewsORM).values(**schema.model_dump())
        await session.execute(statemant_add_review)
        await session.commit()
    return {"status": "OK, Review created"}
