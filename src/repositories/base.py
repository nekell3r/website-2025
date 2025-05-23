from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel

from src.repositories.mappers.base import DataMapper
from src.exceptions.db_exceptions import ObjectNotFoundException


class BaseRepository:
    model = None
    schema: BaseModel = None
    mapper: DataMapper = None
    not_found_exception: ObjectNotFoundException = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        answer = [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]
        if not answer:
            raise self.not_found_exception
        return answer

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise self.not_found_exception
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        add_data_stmt = (
            insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        select_stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(select_stmt)
        try:
            instance = result.scalars_one()
        except NoResultFound:
            raise self.not_found_exception

        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
