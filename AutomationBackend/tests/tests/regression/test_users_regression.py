import pytest

from utils.assertions import assert_body_contains, assert_status_code


@pytest.mark.regression
def test_get_user_not_found(users_service) -> None:
    response = users_service.get_user(user_id=9999)
    assert_status_code(response, 404)


@pytest.mark.regression
def test_list_users_pagination(users_service) -> None:
    response = users_service.list_users(skip=5, limit=5)
    assert_status_code(response, 200)
    assert_body_contains(response, "limit", 5)
