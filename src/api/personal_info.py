import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.dependencies.auth import UserIdDep, PaginationDep
from src.dependencies.db import DBDep
from src.schemas.personal_info import BoughtProduct
from src.schemas.users import (
    UserUpdate,
)

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/me", tags=["Персональная информация"])



@router.get(
    "/info",
    summary="Получение данных о пользователе",
    description="Получение всех данных о пользователе в личном кабинете: купленные продукты, id, имя, телефон, почта, роль",
)
async def get_me(
    db: DBDep,
    user_id: UserIdDep,

):
    user = await db.users.get_one_or_none(id=user_id)
    return user

@router.get(
    "/reviews",
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
    data = await db.reviews.get_mine(
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        current_user_id=current_user_id,
    )
    if not data:
        raise HTTPException(404, detail="Отзывы не найдены")
    return {"status": "Ok", "result": data}


@router.get(
    "/purchases",
    summary="Получение всех покупок пользователя"
    )
async def get_user_purchases(
        user_id: UserIdDep,
        db: DBDep
):
    purchases = await db.purchases.get_all(user_id=user_id, status="Paid")
    if not purchases:
        raise HTTPException(404, detail="Покупки не найдены")
    names = {
        1: "ОГЭ",
        2: "ЕГЭ",
        3: "Материалы для уроков(русский язык)",
        4: "Материалы для уроков(литература)",
        5: "Материалы для уроков(лит+рус)"
    }
    return [
        BoughtProduct(product_id=p.product_id,
                      product_name=names.get(p.product_id, "Unknown"),
                      purchase_time=p.paid_at)
        for p in purchases
    ]

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
    user = await db.users.get_one_or_none(id=user_id)
    if user is None:
        raise HTTPException(404, detail="Пользователь не найден")
    await db.users.edit(new_data, exclude_unset=True, phone=user.phone)
    await db.commit()
    return {"status": "Ok, данные обновлены"}

