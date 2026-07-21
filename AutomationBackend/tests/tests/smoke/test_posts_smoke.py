import pytest

from builders.post_builder import PostBuilder
from utils.assertions import assert_body_contains, assert_status_code


@pytest.mark.smoke
def test_create_post(posts_service) -> None:
    """Caso feliz: crear un post con title/body/userId válidos."""
    payload = (
        PostBuilder()
        .with_title("Nuevo caso de prueba")
        .with_body("Contenido para validar mi automatización")
        .with_user_id(1)
        .build()
    )
    response = posts_service.create_post(payload)

    assert_status_code(response, 201)
    assert_body_contains(response, "title", "Nuevo caso de prueba")
    assert_body_contains(response, "userId", 1)
