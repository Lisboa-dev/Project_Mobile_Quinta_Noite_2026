import pytest

from tests.provider import UsersTestProvider


@pytest.fixture
def users_provider() -> UsersTestProvider:
    return UsersTestProvider()
