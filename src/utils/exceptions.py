from decimal import Decimal


class BaseServiceException(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message or "An unexpected service error occurred")


class ValidationException(BaseServiceException):
    def __init__(self, message: str | None = None):
        super().__init__(message or "Validation error occurred")


class FieldValueValidationException(ValidationException):
    def __init__(self, field_name: str, value: str | int | Decimal):
        super().__init__(f"Invalid value for field {field_name}: {value}")


class RecordLimitException(ValidationException):
    def __init__(self, limit: int):
        super().__init__(f"Exceeded record limit: {limit}")


class FileStructureException(ValidationException):
    def __init__(self, message: str | None = None):
        super().__init__(message or "File must contain one header, at least one transaction and one footer ")


class LineLengthException(ValidationException):
    def __init__(self, limit: int, length: int):
        super().__init__(f"Length of the line must be {limit}, {length}")


class FieldLockedException(BaseServiceException):
    def __init__(self, field_type, field_name):
        super().__init__(f"Field {field_type}.{field_name} is locked")


class FieldNotFoundException(BaseServiceException):
    def __init__(self, field_type):
        super().__init__(f"Field {field_type} not found")


class FooterManualChangeException(BaseServiceException):
    def __init__(self, message: str | None = None):
        super().__init__(message or "Footer manual change is not allowed")
