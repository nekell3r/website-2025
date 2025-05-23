from datetime import datetime, timezone, timedelta

from src.dependencies.auth import PaginationDep, UserRoleDep
from src.dependencies.db import DBDep
from fastapi import HTTPException

from src.exceptions.exceptions import ReviewNotFoundException, ReviewNotFoundServiceException, ProductNotFoundException, \
    ProductNotFoundHTTPException, PurchaseNotFoundHTTPException, PurchaseNotFoundException, \
    ReviewIsExistingHTTPException, ReviewNoRightsHTTPException, MadRussianHTTPException, \
    ReviewWrongFormatHTTPException
from src.schemas.reviews import ReviewAdd, ReviewAddRequest, ReviewPatch


class ReviewsService:
    async def get_reviews(
        self,
        exam: str,
        db: DBDep,
        pagination: PaginationDep,
    ):
        if exam == "ЕГЭ":
            db_exam = "ege"
        elif exam == "ОГЭ":
            db_exam = "oge"
        else:
            raise ReviewWrongFormatHTTPException
        per_page = pagination.per_page or 5
        try:
            data = await db.reviews.get_all_filtered(
                limit=per_page,
                offset=per_page * (pagination.page - 1),
                exam=db_exam,
            )
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException
        return data

    async def get_reviews_with_id(
        self,
        db: DBDep,
        pagination: PaginationDep,
    ):
        per_page = pagination.per_page or 5
        try:
            data = await db.reviews.get_all_with_id(limit=per_page, offset=per_page * (pagination.page - 1))
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException
        return data

    async def get_my_reviews(
            self,
            db: DBDep,
            user_id: int,
    ):
        page = 1
        per_page = 2
        try:
            data = await db.reviews.get_all_filtered(limit=per_page, offset=per_page * (page - 1), user_id=user_id)
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException
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
            raise ReviewWrongFormatHTTPException
        try:
            product_slug = (await db.products.get_one(name=data.exam)).slug
            purchase = await db.purchases.get_one(product_slug=product_slug, user_id=user_id, status="Paid")
        except ProductNotFoundException:
            raise ProductNotFoundHTTPException
        except PurchaseNotFoundException:
            raise PurchaseNotFoundHTTPException

        current_review = await db.reviews.get_one(exam=data.exam, user_id=user_id)
        if current_review:
            raise ReviewIsExistingHTTPException

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
        try:
            review = await db.reviews.get_one_with_id(id=review_id)
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException

        if review.user_id != user_id:
            raise ReviewNoRightsHTTPException

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
            user_id: int,
            review_id: int
    ):
        try:
            try:
                review = await db.reviews.get_one_with_id(id=review_id)
            except ReviewNotFoundException:
                raise ReviewNotFoundServiceException
            if review.user_id != user_id:
                raise ReviewNoRightsHTTPException

            await db.reviews.delete(id=review_id)
            await db.commit()
        except:
            raise MadRussianHTTPException
        await db.commit()
        return {"status": "ok"}

    async def admin_get_reviews(
        self,
        is_super: UserRoleDep,
        db: DBDep,
        pagination: PaginationDep,
    ):
        per_page = pagination.per_page or 5
        if not is_super:
            raise HTTPException(403, detail="Неавторизованный пользователь")
        data = await db.reviews.get_all_with_id(limit=per_page, offset=per_page * (pagination.page - 1))
        if not data:
            raise HTTPException(404, detail="Отзывы не найдены")
        return data

    async def admin_delete_review(
            self,
            db: DBDep,
            is_super: UserRoleDep,
            review_id: int
    ):
        review = await db.reviews.get_one_with_id(id=review_id)
        if review is None:
            raise HTTPException(404, detail="Отзыв не найден")
        if not is_super:
            raise HTTPException(403, detail="Неавторизованный для удаления чужих отзывов пользователь")
        await db.reviews.delete(id=review_id)
        await db.commit()
        return {"status": "ok"}
