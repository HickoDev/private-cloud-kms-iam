import base64
import binascii
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

AES_GCM_NONCE_SIZE = 12
AES_256_KEY_SIZE = 32


def generate_data_key() -> bytes:
    return os.urandom(AES_256_KEY_SIZE)


def get_master_key() -> bytes:
    try:
        master_key = base64.b64decode(get_settings().master_key, validate=True)
    except binascii.Error as exc:
        raise ValueError("MASTER_KEY must be valid base64.") from exc

    if len(master_key) != AES_256_KEY_SIZE:
        raise ValueError("MASTER_KEY must decode to exactly 32 bytes.")

    return master_key


def protect_key_material(key_material: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    ciphertext = AESGCM(get_master_key()).encrypt(nonce, key_material, None)
    return ciphertext, nonce


def unprotect_key_material(encrypted_key_material: bytes, nonce: bytes) -> bytes:
    try:
        return AESGCM(get_master_key()).decrypt(nonce, encrypted_key_material, None)
    except InvalidTag as exc:
        raise ValueError("Stored key material cannot be decrypted.") from exc


def encrypt_text(key_material: bytes, plaintext: str) -> tuple[str, str]:
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    ciphertext = AESGCM(key_material).encrypt(nonce, plaintext.encode("utf-8"), None)
    return (
        base64.b64encode(ciphertext).decode("ascii"),
        base64.b64encode(nonce).decode("ascii"),
    )


def decrypt_text(key_material: bytes, ciphertext: str, nonce: str) -> str:
    try:
        ciphertext_bytes = base64.b64decode(ciphertext, validate=True)
        nonce_bytes = base64.b64decode(nonce, validate=True)
        plaintext = AESGCM(key_material).decrypt(nonce_bytes, ciphertext_bytes, None)
    except (binascii.Error, InvalidTag, ValueError) as exc:
        raise ValueError("Ciphertext or nonce is invalid.") from exc

    return plaintext.decode("utf-8")
