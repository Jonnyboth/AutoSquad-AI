from __future__ import annotations

from requests import Response

from config.endpoints import PostsEndpoints
from core.http_client import HttpClient
from models.post_model import CreatePostRequest


class PostsService:
    """Encapsula las operaciones del dominio de posts sobre HttpClient."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def create_post(self, payload: CreatePostRequest) -> Response:
        return self._client.post(PostsEndpoints.BASE, json_body=payload.model_dump())
