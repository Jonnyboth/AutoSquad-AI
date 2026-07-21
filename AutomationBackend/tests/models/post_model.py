from pydantic import BaseModel


class CreatePostRequest(BaseModel):
    title: str
    body: str
    userId: int | None


class PostResponse(BaseModel):
    id: int
    title: str
    body: str
    userId: int | None
