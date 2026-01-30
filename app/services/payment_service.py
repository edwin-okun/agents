from fastapi import Depends
from tortoise.queryset import QuerySet

from app.models.payment import EndUserPayment
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, payment_repository: PaymentRepository = Depends()):
        self.payment_repository = payment_repository

    def get_payments(self) -> QuerySet[EndUserPayment]:
        return self.payment_repository.get_all_payments()
