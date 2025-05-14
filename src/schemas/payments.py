from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime
from typing import Optional, Literal


class CreatePaymentRequest(BaseModel):
    product_id: int
    email: EmailStr


class CreatePaymentResponse(BaseModel):
    payment_id: str
    payment_url: HttpUrl


class PaymentWebhookData(BaseModel):
    payment_id: str
    status: str
    paid_at: Optional[datetime] = None
    fiscal_receipt_url: Optional[HttpUrl] = None

class Purchase(BaseModel):
    user_id: int
    product_id: int
    email: EmailStr
    payment_id: str
    status: str
    paid_at: Optional[datetime] = None
    fiscal_receipt_url: Optional[str] = None




