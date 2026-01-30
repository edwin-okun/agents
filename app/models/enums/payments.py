from enum import StrEnum


class PaymentDirection(StrEnum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class CountryCode(StrEnum):
    KE = "KE"
    NG = "NG"
    CI = "CI"
    GH = "GH"
