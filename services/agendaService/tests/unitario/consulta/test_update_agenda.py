from .test_list_agenda import AgendaCreate, FakeAgendaRepository


class UpdatableAgendaRepository(FakeAgendaRepository):
    def update(self, agenda_id, agenda):
        for index, item in enumerate(self.data):
            if item["id"] == agenda_id:
                self.data[index] = {**item, **agenda.dict(exclude_unset=True)}
                return self.data[index]
        return None


def test_update():
    repository = UpdatableAgendaRepository()
    created = repository.create(AgendaCreate("Joao Silva", "Dra. Maria Souza", "2026-07-01", "10:00"))

    result = repository.update(created["id"], AgendaCreate("Joao Silva", "Dra. Maria Souza", "2026-07-01", "11:00"))

    assert result["horario"] == "11:00"
