class IncorrectMCCCodeError(Exception):
    def __init__(self, mcc_code: int, message: str):
        self.mcc_code = mcc_code
        self.message = message

    def __str__(self):
        return f"{self.mcc_code}: {self.message}"


class RetryExceededError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class EncryptManagerError(Exception):
    pass


class EncodeExceptionError(EncryptManagerError):
    pass


class DecodeExceptionError(EncryptManagerError):
    pass
