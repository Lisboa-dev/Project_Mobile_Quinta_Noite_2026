import os


def use_mock_data() -> bool:
    return os.getenv("TEST_USE_MOCK_DATA", "true").lower() in {"1", "true", "yes", "on"}


class AuthTestProvider:
    def configure_mock_env(self, monkeypatch):
        from src.config import get_settings
        from tests.mock_data import MOCK_LOGIN, MOCK_USER_ID

        monkeypatch.setenv("ENV", "test")
        monkeypatch.setenv("AUTH_DEV_USER_ID", MOCK_USER_ID)
        monkeypatch.setenv("AUTH_DEV_USER_EMAIL", MOCK_LOGIN["email"])
        monkeypatch.setenv("AUTH_DEV_USER_NAME", MOCK_LOGIN["name"])
        monkeypatch.setenv("AUTH_DEV_USER_PASSWORD", MOCK_LOGIN["password"])
        monkeypatch.setenv("AUTH_DEV_USER_ROLE", "admin")
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        get_settings.cache_clear()

    def login_body(self) -> dict:
        from tests.mock_data import MOCK_LOGIN

        return MOCK_LOGIN.copy()
