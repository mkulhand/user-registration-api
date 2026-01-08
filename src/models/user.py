from .value_objects import ActivationCode, Email, Password, UserId


class User:
    __id: UserId | None
    __email: Email
    __password: Password
    __activationCode: ActivationCode

    def __init__(
        self,
        email: Email,
        password: Password,
        id: UserId | None = None,
    ):
        self.__id = id
        self.__email = email
        self.__password = password
        self.__activationCode = ActivationCode()

    def register(self, id: UserId) -> "User":
        self.__id = id

        return self

    def to_snapshot(self) -> dict:
        return {
            "id": self.__id.to_snapshot() if self.__id else None,
            "email": self.__email.to_snapshot(),
            "password": self.__password.to_snapshot(),
            "activationCode": self.__activationCode.to_snapshot(),
        }
