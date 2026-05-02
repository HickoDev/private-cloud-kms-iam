from fastapi import APIRouter, HTTPException, status

from app.auth.schemas import LoginRequest

router = APIRouter()


@router.post("/login")
def login(_: LoginRequest) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication will be implemented in the IAM phase.",
    )


@router.get("/me")
def get_current_user() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Current user retrieval will be implemented in the IAM phase.",
    )

