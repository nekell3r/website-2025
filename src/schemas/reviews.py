from annotated_types import MinLen, MaxLen
from dotenv.variables import Literal
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing_extensions import Annotated


class ReviewAddRequest(BaseModel):
    review: str

    class Config:
        extra = "ignore"


class ReviewAdd(ReviewAddRequest):
    user_id: int
