from src.dependencies.auth import UserRoleDep
from src.dependencies.db import DBDep
from src.schemas.products import Product, ProductPatch
from src.exceptions.service_exceptions import (
    AdminNoRightsServiceException,
    ProductNotFoundServiceException,
    ProductAlreadyExistsServiceException,
)
from src.exceptions.db_exceptions import ProductNotFoundException


class ProductService:
    async def get_products(self, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise AdminNoRightsServiceException
        try:
            result = await db.products.get_all()
            return result
        except ProductNotFoundException:
            raise ProductNotFoundServiceException

    async def get_product(self, slug: str, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise AdminNoRightsServiceException
        try:
            result = await db.products.get_one_or_none(slug=slug)
            if result is None:
                raise ProductNotFoundServiceException
            return result
        except ProductNotFoundException:
            raise ProductNotFoundServiceException

    async def add_product(self, data: Product, is_super: UserRoleDep, db: DBDep):
        if not is_super:
            raise AdminNoRightsServiceException

        try:
            # Check if product with this slug already exists
            existing_product = await db.products.get_one_or_none(slug=data.slug)
            if existing_product is not None:
                raise ProductAlreadyExistsServiceException

            await db.products.add(data)
            await db.commit()
            return {"status": "Ok, product is added"}
        except ProductNotFoundException:
            raise ProductNotFoundServiceException

    async def edit_product(
        self, data: ProductPatch, slug: str, is_super: UserRoleDep, db: DBDep
    ):
        if not is_super:
            raise AdminNoRightsServiceException
        try:
            product = await db.products.get_one_or_none(slug=slug)
            if product is None:
                raise ProductNotFoundServiceException
            await db.products.edit(data, exclude_unset_for_model=True, slug=slug)
            await db.commit()
            return {"status": "Ok, product is edited"}
        except ProductNotFoundException:
            raise ProductNotFoundServiceException
