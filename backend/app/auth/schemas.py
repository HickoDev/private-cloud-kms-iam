from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    roles: list[str]
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserResponse
