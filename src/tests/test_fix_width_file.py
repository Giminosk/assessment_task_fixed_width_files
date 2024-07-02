import pytest
from decimal import Decimal
from models.fixed_width_file import FixedWidthFile
from models.header import Header
from models.footer import Footer
from models.transaction import Transaction
from utils.exceptions import (
    FieldLockedException,
    FieldNotFoundException,
    FieldValueValidationException,
    RecordLimitException,
)
from utils.constraints import FieldLimits


def test_fixed_width_file_initialization(
    fixed_width_file: FixedWidthFile,
    sample_header: Header,
    sample_transactions: list[Transaction],
    sample_footer: Footer,
):
    assert fixed_width_file.header == sample_header
    assert fixed_width_file.transactions == sample_transactions
    assert fixed_width_file.footer == sample_footer


def test_set_header_field(fixed_width_file: FixedWidthFile):
    fixed_width_file.set_field_value("header", "name", "Jane")
    assert fixed_width_file.header.name == "Jane"


def test_set_transaction_field(fixed_width_file: FixedWidthFile):
    fixed_width_file.set_field_value("transaction", "amount", "000000003000", 0)
    assert fixed_width_file.transactions[0].amount == Decimal("30.00")
    assert fixed_width_file.footer.control_sum == Decimal("50.00")


def test_add_transaction(fixed_width_file: FixedWidthFile):
    new_transaction = Transaction("02", "000003", "000000003000", "GBP")
    fixed_width_file.add_transaction(new_transaction)
    assert fixed_width_file.transactions[-1] == new_transaction
    assert len(fixed_width_file.transactions) == 3
    assert fixed_width_file.footer.total_counter == 3
    assert fixed_width_file.footer.control_sum == Decimal("60.00")


def test_add_transaction_limit_exceeded(fixed_width_file: FixedWidthFile):
    for i in range(FieldLimits.MAX_TRANSACTIONS - 2):
        new_transaction = Transaction("02", f"{i+3:06d}", "000000001000", "USD")
        fixed_width_file.add_transaction(new_transaction)

    assert len(fixed_width_file.transactions) == FieldLimits.MAX_TRANSACTIONS

    with pytest.raises(FieldValueValidationException):
        extra_transaction = Transaction("02", f"{FieldLimits.MAX_TRANSACTIONS+1:06d}", "000000001000", "USD")

    with pytest.raises(RecordLimitException):
        extra_transaction = Transaction("02", "1", "000000001000", "USD")
        fixed_width_file.add_transaction(extra_transaction)


def test_lock_and_unlock_field(fixed_width_file: FixedWidthFile):
    fixed_width_file.lock_field("header", "name")
    assert "name" in fixed_width_file.field_locker.locked_fields["header"]

    with pytest.raises(FieldLockedException):
        fixed_width_file.set_field_value("header", "name", "Jane")

    assert fixed_width_file.header.name != "Jane"

    fixed_width_file.unlock_field("header", "name")
    fixed_width_file.set_field_value("header", "name", "Jane")
    assert fixed_width_file.header.name == "Jane"


def test_validate_footer_consistency(fixed_width_file: FixedWidthFile):

    fixed_width_file.validate()

    fixed_width_file.footer.total_counter += 1
    with pytest.raises(FieldValueValidationException):
        fixed_width_file.validate()


def test_field_not_found(fixed_width_file: FixedWidthFile):
    with pytest.raises(FieldNotFoundException):
        fixed_width_file.set_field_value("header", "non_existent_field", "value")


def test_invalid_transaction_index(fixed_width_file: FixedWidthFile):
    with pytest.raises(ValueError):
        fixed_width_file.set_field_value("transaction", "amount", "000000003000", 99)


def test_invalid_currency(fixed_width_file: FixedWidthFile):
    with pytest.raises(FieldValueValidationException):
        fixed_width_file.set_field_value("transaction", "currency", "INVALID", 0)
