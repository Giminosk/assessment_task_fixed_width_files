from abc import ABC

from utils.exceptions import FieldValueValidationException


class BaseField(ABC):
    def __init__(self, field_id: str) -> None:
        self.field_id = field_id

    def _validate_field_id(self, value) -> None:
        if self.field_id != value:
            raise FieldValueValidationException("Field ID", self.field_id)
