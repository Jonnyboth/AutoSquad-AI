import pytest

from builders.post_builder import PostBuilder
from utils.assertions import assert_body_contains, assert_status_code

_SPECIAL_CHARS = "<script>alert(1)</script> & 100% ñ 你好 😀"

# jsonplaceholder.typicode.com es una API falsa (fake REST API): no valida
# reglas de negocio, siempre responde 201 y hace eco del body recibido con un
# id inventado. Por eso estos casos afirman el comportamiento REAL observado
# (201 + eco), no el que tendría un backend real con validación (la mayoría
# debería responder 400). Documentamos esto explícitamente en vez de asumirlo.
EDGE_CASES = [
    pytest.param({"title": ""}, "title", "", id="title_vacio"),
    pytest.param({"body": ""}, "body", "", id="body_vacio"),
    pytest.param({"userId": 0}, "userId", 0, id="userId_cero"),
    pytest.param({"userId": None}, "userId", None, id="userId_nulo"),
    pytest.param({"userId": 1}, "userId", 1, id="userId_existente_en_bd"),
    pytest.param({"title": "A" * 300}, "title", "A" * 300, id="title_300_caracteres"),
    pytest.param({"title": "A"}, "title", "A", id="title_un_caracter"),
    pytest.param({"title": _SPECIAL_CHARS}, "title", _SPECIAL_CHARS, id="title_caracteres_especiales"),
    pytest.param({"body": "B" * 3000}, "body", "B" * 3000, id="body_3000_caracteres"),
    pytest.param({"body": "B"}, "body", "B", id="body_un_caracter"),
    pytest.param({"body": _SPECIAL_CHARS}, "body", _SPECIAL_CHARS, id="body_caracteres_especiales"),
]


@pytest.mark.component
@pytest.mark.parametrize("overrides, field, expected_value", EDGE_CASES)
def test_create_post_edge_cases(posts_service, overrides, field, expected_value) -> None:
    payload = PostBuilder().build().model_copy(update=overrides)
    response = posts_service.create_post(payload)

    assert_status_code(response, 201)
    assert_body_contains(response, field, expected_value)
