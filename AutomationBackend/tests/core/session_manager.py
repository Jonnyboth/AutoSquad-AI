from __future__ import annotations

from typing import Optional

from core.http_client import HttpClient
from services.auth_service import AuthService


class SessionManager:
    """Crea un HttpClient autenticado y cachea el token durante la sesión de pytest.

    Evita que cada test dispare su propio login: el token se obtiene una sola vez
    (fixture scope="session" en conftest.py) y se reutiliza en todas las llamadas.
    """

    def __init__(self, base_url: str, timeout: int = 15) -> None:
        self._client = HttpClient(base_url=base_url, timeout=timeout)
        self._auth_service = AuthService(self._client)
        self._token: Optional[str] = None

    def authenticated_client(self, email: str, password: str) -> HttpClient:
        if self._token is None:
            self._token = self._auth_service.login(email, password)
            self._client.set_auth_token(self._token)
        return self._client

    @property
    def raw_client(self) -> HttpClient:
        return self._client
