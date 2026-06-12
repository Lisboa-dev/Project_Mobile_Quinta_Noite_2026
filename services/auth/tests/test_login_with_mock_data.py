import asyncio

from src.services.login import loginService, validateLoginService


def test_login_service_uses_mock_dev_user(auth_provider, monkeypatch):
    async def run():
        auth_provider.configure_mock_env(monkeypatch)

        result = await loginService(auth_provider.login_body())

        assert result is not None
        assert result["user_id"] == "auth-user-1"
        assert await validateLoginService(result["tokens"]["access_token"]) is True

    asyncio.run(run())


def test_login_service_rejects_invalid_password(auth_provider, monkeypatch):
    async def run():
        auth_provider.configure_mock_env(monkeypatch)
        body = auth_provider.login_body()
        body["password"] = "wrong"

        assert await loginService(body) is None

    asyncio.run(run())
