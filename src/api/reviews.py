import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.api.dependencies import UserIdDep, PaginationDep
from src.database import async_session_maker
from src.repositories.reviews import ReviewsRepository
from src.schemas.reviews import ReviewAdd, ReviewAddRequest, ReviewPatch

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get(
    "/all",
    summary="Получение отзывов всех пользователей",
    description="Возвращает отзывы с пагинацией",
)
async def get_reviews(pagination: PaginationDep):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await ReviewsRepository(session).get_all(
            limit=per_page, offset=per_page * (pagination.page - 1)
        )


@router.get(
    "/mine",
    summary="Получение отзывов авторизованного пользователя",
    description="Получает отзыв пользователя, данные которого сохранены в куках - если данных нет, то возвращает ошибку 401 с описанием(это еще не сделано)",
)
async def get_current_user_reviews(user_id: UserIdDep, pagination: PaginationDep):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await ReviewsRepository(session).get_mine(
            limit=per_page,
            offset=per_page * (pagination.page - 1),
            current_user_id=user_id,
        )


@router.post(
    "/add",
    summary="Добавление отзыва",
    description="Добавление отзыва в таблицу всех отзывов, также сохраняется информация об авторе",
)
async def create_review(
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
    async with async_session_maker() as session:
        review = await ReviewsRepository(session).add(new_review_data)
        await session.commit()
    return {"status": "OK, Review created", "review": review}


@router.post(
    "/update",
    summary="Изменение отзыва",
    description="Изменение отзыва в таблице всех отзывов, обновляется значение момента последнего"
    "редактирования, информация об авторе остаётся неизменной. Если с момента последнего редактирования прошло меньше ЧАСА, то возвращается 409 ошибка с информацией"
    "о том, когда можно обновить отзыв",
)
async def update_review(
    user_id: UserIdDep,
    review_id: int = Body(),
    review_data: ReviewPatch = Body(
        openapi_examples={
            "1": {
                "summary": "Отзыв 1",
                "value": {
                    "exam": "ЕГЭ",
                    "result": 100,
                },
            },
            "2": {
                "summary": "Отзыв 2",
                "value": {
                    "exam": "ОГЭ",
                    "result": 5,
                },
            },
        }
    ),
):
    async with async_session_maker() as session:
        await ReviewsRepository(session).edit(
            review_data, exclude_unset=True, id=review_id, user_id=user_id
        )
        await session.commit()
    return {"status": "Ok, review is edited"}
