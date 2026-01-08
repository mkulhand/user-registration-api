class DuplicateEmailError(Exception):
    detail = "User already exists with this mail address"


class InvalidActivationCode(Exception):
    detail = "Invalid activation code provided"


class CodeExpired(Exception):
    detail = "Code is expired"


class UserNotFound(Exception):
    detail = "User not found"
