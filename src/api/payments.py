from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import HttpUrl
from uuid import uuid4


from src.api.dependencies import DBDep, UserIdDep
from src.models.purchases import PaymentOrm
from src.schemas.payments import CreatePaymentRequest, CreatePaymentResponse
from src.services.payments import PaymentService

router = APIRouter(prefix="/payments", tags=["Платежи"])

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment_endpoint(
    request: CreatePaymentRequest,
    db: DBDep,
    user_id: UserIdDep,
):
    data = await PaymentService().create_payment(CreatePaymentRequest(
        product_id=request.product_id,
        email=request.email,
        ),
        db=db,
        user_id=user_id,
    )
    return data

@router.post("/webhook")
async def yookassa_webhook(
        request: Request,
        db: DBDep
    ):
    payload = await request.json()
    print(payload)
    result = await PaymentService().process_webhook(payload=payload, db=db)
    return JSONResponse(status_code=200, content=result)