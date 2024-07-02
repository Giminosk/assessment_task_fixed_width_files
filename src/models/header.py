from models.base import BaseField


class Header(BaseField):
    def __init__(self, field_id: str, name: str, surname: str, patronymic: str, address: str):
        super().__init__(field_id)
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.address = address

        self.validate()

    def validate(self) -> None:
        self._validate_field_id(value="01")
        if len(self.name) == 0:
            raise ValueError("Name cannot be empty")
        if len(self.surname) == 0:
            raise ValueError("Surname cannot be empty")
        if len(self.patronymic) == 0:
            raise ValueError("Patronymic cannot be empty")
        if len(self.address) == 0:
            raise ValueError("Address cannot be empty")
