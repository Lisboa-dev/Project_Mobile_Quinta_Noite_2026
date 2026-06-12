import pytest

from tests.provider import AuthTestProvider


@pytest.fixture
def auth_provider() -> AuthTestProvider:
    return AuthTestProvider()
