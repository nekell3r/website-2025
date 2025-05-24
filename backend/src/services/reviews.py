from datetime import datetime, timezone, timedelta

from src.dependencies.auth import PaginationDep, UserRoleDep
from src.dependencies.db import DBDep
from fastapi import HTTPException

from src.exceptions.db_exceptions import ReviewNotFoundException, PurchaseNotFoundException, ProductNotFoundException
from src.exceptions.service_exceptions import (ReviewNoRightsServiceException,
                                               ReviewIsExistingServiceException,
                                               ReviewWrongFormatServiceException,
                                               ReviewNotFoundServiceException,
                                               PurchaseNotFoundServiceException,
                                               ProductNotFoundServiceException,
                                               MadRussianServiceException,
                                               ReviewEditConflictServiceException,
                                               AdminNoRightsServiceException)
from src.schemas.reviews import ReviewAdd, ReviewAddRequest, ReviewPatch


class ReviewsService:
    async def get_reviews(
        self,
        exam_from_api: str,
        db: DBDep,
        pagination: PaginationDep,
    ):
        db_exam_value_for_filter = ""
        if exam_from_api == "ege":
            db_exam_value_for_filter = "ЕГЭ"
        elif exam_from_api == "oge":
            db_exam_value_for_filter = "ОГЭ"
        else:
            raise ReviewWrongFormatServiceException(detail=f"Недопустимый тип экзамена в URL: {exam_from_api}. Ожидается 'ege' или 'oge'.")

        per_page = pagination.per_page or 5
        try:
            data = await db.reviews.get_all_filtered(
                limit=per_page,
                offset=per_page * (pagination.page - 1),
                exam=db_exam_value_for_filter,
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
        # Используем exam как есть из запроса ("ЕГЭ" или "ОГЭ")
        data = ReviewAdd(
            user_id=user_id,
            review=review_data.review,
            exam=review_data.exam, # Используем оригинальное значение review_data.exam
            result=review_data.result,
        )
        # Проверка формата exam на оригинальных значениях
        if data.exam not in ["ЕГЭ", "ОГЭ"]:
            raise ReviewWrongFormatServiceException
        try:
            # Для поиска продукта используем оригинальное значение exam из запроса
            product_slug = (await db.products.get_one(name=data.exam)).slug
            # Для поиска покупки также используем product_slug, полученный по оригинальному имени экзамена
            purchase = await db.purchases.get_one(product_slug=product_slug, user_id=user_id, status="Paid")
        except ProductNotFoundException:
            raise ProductNotFoundServiceException
        except PurchaseNotFoundException:
            raise PurchaseNotFoundServiceException

        # Проверяем существующий отзыв, используя exam как есть ("ЕГЭ" или "ОГЭ")
        current_review = await db.reviews.get_one_or_none(exam=data.exam, user_id=user_id)
        if current_review:
            raise ReviewIsExistingServiceException

        # Добавляем отзыв, где data.exam это "ЕГЭ" или "ОГЭ"
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
            raise ReviewNoRightsServiceException

        now_utc = datetime.now(timezone.utc)
        delta = now_utc - review.edited_at
        if delta < timedelta(hours=1):
            minutes_left = 60 - int(delta.total_seconds() // 60)
            raise ReviewEditConflictServiceException(
                detail=f"Редактирование возможно только через {minutes_left} мин."
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
            review = await db.reviews.get_one_with_id(id=review_id)
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException
        if review.user_id != user_id:
            raise ReviewNoRightsServiceException

        await db.reviews.delete(id=review_id)
        await db.commit()
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
            raise AdminNoRightsServiceException
        try:
            data = await db.reviews.get_all_with_id(limit=per_page, offset=per_page * (pagination.page - 1))
        except ReviewNotFoundException:
             raise ReviewNotFoundServiceException
        if not data:
            raise ReviewNotFoundServiceException
        return data

    async def admin_delete_review(
            self,
            db: DBDep,
            is_super: UserRoleDep,
            review_id: int
    ):
        try:
            review = await db.reviews.get_one_with_id(id=review_id)
        except ReviewNotFoundException:
            raise ReviewNotFoundServiceException
        if review is None:
            raise ReviewNotFoundServiceException
        if not is_super:
            raise AdminNoRightsServiceException
        await db.reviews.delete(id=review_id)
        await db.commit()
        return {"status": "ok"}
