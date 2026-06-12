# Exemplo de arquitetura focada na camada de domínio
# Sem controller / framework

from typing import Protocol
from dataclasses import dataclass
from uuid import uuid4

# =========================
# Entity
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

        return User(
            id=str(uuid4()),
            name=name,
            email=email
        )

# =========================
# Repository (Interface)
# =========================

class IUserRepository(Protocol):
    def save(self, user: User) -> None: ...
    def find_by_email(self, email: str) -> User | None: ...

# =========================
# Use Case
# =========================

class CreateUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, name: str, email: str) -> User:

        # regra de negócio
        existing_user = self.repository.find_by_email(email)
        if existing_user:
            raise ValueError("User already exists")

        user = User.create(name, email)

        self.repository.save(user)

        return user

# =========================
# Infra fake (in-memory)
# =========================

class InMemoryUserRepository:

    def __init__(self):
        self.users = []

    def save(self, user: User) -> None:
        self.users.append(user)

    def find_by_email(self, email: str) -> User | None:
        for u in self.users:
            if u.email == email:
                return u
        return None

# =========================
# Execução (sem controller)
# =========================

if __name__ == "__main__":
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(repo)

    user = use_case.execute("Matheus", "matheus@email.com")

    print(user)
