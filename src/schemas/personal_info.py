from typing import Annotated

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from annotated_types import MinLen, MaxLen, Ge, Le
from datetime import datetime

class BoughtProduct(BaseModel):
    product_id: int
    product_name: str
    purchase_time: datetime

class AccountData(BaseModel):
    id: int
    is_super_user: bool

    name: Annotated[str, MinLen(2), MaxLen(30)] | None = None
    surname: Annotated[str, MinLen(2), MaxLen(30)] | None = None

    telephone: PhoneNumber
    email: EmailStr | None = None
    grade: Annotated[int, Ge(7), Le(11)] | None = None
