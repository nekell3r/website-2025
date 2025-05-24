from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class BoughtProduct(BaseModel):
    name: str
    price: int
    download_link: str
    description: str | None = "Test_description"
    paid_at: Optional[datetime] = None
