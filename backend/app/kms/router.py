from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("")
def list_keys() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Key listing will be implemented in the KMS phase.",
    )


@router.post("")
def create_key() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Key creation will be implemented in the KMS phase.",
    )


@router.post("/{key_id}/encrypt")
def encrypt(key_id: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Encryption for key {key_id} will be implemented in the KMS phase.",
    )


@router.post("/{key_id}/decrypt")
def decrypt(key_id: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Decryption for key {key_id} will be implemented in the KMS phase.",
    )

