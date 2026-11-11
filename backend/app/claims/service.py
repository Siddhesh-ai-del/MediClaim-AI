import hashlib
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.claims import repo
from app.common.errors import (
    DuplicateClaimNumber,
    PayloadTooLarge,
    UnsupportedMediaType,
    ValidationFailed,
)
from app.ingestion.jobs import enqueue_job
from app.ingestion.storage import read_and_validate, store_bytes, validate_upload
from app.models.entities import JobType


async def create_claim_with_files(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    claim_number: str,
    files: list[UploadFile],
    provider_id: uuid.UUID | None = None,
) -> tuple:
    # uniqueness
    from sqlalchemy import select

    from app.models.entities import Claim

    existing = await session.execute(
        select(Claim).where(
            Claim.tenant_id == tenant_id, Claim.claim_number == claim_number
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise DuplicateClaimNumber("claim number already exists")
    if not files:
        raise ValidationFailed("at least one file required")
    if len(files) > 10:
        raise ValidationFailed("max 10 files per claim")
    claim = await repo.create_claim(
        session, tenant_id, user_id, claim_number, provider_id
    )
    file_rows = []
    for f in files:
        validate_upload(f)
        data = await read_and_validate(f)
        path, sha = store_bytes(
            str(tenant_id), str(claim.id), data, f.filename or "file"
        )
        cf = await repo.add_file(
            session,
            claim.id,
            f.filename or "file",
            f.content_type or "application/octet-stream",
            len(data),
            path,
            sha,
        )
        file_rows.append(cf)
    # enqueue job
    import uuid as _u

    idem = f"claim:{claim.id}:process"
    await enqueue_job(session, claim.id, JobType.ocr, idem)
    await session.commit()
    return claim, file_rows
