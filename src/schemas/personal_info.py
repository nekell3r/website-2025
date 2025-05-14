from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from annotated_types import MinLen, MaxLen, Ge, Le
from datetime import datetime

class BoughtProduct(BaseModel):
    product_id: int
    product_name: str
    purchase_time:Optional[datetime]
