# Dependency Injection no FastAPI: Uma ou Múltiplas Fábricas por Rota

Este documento explica como organizar **injeção de dependências** em controllers FastAPI usando `fastapi-restful` e CBV, abordando **duas abordagens**: uma instância de usecase por controller ou múltiplos usecases por rota.

---

## 1️⃣ Conceitos

### Tipos de Dependências

* **UseCase:** representa regras de negócio ou operações do sistema.
* **Factory:** função que retorna a instância do usecase, podendo resolver dependências internas.
* **CBV (`@cbv`):** permite agrupar rotas dentro de uma classe, usando DI com `Depends`.

---

## 2️⃣ Abordagem 1: Um usecase por controller

Nesta abordagem, cada controller recebe **uma única instância de usecase**, compartilhada por todas as rotas.

```python
from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from src.Agenda.API.Interfaces.UseCasesAgendaInterface import UseCasesAgendaInterface
from src.Agenda.API.provider import useCase_factory

routerAgenda = APIRouter(prefix="/agenda", tags=["Agenda"])

class CreateAgendaDTO(BaseModel):
    name: str

@cbv(routerAgenda)
class AgendaController:

    # Injeção de dependência única para todas as rotas
    usecase: UseCasesAgendaInterface = Depends(useCase_factory)

    @routerAgenda.post("/")
    def create_agenda(self, payload: CreateAgendaDTO):
        return self.usecase.create_agendamento(payload.name)

    @routerAgenda.put("/{agenda_id}")
    def update_agenda(self, agenda_id: int, payload: CreateAgendaDTO):
        return self.usecase.update_agendamento(agenda_id, payload.name)
```

✅ **Vantagens**:

* Mais limpo e simples; menos repetição de `Depends`.
* Útil quando todas as rotas do controller usam **o mesmo usecase**.

⚠️ **Desvantagens**:

* Menos flexível; se uma rota precisa de outro usecase, você precisa refatorar o controller.

---

## 3️⃣ Abordagem 2: Múltiplos usecases, factory por rota

Nesta abordagem, cada rota recebe sua própria **factory**, que retorna a instância correta do usecase.

```python
from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from src.Agenda.API.Interfaces.UseCasesAgendaInterface import UseCasesAgendaInterface
from src.Agenda.API.provider import create_agenda_usecase_factory, update_agenda_usecase_factory

routerAgenda = APIRouter(prefix="/agenda", tags=["Agenda"])

class CreateAgendaDTO(BaseModel):
    name: str

class UpdateAgendaDTO(BaseModel):
    name: str

@cbv(routerAgenda)
class AgendaController:

    @routerAgenda.post("/")
    def create_agenda(
        self,
        payload: CreateAgendaDTO,
        usecase: UseCasesAgendaInterface = Depends(create_agenda_usecase_factory)
    ):
        return usecase.create_agendamento(payload.name)

    @routerAgenda.put("/{agenda_id}")
    def update_agenda(
        self,
        agenda_id: int,
        payload: UpdateAgendaDTO,
        usecase: UseCasesAgendaInterface = Depends(update_agenda_usecase_factory)
    ):
        return usecase.update_agendamento(agenda_id, payload.name)
```

✅ **Vantagens**:

* Cada rota pode usar **um usecase diferente**.
* Mais flexível para projetos grandes ou microserviços.
* Facilita **mock de rotas individuais** em testes.

⚠️ **Desvantagens**:

* Mais repetição de `Depends` em cada rota.
* Se todas as rotas usam o mesmo usecase, pode parecer redundante.

---

## 4️⃣ Quando usar cada abordagem

| Situação                                                 | Abordagem recomendada         |
| -------------------------------------------------------- | ----------------------------- |
| Todas as rotas de um controller usam **o mesmo usecase** | 1️⃣ Um usecase por controller |
| Rotas de um controller usam **usecases diferentes**      | 2️⃣ Factory por rota          |
| Quer **testabilidade granular** por rota                 | 2️⃣ Factory por rota          |
| Projeto pequeno, simples                                 | 1️⃣ Um usecase por controller |
| Projeto grande, microserviços ou Clean Architecture      | 2️⃣ Factory por rota          |

---

## 5️⃣ Observações finais

* Você **pode combinar** as abordagens com um container DI inteligente, resolvendo dependências automaticamente.
* Mesmo que hoje você use **uma instância única**, vale a pena projetar para permitir múltiplas factories no futuro, se o projeto crescer.
* FastAPI e CBV funcionam bem com **qualquer das abordagens**, desde que você use `Depends` corretamente.
