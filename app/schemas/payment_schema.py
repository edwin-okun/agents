from pydantic import BaseModel


class PaymentSchema(BaseModel):
    amount: float
    currency: str
    description: str
