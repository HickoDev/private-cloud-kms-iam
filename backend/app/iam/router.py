from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/users")
def list_users() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User listing will be implemented in the IAM phase.",
    )


@router.post("/users")
def create_user() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation will be implemented in the IAM phase.",
    )


@router.get("/roles")
def list_roles() -> list[str]:
    return ["ADMIN", "KEY_MANAGER", "KEY_USER", "AUDITOR"]


@router.get("/permissions")
def list_permissions() -> list[str]:
    return [
        "USER_READ",
        "USER_CREATE",
        "USER_UPDATE",
        "ROLE_ASSIGN",
        "KEY_READ",
        "KEY_CREATE",
        "KEY_DISABLE",
        "KEY_ROTATE",
        "DATA_ENCRYPT",
        "DATA_DECRYPT",
        "AUDIT_READ",
    ]

