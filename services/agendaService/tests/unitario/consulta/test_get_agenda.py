from .test_list_agenda import AgendaCreate, FakeAgendaRepository


class GettableAgendaRepository(FakeAgendaRepository):
    def get_by_id(self, agenda_id):
        return next((agenda for agenda in self.data if agenda["id"] == agenda_id), None)


def test_get_by_id():
    repository = GettableAgendaRepository()
    created = repository.create(AgendaCreate("Joao Silva", "Dra. Maria Souza", "2026-07-01T10:00:00", "10:00"))

    result = repository.get_by_id(created["id"])

    assert result["paciente"] == "Joao Silva"
