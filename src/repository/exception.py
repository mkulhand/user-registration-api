class DuplicateEmailError(Exception):
    detail = "User already exists with this mail address"
