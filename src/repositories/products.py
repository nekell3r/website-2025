from src.repositories.base import BaseRepository
from src.models.products import ProductsOrm
from src.repositories.mappers.mappers import ProductsMapper
from src.schemas.products import Product, ProductAdd


class ProductsRepository(BaseRepository):
    model = ProductsOrm
    schema = ProductAdd
    mapper = ProductsMapper
