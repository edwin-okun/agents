from enum import StrEnum

class PaymentDirection(StrEnum):
    OUTGOING = "OUTGOING"
    INCOMING = "INCOMING"

class CountryCode(StrEnum):
    KE = "KE"
    NG = "NG"
    CI = "CI"
    GH = "GH"