from sqlalchemy import select
from pydantic import EmailStr

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.repositories.mappers.mappers import UsersMapper
from src.schemas.users import User, UserWithHashedPassword, UserAdd


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = UserAdd
    mapper = UsersMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(
            email=email
        )  # нужно исправить на ввод телефона ИЛИ почты
        result = await self.session.execute(query)
        model = result.scalars().one()
        return UserWithHashedPassword.model_validate(model, from_attributes=True)
