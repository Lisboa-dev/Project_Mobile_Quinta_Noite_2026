# Demonstração: UseCase Singleton + Repository Scoped corretamente

from typing import Protocol, Callable
from dataclasses import dataclass
from uuid import uuid4

# =========================
# DOMAIN
# =========================

@dataclass
class User:
    id: str
    name: str
    email: str

    @staticmethod
    def create(name: str, email: str) -> "User":
        if not name:
            raise ValueError("Name is required")
        if "@" not in email:
            raise ValueError("Invalid email")
        return User(str(uuid4()), name, email)


class IUserRepository(Protocol):
    def save(self, user: User) -> None: ...
    def find_by_email(self, email: str) -> User | None: ...


# =========================
# USE CASE (Singleton)
# =========================

class CreateUserUseCase:

    def __init__(self, repo_factory: Callable[[], IUserRepository]):
        # ⚠️ recebe uma factory, NÃO o repo
        self.repo_factory = repo_factory

    def execute(self, name: str, email: str) -> User:
        # 🔥 cria um repo NOVO por execução (scoped)
        repo = self.repo_factory()

        if repo.find_by_email(email):
            raise ValueError("User already exists")

        user = User.create(name, email)
        repo.save(user)

        return user


# =========================
# INFRA (Scoped)
# =========================

class InMemoryUserRepository:

    def __init__(self):
        print("[Repo] Nova instância criada")  # debug
        self._users = []

    def save(self, user: User) -> None:
        self._users.append(user)

    def find_by_email(self, email: str) -> User | None:
        for u in self._users:
            if u.email == email:
                return u
        return None


# =========================
# CONTROLLER (Singleton)
# =========================

class UserController:

    def __init__(self, use_case: CreateUserUseCase):
        self.use_case = use_case

    def create(self, name: str, email: str):
        return self.use_case.execute(name, email)


# =========================
# FACTORY (Composition Root)
# =========================

class AppFactory:
    _controller = None

    @classmethod
    def create_controller(cls):
        if cls._controller is None:

            # 🔥 Factory de repository (scoped)
            def repo_factory():
                return InMemoryUserRepository()

            use_case = CreateUserUseCase(repo_factory)
            cls._controller = UserController(use_case)

        return cls._controller


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    controller = AppFactory.create_controller()

    print("--- Request 1 ---")
    controller.create("Matheus", "matheus@email.com")

    print("--- Request 2 ---")
    controller.create("Joao", "joao@email.com")

# Saída esperada:
# [Repo] Nova instância criada
# [Repo] Nova instância criada
#
# 👉 Um repository novo por execução (scoped)
# 👉 UseCase e Controller continuam singleton


### 📌 Importante

* atualmente o modelo que propus no codigo é todo scoped, caso queira mudar para singleton, basta mudar a implementação da factory e criar uma factory que cria um repository scoped



# UseCase Singleton vs Dados por Request

## 📌 Problema comum

É comum pensar:

> “Se o UseCase é singleton, como ele lida com dados diferentes a cada request?”

Essa dúvida surge porque há uma confusão entre:

* **lifecycle de objetos**
* **lifecycle dos dados**

---

## 🧠 1. Lifecycle de objetos

Refere-se a quanto tempo uma instância vive na aplicação:

* **Singleton** → uma única instância para toda a aplicação
* **Scoped** → uma instância por request
* **Transient** → nova instância sempre

---

## 🧠 2. Lifecycle dos dados

Refere-se a **de onde vêm e para onde vão os dados**.

Em um sistema bem projetado:

* dados entram via parâmetros
* são processados
* não ficam armazenados no objeto

---

## ❌ Onde dá problema

Quando você mistura os dois conceitos.

### Exemplo errado

```python
class CreateUserUseCase:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

🔴 Problema:

* estado fica preso no objeto
* singleton causaria conflito entre requests

---

## ✅ Forma correta

```python
class CreateUserUseCase:
    def execute(self, name: str, email: str):
        return User.create(name, email)
```

✔️ Dados vêm por parâmetro
✔️ Nenhum estado interno

---

## 🧠 Regra de ouro

> UseCase não armazena dados — ele processa dados

---

## 🧩 Onde o estado realmente vive?

| Camada     | Possui estado? |
| ---------- | -------------- |
| Controller | ❌ Não          |
| UseCase    | ❌ Não          |
| Entity     | ✅ Sim          |
| Repository | ⚠️ Depende     |

---

## 🧱 Papel da Entity

```python
user = User.create(name, email)
```

* cada chamada cria uma nova instância
* estado isolado por execução

👉 Isso resolve o problema de concorrência

---

## ⚠️ Quando singleton vira problema?

Se o UseCase tiver estado mutável:

### ❌ Exemplo 1

```python
self.last_user = None
```

### ❌ Exemplo 2

```python
self.cache = {}
```

### ❌ Exemplo 3

```python
self.current_user = ...
```

🔴 Isso causa:

* vazamento de dados entre requests
* problemas de concorrência

---

## 🧠 Forma mental correta

Pense no UseCase como uma função:

```python
def create_user(repo, name, email):
    ...
```

👉 A função não precisa ser recriada a cada chamada
👉 Apenas recebe novos dados

---

## 🚀 Conclusão

* ✔️ UseCase pode ser singleton
* ✔️ Dados por request entram via parâmetros
* ✔️ Entities carregam o estado
* ❌ Problema só existe se houver estado interno

---

## 🔥 Insight final

> Lifecycle do objeto ≠ Lifecycle dos dados

---
