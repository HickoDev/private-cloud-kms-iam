from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUserResponse, LoginRequest, TokenResponse
from app.auth.service import authenticate_user, build_current_user_response
from app.core.database import get_db
from app.core.security import create_access_token
from app.iam.models import User

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        audit_service.log_action(
            db,
            user_id=None,
            action="LOGIN_FAILED",
            status=audit_service.STATUS_FAILED,
            ip_address=audit_service.get_request_ip(request),
            details=f"Failed login for {payload.email}.",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    audit_service.log_action(
        db,
        user_id=user.id,
        action="LOGIN_SUCCESS",
        ip_address=audit_service.get_request_ip(request),
        details=f"User {user.email} logged in.",
    )

    return TokenResponse(
        access_token=create_access_token(subject=str(user.id)),
        user=build_current_user_response(user),
    )


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    return build_current_user_response(current_user)
