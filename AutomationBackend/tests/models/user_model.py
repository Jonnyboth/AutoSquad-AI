from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    firstName: str
    lastName: str
    age: int


class UserResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
