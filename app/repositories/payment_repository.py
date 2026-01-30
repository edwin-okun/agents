from tortoise.queryset import QuerySet

from app.models.payment import EndUserPayment


class PaymentRepository:
    def get_all_payments(self) -> QuerySet[EndUserPayment]:
        return EndUserPayment.all()
