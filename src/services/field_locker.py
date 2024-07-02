from utils.exceptions import FieldNotFoundException


class FieldLocker:
    def __init__(self):
        self.locked_fields = {
            "header": set(),
            "transaction": set(),
            "footer": set(),
        }

    def lock_field(self, field_type: str, field_name: str) -> None:
        if field_type not in self.locked_fields:
            raise FieldNotFoundException(field_type)
        self.locked_fields[field_type].add(field_name)

    def unlock_field(self, field_type: str, field_name: str) -> None:
        if field_type not in self.locked_fields:
            raise FieldNotFoundException(field_type)
        if field_name in self.locked_fields[field_type]:
            self.locked_fields[field_type].remove(field_name)

    def is_field_locked(self, field_type: str, field_name: str) -> bool:
        if field_type not in self.locked_fields:
            raise FieldNotFoundException(field_type)
        return field_name in self.locked_fields[field_type]
