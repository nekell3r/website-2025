from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from src.repositories.base import BaseRepository
from src.models.reviews import ReviewsOrm
from src.repositories.mappers.mappers import (
    ReviewsMapper,
    ReviewsIdMapper,
)
from src.schemas.reviews import (
    ReviewPatch,
    Review,
    ReviewWithId,
)
from src.exceptions.db_exceptions import ReviewNotFoundException


class ReviewsRepository(BaseRepository):
    model = ReviewsOrm
    schema = Review
    mapper = ReviewsMapper
    not_found_exception = ReviewNotFoundException

    async def get_all(self, exam, limit, offset) -> list[Review]:
        query = select(ReviewsOrm).filter_by(exam=exam)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        answer = [
            self.mapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]
        if not answer:
            raise self.not_found_exception
        return answer

    async def get_all_with_id(self, limit, offset, **filter_by) -> list[ReviewWithId]:
        query = select(ReviewsOrm).filter_by(**filter_by)
        query = query.limit(limit).offset(offset)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        answer = [
            ReviewsIdMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]
        if not answer:
            raise self.not_found_exception
        return answer

    async def get_all_filtered(self, limit, offset, **filter_by) -> list[ReviewWithId]:
        query = select(ReviewsOrm).filter_by(**filter_by).limit(limit).offset(offset)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        answer = [
            ReviewsIdMapper.map_to_domain_entity(review)
            for review in result.scalars().all()
        ]
        if not answer:
            raise self.not_found_exception
        return answer

    async def get_one_with_id(self, **filter_by) -> ReviewWithId | None:
        query = select(ReviewsOrm).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            result = result.scalar_one()
        except NoResultFound:
            raise self.not_found_exception
        return ReviewsIdMapper.map_to_domain_entity(result)

    async def edit(
        self, data: ReviewPatch, exclude_unset: bool = False, **filter_by
    ) -> None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        try:
            result.scalar_one()
        except NoResultFound:
            raise self.not_found_exception

        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )

        await self.session.execute(update_stmt)
