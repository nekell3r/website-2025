from typing import Annotated, Optional
from annotated_types import MinLen, MaxLen, Ge, Le

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRequestAdd(BaseModel):
    phone: PhoneNumber
    email: EmailStr | None = None
    code_phone: int
    code_email: int | None = None
    password: str
    password_repeat: str


class UserLogin(BaseModel):
    phone: PhoneNumber
    password: str


class UserAdd(BaseModel):
    is_super_user: Optional[bool] = False

    name: Optional[str] = Field(default=None, min_length=2, max_length=30)
    surname: Optional[str] = Field(default=None, min_length=2, max_length=30)

    phone: PhoneNumber
    email: Optional[EmailStr] = None
    grade: Optional[int] = Field(default=None, ge=7, le=11)
    hashed_password: str

    model_config = ConfigDict(extra="ignore")


class User(BaseModel):
    id: int
    is_super_user: bool

    name: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None

    phone: PhoneNumber
    email: EmailStr | None = None
    grade: Annotated[int, Ge(7), Le(11)] | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    grade: Annotated[int, Ge(7), Le(11)] | None = None


class UserWithHashedPassword(User):
    hashed_password: str


class PhoneInput(BaseModel):
    phone: PhoneNumber


class PhoneWithCode(PhoneInput):
    code: int


class EmailInput(BaseModel):
    email: EmailStr


class EmailWithCode(EmailInput):
    code: int


class PhoneWithPassword(PhoneInput):
    password: str
    password_repeat: str
