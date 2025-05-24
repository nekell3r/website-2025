import sys
from pathlib import Path

from fastapi import APIRouter, Body

from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.schemas.users import UserUpdate
# Импорты для возвращаемых эндпоинтов
from src.services.reviews import ReviewsService
from src.services.payments import PaymentsService
from src.services.personal_info import InfoService # InfoService уже импортирован, но для ясности

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/me", tags=["Персональная информация"])


@router.get(
    "/info",
    summary="Получение данных о пользователе",
    description="Получение всех данных о пользователе в личном кабинете: id, имя, телефон, почта, роль",
)
async def get_me(
    db: DBDep,
    user_id: UserIdDep,
):
    return await InfoService().get_user_info(user_id=user_id, db=db)

@router.patch("/info", summary="Изменение данных о пользователе")
async def update_data(
    db: DBDep,
    user_id: UserIdDep,
    new_data: UserUpdate = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь 1",
                "value": {"name": "Павел", "surname": "Жабский", "grade": 11},
            }
        }
    ),
):
    return await InfoService().update_user_info(new_data=new_data, user_id=user_id, db=db)

# Возвращаем эндпоинт для получения отзывов пользователя
@router.get(
    "/reviews",
    summary="Получение отзывов авторизованного пользователя",
    description="Получает отзывы авторизованного пользователя.",
)
async def get_current_user_reviews(
    db: DBDep,
    user_id: UserIdDep
):
    return await ReviewsService().get_my_reviews(user_id=user_id, db=db)

# Возвращаем эндпоинт для получения покупок пользователя
@router.get(
    "/purchases",
    summary="Получение всех покупок пользователя"
)
async def get_user_purchases(
    user_id: UserIdDep,
    db: DBDep
):
    return await PaymentsService().get_purchases(user_id=user_id, db=db)

# Возвращаем эндпоинт для получения информации о купленном продукте
@router.get("/purchases/{slug}", summary="Получение информации о купленном продукте (проверка покупки)")
async def get_purchased_product_info(
    slug: str,
    db: DBDep,
    user_id: UserIdDep
):
    # Этот метод в InfoService проверяет, что продукт куплен, и возвращает информацию о продукте
    return await InfoService().get_product(slug=slug, user_id=user_id, db=db)