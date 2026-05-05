from pydantic import BaseModel, EmailStr, Field


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[str]


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    roles: list[str]


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    roles: list[str] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    is_active: bool | None = None


class AssignRolesRequest(BaseModel):
    roles: list[str]
