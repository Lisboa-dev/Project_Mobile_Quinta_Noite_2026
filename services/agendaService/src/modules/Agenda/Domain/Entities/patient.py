

from src.modules.agenda.domain.valueObjects.Id import ID


class Patient:
    


    def __init__(self, id: str | None, name: str, externId: str | None = None, appointments: list[str] | None = None):
        self._id = ID(id)
        self._name = name
        self._appoiments = appointments or []
        self._extern_id = externId or str(self.id)
        
    def add_appoiment(self, appoiment: str):
        self.appointments.append(appoiment)

    def update(self, name: str | None = None):
        if name is not None:
            self.name = name
        return self

    def destroy(self) -> bool:
        return True

    @property
    def id(self) -> ID:
        return self._id

    @id.setter
    def id(self, value: ID | str) -> None:
        self._id = value if isinstance(value, ID) else ID(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def appointments(self) -> list[str]:
        return self._appoiments

    @appointments.setter
    def appointments(self, value: list[str] | None) -> None:
        self._appoiments = value or []

    @property
    def appoiments(self) -> list[str]:
        return self._appoiments

    @appoiments.setter
    def appoiments(self, value: list[str] | None) -> None:
        self._appoiments = value or []

    @property
    def extern_id(self) -> str:
        return self._extern_id

    @extern_id.setter
    def extern_id(self, value: str) -> None:
        self._extern_id = value

    @property
    def externId(self) -> str:
        return self._extern_id

    @externId.setter
    def externId(self, value: str) -> None:
        self._extern_id = value
 
