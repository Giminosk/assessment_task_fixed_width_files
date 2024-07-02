import logging
import pytest

from models.transaction import Transaction
from models.fixed_width_file import FixedWidthFile
from models.footer import Footer
from models.header import Header


@pytest.fixture(autouse=True)
def disable_logging(caplog):
    logging.getLogger().setLevel(99)
    yield
    logging.getLogger().setLevel(logging.NOTSET)


@pytest.fixture(scope="function")
def sample_header() -> Header:
    return Header("01", "John", "Doe", "Smith", "123 Main St")


@pytest.fixture(scope="function")
def sample_transactions() -> list[Transaction]:
    return [
        Transaction("02", "000001", "000000001000", "USD"),
        Transaction("02", "000002", "000000002000", "EUR"),
    ]


@pytest.fixture(scope="function")
def sample_footer(sample_transactions) -> Footer:
    total_sum = sum(t.amount for t in sample_transactions)
    return Footer("03", f"{len(sample_transactions):06d}", f"{total_sum:012.2f}".replace(".", ""))


@pytest.fixture(scope="function")
def fixed_width_file(sample_header, sample_transactions, sample_footer) -> FixedWidthFile:
    return FixedWidthFile(sample_header, sample_transactions, sample_footer)
