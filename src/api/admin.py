import sys

from fastapi import APIRouter, Body
from pathlib import Path

from src.dependencies.auth import UserRoleDep, PaginationDep
from src.dependencies.db import DBDep
from src.schemas.products import Product, ProductPatch
from src.services.products import ProductService
from src.services.reviews import ReviewsService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/admin", tags=["Админка"])

@router.get(
    "/reviews"
)
async def get_reviews(
    is_super: UserRoleDep,
    db: DBDep,
    pagination: PaginationDep,
    ):
        return await ReviewsService().admin_get_reviews(is_super, db, pagination)

@router.delete(
    "/reviews/{review_id}",
    summary="Удаление отзыва",
    description="Удаляет отзыв по id. id передается в теле запроса в формате json. "
                "Пример: {\"id\": 1}. Возвращает статус 200 и сообщение об ус��ешном удалении",
)
async def delete_review(
    is_super: UserRoleDep,
    db: DBDep,
    review_id: int,
):
    return await ReviewsService().admin_delete_review(db, is_super, review_id)


@router.get("/products", summary="Все продукты. Используется в личном кабинете суперюзера")
async def get_products(is_super: UserRoleDep, db: DBDep):
    return await ProductService().get_products(is_super=is_super, db=db)


@router.get("/products/{slug}", summary="Определенный продукт")
async def get_product(
        is_super: UserRoleDep,
        db: DBDep,
        slug: str
):
    return await ProductService().get_product(slug=slug, is_super=is_super, db=db)


@router.post("/products", summary="Добавление продукта")
async def add_product(
    is_super: UserRoleDep,
    db: DBDep,
    data: Product = Body(
        openapi_examples={
            "1": {
                "summary": "ОГЭ",
                "value": {
                    "name": "ОГЭ",
                    "price": 2000,
                    "download_link": "https://example.com/oge",
                    "description": "Тестовое описание для ОГЭ",
                    "slug": "oge",
                },
            },
            "2": {
                "summary": "ЕГЭ",
                "value": {
                    "name": "ЕГЭ",
                    "price": 3000,
                    "download_link": "https://example.com/ege",
                    "description": "Тестовое описание для ЕГЭ",
                    "slug": "ege",
                },
            },
        }
    ),
):
    return await ProductService().add_product(data=data, is_super=is_super, db=db)


@router.patch(
    "/products/{slug}",
    summary="Изменение продукта. Используется в лк суперюзера при нажатии кнопки редактирования определенного отзыва",
)
async def update_product(
    is_super: UserRoleDep,
    db: DBDep,
    slug: str,
    data: ProductPatch = Body(
        openapi_examples={
            "1": {
                "summary": "ОГЭ",
                "value": {
                    "name": "ОГЭ",
                    "price": 2000,
                    "download_link": "https://example.com/oge",
                    "description": "Тестовое описание для ОГЭ",
                },
            },
            "2": {
                "summary": "ЕГЭ",
                "value": {
                    "name": "ЕГЭ",
                    "price": 3000,
                    "download_link": "https://example.com/ege",
                    "description": "Тестовое описание для ЕГЭ",
                },
            },
        }
    ),
):
    return await ProductService().edit_product(data=data, slug=slug, is_super=is_super, db=db)
