from src.models.reviews import ReviewsOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.reviews import (
    ReviewBase,
    ReviewPatch,
    ReviewsGetBySuperUser,
    ReviewSelfGet,
)
from src.models.users import UsersOrm
from src.schemas.users import User
from src.models.products import ProductsOrm
from src.models.purchases import PurchasesOrm
from src.schemas.products import Product
from src.schemas.payments import Purchase


class UsersMapper(DataMapper):
    schema = User
    db_model = UsersOrm


class SuperUserReviewsMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewsGetBySuperUser


class ReviewsSelfMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewSelfGet


class ReviewsMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewBase


class ReviewsPatchMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewPatch


class ProductsMapper(DataMapper):
    db_model = ProductsOrm
    schema = Product


class PurchasesMapper(DataMapper):
    db_model = PurchasesOrm
    schema = Purchase
