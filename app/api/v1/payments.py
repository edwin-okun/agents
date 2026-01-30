from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import apaginate

from app.schemas.payment_schema import PaymentSchema
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=Page[PaymentSchema])
async def get_payments(
    payment_service: PaymentService = Depends(PaymentService),
):
    return await apaginate(payment_service.get_payments())
