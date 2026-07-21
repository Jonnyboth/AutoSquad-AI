from __future__ import annotations

from models.post_model import CreatePostRequest
from utils.data_generator import random_body, random_title


class PostBuilder:
    """Builder encadenable para construir payloads de post de forma legible en los tests.

    Por defecto genera datos válidos con Faker; los métodos with_* permiten
    sobreescribir solo el campo que un caso de prueba puntual necesita variar
    (ej. dejar title vacío mientras body/userId quedan con su valor válido).
    """

    def __init__(self) -> None:
        self._title: str = random_title()
        self._body: str = random_body()
        self._user_id: int | None = 1

    def with_title(self, title: str) -> "PostBuilder":
        self._title = title
        return self

    def with_body(self, body: str) -> "PostBuilder":
        self._body = body
        return self

    def with_user_id(self, user_id: int | None) -> "PostBuilder":
        self._user_id = user_id
        return self

    def build(self) -> CreatePostRequest:
        return CreatePostRequest(title=self._title, body=self._body, userId=self._user_id)
