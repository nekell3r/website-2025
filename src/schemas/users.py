from typing import Annotated
from annotated_types import MinLen, MaxLen, Ge, Le

from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRequestAdd(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(30)]
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    telephone: PhoneNumber | None = None
    email: EmailStr
    grade: Annotated[int, Ge(7), Le(11)] | None = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    is_super_user: bool | None = False

    name: Annotated[str, MinLen(2), MaxLen(30)]
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    telephone: PhoneNumber | None = None
    email: EmailStr
    grade: Annotated[int, Ge(7), Le(11)] | None = None
    hashed_password: str

    model_config = ConfigDict(extra="ignore")


class User(BaseModel):
    id: int
    is_super_user: bool

    name: Annotated[str, MinLen(2), MaxLen(30)]
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None

    telephone: PhoneNumber | None = None
    email: EmailStr
    grade: Annotated[int, Ge(7), Le(11)] | None = None

    has_product_1: bool
    has_product_2: bool
    has_product_3: bool
    has_product_4: bool
    has_product_5: bool


class UserWithHashedPassword(User):
    hashed_password: str
