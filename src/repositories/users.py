from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.repositories.mappers.mappers import UsersMapper
from src.schemas.users import UserWithHashedPassword, User
from src.exceptions.exceptions import UserNotFoundException

class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User
    mapper = UsersMapper
    not_found_exception = UserNotFoundException

    async def get_user_with_hashed_password(self, phone: str):
        query = select(self.model).filter_by(phone=phone)
        result = await self.session.execute(query)

        try:
            model = result.scalars().one_or_none()
        except NoResultFound:
            raise self.not_found_exception

        return UserWithHashedPassword.model_validate(model, from_attributes=True)
