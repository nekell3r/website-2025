from src.repositories.base import BaseRepository
from src.models.reviews import ReviewsOrm
from src.schemas.reviews import ReviewAdd, ReviewAddRequest
from sqlalchemy import select, func, insert


class ReviewsRepository(BaseRepository):
    model = ReviewsOrm  # id, user_id, review
    schema = ReviewAdd  # user_id, review

    async def get_all(self, limit, offset) -> list[ReviewAddRequest]:
        query = select(ReviewsOrm)
        query = query.limit(limit).offset(offset)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            ReviewAddRequest.model_validate(review, from_attributes=True)
            for review in result.scalars().all()
        ]

    async def get_mine(self, limit, offset, current_user_id) -> list[ReviewAddRequest]:
        query = (
            select(ReviewsOrm)
            .where(ReviewsOrm.user_id == current_user_id)
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            ReviewAddRequest.model_validate(review, from_attributes=True)
            for review in result.scalars().all()
        ]
