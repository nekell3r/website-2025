from annotated_types import MinLen, MaxLen
from dotenv.variables import Literal
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing_extensions import Annotated


class ReviewAddRequest(BaseModel):
    review: str
    exam: str
    result: int

    class Config:
        extra = "ignore"


class ReviewPatch(BaseModel):
    review: str | None = Field(None)
    exam: str | None = Field(None)
    result: int | None = Field(None)


class ReviewAdd(ReviewAddRequest):
    user_id: int


class Review(ReviewAdd):
    id: int
