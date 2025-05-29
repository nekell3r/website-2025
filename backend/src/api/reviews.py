import sys

from fastapi import APIRouter, Body
from pathlib import Path

from src.dependencies.auth import UserIdDep, PaginationDep
from src.dependencies.db import DBDep
from src.schemas.reviews import (
    ReviewAddRequest,
    ReviewPatch,
)
from src.services.reviews import ReviewsService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["Отзывы"])


@router.get(
    "/{exam_type}",
    summary="Получение отзывов всех пользователей по типу экзамена",
    description="Принимает на вход тип экзамена (например, ЕГЭ или ОГЭ) как часть пути. "
    "Также принимает параметры пагинации per_page и page. "
    "Эти параметры опциональны, но на фронте мы реализуем именно такой механизм",
)
async def get_reviews_by_exam_type(
    exam_type: str, db: DBDep, pagination: PaginationDep, user_id: UserIdDep
):
    return await ReviewsService().get_reviews(exam_type, db, pagination)


@router.post(
    "",
    summary="Добавление отзыва",
    description="Добавление отзыва авторизованного пользователя в бд. Механизм проверки авторизации - аналогичный получению"
    "Возвращает ответ формата {'status' : 'ok', 'review' : review}",
)
async def create_review(
    db: DBDep,
    user_id: UserIdDep,
    review_data: ReviewAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Отзыв 1",
                "value": {
                    "exam": "ЕГЭ",
                    "result": 97,
                    "review": "Замечательный учитель",
                },
            },
            "2": {
                "summary": "Отзыв 2",
                "value": {
                    "exam": "ОГЭ",
                    "result": 4,
                    "review": "кайфово было вообще блин",
                },
            },
        }
    ),
):
    result = await ReviewsService().create_review(db, user_id, review_data)
    return result


@router.patch(
    "/{review_id}",
    summary="Изменение отзывааа",
    description="Изменение отзыва в бд. Принимается id отзыва(из личного кабинета). Если с момента последнего"
    " редактирования прошло меньше ЧАСА, то возвращается 409 ошибка с информацией о том, когда можно обновить отзыв."
    " Если прошло больше часа, изменения вносятся и возвращается ответ формата {'status' : 'ok'}",
)
async def update_review(
    db: DBDep,
    user_id: UserIdDep,
    review_id: int,
    review_data: ReviewPatch = Body(
        openapi_examples={
            "1": {
                "summary": "Отзыв 1",
                "value": {
                    "result": 97,
                    "review": "Замечательный учитель",
                },
            },
            "2": {
                "summary": "Отзыв 2",
                "value": {
                    "result": 4,
                    "review": "кайфово было вообще блин",
                },
            },
        }
    ),
):
    result = await ReviewsService().edit_review(db, user_id, review_id, review_data)
    return result


@router.delete(
    "/{review_id}",
    summary="Удаление отзыва",
    description="Удаление отзыва по id из личного кабинета. Принимает на вход только id отзыва. Если отзыва не существует, вернется ошибка 404."
    "Если удалено успешно, ответ формата {'status' : 'ok'}",
)
async def delete_review(db: DBDep, user_id: UserIdDep, review_id: int):
    result = await ReviewsService().delete_review(db, user_id, review_id)
    return result
