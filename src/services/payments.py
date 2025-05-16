import uuid
from datetime import datetime

from fastapi import HTTPException
from uuid import uuid4
import httpx


from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.config import settings
from src.schemas.payments import CreatePaymentRequest, CreatePaymentResponse, Purchase


class PaymentService:
    async def create_payment(
            self,
            data: CreatePaymentRequest,
            db: DBDep,
            user_id: UserIdDep,
    ) -> CreatePaymentResponse:

        if data.email is None:
            raise HTTPException(status_code=400, detail="Email is required")
        if data.product_slug is None:
            raise HTTPException(status_code=400, detail="Product slug is required")

        product = await db.products.get_one_or_none(slug=data.product_slug)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        existing_created_purchase = await db.purchases.get_one_or_none(
            user_id=user_id,
            product_slug=data.product_slug,
            status="Created"
        )
        if existing_created_purchase:
            raise HTTPException(status_code=400, detail="Payment already created")
        existing_paid_purchase = await db.purchases.get_one_or_none(
            user_id=user_id,
            product_slug=data.product_slug,
            status="Paid"
        )
        if existing_paid_purchase:
            raise HTTPException(status_code=409, detail="Payment already paid")
        payment_id = str(uuid4())

        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": payment_id
        }

        payload = {
            "amount": {
                "value": f"{product.price:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://example.com"
            },
            "description": product.name,
            "metadata": {
                "invoice_id": payment_id
            }
        }
        await db.purchases.add(
            Purchase(
            user_id=user_id,
            product_slug=data.product_slug,
            email=data.email,
            payment_id=payment_id,
            status = "Created"
            )
        )
        await db.commit()
        async with httpx.AsyncClient(auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)) as client:
            response = await client.post(settings.YOOKASSA_API_URL, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            resp_json = response.json()
            confirmation_url = resp_json["confirmation"]["confirmation_url"]
            return CreatePaymentResponse(
                payment_id=payment_id,
                payment_url=confirmation_url
            )
        else:
            raise Exception(f"ЮKassa error: {response.status_code}, {response.text}")
# кастомные исключения

    async def confirm_payment(self, payment_id: str):
        url = f"{settings.YOOKASSA_API_URL}/{payment_id}/capture"
        idempotence_key = str(uuid.uuid4())

        headers = {
            "Idempotence-Key": idempotence_key
        }

        async with httpx.AsyncClient(auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)) as client:
            response = await client.post(url, headers=headers, json={})

        if response.status_code not in (200, 201):
            raise Exception(f"Failed to capture payment: {response.status_code}, {response.text}")

    async def process_webhook(
            self,
            payload: dict,
            db: DBDep
    ):
        event = payload.get("event")
        obj = payload.get("object", {})

        payment_id = obj.get("metadata").get("invoice_id")
        if not payment_id:
            raise HTTPException(status_code=400, detail="Missing payment ID")

        purchase = await db.purchases.get_one_or_none(payment_id=payment_id)
        if not purchase:
            raise HTTPException(status_code=200, detail="Purchase not found")

        if event == "payment.succeeded":
            purchase.status = "Paid"
            paid_at = obj.get("paid_at")
            if paid_at:
                purchase.paid_at = datetime.fromisoformat(paid_at)
        elif event == "payment.canceled":
            purchase.status = "Canceled"
        elif event == "payment.waiting_for_capture":
            await self.confirm_payment(obj["id"])
            return {"status": "capturing"}
        else:
            # Неизвестное событие — можно проигнорировать или логировать
            return {"status": "ignored", "reason": f"Unhandled event: {event}"}

        await db.purchases.edit(purchase, payment_id=payment_id)
        await db.commit()
        return {"status": "ok"}


