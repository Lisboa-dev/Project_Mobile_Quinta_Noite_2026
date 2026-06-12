from .test_list_agenda import AgendaCreate, FakeAgendaRepository


class DeletableAgendaRepository(FakeAgendaRepository):
    def delete(self, agenda_id):
        for index, item in enumerate(self.data):
            if item["id"] == agenda_id:
                del self.data[index]
                return True
        return False


def test_delete():
    repository = DeletableAgendaRepository()
    created = repository.create(AgendaCreate("Joao Silva", "Dra. Maria Souza", "2026-07-01", "10:00"))

    assert repository.delete(created["id"]) is True
    assert repository.list_all() == []
