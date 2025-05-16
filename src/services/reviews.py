from datetime import datetime, timezone, timedelta

from src.dependencies.auth import PaginationDep, UserRoleDep
from src.dependencies.db import DBDep
from fastapi import HTTPException

from src.schemas.reviews import ReviewAdd, ReviewAddRequest, ReviewPatch


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
    ):
        page = 1
        per_page = 2
        data = await db.reviews.get_all_filtered(limit=per_page, offset=per_page * (page - 1), user_id=user_id)
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

        product_slug = (await db.products.get_one_or_none(name=data.exam)).slug
        purchase = await db.purchases.get_one_or_none(product_slug=product_slug, user_id=user_id, status="Paid")
        if not purchase:
            raise HTTPException(404, detail="Пользователь не купил данный продукт")
        current_review = await db.reviews.get_one_or_none(exam=data.exam, user_id=user_id)
        if current_review:
            raise HTTPException(409, detail="Пользователь уже оставил отзыв на данный продукт")
        await db.reviews.add(data)
        await db.commit()
        return {"status" : "Ok"}
    async def edit_review(
            self,
            db: DBDep,
            user_id: int,
            review_id: int,
            review_data: ReviewPatch,
    ):
        review = await db.reviews.get_one_or_none_with_id(id=review_id)
        if not review:
            raise HTTPException(404, detail="Отзыв не найден")
        if review.user_id != user_id:
            raise HTTPException(403, detail="У вас нет прав редактировать этот отзыв")
        now_utc = datetime.now(timezone.utc)
        delta = now_utc - review.edited_at
        if delta < timedelta(hours=1):
            minutes_left = 60 - int(delta.total_seconds() // 60)
            raise HTTPException(
                status_code=409,
                detail=f"Редактирование возможно только через {minutes_left} мин.",
            )

        await db.reviews.edit(review_data, exclude_unset=True, id=review_id)
        await db.commit()
        return {"status": "Ok"}
    async def delete_review(
            self,
            db: DBDep,
            is_super: UserRoleDep,
            user_id: int,
            review_id: int
    ):
        review = await db.reviews.get_one_or_none_with_id(id=review_id)
        if review is None:
            raise HTTPException(404, detail="Отзыв не найден")
        if is_super:
            await db.reviews.delete(id=review_id)
        else:
            if review.user_id != user_id:
                raise HTTPException(
                    403, "Неавторизованный для удаления чужих отзывов пользователь"
                )
            await db.reviews.delete(id=review_id)
        await db.commit()
        return {"status": "ok"}