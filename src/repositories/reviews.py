from datetime import datetime, timezone, timedelta

from fastapi import HTTPException

from src.repositories.base import BaseRepository
from src.models.reviews import ReviewsOrm
from src.repositories.mappers.mappers import (
    ReviewsMapper,
    ReviewsPatchMapper,
    ReviewsIdMapper,
)
from src.schemas.reviews import (
    ReviewBase,
    ReviewPatch,
    Review,
    ReviewWithId,
)
from sqlalchemy import select, update


class ReviewsRepository(BaseRepository):
    model = ReviewsOrm  # id, user_id, review
    schema = Review  # user_id, review
    mapper = ReviewsMapper

    async def get_all(self, limit, offset) -> list[Review]:
        query = select(ReviewsOrm)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def superuser_get_all(self, limit, offset) -> list[ReviewWithId]:
        query = select(ReviewsOrm)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            ReviewsIdMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def get_all_filtered(self, limit, offset, **filter_by) -> list[ReviewWithId]:
        query = (
            select(ReviewsOrm)
            .filter_by(**filter_by)
            .limit(limit)
            .offset(offset)
        )
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            ReviewsIdMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]

    async def get_one_or_none_with_id(self, **filter_by) -> ReviewWithId | None:
        query = select(ReviewsOrm).filter_by(**filter_by)
        result = await self.session.execute(query)
        result = result.scalars().one_or_none()
        if result is None:
            return None
        return ReviewsIdMapper.map_to_domain_entity(result)

    async def edit(
        self, data: ReviewPatch, exclude_unset: bool = False, **filter_by
    ) -> None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise HTTPException(status_code=409, detail="Такого отзыва не существует")
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(
                **data.model_dump(exclude_unset=exclude_unset)
                )
            )

        await self.session.execute(update_stmt)
