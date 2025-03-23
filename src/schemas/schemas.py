from dataclasses import Field

from annotated_types import MinLen, MaxLen
from dotenv.variables import Literal
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing_extensions import Annotated


class ReviewSchema(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(30)]
    exam: Literal = ["EGE", "OGE"]
    score: Literal = [1, 2, 3]
    review: Annotated[str, MinLen(10), MaxLen(1000)]


class UserSchema(
    BaseModel
):  # нужно добавить в фронте, что надо указать, в какой класс поступаешь, а не из какого выпускаешься
    name: Annotated[str, MinLen(2), MaxLen(30)]
    exam: Literal = ["EGE", "OGE"]
    _class: Literal = [
        8,
        9,
        10,
        11,
    ]
    number: PhoneNumber


class UserWithEmailSchema(UserSchema):
    email: EmailStr
