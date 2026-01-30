from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums.payments import CountryCode, PaymentDirection


class PaymentSchema(BaseModel):
    id: int
    consumer_uid: str
    transaction_id: str
    name: Optional[str] = None
    is_business: bool
    direction: PaymentDirection
    amount: float
    sender_id: str
    country_code: CountryCode
    consumer_phone_number: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
