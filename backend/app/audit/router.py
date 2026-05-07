from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.audit import service
from app.audit.schemas import AuditLogResponse
from app.auth.dependencies import require_permissions
from app.core.database import get_db
from app.core.permissions import Permission
from app.iam.models import User

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = Depends(require_permissions(Permission.AUDIT_READ)),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    return service.list_audit_logs(
        db,
        user_id=user_id,
        action=action,
        status=status,
    )
