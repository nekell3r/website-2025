from src.exceptions.exceptions import ProductNotFoundException
from src.repositories.base import BaseRepository
from src.models.products import ProductsOrm
from src.repositories.mappers.mappers import ProductsMapper
from src.schemas.products import Product


class ProductsRepository(BaseRepository):
    model = ProductsOrm
    schema = Product
    mapper = ProductsMapper
    not_found_exception = ProductNotFoundException
