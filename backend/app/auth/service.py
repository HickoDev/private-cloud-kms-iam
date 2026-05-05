from sqlalchemy.orm import Session, selectinload

from app.auth.schemas import CurrentUserResponse
from app.core.security import verify_password
from app.iam.models import Permission, Role, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.email == email)
        .one_or_none()
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.id == user_id)
        .one_or_none()
    )


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)

    if user is None or not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def build_current_user_response(user: User) -> CurrentUserResponse:
    roles = sorted(role.name for role in user.roles)
    permissions = sorted(
        {
            permission.name
            for role in user.roles
            for permission in role.permissions
            if isinstance(permission, Permission)
        }
    )

    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=roles,
        permissions=permissions,
    )
