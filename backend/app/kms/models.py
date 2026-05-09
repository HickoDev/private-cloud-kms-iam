from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KmsKey(Base):
    __tablename__ = "kms_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    algorithm: Mapped[str] = mapped_column(String(50), default="AES-256-GCM")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    disabled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    versions: Mapped[list["KeyVersion"]] = relationship(
        back_populates="key",
        cascade="all, delete-orphan",
    )
    access_entries: Mapped[list["KeyAccess"]] = relationship(
        back_populates="key",
        cascade="all, delete-orphan",
    )


class KeyVersion(Base):
    __tablename__ = "key_versions"
    __table_args__ = (
        UniqueConstraint("key_id", "version_number", name="uq_key_version_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key_id: Mapped[int] = mapped_column(ForeignKey("kms_keys.id"), index=True)
    version_number: Mapped[int] = mapped_column()
    encrypted_key_material: Mapped[bytes] = mapped_column(LargeBinary)
    key_material_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    key: Mapped[KmsKey] = relationship(back_populates="versions")


class KeyAccess(Base):
    __tablename__ = "key_access"
    __table_args__ = (
        UniqueConstraint("key_id", "user_id", name="uq_key_access_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key_id: Mapped[int] = mapped_column(ForeignKey("kms_keys.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    can_encrypt: Mapped[bool] = mapped_column(Boolean, default=True)
    can_decrypt: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    key: Mapped[KmsKey] = relationship(back_populates="access_entries")
