import hashlib
import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.common.errors import PayloadTooLarge, UnsupportedMediaType, ValidationFailed


ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
MAX_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024


def _storage_root() -> Path:
    root = Path(settings.STORAGE_PATH)
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_upload(upload: UploadFile) -> None:
    if upload.content_type not in ALLOWED_TYPES:
        raise UnsupportedMediaType(f"unsupported type {upload.content_type}")
    # size checked after read


async def read_and_validate(upload: UploadFile) -> bytes:
    data = await upload.read()
    if len(data) == 0:
        raise ValidationFailed("empty file")
    if len(data) > MAX_BYTES:
        raise PayloadTooLarge(f"file exceeds {settings.MAX_UPLOAD_MB}MB")
    # magic bytes
    if data[:4] == b"%PDF":
        pass
    elif data[:8] in (b"\x89PNG\r\n\x1a\n",) or data[:3] == b"\xff\xd8\xff":
        pass
    else:
        raise UnsupportedMediaType("file content does not match allowed types")
    return data


def store_bytes(
    tenant_id: str, claim_id: str, data: bytes, original_filename: str
) -> tuple[str, str]:
    """Returns (storage_path, sha256). Server-generated UUID filename (H-5)."""
    root = _storage_root()
    subdir = root / tenant_id / claim_id
    subdir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    # preserve extension based on magic bytes
    ext = (
        ".pdf"
        if data[:4] == b"%PDF"
        else (".png" if data[:4] == b"\x89PNG" else ".jpg")
    )
    name = file_id + ext
    path = subdir / name
    # safety: ensure within root
    path.resolve().relative_to(root.resolve())
    path.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    return str(path), sha
