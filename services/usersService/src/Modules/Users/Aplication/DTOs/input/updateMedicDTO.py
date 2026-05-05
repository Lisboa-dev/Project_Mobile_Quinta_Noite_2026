from typing import Optional, Protocol


class UpdateMedicDTO(Protocol):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    userName: Optional[str]