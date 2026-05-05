from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.service import get_user_by_id
from app.core.database import get_db
from app.core.permissions import Permission as PermissionEnum
from app.core.security import decode_access_token
from app.iam.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    subject = payload.get("sub")

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permissions(*required_permissions: PermissionEnum) -> Callable[..., User]:
    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_permissions = {
            permission.name
            for role in current_user.roles
            for permission in role.permissions
        }
        required = {permission.value for permission in required_permissions}

        if not required.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return permission_dependency
