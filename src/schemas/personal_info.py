from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from annotated_types import MinLen, MaxLen, Ge, Le
from datetime import datetime

class BoughtProduct(BaseModel):
    name: str
    price: int
    download_link: str
    description: str | None = "Test_description"
    paid_at: Optional[datetime] = None