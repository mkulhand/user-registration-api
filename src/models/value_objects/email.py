import re

from src.models.exceptions import ValidationError


class Email:
    __value: str
    __validation_pattern = r"[^@]+@[^@]+\.[^@]+"

    def __init__(self, email: str):
        self.__value = email.lower()
        self.__validate()

    def __validate(self):
        if not re.match(self.__validation_pattern, self.__value):
            raise ValidationError(
                infos={"prop": "email", "reason": "invalid mail syntax"}
            )

    def to_snapshot(self) -> str:
        return self.__value
