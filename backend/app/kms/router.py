from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.auth.dependencies import require_permissions
from app.core.database import get_db
from app.core.permissions import Permission
from app.iam.models import User
from app.kms import service
from app.kms.schemas import (
    DecryptRequest,
    DecryptResponse,
    EncryptRequest,
    EncryptResponse,
    KeyCreateRequest,
    KeyResponse,
    KeyVersionResponse,
)

router = APIRouter()


@router.get("", response_model=list[KeyResponse])
def list_keys(
    _: User = Depends(require_permissions(Permission.KEY_READ)),
    db: Session = Depends(get_db),
) -> list[KeyResponse]:
    return service.list_keys(db)


@router.post("", response_model=KeyResponse, status_code=status.HTTP_201_CREATED)
def create_key(
    payload: KeyCreateRequest,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.KEY_CREATE)),
    db: Session = Depends(get_db),
) -> KeyResponse:
    key = service.create_key(db, payload, owner_id=current_user.id)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="KEY_CREATED",
        resource_type="KEY",
        resource_id=str(key.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Created key {key.name}.",
    )
    return key


@router.get("/{key_id}", response_model=KeyResponse)
def get_key(
    key_id: int,
    _: User = Depends(require_permissions(Permission.KEY_READ)),
    db: Session = Depends(get_db),
) -> KeyResponse:
    return service.build_key_response(service.get_key(db, key_id))


@router.post("/{key_id}/disable", response_model=KeyResponse)
def disable_key(
    key_id: int,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.KEY_DISABLE)),
    db: Session = Depends(get_db),
) -> KeyResponse:
    key = service.disable_key(db, key_id)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="KEY_DISABLED",
        resource_type="KEY",
        resource_id=str(key.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Disabled key {key.name}.",
    )
    return key


@router.post("/{key_id}/rotate", response_model=KeyResponse)
def rotate_key(
    key_id: int,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.KEY_ROTATE)),
    db: Session = Depends(get_db),
) -> KeyResponse:
    key = service.rotate_key(db, key_id)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="KEY_ROTATED",
        resource_type="KEY",
        resource_id=str(key.id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Rotated key {key.name} to version {key.active_version}.",
    )
    return key


@router.get("/{key_id}/versions", response_model=list[KeyVersionResponse])
def list_versions(
    key_id: int,
    _: User = Depends(require_permissions(Permission.KEY_READ)),
    db: Session = Depends(get_db),
) -> list[KeyVersionResponse]:
    return service.list_versions(db, key_id)


@router.post("/{key_id}/encrypt", response_model=EncryptResponse)
def encrypt(
    key_id: int,
    payload: EncryptRequest,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.DATA_ENCRYPT)),
    db: Session = Depends(get_db),
) -> EncryptResponse:
    result = service.encrypt_data(db, key_id, payload)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="DATA_ENCRYPTED",
        resource_type="KEY",
        resource_id=str(result.key_id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Encrypted data with key version {result.key_version}.",
    )
    return result


@router.post("/{key_id}/decrypt", response_model=DecryptResponse)
def decrypt(
    key_id: int,
    payload: DecryptRequest,
    request: Request,
    current_user: User = Depends(require_permissions(Permission.DATA_DECRYPT)),
    db: Session = Depends(get_db),
) -> DecryptResponse:
    result = service.decrypt_data(db, key_id, payload)
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="DATA_DECRYPTED",
        resource_type="KEY",
        resource_id=str(key_id),
        ip_address=audit_service.get_request_ip(request),
        details=f"Decrypted data with key version {payload.key_version}.",
    )
    return result
