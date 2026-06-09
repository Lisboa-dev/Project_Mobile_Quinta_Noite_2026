import pytest


@pytest.mark.global_suite
def test_global_provider_lists_all_services(global_test_provider):
    assert set(global_test_provider.services) == {
        "agendaService",
        "usersService",
        "auth",
        "notificationService",
        "analyticService",
    }


@pytest.mark.global_suite
def test_global_provider_builds_test_environment(global_test_provider):
    env = global_test_provider.env_for_service("agendaService")

    assert env["ENV"] == "test"
    assert env["TEST_USE_MOCK_DATA"] in {"true", "false"}
    assert "agendaService" in env["PYTHONPATH"]
