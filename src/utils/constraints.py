from dataclasses import dataclass


@dataclass(frozen=True)
class FieldLengths:
    FIELD_ID: int = 2
    NAME: int = 28
    SURNAME: int = 30
    PATRONYMIC: int = 30
    ADDRESS: int = 30
    COUNTER: int = 6
    AMOUNT: int = 12
    CURRENCY: int = 3
    TOTAL_COUNTER: int = 6
    CONTROL_SUM: int = 12
    RECORD: int = 120
    TRANSACTION_RESERVED: int = 96
    FOOTER_RESERVED: int = 100


@dataclass(frozen=True)
class FieldLimits:
    MIN_COUNTER: int = 1
    MAX_COUNTER: int = 20000
    MAX_TRANSACTIONS: int = 20000
    DECIMAL_PART: int = 2
    VALID_CURRENCIES: tuple[str, ...] = ("USD", "EUR", "GBP")
