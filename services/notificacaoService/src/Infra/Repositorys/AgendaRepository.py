class AgendaRepository:
    def __init__(self):
        self.agendas = []

    def add_agenda(self, agenda):
        self.agendas.append(agenda)

    def get_agendas(self):
        return self.agendas