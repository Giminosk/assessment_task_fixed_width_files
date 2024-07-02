from decimal import Decimal
from models.footer import Footer
from models.header import Header
from models.transaction import Transaction
from services.field_locker import FieldLocker
from utils.constraints import FieldLimits
from utils.exceptions import (
    FieldLockedException,
    FieldNotFoundException,
    FieldValueValidationException,
    FooterManualChangeException,
    RecordLimitException,
)
from utils.logger import logger


class FixedWidthFile:
    def __init__(self, header: Header, transactions: list[Transaction], footer: Footer) -> None:
        self.header: Header = header
        self.footer: Footer = footer
        self.transactions: list[Transaction] = transactions

        self.field_locker: FieldLocker = FieldLocker()

        self.validate()
        logger.info("FixedWidthFile instance created and validated")

    def set_field_value(self, field_type: str, field_name: str, field_value: str, index: int | None = None) -> None:
        if self.field_locker.is_field_locked(field_type, field_name):
            logger.error(f"Attempted to modify locked field: {field_type}.{field_name}")
            raise FieldLockedException(field_type, field_name)

        if field_type == "header":
            self._set_header_field(field_name, field_value)
        elif field_type == "transaction":
            self._set_transaction_field(field_name, field_value, index)
        elif field_type == "footer":
            raise FooterManualChangeException()
        else:
            logger.error(f"Attempted to set value for unknown field type: {field_type}")
            raise FieldNotFoundException(field_type)

        logger.info(f"Field value updated: {field_type}.{field_name}")

    def _set_header_field(self, field_name: str, field_value: str) -> None:
        if not hasattr(self.header, field_name):
            logger.error(f"Attempted to set non-existent header field: {field_name}")
            raise FieldNotFoundException(f"header.{field_name}")
        setattr(self.header, field_name, field_value)
        logger.debug(f"Header field updated: {field_name} = {field_value}")

    def _set_transaction_field(self, field_name: str, field_value: str, index: int | None) -> None:
        if index is None or index < 0 or index >= len(self.transactions):
            logger.error(f"Invalid transaction index: {index}")
            raise ValueError(f"Invalid transaction index: {index}")

        if field_name == "amount":
            self._update_transaction_amount(index, field_value)
        elif field_name == "currency":
            self._update_transaction_currency(index, field_value)
        elif hasattr(self.transactions[index], field_name):
            setattr(self.transactions[index], field_name, field_value)
            logger.debug(f"Transaction field updated: index {index}, {field_name} = {field_value}")
        else:
            logger.error(f"Attempted to set non-existent transaction field: {field_name}")
            raise FieldNotFoundException(f"transaction.{field_name}")

    def _update_transaction_amount(self, index: int, amount: str) -> None:
        try:
            new_amount = Decimal(f"{amount[:-2]}.{amount[-2:]}")
        except (ValueError, IndexError):
            logger.error(f"Invalid amount value: {amount}")
            raise FieldValueValidationException("amount", amount)

        old_amount = self.transactions[index].amount
        self.transactions[index].amount = new_amount
        self.footer.control_sum += new_amount - old_amount
        logger.info(f"Transaction amount updated: index {index}, old: {old_amount}, new: {new_amount}")

    def _update_transaction_currency(self, index: int, currency: str) -> None:
        if currency not in FieldLimits.VALID_CURRENCIES:
            logger.error(f"Invalid currency value: {currency}")
            raise FieldValueValidationException("currency", currency)
        self.transactions[index].currency = currency
        logger.info(f"Transaction currency updated: index {index}, new currency: {currency}")

    def add_transaction(self, transaction: Transaction) -> None:
        if len(self.transactions) >= FieldLimits.MAX_TRANSACTIONS:
            logger.error(f"Attempted to add transaction beyond limit of {FieldLimits.MAX_TRANSACTIONS}")
            raise RecordLimitException(FieldLimits.MAX_TRANSACTIONS)

        self.transactions.append(transaction)
        self._update_footer_with_last_transaction()
        logger.info(f"New transaction added, total count: {len(self.transactions)}")

    def lock_field(self, field_type: str, field_name: str) -> None:
        self.field_locker.lock_field(field_type, field_name)
        logger.info(f"Field locked: {field_type}.{field_name}")

    def unlock_field(self, field_type: str, field_name: str) -> None:
        self.field_locker.unlock_field(field_type, field_name)
        logger.info(f"Field unlocked: {field_type}.{field_name}")

    def _update_footer_with_last_transaction(self) -> None:
        self.footer.total_counter += 1
        self.footer.control_sum += self.transactions[-1].amount
        logger.debug(
            f"Footer updated: total_counter = {self.footer.total_counter}, control_sum = {self.footer.control_sum}"
        )

    def validate(self) -> None:
        self._validate_footer_consistency()
        logger.info("FixedWidthFile validated successfully")

    def _validate_footer_consistency(self) -> None:
        if self.footer.total_counter != len(self.transactions):
            logger.error(
                f"Footer total_counter ({self.footer.total_counter}) does not match transaction count ({len(self.transactions)})"
            )
            raise FieldValueValidationException("Total counter", self.footer.total_counter)

        expected_control_sum = sum(transaction.amount for transaction in self.transactions)
        if self.footer.control_sum != expected_control_sum:
            logger.error(
                f"Footer control_sum ({self.footer.control_sum}) does not match calculated sum ({expected_control_sum})"
            )
            raise FieldValueValidationException("Control sum", self.footer.control_sum)
