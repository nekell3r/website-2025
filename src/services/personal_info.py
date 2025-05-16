from fastapi import HTTPException


from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.schemas.users import UserUpdate


class InfoService:
    async def get_user_info(self, user_id: UserIdDep, db: DBDep):
        user = await db.users.get_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user_info(self, new_data: UserUpdate, user_id: UserIdDep, db: DBDep):
        user = await db.users.get_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await db.users.edit(new_data, exclude_unset=True, phone=user.phone)
        await db.commit()
        return {"status": "Ok, данные обновлены"}

    async def get_product(self, slug: str, user_id: UserIdDep, db: DBDep):
        user = await db.users.get_one_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        product = await db.products.get_one_or_none(slug=slug)
        if product is None:
            raise HTTPException(404, detail="Продукт не найден")
        result = await db.purchases.get_one_or_none(product_slug=slug, user_id=user_id, status="Paid")
        if result is None:
            raise HTTPException(404, detail="Продукт не куплен")
        return product