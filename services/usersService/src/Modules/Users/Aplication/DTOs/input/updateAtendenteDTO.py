from typing import Optional, Protocol


class UpdateAtendenteDTO(Protocol):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    userName: Optional[str]