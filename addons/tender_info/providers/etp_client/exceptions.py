class ETPException(Exception):
    """Base Exception class for all ETP errors"""
    pass


class ETPRequestError(ETPException):
    """Raised when received an expected error code from ETP api"""
    pass
