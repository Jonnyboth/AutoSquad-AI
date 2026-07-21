import pytest

from utils.assertions import assert_status_code


@pytest.mark.regression
def test_login_missing_password(http_client) -> None:
    response = http_client.post("/auth/login", json_body={"username": "emilys"})
    assert_status_code(response, 400)


@pytest.mark.regression
def test_login_invalid_credentials(http_client) -> None:
    response = http_client.post(
        "/auth/login", json_body={"username": "emilys", "password": "wrong-password"}
    )
    assert_status_code(response, 400)
