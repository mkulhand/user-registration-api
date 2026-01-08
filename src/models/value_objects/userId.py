class UserId:
    __value: int

    def __init__(self, id: int):
        self.__value = id

    def to_snapshot(self) -> dict:
        return self.__value
