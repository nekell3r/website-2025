import sys

from fastapi import APIRouter, Body, Response, HTTPException, Request
from pathlib import Path

from src.api.dependencies import UserIdDep, DBDep
from src.init import redis_manager
from src.schemas.personal_info import BoughtProduct
from src.schemas.users import (
    UserAdd,
    UserRequestAdd,
    UserLogin,
    PhoneInput,
    PhoneWithCode,
    EmailInput,
    PhoneWithPassword,
    UserWithHashedPassword,
    UserUpdate,
    EmailWithCode,
)
from src.services.auth import AuthService

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
    "/purchases",
    summary="Получение всех покупок пользователя"
    )
async def get_user_purchases(
        user_id: UserIdDep,
        db: DBDep
):
    purchases = await db.purchases.get_all(user_id=user_id)
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

@router.post("/update", summary="Изменение данных о пользователе")
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
    await db.users.edit(new_data, exclude_unset=True, telephone=user.telephone)
    await db.commit()
    return {"status": "Ok, данные обновлены"}

