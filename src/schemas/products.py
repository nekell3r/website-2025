from pydantic import BaseModel


class ProductAdd(BaseModel):
    name: str
    price: int
    download_link: str


class ProductPatch(BaseModel):
    name: str | None = None
    price: int | None = None
    download_link: str | None = None


class Product(ProductAdd):
    id: int
