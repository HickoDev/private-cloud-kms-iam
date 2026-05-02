from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("")
def list_audit_logs() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Audit logs will be implemented in the audit phase.",
    )

