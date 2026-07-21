from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str = Field(alias="accessToken")
