import random


class ActivationCode:
    __value: str

    def __init__(self):
        self.__value = str(random.randint(1000, 9999))

    def to_snapshot(self) -> str:
        return self.__value
