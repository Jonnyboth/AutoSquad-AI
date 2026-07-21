import pytest

from services.auth_service import AuthService


@pytest.mark.smoke
def test_login_success(auth_service: AuthService) -> None:
    token = auth_service.login(username="emilys", password="emilyspass")
    assert token, "El token no debería estar vacío"
