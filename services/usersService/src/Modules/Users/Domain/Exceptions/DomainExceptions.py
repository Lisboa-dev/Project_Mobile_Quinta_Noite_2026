class DomainException(Exception):
    """Base exception for user domain rules."""


class InvalidEmailException(DomainException):
    def __init__(self, value: str):
        super().__init__(f"email invalido: {value}")


class InvalidNameException(DomainException):
    pass


class InvalidUsernameException(DomainException):
    pass


class InvalidPasswordException(DomainException):
    pass


class InvalidCargoException(DomainException):
    def __init__(self, value: str):
        super().__init__(f"cargo invalido: {value}")


class UserAlreadyExistsException(DomainException):
    def __init__(self, field: str):
        super().__init__(f"usuario ja existe com este {field}")


class UserNotFoundException(DomainException):
    def __init__(self, user_id: str):
        super().__init__(f"usuario nao encontrado: {user_id}")
