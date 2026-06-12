from dataclasses import dataclass


@dataclass
class AgendaCreate:
    paciente: str
    profissional: str
    data_hora: str
    horario: str

    def dict(self, exclude_unset=False):
        return self.__dict__.copy()


class FakeAgendaRepository:
    def __init__(self):
        self.data = []
        self.current_id = 1

    def create(self, agenda):
        item = agenda.dict()
        item["id"] = self.current_id
        self.current_id += 1
        self.data.append(item)
        return item

    def list_all(self):
        return self.data


def test_list_all():
    repository = FakeAgendaRepository()

    repository.create(AgendaCreate("Joao Silva", "Dra. Maria Souza", "2026-07-01T10:00:00", "10:00"))
    repository.create(AgendaCreate("Ana Pereira", "Dr. Carlos Lima", "2026-07-01T11:00:00", "11:00"))

    result = repository.list_all()

    assert len(result) == 2
    assert result[0]["paciente"] == "Joao Silva"
    assert result[1]["paciente"] == "Ana Pereira"
