from models.fixed_width_file import FixedWidthFile
from models.footer import Footer
from models.header import Header
from models.transaction import Transaction
from utils.constraints import FieldLengths
from utils.exceptions import FileStructureException, LineLengthException


class FileReader:
    @staticmethod
    def read_file(file_path: str) -> FixedWidthFile:
        with open(file_path, "r") as f:
            lines = f.readlines()

        if len(lines) < 3:
            raise FileStructureException("File must contain at least a header, one transaction, and a footer")

        header = FileReader._parse_header(lines[0])
        transactions = [FileReader._parse_transaction(line) for line in lines[1:-1]]
        footer = FileReader._parse_footer(lines[-1])

        return FixedWidthFile(header=header, transactions=transactions, footer=footer)

    @staticmethod
    def _extract_fields(line: str, field_lengths: list[int]) -> list[str]:
        if len(line) != FieldLengths.RECORD:
            raise LineLengthException(FieldLengths.RECORD, len(line))

        fields = []
        start = 0
        for length in field_lengths:
            fields.append(line[start : start + length])
            start += length
        return fields

    @staticmethod
    def _parse_header(line: str) -> Header:
        field_id, name, surname, patronymic, address = FileReader._extract_fields(
            line=line,
            field_lengths=[
                FieldLengths.FIELD_ID,
                FieldLengths.NAME,
                FieldLengths.SURNAME,
                FieldLengths.PATRONYMIC,
                FieldLengths.ADDRESS,
            ],
        )
        return Header(field_id=field_id, name=name, surname=surname, patronymic=patronymic, address=address)

    @staticmethod
    def _parse_transaction(line: str) -> Transaction:
        field_id, counter, amount, currency = FileReader._extract_fields(
            line=line,
            field_lengths=[
                FieldLengths.FIELD_ID,
                FieldLengths.COUNTER,
                FieldLengths.AMOUNT,
                FieldLengths.CURRENCY,
            ],
        )
        return Transaction(field_id=field_id, counter=counter, amount=amount, currency=currency)

    @staticmethod
    def _parse_footer(line: str) -> Footer:
        field_id, total_counter, control_sum = FileReader._extract_fields(
            line=line,
            field_lengths=[
                FieldLengths.FIELD_ID,
                FieldLengths.TOTAL_COUNTER,
                FieldLengths.CONTROL_SUM,
            ],
        )
        return Footer(field_id=field_id, total_counter=total_counter, control_sum=control_sum)
