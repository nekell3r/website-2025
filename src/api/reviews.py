import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.api.dependencies import UserIdDep, PaginationDep, DBDep, UserRoleDep
from src.schemas.reviews import (
    ReviewBase,
    ReviewAddRequest,
    ReviewPatch,
    ReviewsGetBySuperUser,
    ReviewAdd,
)

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["Отзывы"])

super_user_router = APIRouter(
    prefix="/superuser/reviews", tags=["Отзывы(доступ суперпользователя)"]
)


@super_user_router.get(
    "/all",
    summary="Получение отзывов всех пользователей суперюзером. На вход получает page и per_page",
)
async def superuser_get_reviews(
    db: DBDep, is_super_user: UserRoleDep, pagination: PaginationDep
):
    if not is_super_user:
        raise HTTPException(
            409, detail="Неавторизованный для изменения продукта пользователь"
        )
    per_page = pagination.per_page or 5
    return await db.reviews.superuser_get_all(
        limit=per_page, offset=per_page * (pagination.page - 1)
    )


@super_user_router.delete(
    "/delete/{review_id}",
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
    "/all",
    summary="Получение отзывов всех пользователей",
    description="Принимает на вход per_page - количество отзывов за 1 прогрузку, page - номер прогрузки(страницы/блока отзывов). "
    "Эти параметры опциональны, но на фронте мы реализуем именно такой механизм",
)
async def get_reviews(db: DBDep, pagination: PaginationDep):
    per_page = pagination.per_page or 5
    return await db.reviews.get_all(
        limit=per_page, offset=per_page * (pagination.page - 1)
    )


@router.get(
    "/me",
    summary="Получение отзывов авторизованного пользователя",
    description="Получает отзывы авторизованного пользователя(данные которого хранятся в jwt-токене в куках. Если пользователь"
    "не авторизован или если токен устарел/не валиден, вернется ошибка 401 с описанием",
)
async def get_current_user_reviews(
    db: DBDep,
    current_user_id: UserIdDep,
    pagination: PaginationDep,
):
    per_page = pagination.per_page or 5
    return await db.reviews.get_mine(
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        current_user_id=current_user_id,
    )


@router.post(
    "/add",
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
    new_review_data = ReviewAdd(
        user_id=user_id,
        review=review_data.review,
        exam=review_data.exam,
        result=review_data.result,
    )
    review = await db.reviews.add(new_review_data)
    await db.commit()
    return {"status": "OK, Review created", "review": review}


@router.patch(
    "/update",
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
    await db.reviews.edit(
        review_data, exclude_unset=True, id=review_id, user_id=user_id
    )
    await db.commit()
    return {"status": "Ok, review is edited"}


@router.delete(
    "/delete/{review_id}",
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
