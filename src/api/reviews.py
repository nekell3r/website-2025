import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.dependencies.auth import UserIdDep, PaginationDep, UserRoleDep
from src.dependencies.db import DBDep
from src.schemas.reviews import (
    ReviewAddRequest,
    ReviewPatch,
    ReviewAdd,
)
from src.services.reviews import ReviewService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["Отзывы"])

super_user_router = APIRouter(
    prefix="/superuser/reviews", tags=["Отзывы(доступ суперпользователя)"]
)


@super_user_router.delete(
    "/{review_id}",
    summary="Удаление определенного отзыва. На вход получает id отзыва",
)
async def superuser_delete_review(
    db: DBDep, review_id: int, is_super_user: UserRoleDep
):
    if not is_super_user:
        raise HTTPException(
            409, "Неавторизованный для удаления чужих отзывов пользователь"
        )
    try:
        await db.reviews.delete(id=review_id)
    except HTTPException:
        raise HTTPException(404, detail="Отзыв не найден")
    await db.commit()
    return {"status": "Ok, review is deleted"}


@router.get(
    "",
    summary="Получение отзывов всех пользователей",
    description="Принимает на вход per_page - количество отзывов за 1 прогрузку, page - номер прогрузки(страницы/блока отзывов). "
    "Эти параметры опциональны, но на фронте мы реализуем именно такой механизм",
)
async def get_reviews(is_super: UserRoleDep, db: DBDep, pagination: PaginationDep):
    return await ReviewService().get_reviews(is_super, db, pagination)

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
    result = await ReviewService().create_review(db, user_id, review_data)
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
    review = await db.reviews.get_definite_mine(review_id=review_id)
    if review is None:
        raise HTTPException(404, detail="Отзыв не найден")
    await db.reviews.edit(
        review_data, exclude_unset=True, id=review_id, user_id=user_id
    )
    await db.commit()
    return {"status": "Ok, review is edited"}


@router.delete(
    "/{review_id}",
    summary="Удаление отзыва",
    description="Удаление отзыва по id из личного кабинета. Принимает на вход только id отзыва. Если отзыва не существует, вернется ошибка 404."
    "Если удалено успешно, ответ формата {'status' : 'ok'}",
)
async def delete_review(db: DBDep, user_id: UserIdDep, review_id: int):
    review = await db.reviews.get_definite_mine(review_id=review_id)
    if review is None:
        raise HTTPException(404, detail="Отзыв не найден")
    if review.user_id == user_id:
        await db.reviews.delete(id=review_id)
    await db.commit()
    return {"status": "OK, review is deleted"}
