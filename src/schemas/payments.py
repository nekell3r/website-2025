from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime
from typing import Optional, Literal


class CreatePaymentRequest(BaseModel):
    product_id: int
    email: EmailStr


class CreatePaymentResponse(BaseModel):
    invoice_id: str
    payment_url: HttpUrl


class PaymentWebhookData(BaseModel):
    invoice_id: str  # InvoiceId всегда приходит
    status: str  # Status всегда приходит (Completed, Failed и т.д.)
    paid_at: Optional[datetime] = None  # Только при успешной оплате
    receipt_url: Optional[HttpUrl] = None  # Только при успешной оплате


class Purchase(BaseModel):
    user_id: int
    email: EmailStr
    product_id: int
    invoice_id: str
    status: Literal["Created", "Completed", "Failed"] = "Created"
    paid_at: Optional[datetime] = None
    receipt_url: Optional[HttpUrl] = None
