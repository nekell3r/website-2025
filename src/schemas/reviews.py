from pydantic import BaseModel, Field, ConfigDict


from pydantic import BaseModel, field_validator, Field
from typing import Literal


class ReviewAddRequest(BaseModel):
    exam: Literal["ЕГЭ", "ОГЭ"]
    result: int = Field(..., ge=0)
    review: str

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


class ReviewPatch(BaseModel):
    exam: Literal["ЕГЭ", "ОГЭ"] | None = None
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


class ReviewAdd(ReviewAddRequest):
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class Review(ReviewAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)
