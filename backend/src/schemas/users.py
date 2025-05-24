from typing import Annotated, Optional
from annotated_types import MinLen, MaxLen, Ge, Le

from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
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
    code: Annotated[int, Ge(1000), Le(9999)]


class RegistrationInput(BaseModel):
    phone: PhoneNumber
    email: EmailStr | None = None
    password: str = Field(..., min_length=8)
    password_repeat: str = Field(..., min_length=8)
    phone_code: Annotated[int, Ge(1000), Le(9999)]
    email_code: Annotated[int, Ge(1000), Le(9999)] | None = None

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegistrationInput":
        if self.password != self.password_repeat:
            raise ValueError("passwords do not match")
        return self

    @model_validator(mode="after")
    def check_email_and_code_consistency(self) -> "RegistrationInput":
        if self.email and self.email_code is None:
            raise ValueError("email_code is required when email is provided")
        if not self.email and self.email_code is not None:
            raise ValueError(
                "email_code should not be provided without an email address"
            )
        return self


class ResetCodeVerifyInput(BaseModel):
    phone: PhoneNumber
    code: Annotated[int, Ge(1000), Le(9999)]


class SetNewPasswordAfterResetInput(BaseModel):
    phone: PhoneNumber
    new_password: str = Field(..., min_length=8)
    new_password_repeat: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def check_new_passwords_match(self) -> "SetNewPasswordAfterResetInput":
        if self.new_password != self.new_password_repeat:
            raise ValueError("new passwords do not match")
        return self


class SetPasswordInput(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    new_password_repeat: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def check_new_passwords_match(self) -> "SetPasswordInput":
        if self.new_password != self.new_password_repeat:
            raise ValueError("new passwords do not match")
        return self
