from datetime import datetime, timezone, timedelta

from fastapi import HTTPException

from src.repositories.base import BaseRepository
from src.models.reviews import ReviewsOrm
from src.schemas.reviews import ReviewAdd, ReviewAddRequest, Review, ReviewPatch
from sqlalchemy import select, func, insert, update


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
            Review.model_validate(review, from_attributes=True)
            for review in result.scalars().all()
        ]

    async def edit(
        self, data: ReviewPatch, exclude_unset: bool = False, **filter_by
    ) -> None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()

        now_utc = datetime.now(timezone.utc)
        delta = now_utc - obj.last_edit_time
        if delta < timedelta(hours=1):
            minutes_left = 60 - int(delta.total_seconds() // 60)
            raise HTTPException(
                status_code=409,
                detail=f"Редактирование возможно только через {minutes_left} мин.",
            )

        # Обновление
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)
