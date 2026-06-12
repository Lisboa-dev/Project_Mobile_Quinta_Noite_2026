class AgendaDomainException(Exception):
    code = "AGENDA_DOMAIN_ERROR"

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}


class InvalidTimeRangeException(AgendaDomainException):
    code = "INVALID_TIME_RANGE"


class InvalidTimeFormatException(AgendaDomainException):
    code = "INVALID_TIME_FORMAT"


class MissingTimeBoundaryException(AgendaDomainException):
    code = "MISSING_TIME_BOUNDARY"


class InvalidIdComparisonException(AgendaDomainException):
    code = "INVALID_ID_COMPARISON"


class EntityNotAvailableException(AgendaDomainException):
    code = "ENTITY_NOT_AVAILABLE"
