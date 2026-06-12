import pytest

from tests.provider import AnalyticTestProvider


@pytest.fixture
def analytic_provider() -> AnalyticTestProvider:
    return AnalyticTestProvider()
