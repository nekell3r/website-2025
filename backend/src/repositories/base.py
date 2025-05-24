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
        dumped_data = data.model_dump()
        # В UsersRepository.add мы уже нормализуем 'phone', если это он
        add_data_stmt_returning_model = (
            insert(self.model).values(**dumped_data).returning(self.model)
        )
        result_model = await self.session.execute(add_data_stmt_returning_model)
        created_model_instance = result_model.scalars().one()
        return self.mapper.map_to_domain_entity(created_model_instance)

    async def edit(
        self, data: BaseModel | dict, exclude_unset_for_model: bool = True, **filter_by
    ):
        if not filter_by:
            # Можно выбросить ValueError, если фильтр обязателен и не должен быть пустым
            # Либо, если обновление без фильтра недопустимо, это должно быть более строгой ошибкой.
            # Пока оставим возможность вызова без ошибки, но это может быть нежелательно.
            print(
                "ПРЕДУПРЕЖДЕНИЕ (BaseRepository.edit): Вызов edit без критериев фильтрации (**filter_by пуст)."
            )
            # return # Если хотим прервать выполнение
            raise ValueError(
                "Критерии фильтрации для операции edit не могут быть пустыми."
            )

        values_to_update = {}
        if isinstance(data, BaseModel):
            values_to_update = data.model_dump(exclude_unset=exclude_unset_for_model)
        elif isinstance(data, dict):
            values_to_update = data
        else:
            raise TypeError("Data for edit must be a Pydantic model or a dictionary.")

        if not values_to_update:
            print(
                f"DEBUG (BaseRepository.edit): Нет данных для обновления по фильтру: {filter_by}."
            )
            return

        update_stmt = (
            update(self.model).filter_by(**filter_by).values(**values_to_update)
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by):
        if not filter_by:
            # Аналогично edit, можно добавить проверку на пустой filter_by
            print(
                "ПРЕДУПРЕЖДЕНИЕ (BaseRepository.delete): Вызов delete без критериев фильтрации (**filter_by пуст)."
            )
            # return
            raise ValueError(
                "Критерии фильтрации для операции delete не могут быть пустыми."
            )
        query = delete(self.model).filter_by(**filter_by)
        await self.session.execute(query)
