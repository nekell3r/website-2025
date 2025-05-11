from datetime import datetime, timezone, timedelta

from fastapi import HTTPException

from src.repositories.base import BaseRepository
from src.models.reviews import ReviewsOrm
from src.repositories.mappers.mappers import (
    ReviewsMapper,
    SuperUserReviewsMapper,
    ReviewsPatchMapper,
    ReviewsSelfMapper,
)
from src.schemas.reviews import (
    ReviewBase,
    ReviewPatch,
    ReviewsGetBySuperUser,
    ReviewSelfGet,
)
from sqlalchemy import select, update


class ReviewsRepository(BaseRepository):
    model = ReviewsOrm  # id, user_id, review
    schema = ReviewBase  # user_id, review
    mapper = ReviewsMapper

    async def get_all(self, limit, offset) -> list[ReviewBase]:
        query = select(ReviewsOrm)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def superuser_get_all(self, limit, offset) -> list[ReviewsGetBySuperUser]:
        query = select(ReviewsOrm)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            SuperUserReviewsMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def get_mine(self, limit, offset, current_user_id) -> list[ReviewSelfGet]:
        query = (
            select(ReviewsOrm)
            .where(ReviewsOrm.user_id == current_user_id)
            .limit(limit)
            .offset(offset)
        )
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            ReviewsSelfMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def get_definite_mine(self, review_id: int):
        query = select(ReviewsOrm).where(ReviewsOrm.id == review_id)
        result = await self.session.execute(query)
        result = result.scalars().one_or_none()
        if result is None:
            return None
        return ReviewsSelfMapper.map_to_domain_entity(result)

    async def edit(
        self, data: ReviewPatch, exclude_unset: bool = False, **filter_by
    ) -> None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise HTTPException(status_code=409, detail="Такого отзыва не существует")
        now_utc = datetime.now(timezone.utc)
        delta = now_utc - obj.edited_at
        if delta < timedelta(hours=1):
            minutes_left = 60 - int(delta.total_seconds() // 60)
            raise HTTPException(
                status_code=409,
                detail=f"Редактирование возможно только через {minutes_left} мин.",
            )

        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(
                ReviewsPatchMapper.map_to_persistence_entity_with_unset_filter(
                    data=data, exclude_unset=exclude_unset
                )
            )
        )
        await self.session.execute(update_stmt)
