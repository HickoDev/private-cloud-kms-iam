from fastapi import Request
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.audit.schemas import AuditLogResponse

STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"


def get_request_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host


def log_action(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    status: str = STATUS_SUCCESS,
    ip_address: str | None = None,
    details: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        ip_address=ip_address,
        details=details,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def build_audit_log_response(audit_log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=audit_log.id,
        user_id=audit_log.user_id,
        action=audit_log.action,
        resource_type=audit_log.resource_type,
        resource_id=audit_log.resource_id,
        status=audit_log.status,
        ip_address=audit_log.ip_address,
        details=audit_log.details,
        created_at=audit_log.created_at,
    )


def list_audit_logs(
    db: Session,
    *,
    user_id: int | None = None,
    action: str | None = None,
    status: str | None = None,
) -> list[AuditLogResponse]:
    query = db.query(AuditLog)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if status is not None:
        query = query.filter(AuditLog.status == status)

    logs = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).limit(200).all()
    return [build_audit_log_response(log) for log in logs]
