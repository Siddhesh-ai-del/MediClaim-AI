import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Claim, ClaimFile, ClaimStatus, UserAccount


SORT_ALLOWLIST = {
    "created_at",
    "processed_at",
    "risk_score",
    "total_claimed_amount",
    "claim_number",
    "status",
}


async def create_claim(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    claim_number: str,
    provider_id: uuid.UUID | None = None,
) -> Claim:
    claim = Claim(
        tenant_id=tenant_id,
        claim_number=claim_number,
        submitted_by=user_id,
        provider_id=provider_id,
        status=ClaimStatus.queued,
    )
    session.add(claim)
    await session.flush()
    return claim


async def get_claim(
    session: AsyncSession, claim_id: uuid.UUID, tenant_id: uuid.UUID
) -> Claim | None:
    result = await session.execute(
        select(Claim).where(Claim.id == claim_id, Claim.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def list_claims(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user: UserAccount,
    status: str | None,
    provider_id: uuid.UUID | None,
    date_from,
    date_to,
    sort: str,
    search: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Claim], int]:
    q = select(Claim).where(Claim.tenant_id == tenant_id)
    # ownership
    if user.role.value == "officer":
        q = q.where((Claim.submitted_by == user.id) | (Claim.assigned_to == user.id))
    if status:
        q = q.where(Claim.status == status)
    if provider_id:
        q = q.where(Claim.provider_id == provider_id)
    if date_from:
        q = q.where(Claim.created_at >= date_from)
    if date_to:
        q = q.where(Claim.created_at <= date_to)
    if search:
        q = q.where(Claim.claim_number.ilike(f"%{search}%"))
    # sort
    sort_field, _, direction = sort.partition(":")
    if sort_field not in SORT_ALLOWLIST:
        sort_field = "created_at"
    direction = direction or "desc"
    col = getattr(Claim, sort_field)
    q = q.order_by(col.desc() if direction == "desc" else col.asc())
    # count
    count_q = select(func.count()).select_from(q.subquery())
    total = (await session.execute(count_q)).scalar_one()
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(q)
    return list(result.scalars().all()), total


async def add_file(
    session: AsyncSession,
    claim_id: uuid.UUID,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    storage_path: str,
    sha256: str,
) -> ClaimFile:
    cf = ClaimFile(
        claim_id=claim_id,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        storage_path=storage_path,
        sha256=sha256,
    )
    session.add(cf)
    await session.flush()
    return cf


async def update_claim_status(
    session: AsyncSession,
    claim: Claim,
    status: ClaimStatus,
    error_reason: str | None = None,
) -> None:
    claim.status = status
    if error_reason is not None:
        claim.error_reason = error_reason
    if status in (ClaimStatus.scored, ClaimStatus.adjudicated, ClaimStatus.extracted):
        claim.processed_at = datetime.now(timezone.utc)
    await session.flush()
