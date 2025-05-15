from src.dependencies.auth import PaginationDep, UserRoleDep
from src.dependencies.db import DBDep
from fastapi import HTTPException

from src.schemas.reviews import ReviewAdd, ReviewAddRequest


class ReviewService:
    async def get_reviews_without_id(
        self,
        db: DBDep,
        pagination: PaginationDep,
    ):
        per_page = pagination.per_page or 5
        data = await db.reviews.get_all(
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )
        if not data:
            raise HTTPException(404, detail="Отзывы не найдены")
        return data

    async def get_reviews_with_id(
        self,
        db: DBDep,
        pagination: PaginationDep,
    ):
        per_page = pagination.per_page or 5
        data = await db.reviews.superuser_get_all(
            limit=per_page, offset=per_page * (pagination.page - 1)
        )
        if not data:
            raise HTTPException(404, detail="Отзывы не найдены")
        return data

    async def get_my_reviews(
            self,
            db: DBDep,
            user_id: int,
            pagination: PaginationDep,
    ):
        per_page = pagination.per_page or 5
        data = await db.reviews.get_mine(
            limit=per_page,
            offset=per_page * (pagination.page - 1),
            current_user_id=user_id,
        )
        if not data:
            raise HTTPException(404, detail="Отзывы не найдены")
        return data

    async def get_reviews(
        self,
        is_super: UserRoleDep,
        db: DBDep,
        pagination: PaginationDep,
    ):
        if is_super:
            data = await self.get_reviews_with_id(db, pagination)
        else:
            data = await self.get_reviews_without_id(db, pagination)
        return data

    async def create_review(
        self,
        db: DBDep,
        user_id: int,
        review_data: ReviewAddRequest,
    ):
        data = ReviewAdd(
            user_id=user_id,
            review=review_data.review,
            exam=review_data.exam,
            result=review_data.result,
        )
        if data.exam not in ["ЕГЭ", "ОГЭ"]:
            raise HTTPException(400, detail="Неверный экзамен, возможные варианты - ЕГЭ, ОГЭ")

        product_id = (await db.products.get_one_or_none(name=data.exam)).id
        purchase = await db.purchases.get_one_or_none(product_id=product_id, user_id=user_id, status="Paid")
        if not purchase:
            raise HTTPException(404, detail="Пользователь не купил данный продукт")

        await db.reviews.add(data)
        await db.commit()
        return {"status" : "Ok"}