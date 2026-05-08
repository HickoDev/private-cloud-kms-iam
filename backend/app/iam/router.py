from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
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
    request: Request,
    current_user: User = Depends(require_permissions(Permission.USER_CREATE)),
    db: Session = Depends(get_db),
) -> UserResponse:
    created_user = service.create_user(db, payload)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="USER_CREATED",
        resource_type="USER",
        resource_id=str(created_user.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Created user {created_user.email}.",
    )
    return created_user


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
    request: Request,
    current_user: User = Depends(require_permissions(Permission.USER_UPDATE)),
    db: Session = Depends(get_db),
) -> UserResponse:
    updated_user = service.update_user(db, user_id, payload)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="USER_UPDATED",
        resource_type="USER",
        resource_id=str(updated_user.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Updated user {updated_user.email}.",
    )
    return updated_user


@router.post("/users/{user_id}/roles", response_model=UserResponse)
def assign_roles(
    user_id: int,
    payload: AssignRolesRequest,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.ROLE_ASSIGN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    updated_user = service.assign_roles(db, user_id, payload.roles)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="ROLE_ASSIGNED",
        resource_type="USER",
        resource_id=str(updated_user.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Assigned roles to {updated_user.email}: {', '.join(updated_user.roles)}.",
    )
    return updated_user


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
