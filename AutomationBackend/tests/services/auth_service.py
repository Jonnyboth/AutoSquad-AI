from __future__ import annotations

from config.endpoints import AuthEndpoints
from core.http_client import HttpClient
from models.auth_model import LoginRequest, LoginResponse
from utils.assertions import assert_status_code


class AuthService:
    """Encapsula la lógica de negocio del dominio de autenticación.

    Los tests no arman payloads ni llaman rutas directamente: dependen de este
    servicio, así que si el contrato de /login cambia, solo se actualiza aquí.
    """

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def login(self, username: str, password: str) -> str:
        payload = LoginRequest(username=username, password=password)
        response = self._client.post(AuthEndpoints.LOGIN, json_body=payload.model_dump())
        assert_status_code(response, 200)
        return LoginResponse(**response.json()).token
