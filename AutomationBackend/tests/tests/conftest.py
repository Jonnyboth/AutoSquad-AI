from __future__ import annotations

import pytest

from core import console_reporter
from core.http_client import HttpClient
from services.auth_service import AuthService
from services.posts_service import PostsService
from services.users_service import UsersService


@pytest.fixture(scope="module", autouse=True)
def _print_module_art() -> None:
    """Imprime el arte de bienvenida una sola vez, al iniciar cada archivo de test."""
    console_reporter.print_module_banner()


@pytest.fixture(autouse=True)
def _reset_console_buffer() -> None:
    """Limpia el buffer de request/response/aserciones antes de cada test individual."""
    console_reporter.reset_buffer()


@pytest.fixture
def users_service(http_client: HttpClient) -> UsersService:
    return UsersService(http_client)


@pytest.fixture
def auth_service(http_client: HttpClient) -> AuthService:
    return AuthService(http_client)


@pytest.fixture
def posts_service(posts_http_client: HttpClient) -> PostsService:
    return PostsService(posts_http_client)
