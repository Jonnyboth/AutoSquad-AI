import pytest

from builders.user_builder import UserBuilder
from utils.assertions import assert_status_code


@pytest.mark.e2e
def test_user_lifecycle(users_service) -> None:
    """Flujo completo: crear -> consultar -> actualizar -> eliminar un usuario.

    dummyjson.com simula el CRUD (no persiste realmente lo creado), por eso
    los pasos de consulta/actualización/borrado operan sobre un id fijo (1)
    en lugar del id devuelto por el create. Contra un backend real, aquí se
    usaría el id devuelto por create_user.
    """
    create_response = users_service.create_user(UserBuilder().build())
    assert_status_code(create_response, 201)

    get_response = users_service.get_user(user_id=1)
    assert_status_code(get_response, 200)

    update_response = users_service.update_user(user_id=1, payload={"lastName": "E2E-Flow"})
    assert_status_code(update_response, 200)

    delete_response = users_service.delete_user(user_id=1)
    assert_status_code(delete_response, 200)
