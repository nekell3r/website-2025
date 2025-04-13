# from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict

# from pydantic_extra_types.phone_numbers import PhoneNumber
# from typing_extensions import Annotated


class UserRequestAdd(BaseModel):
    # name: Annotated[str, MinLen(2), MaxLen(25)]
    # exam: Annotated[str, MinLen(2), MaxLen(30)]
    # telephone: Annotated[str, PhoneNumber]
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str
