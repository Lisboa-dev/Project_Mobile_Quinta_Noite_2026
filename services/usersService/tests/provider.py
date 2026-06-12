import os
from uuid import NAMESPACE_URL, uuid4, uuid5

from modules.users.application.dtos.useCase.command.CreateMedicCommand import CreateMedicCommand
from modules.users.application.useCases.commands.medic.CreateUseCase import CreateMedicUseCase
from modules.users.domain.valueObjects.Id import ID

from tests import mock_data


def use_mock_data() -> bool:
    return os.getenv("TEST_USE_MOCK_DATA", "true").lower() in {"1", "true", "yes", "on"}


class FakeUserRepository:
    def __init__(self):
        self.items = {}

    def _mock_uuid(self, user) -> str:
        username = getattr(getattr(user, "userName", None), "value", None)
        email = getattr(getattr(user, "email", None), "value", None)
        if username and email:
            return str(uuid5(NAMESPACE_URL, f"usersService/tests/{username}:{email}"))
        return str(uuid4())

    def save(self, user):
        if getattr(user, "id", None) is None:
            user.id = ID(self._mock_uuid(user))
        self.items[str(user.id)] = user
        return user

    def find_by_username(self, username: str):
        return next((user for user in self.items.values() if user.userName.value == username), None)

    def find_by_email(self, email: str):
        return next((user for user in self.items.values() if user.email.value == email), None)

    def find_by_id(self, user_id: str):
        return self.items.get(str(user_id))

    def find_all(self):
        return list(self.items.values())

    def update(self, user_id: str, changes: dict):
        user = self.find_by_id(user_id)
        if user is None:
            return None
        user.update(**changes)
        return user

    def delete(self, user_id: str):
        return self.items.pop(str(user_id), None) is not None


class FakeEventBus:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


class UsersTestProvider:
    def medic_command(self) -> CreateMedicCommand:
        data = mock_data.MOCK_MEDIC if use_mock_data() else {}
        return CreateMedicCommand(**data)

    def repository(self) -> FakeUserRepository:
        return FakeUserRepository()

    def event_bus(self) -> FakeEventBus:
        return FakeEventBus()

    def create_medic_use_case(self, repository=None, event_bus=None) -> CreateMedicUseCase:
        return CreateMedicUseCase(repository or self.repository(), event_bus or self.event_bus())
