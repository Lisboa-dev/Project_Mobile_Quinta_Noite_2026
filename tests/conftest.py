import pytest

from tests.providers import GlobalTestProvider


@pytest.fixture(scope="session")
def global_test_provider() -> GlobalTestProvider:
    return GlobalTestProvider()
