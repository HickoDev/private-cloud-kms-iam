from datetime import datetime

from pydantic import BaseModel, Field


class KeyCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    algorithm: str = "AES-256-GCM"


class KeyResponse(BaseModel):
    id: int
    name: str
    description: str | None
    algorithm: str
    status: str
    active_version: int | None
    created_at: datetime
    disabled_at: datetime | None


class KeyVersionResponse(BaseModel):
    id: int
    key_id: int
    version_number: int
    is_active: bool
    created_at: datetime
    rotated_at: datetime | None


class KeyAccessGrantRequest(BaseModel):
    user_id: int
    can_encrypt: bool = True
    can_decrypt: bool = True


class KeyAccessResponse(BaseModel):
    id: int
    key_id: int
    user_id: int
    username: str
    email: str
    can_encrypt: bool
    can_decrypt: bool


class EncryptRequest(BaseModel):
    plaintext: str = Field(min_length=1)


class EncryptResponse(BaseModel):
    key_id: int
    key_version: int
    algorithm: str
    ciphertext: str
    nonce: str


class DecryptRequest(BaseModel):
    key_version: int
    ciphertext: str = Field(min_length=1)
    nonce: str = Field(min_length=1)


class DecryptResponse(BaseModel):
    plaintext: str
