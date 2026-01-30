from tortoise import Model, fields

from app.models.enums.payments import CountryCode, PaymentDirection


class EndUserPayment(Model):
    """
    Tracks payments made by end-users or consumers of the app.
    """

    id = fields.BigIntField(pk=True)
    consumer_uid = fields.CharField(max_length=255, index=True)
    transaction_id = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255, null=True, index=True)
    is_business = fields.BooleanField(default=False)
    direction = fields.CharEnumField(
        PaymentDirection, max_length=10
    )  # outgoing or incoming
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    sender_id = fields.CharField(max_length=50, index=True)  # MPESA, AIRTELMONEY etc
    country_code = fields.CharEnumField(
        CountryCode, max_length=2, default=CountryCode.KE
    )  # ISO Alpha-2 country code i.e KE, NG, CI, GH
    consumer_phone_number = fields.CharField(max_length=15, index=True)
    paid_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "end_user_payments"
        unique_together = ["consumer_phone_number", "transaction_id"]
