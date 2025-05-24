from typing import Annotated, Optional
from annotated_types import MinLen, MaxLen, Ge, Le

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserLogin(BaseModel):
    phone: PhoneNumber
    password: str = Field(..., min_length=8)


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


class EmailInput(BaseModel):
    email: EmailStr


class CodeInput(BaseModel):
    code: str = Field(..., min_length=4, max_length=6)


class RegistrationInput(CodeInput):
    phone: PhoneNumber | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: str = Field(..., min_length=8)


class ResetCodeVerifyInput(BaseModel):
    phone: PhoneNumber | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    code: str = Field(..., min_length=4, max_length=4)


class SetNewPasswordAfterResetInput(BaseModel):
    phone: PhoneNumber | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    new_password: str = Field(..., min_length=8)


class SetPasswordInput(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
