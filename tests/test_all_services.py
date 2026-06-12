import pytest

from tests.run_tests import run_all


@pytest.mark.service_suite
def test_all_service_suites_pass():
    assert run_all(include_global=False) == 0
