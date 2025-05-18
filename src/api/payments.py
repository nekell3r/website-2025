from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.dependencies.auth import UserIdDep
from src.dependencies.db import DBDep
from src.schemas.payments import CreatePaymentRequest, CreatePaymentResponse
from src.services.payments import PaymentsService

router = APIRouter(prefix="/payments", tags=["Платежи"])

@router.post("", response_model=CreatePaymentResponse)
async def create_payment_endpoint(
    request: CreatePaymentRequest,
    db: DBDep,
    #user_id: UserIdDep,
):
    data = await PaymentsService().test_create_payment(data = request, db=db)
    return data

@router.post("/webhook")
async def yookassa_webhook(
        request: Request,
        db: DBDep
    ):
    payload = await request.json()
    result = await PaymentsService().process_webhook(payload=payload, db=db)
    return JSONResponse(status_code=200, content=result)