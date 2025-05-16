import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.dependencies.auth import UserRoleDep
from src.dependencies.db import DBDep
from src.schemas.products import ProductPatch, Product
from src.services.products import ProductService

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/products", tags=["Продукты(доступ суперюзера)"])


@router.get("", summary="Все продукты. Используется в личном кабинете суперюзера")
async def get_products(is_super: UserRoleDep, db: DBDep):
    return await ProductService().get_products(is_super=is_super, db=db)


@router.get("/{slug}", summary="Определенный продукт")
async def get_product(
        is_super: UserRoleDep,
        db: DBDep,
        slug: str
):
    return await ProductService().get_product(slug=slug, is_super=is_super, db=db)


@router.post("", summary="Добавление продукта")
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
    "/{slug}",
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
