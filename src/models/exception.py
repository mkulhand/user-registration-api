class ValidationError(Exception):
    detail = "Error while validating data"
    infos = {}

    def __init__(self, infos: dict | None = None):
        self.infos = infos or {}


class ActivationCodeMailError(Exception):
    detail = "Activation code couldn't be send"


class ActivationCodeError(Exception):
    detail = "Unknown or expired code"
