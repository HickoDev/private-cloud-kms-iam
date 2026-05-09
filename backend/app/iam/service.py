from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.iam.models import Permission, Role, User
from app.iam.schemas import (
    PermissionResponse,
    RoleResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)


def build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=sorted(role.name for role in user.roles),
    )


def build_role_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=sorted(permission.name for permission in role.permissions),
    )


def list_users(db: Session) -> list[UserResponse]:
    users = (
        db.query(User)
        .options(selectinload(User.roles))
        .order_by(User.id)
        .all()
    )
    return [build_user_response(user) for user in users]


def get_user(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(selectinload(User.roles))
        .filter(User.id == user_id)
        .one_or_none()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


def get_roles_by_name(db: Session, role_names: list[str]) -> list[Role]:
    normalized_names = sorted({role_name.strip().upper() for role_name in role_names})
    if not normalized_names:
        return []

    roles = db.query(Role).filter(Role.name.in_(normalized_names)).all()
    found_names = {role.name for role in roles}
    missing_names = sorted(set(normalized_names) - found_names)

    if missing_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown roles: {', '.join(missing_names)}.",
        )

    return roles


def create_user(db: Session, payload: UserCreateRequest) -> UserResponse:
    existing_user = (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .one_or_none()
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or username already exists.",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
        roles=get_roles_by_name(db, payload.roles),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return build_user_response(get_user(db, user.id))


def update_user(db: Session, user_id: int, payload: UserUpdateRequest) -> UserResponse:
    user = get_user(db, user_id)

    if payload.is_active is False and any(role.name == "ADMIN" for role in user.roles):
        active_admin_count = (
            db.query(User)
            .join(User.roles)
            .filter(Role.name == "ADMIN", User.is_active.is_(True))
            .count()
        )
        if active_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the only active admin user.",
            )

    if payload.username is not None:
        duplicate = (
            db.query(User)
            .filter(User.username == payload.username, User.id != user_id)
            .one_or_none()
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already used by another user.",
            )
        user.username = payload.username

    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)

    return build_user_response(get_user(db, user.id))


def assign_roles(db: Session, user_id: int, role_names: list[str]) -> UserResponse:
    user = get_user(db, user_id)
    user.roles = get_roles_by_name(db, role_names)
    db.commit()
    db.refresh(user)

    return build_user_response(get_user(db, user.id))


def list_roles(db: Session) -> list[RoleResponse]:
    roles = (
        db.query(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.name)
        .all()
    )
    return [build_role_response(role) for role in roles]


def list_permissions(db: Session) -> list[PermissionResponse]:
    permissions = db.query(Permission).order_by(Permission.name).all()
    return [
        PermissionResponse(
            id=permission.id,
            name=permission.name,
            description=permission.description,
        )
        for permission in permissions
    ]
