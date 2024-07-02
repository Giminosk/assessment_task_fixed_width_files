from models.fixed_width_file import FixedWidthFile
from models.footer import Footer
from models.header import Header
from models.transaction import Transaction
from utils.constraints import FieldLengths


class FileWriter:
    @staticmethod
    def write_file(file_path: str, fw_file: FixedWidthFile):
        with open(file_path, "w") as f:
            f.write(FileWriter._format_header(fw_file.header))
            for transaction in fw_file.transactions:
                f.write(FileWriter._format_transaction(transaction))
            f.write(FileWriter._format_footer(fw_file.footer))

    @staticmethod
    def _format_header(header: Header) -> str:
        return (
            f"{header.field_id:<{FieldLengths.FIELD_ID}}"
            f"{header.name:<{FieldLengths.NAME}}"
            f"{header.surname:<{FieldLengths.SURNAME}}"
            f"{header.patronymic:<{FieldLengths.PATRONYMIC}}"
            f"{header.address:<{FieldLengths.ADDRESS}}"
        )

    @staticmethod
    def _format_transaction(transaction: Transaction) -> str:
        return (
            f"{transaction.field_id:<{FieldLengths.FIELD_ID}}"
            f"{transaction.counter:0>{FieldLengths.COUNTER}}"
            f"{str(transaction.amount).replace('.', ''):0>{FieldLengths.AMOUNT}}"
            f"{transaction.currency:<{FieldLengths.CURRENCY}}"
            f"{'':<{FieldLengths.TRANSACTION_RESERVED}}\n"
        )

    @staticmethod
    def _format_footer(footer: Footer) -> str:
        return (
            f"{footer.field_id:<{FieldLengths.FIELD_ID}}"
            f"{footer.total_counter:0>{FieldLengths.TOTAL_COUNTER}}"
            f"{str(footer.control_sum).replace('.', ''):0>{FieldLengths.CONTROL_SUM}}"
            f"{'':<{FieldLengths.FOOTER_RESERVED}}"
        )
