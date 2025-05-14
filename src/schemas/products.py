from pydantic import BaseModel


class ProductAdd(BaseModel):
    name: str
    price: int
    download_link: str
    description: str | None = "Test_description"
    slug: str

class ProductPatch(BaseModel):
    name: str | None = None
    price: int | None = None
    download_link: str | None = None
    description: str | None

class Product(ProductAdd):
    description: str
