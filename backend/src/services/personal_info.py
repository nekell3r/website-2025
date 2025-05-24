from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.schemas.users import UserUpdate, User
from src.exceptions.db_exceptions import (
    UserNotFoundException,
    ProductNotFoundException,
    PurchaseNotFoundException,
)
from src.exceptions.service_exceptions import (
    UserNotFoundServiceException,
    ProductNotFoundServiceException,
    ProductNotPurchasedServiceException,
)


class InfoService:
    async def get_user_info(self, user_id: UserIdDep, db: DBDep) -> User:
        try:
            user = await db.users.get_one(id=user_id)
        except UserNotFoundException:
            raise UserNotFoundServiceException
        return user

    async def update_user_info(
        self, new_data: UserUpdate, user_id: UserIdDep, db: DBDep
    ):
        try:
            await db.users.get_one(id=user_id)
        except UserNotFoundException:
            raise UserNotFoundServiceException
        await db.users.edit(data=new_data, exclude_unset_for_model=True, id=user_id)
        await db.commit()
        return {"status": "User info updated"}

    async def get_product(self, slug: str, user_id: UserIdDep, db: DBDep):
        try:
            await db.users.get_one(id=user_id)
        except UserNotFoundException:
            raise UserNotFoundServiceException
        try:
            product = await db.products.get_one(slug=slug)
        except ProductNotFoundException:
            raise ProductNotFoundServiceException
        try:
            await db.purchases.get_one(
                product_slug=slug, user_id=user_id, status="Paid"
            )
        except PurchaseNotFoundException:
            raise ProductNotPurchasedServiceException
        return product
