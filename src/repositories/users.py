from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.repositories.mappers.mappers import UsersMapper
from src.schemas.users import UserWithHashedPassword, UserAdd, User


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User
    mapper = UsersMapper

    async def get_user_with_hashed_password(self, phone: str):
        query = select(self.model).filter_by(telephone=phone)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserWithHashedPassword.model_validate(model, from_attributes=True)
