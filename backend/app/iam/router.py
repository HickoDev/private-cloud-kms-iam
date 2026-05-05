from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.core.database import get_db
from app.core.permissions import Permission
from app.iam import service
from app.iam.models import User
from app.iam.schemas import (
    AssignRolesRequest,
    PermissionResponse,
    RoleResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(require_permissions(Permission.USER_READ)),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return service.list_users(db)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateRequest,
    _: User = Depends(require_permissions(Permission.USER_CREATE)),
    db: Session = Depends(get_db),
) -> UserResponse:
    return service.create_user(db, payload)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _: User = Depends(require_permissions(Permission.USER_READ)),
    db: Session = Depends(get_db),
) -> UserResponse:
    return service.build_user_response(service.get_user(db, user_id))


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    _: User = Depends(require_permissions(Permission.USER_UPDATE)),
    db: Session = Depends(get_db),
) -> UserResponse:
    return service.update_user(db, user_id, payload)


@router.post("/users/{user_id}/roles", response_model=UserResponse)
def assign_roles(
    user_id: int,
    payload: AssignRolesRequest,
    _: User = Depends(require_permissions(Permission.ROLE_ASSIGN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    return service.assign_roles(db, user_id, payload.roles)


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(
    _: User = Depends(require_permissions(Permission.ROLE_ASSIGN)),
    db: Session = Depends(get_db),
) -> list[RoleResponse]:
    return service.list_roles(db)


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    _: User = Depends(require_permissions(Permission.ROLE_ASSIGN)),
    db: Session = Depends(get_db),
) -> list[PermissionResponse]:
    return service.list_permissions(db)
