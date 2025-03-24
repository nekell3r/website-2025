from annotated_types import MinLen, MaxLen
from dotenv.variables import Literal
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing_extensions import Annotated


class ReviewSchema(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(30)]
    exam: Annotated[str, MinLen(2), MaxLen(30)]
    result: int
    review: Annotated[str, MinLen(10), MaxLen(1000)]
    user_id: int


class UserSchema(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(25)]
    exam: Annotated[str, MinLen(2), MaxLen(30)]
    telephone: Annotated[str, PhoneNumber]
    email: Annotated[str, EmailStr] | None = None
