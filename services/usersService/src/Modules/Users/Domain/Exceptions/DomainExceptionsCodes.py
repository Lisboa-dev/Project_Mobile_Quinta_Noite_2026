class UserDomainException(Exception):
    code = "USER_DOMAIN_ERROR"

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}


class InvalidTimeRangeException(UserDomainException):
    code = "INVALID_TIME_RANGE"


class InvalidTimeFormatException(UserDomainException):
    code = "INVALID_TIME_FORMAT"


class MissingTimeBoundaryException(UserDomainException):
    code = "MISSING_TIME_BOUNDARY"


class InvalidIdComparisonException(UserDomainException):
    code = "INVALID_ID_COMPARISON"

