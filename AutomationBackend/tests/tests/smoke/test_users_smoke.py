import pytest

from builders.user_builder import UserBuilder
from utils.assertions import assert_response_time, assert_status_code


@pytest.mark.smoke
def test_create_user(users_service) -> None:
    payload = UserBuilder().build()
    response = users_service.create_user(payload)

    assert_status_code(response, 201)
    assert_response_time(response, max_ms=2000)
