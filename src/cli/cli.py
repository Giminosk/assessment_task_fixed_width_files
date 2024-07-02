from typing import Callable
import os
from services.file_reader import FileReader
from services.file_writer import FileWriter
from models.fixed_width_file import FixedWidthFile
from models.transaction import Transaction
from utils.exceptions import (
    BaseServiceException,
    FieldNotFoundException,
    ValidationException,
    FieldValueValidationException,
    RecordLimitException,
    FileStructureException,
    LineLengthException,
    FieldLockedException,
)
from utils.constraints import FieldLimits
from utils.logger import logger


class CLI:
    def __init__(self) -> None:
        self.fw_file: FixedWidthFile | None = None
        self.file_path: str = ""

        self.choice_handlers: dict[str, Callable[[], None]] = {
            "1": self._load_file,
            "2": self._save_file,
            "3": self._get_field_value,
            "4": self._update_field_value,
            "5": self._add_transaction,
            "6": self._lock_field,
            "7": self._unlock_field,
            "8": exit,
        }
        logger.info("CLI initialized")

    def run(self) -> None:
        logger.info("Starting Fixed Width File Handler")
        print("Welcome to the Fixed Width File Handler!")
        while True:
            self._print_menu()
            choice = input("Enter your choice: ")
            self._handle_choice(choice)

    def _print_menu(self) -> None:
        print("\nMenu:")
        print("1. Load a file")
        print("2. Save the file")
        print("3. Get field value")
        print("4. Update field value")
        print("5. Add transaction")
        print("6. Lock field")
        print("7. Unlock field")
        print("8. Exit")

    def _handle_choice(self, choice: str) -> None:
        try:
            handler = self.choice_handlers.get(choice)
            if handler:
                logger.info(f"User selected option: {choice}")
                handler()
            else:
                logger.warning(f"Invalid choice entered: {choice}")
                print("Invalid choice. Please try again.")
        except BaseServiceException as e:
            logger.error(f"Service exception occurred: {str(e)}")
            print(f"An error occurred: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")
            print(f"An unexpected error occurred: {str(e)}")

    def _load_file(self) -> None:
        file_path = input("Enter the path to the file: ")
        if not os.path.exists(file_path):
            logger.warning(f"Attempted to load non-existent file: {file_path}")
            print("File does not exist. Please check the path and try again.")
            return
        try:
            self.fw_file = FileReader.read_file(file_path)
            self.file_path = file_path
            logger.info(f"File loaded successfully from {file_path}")
            print(f"File loaded successfully from {file_path}")
        except (FileStructureException, LineLengthException) as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            print(f"Error loading file: {str(e)}")

    def _save_file(self) -> None:
        if not self.fw_file:
            logger.warning("Attempted to save file when no file was loaded")
            print("No file is currently loaded. Please load a file first.")
            return
        file_path: str = (
            input("Enter the path to save the file (leave empty to save to the same path): ") or self.file_path
        )
        try:
            FileWriter.write_file(file_path, self.fw_file)
            logger.info(f"File saved successfully to {file_path}")
            print(f"File saved successfully to {file_path}")
            self.file_path = file_path
        except Exception as e:
            logger.error(f"Error saving file to {file_path}: {str(e)}")
            print(f"Error saving file: {str(e)}")

    def _get_field_value(self) -> None:
        if not self.fw_file:
            print("No file is currently loaded. Please load a file first.")
            return
        record_type = self._get_valid_input(
            "Enter record type (header/transaction/footer): ",
            lambda x: x.lower() in ["header", "transaction", "footer"],
            "Invalid record type. Please enter header, transaction, or footer.",
        )
        if record_type == "header":
            field = input("Enter field name: ").lower()
            value = getattr(self.fw_file.header, field, None)
        elif record_type == "transaction":
            index = self._get_valid_input(
                "Enter transaction index: ",
                lambda x: x.isdigit() and 0 <= int(x) < len(self.fw_file.transactions),  # type: ignore
                "Invalid transaction index. Please enter a valid number.",
            )
            field = input("Enter field name: ").lower()
            value = getattr(self.fw_file.transactions[int(index)], field, None)
        else:
            field = input("Enter field name: ").lower()
            value = getattr(self.fw_file.footer, field, None)

        if value is not None:
            print(f"Value: {value}")
        else:
            print("Field not found.")

    def _update_field_value(self) -> None:
        if not self.fw_file:
            print("No file is currently loaded. Please load a file first.")
            return

        field_type = self._get_valid_input(
            "Enter record type (header/transaction/footer): ",
            lambda x: x.lower() in ["header", "transaction", "footer"],
            "Invalid record type. Please enter header, transaction, or footer.",
        )

        index = None
        if field_type == "transaction":
            index = self._get_valid_input(
                "Enter transaction index: ",
                lambda x: x.isdigit() and 0 <= int(x) < len(self.fw_file.transactions),  # type: ignore
                "Invalid transaction index. Please enter a valid number.",
            )
            index = int(index)  # type: ignore

        field_name = input("Enter field name: ").lower()
        field_value = input("Enter new value: ")

        try:
            self.fw_file.set_field_value(field_type, field_name, field_value, index)  # type: ignore
            print("Field updated successfully.")
        except (FieldValueValidationException, FieldLockedException, FieldNotFoundException) as e:
            print(f"Error updating field: {str(e)}")

    def _add_transaction(self) -> None:
        if not self.fw_file:
            print("No file is currently loaded. Please load a file first.")
            return
        try:
            amount = self._get_valid_input(
                "Enter amount (without comma, last 2 digits is decimal part): ",
                lambda x: x.isdigit() and len(x) >= 3,
                "Invalid amount. Please enter a valid number with at least 3 digits.",
            )
            currency = self._get_valid_input(
                "Enter currency: ",
                lambda x: x.upper() in FieldLimits.VALID_CURRENCIES,
                f"Invalid currency. Please enter one of {', '.join(FieldLimits.VALID_CURRENCIES)}.",
            ).upper()

            new_transaction = Transaction(
                field_id="02", counter=str(len(self.fw_file.transactions) + 1), amount=amount, currency=currency
            )
            self.fw_file.add_transaction(new_transaction)
            print("Transaction added successfully.")
        except (ValidationException, RecordLimitException) as e:
            print(f"Error adding transaction: {str(e)}")

    def _lock_field(self) -> None:
        self._toggle_field_lock(True)

    def _unlock_field(self) -> None:
        self._toggle_field_lock(False)

    def _toggle_field_lock(self, lock: bool) -> None:
        if not self.fw_file:
            print("No file is currently loaded. Please load a file first.")
            return
        field_type = self._get_valid_input(
            "Enter field type (header/transaction/footer): ",
            lambda x: x.lower() in ["header", "transaction", "footer"],
            "Invalid field type. Please enter header, transaction, or footer.",
        )
        field_name = input("Enter field name: ")
        try:
            if lock:
                self.fw_file.lock_field(field_type, field_name)
                print(f"Field {field_type}.{field_name} locked successfully.")
            else:
                self.fw_file.unlock_field(field_type, field_name)
                print(f"Field {field_type}.{field_name} unlocked successfully.")
        except FieldNotFoundException as e:
            print(f"Error {'locking' if lock else 'unlocking'} field: {str(e)}")

    def _get_valid_input(self, prompt: str, validator: Callable[[str], bool], error_message: str) -> str:
        while True:
            user_input = input(prompt)
            if validator(user_input):
                return user_input.lower()
            logger.warning(f"Invalid input: {user_input}")
            print(error_message)
