import uuid
from datetime import datetime

from uuid import uuid4
import httpx

from src.exceptions.db_exceptions import (
    PurchaseNotFoundException,
    ProductNotFoundException,
)
from src.exceptions.service_exceptions import (
    PurchaseNotFoundServiceException,
    ProductNotFoundServiceException,
    WebhookWrongFormatServiceException,
    PaymentValidationServiceException,
    PaymentAlreadyCreatedServiceException,
    PaymentAlreadyPaidServiceException,
    YooKassaServiceException,
)
from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.config import settings
from src.schemas.payments import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    Purchase,
    PaymentWebhookData,
)
from src.schemas.personal_info import BoughtProduct


class PaymentsService:
    async def test_create_payment(
        self, data: CreatePaymentRequest, db: DBDep
    ) -> CreatePaymentResponse:
        if data.email is None:
            raise PaymentValidationServiceException(detail="Email is required")
        if data.product_slug is None:
            raise PaymentValidationServiceException(detail="Product slug is required")

        try:
            product = await db.products.get_one(slug=data.product_slug)
        except ProductNotFoundException:
            raise ProductNotFoundServiceException

        existing_created_purchase = await db.purchases.get_one_or_none(
            user_id=1, product_slug=data.product_slug, status="Created"
        )
        if existing_created_purchase:
            raise PaymentAlreadyCreatedServiceException

        existing_paid_purchase = await db.purchases.get_one_or_none(
            user_id=1, product_slug=data.product_slug, status="Paid"
        )
        if existing_paid_purchase:
            raise PaymentAlreadyPaidServiceException
        payment_id = str(uuid4())

        headers = {"Content-Type": "application/json", "Idempotence-Key": payment_id}

        payload = {
            "amount": {"value": f"{product.price:.2f}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "http://localhost:3000/pages/profile/standart.html",
            },
            "description": product.name,
            "metadata": {"invoice_id": payment_id},
        }
        await db.purchases.add(
            Purchase(
                user_id=1,
                product_slug=data.product_slug,
                email=data.email,
                payment_id=payment_id,
                status="Created",
            )
        )
        await db.commit()
        async with httpx.AsyncClient(
            auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
        ) as client:
            response = await client.post(
                settings.YOOKASSA_API_URL, json=payload, headers=headers
            )
        if response.status_code == 200 or response.status_code == 201:
            resp_json = response.json()
            confirmation_url = resp_json["confirmation"]["confirmation_url"]
            return CreatePaymentResponse(
                payment_id=payment_id, payment_url=confirmation_url
            )
        else:
            raise YooKassaServiceException(
                detail=f"ЮKassa error: {response.status_code}, {response.text}"
            )

    async def confirm_payment(self, payment_id: str):
        url = f"{settings.YOOKASSA_API_URL}/{payment_id}/capture"
        idempotence_key = str(uuid.uuid4())

        headers = {"Idempotence-Key": idempotence_key}

        async with httpx.AsyncClient(
            auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
        ) as client:
            response = await client.post(url, headers=headers, json={})

        if response.status_code not in (200, 201):
            raise YooKassaServiceException(
                detail=f"Failed to capture payment: {response.status_code}, {response.text}"
            )

    async def create_payment(
        self,
        data: CreatePaymentRequest,
        db: DBDep,
        user_id: UserIdDep,
    ) -> CreatePaymentResponse:
        if data.email is None:
            raise PaymentValidationServiceException(detail="Email is required")
        if data.product_slug is None:
            raise PaymentValidationServiceException(detail="Product slug is required")
        try:
            product = await db.products.get_one(slug=data.product_slug)
        except ProductNotFoundException:
            raise ProductNotFoundServiceException

        existing_created_purchase = await db.purchases.get_one_or_none(
            user_id=user_id, product_slug=data.product_slug, status="Created"
        )
        if existing_created_purchase:
            raise PaymentAlreadyCreatedServiceException

        existing_paid_purchase = await db.purchases.get_one_or_none(
            user_id=user_id, product_slug=data.product_slug, status="Paid"
        )
        if existing_paid_purchase:
            raise PaymentAlreadyPaidServiceException
        payment_id = str(uuid4())

        headers = {"Content-Type": "application/json", "Idempotence-Key": payment_id}

        payload = {
            "amount": {"value": f"{product.price:.2f}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "http://localhost:3000/pages/profile/standart.html",
            },
            "description": product.name,
            "metadata": {"invoice_id": payment_id},
        }
        await db.purchases.add(
            Purchase(
                user_id=user_id,
                product_slug=data.product_slug,
                email=data.email,
                payment_id=payment_id,
                status="Created",
            )
        )
        await db.commit()
        async with httpx.AsyncClient(
            auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
        ) as client:
            response = await client.post(
                settings.YOOKASSA_API_URL, json=payload, headers=headers
            )
        if response.status_code == 200 or response.status_code == 201:
            resp_json = response.json()
            confirmation_url = resp_json["confirmation"]["confirmation_url"]
            return CreatePaymentResponse(
                payment_id=payment_id, payment_url=confirmation_url
            )
        else:
            raise YooKassaServiceException(
                detail=f"ЮKassa error: {response.status_code}, {response.text}"
            )

    async def process_webhook(self, payload: dict, db: DBDep):
        event = payload.get("event")
        obj = payload.get("object", {})

        payment_id = obj.get("metadata", {}).get("invoice_id")
        if not payment_id:
            raise WebhookWrongFormatServiceException
        try:
            purchase_orm_object = await db.purchases.get_one(payment_id=payment_id)
        except PurchaseNotFoundException:
            raise PurchaseNotFoundServiceException

        purchase_update_data = PaymentWebhookData(
            payment_id=purchase_orm_object.payment_id,
            status=purchase_orm_object.status,
            paid_at=purchase_orm_object.paid_at,
            fiscal_receipt_url=purchase_orm_object.fiscal_receipt_url,
        )

        if event == "payment.succeeded":
            purchase_update_data.status = "Paid"
            paid_at_str = obj.get("paid_at")
            if paid_at_str:
                try:
                    purchase_update_data.paid_at = datetime.fromisoformat(
                        paid_at_str.replace("Z", "+00:00").split(".")[0]
                    )
                except ValueError:
                    try:
                        purchase_update_data.paid_at = datetime.fromisoformat(
                            paid_at_str
                        )
                    except ValueError:
                        print(
                            f"Warning: Could not parse paid_at_str from webhook: {paid_at_str}"
                        )
                        pass

            receipt_object = obj.get("receipt")
            if receipt_object and receipt_object.get("status") == "succeeded":
                pass

        elif event == "payment.canceled":
            purchase_update_data.status = "Canceled"
        elif event == "payment.waiting_for_capture":
            await self.confirm_payment(obj["id"])
            return {"status": "capturing"}
        else:
            return {"status": "ignored", "reason": f"Unhandled event: {event}"}

        try:
            await db.purchases.edit(purchase_update_data, payment_id=payment_id)
        except PurchaseNotFoundException:
            raise PurchaseNotFoundServiceException
        await db.commit()
        return {"status": "ok"}

    async def get_purchases(self, user_id: UserIdDep, db: DBDep):
        try:
            purchases = await db.purchases.get_all(user_id=user_id, status="Paid")
        except PurchaseNotFoundException:
            raise PurchaseNotFoundServiceException

        answer = []
        for p in purchases:
            try:
                product_model = await db.products.get_one(slug=p.product_slug)
                answer.append(
                    BoughtProduct(**(product_model.model_dump()), paid_at=p.paid_at)
                )
            except ProductNotFoundException:
                pass
        return answer
