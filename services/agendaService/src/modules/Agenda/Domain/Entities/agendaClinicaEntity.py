
class AgendaEntity:
    def __init__(self, id: IdAgenda, name: str, consultas: list[Consulta] = [], eventos: list[Evento] = [], pacientes: list[Paciente] = [], profissionais: list[Profissional] = [], especialidades: list[Especialidade] = [], horarios: list[Horario] = []):
        self.id = id
        self.name = name

    def __repr__(self): 
        return f"Agenda(id={self.id}, name={self.name})"

    def __str__(self):
        return f"Agenda(id={self.id}, name={self.name})"