from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


from pydantic import field_validator
from typing import Literal


class ReviewBase(BaseModel):
    exam: Literal["ЕГЭ", "ОГЭ"]
    result: int = Field(..., ge=0)
    review: str

class Review(ReviewBase):
    created_at: datetime
    edited_at: datetime

class ReviewWithId(Review):
    user_id: int
    id: int

class ReviewAddRequest(ReviewBase):
    @field_validator("result")
    @classmethod
    def validate_result(cls, value, info):
        exam = info.data.get("exam")

        if exam == "ЕГЭ" and not (0 <= value <= 100):
            raise ValueError("Для ЕГЭ результат должен быть от 0 до 100")
        elif exam == "ОГЭ" and not (2 <= value <= 5):
            raise ValueError("Для ОГЭ результат должен быть от 2 до 5")
        return value

    model_config = ConfigDict(extra="ignore")


class ReviewAdd(ReviewBase):
    user_id: int


class ReviewPatch(BaseModel):
    result: int | None = None
    review: str | None = None

    @field_validator("result")
    @classmethod
    def validate_result(cls, value, info):
        exam = info.data.get("exam")

        # Проверяем только если передан exam и result
        if value is None or exam is None:
            return value

        if exam == "ЕГЭ" and not (0 <= value <= 100):
            raise ValueError("Для ЕГЭ результат должен быть от 0 до 100")
        elif exam == "ОГЭ" and not (2 <= value <= 5):
            raise ValueError("Для ОГЭ результат должен быть от 2 до 5")

        return value

    model_config = ConfigDict(extra="ignore")


class ReviewsGetBySuperUser(ReviewBase):
    user_id: int
    id: int


class ReviewSelfGet(Review):
    user_id: int
    id: int
