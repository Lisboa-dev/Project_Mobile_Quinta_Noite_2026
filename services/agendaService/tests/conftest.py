import pytest

from tests.provider import AgendaTestProvider


@pytest.fixture
def agenda_provider() -> AgendaTestProvider:
    return AgendaTestProvider()
