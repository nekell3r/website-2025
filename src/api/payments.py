import sys
import uuid

from fastapi import APIRouter, Body, HTTPException
from pathlib import Path
from pydantic import HttpUrl

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.payments import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentWebhookData,
    Purchase,
)

# from src.config import settings
sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/payments", tags=["Покупка материалов и платежи"])


@router.post("/create", summary="Создание платежа")
async def create_payment(
    user_id: UserIdDep,
    db: DBDep,
    data: CreatePaymentRequest = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {"product_id": 1, "email": "pashok@gmail.com"},
            }
        },
    ),
):
    product = await db.products.get_one_or_none(id=data.product_id)
    if not product:
        raise HTTPException(404, detail="Продукт не найден")
    # amount = product.price
    invoice_id = str(uuid.uuid4())
    """
    payload = {
        "publicId": settings.TEST_PUBLIC_KEY,
        "description": f"Покупка продукта {data.product_id}",
        "amount": amount,
        "currency": "RUB",
        "invoiceId": invoice_id,
        "accountId": str(user_id),
        "skin": "classic",
        "data": {
            "product_id": data.product_id,
            "email": data.email,
        }
    }
    """
    current_data = await db.purchases.get_one_or_none(
        product_id=data.product_id, user_id=user_id, status="Completed"
    )
    if current_data:
        raise HTTPException(403, detail="У вас уже приобретён данный продукт")

    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.TEST_PUBLIC_KEY}/payments/charge", json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Ошибка CloudPayments")

    data = response.json()
    if "paymentUrl" not in data:
        raise HTTPException(status_code=500, detail="Не получена ссылка для оплаты")

    payment_url = data["paymentUrl"]
    """
    payment_url = HttpUrl("https://someservice.ru")
    payment_data = Purchase(
        user_id=user_id,
        product_id=data.product_id,
        email=data.email,
        invoice_id=invoice_id,
    )
    await db.purchases.add(payment_data)
    await db.commit()
    return CreatePaymentResponse(invoice_id=invoice_id, payment_url=payment_url)


@router.post("/webhook", summary="Получение вебхука от cloudpayments")
async def payment_webhook(
    db: DBDep,
    data: PaymentWebhookData = Body(
        openapi_examples={
            "1": {
                "summary": "number 1",
                "value": {
                    "invoice_id": "0",
                    "status": "Completed",
                    "paid_at": "2025-05-09T19:50:17.899+03:00",
                    "receipt_url": "https://receipt.ru",
                },
            }
        },
    ),
):
    purchase = await db.purchases.get_one_or_none(invoice_id=data.invoice_id)
    if not purchase:
        raise HTTPException(404, detail="Покупка не найдена")
    if purchase.status == "Completed":
        return {"status": "br, already_paid"}
        # return {"status": "ok"}
    await db.purchases.edit(data, invoice_id=data.invoice_id)
    await db.commit()

    if data.status == "Completed":
        return {"status": "ok, платеж успешен"}
    elif data.status == "Failed":
        return {"status": "br, платеж не успешен"}
    # return {"status": "ok"}
