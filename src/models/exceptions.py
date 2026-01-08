class ValidationError(Exception):
    detail = "Error while validating data"
    infos = {}

    def __init__(self, infos: dict | None = None):
        self.infos = infos or {}
