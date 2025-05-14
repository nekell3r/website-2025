import sys

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path

from src.api.dependencies import DBDep, UserRoleDep
from src.schemas.products import ProductPatch, ProductAdd

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/products", tags=["Продукты(доступ суперюзера)"])


@router.get("/all", summary="Все продукты. Используется в личном кабинете суперюзера")
async def get_products(is_super_user: UserRoleDep, db: DBDep):
    if not is_super_user:
        raise HTTPException(
            409, detail="Неавторизованный для получения продуктов пользователь"
        )
    result = await db.products.get_all()
    return {"status": "Ok", "result": result}


@router.get("/{slug}", summary="Определенный продукт")
async def get_product(
        is_super_user: UserRoleDep,
        db: DBDep,
        slug: str
):
    if not is_super_user:
        raise HTTPException(
            409, detail="Неавторизованный для получения продуктов пользователь"
        )
    result = await db.products.get_one_or_none(slug =  slug)
    if result is None:
        raise HTTPException(404, detail="Продукт не найден")
    return {"status": "Ok", "result": result}


@router.post("/add", summary="Добавление продукта")
async def add_product(
    is_super_user: UserRoleDep,
    db: DBDep,
    data: ProductAdd = Body(
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
    if not is_super_user:
        raise HTTPException(
            409, detail="Неавторизованный для добавления продукта пользователь"
        )
    result = await db.products.add(data)
    await db.commit()
    return {
        "status": "Ok, product is added",
        "data": db.products.mapper.map_to_domain_entity(result),
    }


@router.patch(
    "/update/{slug}",
    summary="Изменение продукта. Используется в лк суперюзера при нажатии кнопки редактирования определенного отзыва",
)
async def update_product(
    is_super_user: UserRoleDep,
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
) -> None:
    if not is_super_user:
        raise HTTPException(
            409, detail="Неавторизованный для изменения продукта пользователь"
        )
    product = await db.products.get_one_or_none(slug=slug)
    if product is None:
        raise HTTPException(404, detail="Продукт не найден")
    await db.products.edit(data, exclude_unset=True, slug=slug)
    await db.commit()
