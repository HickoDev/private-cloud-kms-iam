from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.iam.models import User
from app.kms.crypto import (
    decrypt_text,
    encrypt_text,
    generate_data_key,
    protect_key_material,
    unprotect_key_material,
)
from app.kms.models import KeyAccess, KeyVersion, KmsKey
from app.kms.schemas import (
    DecryptRequest,
    DecryptResponse,
    EncryptRequest,
    EncryptResponse,
    KeyAccessGrantRequest,
    KeyAccessResponse,
    KeyCreateRequest,
    KeyResponse,
    KeyVersionResponse,
)

SUPPORTED_ALGORITHM = "AES-256-GCM"
STATUS_ACTIVE = "ACTIVE"
STATUS_DISABLED = "DISABLED"
VIEW_ALL_KEY_ROLES = {"ADMIN", "KEY_MANAGER", "AUDITOR"}


def build_key_response(key: KmsKey) -> KeyResponse:
    active_version = next(
        (version.version_number for version in key.versions if version.is_active),
        None,
    )

    return KeyResponse(
        id=key.id,
        name=key.name,
        description=key.description,
        algorithm=key.algorithm,
        status=key.status,
        active_version=active_version,
        created_at=key.created_at,
        disabled_at=key.disabled_at,
    )


def user_has_role(user: User, *role_names: str) -> bool:
    allowed_roles = set(role_names)
    return any(role.name in allowed_roles for role in user.roles)


def can_view_all_keys(user: User) -> bool:
    return user_has_role(user, *VIEW_ALL_KEY_ROLES)


def build_access_response(access: KeyAccess, user: User) -> KeyAccessResponse:
    return KeyAccessResponse(
        id=access.id,
        key_id=access.key_id,
        user_id=access.user_id,
        username=user.username,
        email=user.email,
        can_encrypt=access.can_encrypt,
        can_decrypt=access.can_decrypt,
    )


def build_version_response(version: KeyVersion) -> KeyVersionResponse:
    return KeyVersionResponse(
        id=version.id,
        key_id=version.key_id,
        version_number=version.version_number,
        is_active=version.is_active,
        created_at=version.created_at,
        rotated_at=version.rotated_at,
    )


def list_keys(db: Session, current_user: User) -> list[KeyResponse]:
    query = db.query(KmsKey).options(selectinload(KmsKey.versions))

    if not can_view_all_keys(current_user):
        query = (
            query.join(KeyAccess, KeyAccess.key_id == KmsKey.id)
            .filter(
                KeyAccess.user_id == current_user.id,
                or_(KeyAccess.can_encrypt.is_(True), KeyAccess.can_decrypt.is_(True)),
            )
            .distinct()
        )

    keys = query.order_by(KmsKey.id).all()
    return [build_key_response(key) for key in keys]


def get_key(db: Session, key_id: int) -> KmsKey:
    key = (
        db.query(KmsKey)
        .options(selectinload(KmsKey.versions))
        .filter(KmsKey.id == key_id)
        .one_or_none()
    )
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found.",
        )
    return key


def ensure_key_visible(db: Session, key_id: int, current_user: User) -> None:
    if can_view_all_keys(current_user):
        return

    access = (
        db.query(KeyAccess)
        .filter(
            KeyAccess.key_id == key_id,
            KeyAccess.user_id == current_user.id,
            or_(KeyAccess.can_encrypt.is_(True), KeyAccess.can_decrypt.is_(True)),
        )
        .one_or_none()
    )
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this key.",
        )


def ensure_key_operation_access(
    db: Session,
    key_id: int,
    current_user: User,
    operation: str,
) -> None:
    if user_has_role(current_user, "ADMIN"):
        return

    column = KeyAccess.can_encrypt if operation == "encrypt" else KeyAccess.can_decrypt
    access = (
        db.query(KeyAccess)
        .filter(
            KeyAccess.key_id == key_id,
            KeyAccess.user_id == current_user.id,
            column.is_(True),
        )
        .one_or_none()
    )
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not allowed to {operation} with this key.",
        )


def get_active_version(key: KmsKey) -> KeyVersion:
    active_version = next((version for version in key.versions if version.is_active), None)
    if active_version is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key does not have an active version.",
        )
    return active_version


def create_key(db: Session, payload: KeyCreateRequest, owner_id: int) -> KeyResponse:
    if payload.algorithm != SUPPORTED_ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only AES-256-GCM is supported.",
        )

    existing_key = db.query(KmsKey).filter(KmsKey.name == payload.name).one_or_none()
    if existing_key is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A key with this name already exists.",
        )

    key_material = generate_data_key()
    encrypted_key_material, key_material_nonce = protect_key_material(key_material)
    key = KmsKey(
        name=payload.name,
        description=payload.description,
        algorithm=payload.algorithm,
        status=STATUS_ACTIVE,
        owner_id=owner_id,
        versions=[
            KeyVersion(
                version_number=1,
                encrypted_key_material=encrypted_key_material,
                key_material_nonce=key_material_nonce,
                is_active=True,
            )
        ],
    )

    db.add(key)
    db.commit()

    return build_key_response(get_key(db, key.id))


