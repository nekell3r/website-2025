from fastapi import HTTPException


from src.dependencies.auth import UserRoleDep
from src.dependencies.db import DBDep
from src.schemas.products import Product, ProductPatch


class ProductService:
    async def get_products(self, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise HTTPException(
                409, detail="Неавторизованный для получения продуктов пользователь"
            )
        result = await db.products.get_all()
        if result is None:
            raise HTTPException(
                404, detail="Продукты не найдены"
            )
        return result

    async def get_product(self, slug: str, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise HTTPException(
                409, detail="Неавторизованный для получения продуктов пользователь"
            )
        result = await db.products.get_one_or_none(slug=slug)
        if result is None:
            raise HTTPException(404, detail="Продукт не найден")
        return result


    async def add_product(self, data: Product, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise HTTPException(
                409, detail="Неавторизованный для добавления продукта пользователь"
            )
        await db.products.add(data)
        await db.commit()
        return {"status": "Ok, product is added"}

    async def edit_product(self, data: ProductPatch, slug: str, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise HTTPException(
                409, detail="Неавторизованный для изменения продукта пользователь"
            )
        product = await db.products.get_one_or_none(slug=slug)
        if product is None:
            raise HTTPException(404, detail="Продукт не найден")
        await db.products.edit(data, exclude_unset=True, slug=slug)
        await db.commit()
        return {"status": "Ok, product is edited"}