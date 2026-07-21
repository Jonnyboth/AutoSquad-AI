import pytest

from services.auth_service import AuthService
from utils.assertions import assert_status_code


@pytest.mark.component
def test_login_returns_valid_jwt_structure(auth_service: AuthService) -> None:
    token = auth_service.login(username="emilys", password="emilyspass")
    assert token.count(".") == 2, "El accessToken debe tener formato JWT (header.payload.signature)"


@pytest.mark.component
def test_login_response_contains_refresh_token(http_client) -> None:
    response = http_client.post(
        "/auth/login", json_body={"username": "emilys", "password": "emilyspass"}
    )
    assert_status_code(response, 200)
    assert "refreshToken" in response.json()