def disable_key(db: Session, key_id: int) -> KeyResponse:
    key = get_key(db, key_id)
    if key.status == STATUS_DISABLED:
        return build_key_response(key)

    key.status = STATUS_DISABLED
    key.disabled_at = datetime.now(UTC)
    db.commit()

    return build_key_response(get_key(db, key.id))


def rotate_key(db: Session, key_id: int) -> KeyResponse:
    key = get_key(db, key_id)
    if key.status != STATUS_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active keys can be rotated.",
        )

    now = datetime.now(UTC)
    latest_version_number = max(
        (version.version_number for version in key.versions),
        default=0,
    )

    for version in key.versions:
        if version.is_active:
            version.is_active = False
            version.rotated_at = now

    key_material = generate_data_key()
    encrypted_key_material, key_material_nonce = protect_key_material(key_material)
    key.versions.append(
        KeyVersion(
            version_number=latest_version_number + 1,
            encrypted_key_material=encrypted_key_material,
            key_material_nonce=key_material_nonce,
            is_active=True,
        )
    )

    db.commit()

    return build_key_response(get_key(db, key.id))


def list_versions(
    db: Session,
    key_id: int,
    current_user: User,
) -> list[KeyVersionResponse]:
    ensure_key_visible(db, key_id, current_user)
    key = get_key(db, key_id)
    return [
        build_version_response(version)
        for version in sorted(key.versions, key=lambda item: item.version_number)
    ]


def encrypt_data(
    db: Session,
    key_id: int,
    payload: EncryptRequest,
    current_user: User,
) -> EncryptResponse:
    ensure_key_operation_access(db, key_id, current_user, "encrypt")
    key = get_key(db, key_id)
    if key.status != STATUS_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disabled keys cannot encrypt new data.",
        )

    active_version = get_active_version(key)
    key_material = unprotect_key_material(
        active_version.encrypted_key_material,
        active_version.key_material_nonce,
    )
    ciphertext, nonce = encrypt_text(key_material, payload.plaintext)

    return EncryptResponse(
        key_id=key.id,
        key_version=active_version.version_number,
        algorithm=key.algorithm,
        ciphertext=ciphertext,
        nonce=nonce,
    )


def decrypt_data(
    db: Session,
    key_id: int,
    payload: DecryptRequest,
    current_user: User,
) -> DecryptResponse:
    ensure_key_operation_access(db, key_id, current_user, "decrypt")
    key = get_key(db, key_id)
    key_version = next(
        (
            version
            for version in key.versions
            if version.version_number == payload.key_version
        ),
        None,
    )
    if key_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key version not found.",
        )

    try:
        key_material = unprotect_key_material(
            key_version.encrypted_key_material,
            key_version.key_material_nonce,
        )
        plaintext = decrypt_text(key_material, payload.ciphertext, payload.nonce)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return DecryptResponse(plaintext=plaintext)


def list_key_access(db: Session, key_id: int) -> list[KeyAccessResponse]:
    get_key(db, key_id)
    rows = (
        db.query(KeyAccess, User)
        .join(User, User.id == KeyAccess.user_id)
        .filter(KeyAccess.key_id == key_id)
        .order_by(User.email)
        .all()
    )
    return [build_access_response(access, user) for access, user in rows]


def grant_key_access(
    db: Session,
    key_id: int,
    payload: KeyAccessGrantRequest,
) -> KeyAccessResponse:
    get_key(db, key_id)
    user = db.query(User).filter(User.id == payload.user_id).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    access = (
        db.query(KeyAccess)
        .filter(KeyAccess.key_id == key_id, KeyAccess.user_id == payload.user_id)
        .one_or_none()
    )

    if access is None:
        access = KeyAccess(
            key_id=key_id,
            user_id=payload.user_id,
            can_encrypt=payload.can_encrypt,
            can_decrypt=payload.can_decrypt,
        )
        db.add(access)
    else:
        access.can_encrypt = payload.can_encrypt
        access.can_decrypt = payload.can_decrypt

    db.commit()
    db.refresh(access)

    return build_access_response(access, user)


def revoke_key_access(db: Session, key_id: int, user_id: int) -> None:
    access = (
        db.query(KeyAccess)
        .filter(KeyAccess.key_id == key_id, KeyAccess.user_id == user_id)
        .one_or_none()
    )
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key access entry not found.",
        )

    db.delete(access)
    db.commit()
