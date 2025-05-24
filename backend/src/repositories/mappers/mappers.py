from src.models.reviews import ReviewsOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.reviews import ReviewPatch, ReviewWithId, Review
from src.models.users import UsersOrm
from src.schemas.users import User
from src.models.products import ProductsOrm
from src.models.purchases import PaymentOrm
from src.schemas.products import Product
from src.schemas.payments import Purchase


class UsersMapper(DataMapper):
    schema = User
    db_model = UsersOrm


class ReviewsIdMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewWithId


class ReviewsMapper(DataMapper):
    db_model = ReviewsOrm
    schema = Review


class ReviewsPatchMapper(DataMapper):
    db_model = ReviewsOrm
    schema = ReviewPatch


class ProductsMapper(DataMapper):
    db_model = ProductsOrm
    schema = Product


class PurchasesMapper(DataMapper):
    db_model = PaymentOrm
    schema = Purchase
