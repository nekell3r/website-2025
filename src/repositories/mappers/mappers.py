from src.models.reviews import ReviewsOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.reviews import Review, ReviewPatch, ReviewAddRequest
from src.models.users import UsersOrm
from src.schemas.users import User
from src.models.products import ProductsOrm
from src.schemas.products import Product


class UsersMapper(DataMapper):
    schema = User
    db_model = UsersOrm


class SuperUserReviewsMapper(DataMapper):
    db_model = ReviewsOrm
    schema = Review


class ReviewsMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewAddRequest


class ReviewsPatchMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewPatch


class ProductsMapper(DataMapper):
    db_model = ProductsOrm
    schema = Product


class PurchasesMapper(DataMapper): ...
