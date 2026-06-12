import pytest

from modules.users.domain.exceptions.DomainExceptions import UserAlreadyExistsException
from tests import mock_data


@pytest.mark.asyncio
async def test_create_medic_with_mock_data_persists_and_emits_event(users_provider):
    repository = users_provider.repository()
    event_bus = users_provider.event_bus()
    use_case = users_provider.create_medic_use_case(repository=repository, event_bus=event_bus)

    result = await use_case.execute(users_provider.medic_command())

    assert result.success is True
    assert result.resource == "medic"
    assert result.resource_id == mock_data.MOCK_MEDIC_ID
    assert len(event_bus.events) == 1


@pytest.mark.asyncio
async def test_create_medic_rejects_duplicate_username(users_provider):
    repository = users_provider.repository()
    use_case = users_provider.create_medic_use_case(repository=repository, event_bus=users_provider.event_bus())
    command = users_provider.medic_command()

    await use_case.execute(command)

    with pytest.raises(UserAlreadyExistsException):
        await use_case.execute(command)
