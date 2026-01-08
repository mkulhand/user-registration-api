import re

import bcrypt

from src.models.exceptions import ValidationError


class Password:
    __value: str
    __validation_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]{8,20}$"

    def __init__(self, password: str):
        self.__value = password
        self.__validate()

    def __validate(self):
        if not re.match(self.__validation_pattern, self.__value):
            raise ValidationError(
                infos={
                    "prop": "password",
                    "reason": (
                        "Password must be 8-20 characters long and contain at least:\n"
                        "• one uppercase letter (A-Z)\n"
                        "• one lowercase letter (a-z)\n"
                        "• one number (0-9)\n"
                        "• one special character: ! @ # $ % ^ & * ( ) _ + - = [ ] { } ; : ' \" , . < > / ? ` ~"
                    ),
                }
            )

    def to_snapshot(self) -> str:
        return bcrypt.hashpw(self.__value.encode(), bcrypt.gensalt()).decode()
