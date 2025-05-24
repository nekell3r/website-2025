from sqlalchemy import select, insert
import phonenumbers  # Убедитесь, что импортирован
from phonenumbers.phonenumberutil import NumberParseException  # Для обработки ошибок
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.repositories.mappers.mappers import UsersMapper
from src.schemas.users import (
    UserWithHashedPassword,
    User,
    UserAdd,
)  # UserAdd для тайпхинта
from src.exceptions.db_exceptions import UserNotFoundException


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User
    mapper = UsersMapper
    not_found_exception = UserNotFoundException

    async def get_user_with_hashed_password(
        self, phone: str
    ) -> UserWithHashedPassword | None:
        query = select(self.model).filter_by(phone=phone)
        result = await self.session.execute(query)
        db_model = result.scalars().one_or_none()
        if db_model is None:
            return None
        return UserWithHashedPassword.model_validate(db_model, from_attributes=True)

    async def add(self, data: UserAdd) -> User:
        phone_to_save = None
        if data.phone:
            if isinstance(data.phone, PydanticPhoneNumber):
                phone_to_save = data.phone.e164
            elif isinstance(data.phone, str):
                temp_phone_str = data.phone.replace("tel:", "")
                try:
                    parsed_phone = phonenumbers.parse(temp_phone_str, None)
                    phone_to_save = phonenumbers.format_number(
                        parsed_phone, phonenumbers.PhoneNumberFormat.E164
                    )
                except NumberParseException:
                    phone_to_save = data.phone
            else:
                raise ValueError(f"Unexpected type for data.phone: {type(data.phone)}")

        data_dict_for_db = data.model_dump(exclude_unset=True)
        if phone_to_save:
            data_dict_for_db["phone"] = phone_to_save

        stmt = insert(self.model).values(**data_dict_for_db).returning(self.model)
        result_model = await self.session.execute(stmt)
        created_model_instance = result_model.scalars().one()
        return self.mapper.map_to_domain_entity(created_model_instance)
