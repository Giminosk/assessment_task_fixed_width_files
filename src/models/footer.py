from decimal import Decimal
from models.base import BaseField
from utils.constraints import FieldLimits
from utils.exceptions import FieldValueValidationException


class Footer(BaseField):
    def __init__(self, field_id: str, total_counter: str, control_sum: str):
        super().__init__(field_id)
        self.total_counter: int = self._process_total_counter(total_counter)
        self.control_sum: Decimal = self._process_control_sum(control_sum)

        self.validate()

    def _process_total_counter(self, total_counter: str) -> int:
        try:
            total_counter_int = int(total_counter)
        except ValueError:
            raise FieldValueValidationException(field_name="Total counter", value=total_counter)
        return total_counter_int

    def _process_control_sum(self, control_sum: str) -> Decimal:
        try:
            control_sum_dec = Decimal(f"{control_sum[:-2]}.{control_sum[-2:]}")
        except ValueError:
            raise FieldValueValidationException(field_name="Control sum", value=control_sum)
        return control_sum_dec

    def _validate_total_counter(self) -> None:
        if not FieldLimits.MIN_COUNTER <= self.total_counter <= FieldLimits.MAX_COUNTER:
            raise FieldValueValidationException(field_name="Total counter", value=self.total_counter)

    def validate(self) -> None:
        self._validate_field_id(value="03")
        self._validate_total_counter()
