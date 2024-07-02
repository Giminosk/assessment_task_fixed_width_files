from decimal import Decimal
from models.base import BaseField
from utils.constraints import FieldLimits
from utils.exceptions import FieldValueValidationException


class Transaction(BaseField):
    def __init__(self, field_id: str, counter: str, amount: str, currency: str):
        super().__init__(field_id=field_id)
        self.counter: int = self._process_counter(counter)
        self.amount: Decimal = self._process_amount(amount)
        self.currency = currency

        self.validate()

    def _process_counter(self, counter: str) -> int:
        try:
            counter_int = int(counter)
        except ValueError:
            raise FieldValueValidationException(field_name="Counter", value=counter)
        return counter_int

    def _process_amount(self, amount: str) -> Decimal:
        try:
            amount_dec = Decimal(f"{amount[:-2]}.{amount[-2:]}")
        except ValueError:
            raise FieldValueValidationException(field_name="Amount", value=amount)
        return amount_dec

    def _validate_counter(self) -> None:
        if not FieldLimits.MIN_COUNTER <= self.counter <= FieldLimits.MAX_COUNTER:
            raise FieldValueValidationException(field_name="Counter", value=self.counter)

    def _validate_currency(self) -> None:
        if self.currency not in FieldLimits.VALID_CURRENCIES:
            raise FieldValueValidationException(field_name="Currency", value=self.currency)

    def validate(self) -> None:
        self._validate_field_id(value="02")
        self._validate_counter()
        self._validate_currency()
