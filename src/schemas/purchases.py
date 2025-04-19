from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class PurchaseAddRequest(BaseModel):
    product_id: int


class PurchaseAdd(BaseModel):
    user_id: int
    product_id: int
    invoice_id: str
    receipt_url: HttpUrl | None = None
    paid_at: datetime


class WebhookNotification(BaseModel):

    invoice_id: str
    receipt_url: HttpUrl | None = None
    paid_at: datetime
    status: str
