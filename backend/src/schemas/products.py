from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    name: str
    price: int
    download_link: str
    description: str | None = "Test_description"
    slug: str


class ProductPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    download_link: Optional[str] = None
    description: Optional[str] = None
