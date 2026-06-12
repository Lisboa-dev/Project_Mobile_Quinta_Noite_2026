#abstração de um user admin que criará regras para a agenda, é importante que as policies sejam armazenadas aqui para manter a estrutura que o usuario criou
#isso pois as regras serão otimizadas para eliminar redundancias e facilitar os cálculos de agendamentos
from src.modules.agenda.domain.valueObjects.Id import ID

from ..rules.BaseRule import BaseRule





class Clinic:
    
    def __init__(
        self,
        rules: list[BaseRule],
        name: str,
        id: str | None = None,
    ):
        
        self._id = ID.generate_id() if id==None else ID(id)
        self._rules = rules or []
        self._name = name

    def update(self, name: str | None = None, rules: list[BaseRule] | None = None):
        if name is not None:
            self.name = name
        if rules is not None:
            self.rules = rules
        return self

    def addRule(self, rule: BaseRule):
        self._rules.append(rule)

    def deleteRule(self, rule: BaseRule):
        self._rules.remove(rule)

    @property
    def id(self) -> ID:
        return self._id

    @id.setter
    def id(self, value: ID | str) -> None:
        self._id = value if isinstance(value, ID) else ID(value)

    @property
    def rules(self) -> list[BaseRule]:
        return self._rules

    @rules.setter
    def rules(self, value: list[BaseRule] | None) -> None:
        self._rules = value or []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
