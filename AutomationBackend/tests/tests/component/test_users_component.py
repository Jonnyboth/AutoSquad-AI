import pytest

from utils.assertions import assert_json_schema, assert_status_code

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
    },
    "required": ["id", "firstName", "lastName"],
}



@pytest.mark.component
def test_get_user_matches_schema(users_service) -> None:
    response = users_service.get_user(user_id=1)
    assert_status_code(response, 200)
    assert_json_schema(response, USER_SCHEMA)


@pytest.mark.component
def test_update_user_persists_field(users_service) -> None:
    response = users_service.update_user(user_id=1, payload={"lastName": "QA-Up"
    "dated"})
    assert_status_code(response, 200)
