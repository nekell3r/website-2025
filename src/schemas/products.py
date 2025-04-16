from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    download_link: str
