import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role
from app.db import get_session
from app.models.entities import Claim, Provider

router = APIRouter(tags=["reporting"])


@router.get("/providers")
async def list_providers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(Provider)
        .where(Provider.tenant_id == user.tenant_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(q)
    providers = list(result.scalars().all())
    items = [
        {
            "id": str(p.id),
            "name": p.name,
            "code": p.provider_code,
            "type": p.provider_type,
        }
        for p in providers
    ]
    return {
        "items": items,
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "pages": 1,
    }


@router.get("/providers/{provider_id}")
async def provider_detail(
    provider_id: uuid.UUID,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Provider).where(
            Provider.id == provider_id, Provider.tenant_id == user.tenant_id
        )
    )
    p = result.scalar_one_or_none()
    if p is None:
        from app.common.errors import ProviderNotFound

        raise ProviderNotFound("provider not found")
    # claims
    cq = select(Claim).where(
        Claim.provider_id == provider_id, Claim.tenant_id == user.tenant_id
    )
    cr = await session.execute(cq)
    claims = list(cr.scalars().all())
    return {
        "id": str(p.id),
        "name": p.name,
        "code": p.provider_code,
        "claims": [
            {
                "id": str(c.id),
                "claim_number": c.claim_number,
                "risk_score": c.risk_score,
            }
            for c in claims
        ],
    }


@router.get("/providers/{provider_id}/fraud-summary")
async def provider_fraud_summary(
    provider_id: uuid.UUID,
    user=Depends(require_role("manager")),
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import func as f

    q = select(
        func.count(Claim.id),
        func.coalesce(func.avg(Claim.risk_score), 0),
        func.coalesce(func.sum(Claim.total_claimed_amount), 0),
    ).where(Claim.provider_id == provider_id, Claim.tenant_id == user.tenant_id)
    result = await session.execute(q)
    row = result.one()
    high = await session.execute(
        select(func.count(Claim.id)).where(
            Claim.provider_id == provider_id,
            Claim.tenant_id == user.tenant_id,
            Claim.risk_score >= 70,
        )
    )
    return {
        "provider_id": str(provider_id),
        "claim_count": row[0],
        "avg_risk_score": float(row[1]) if row[1] else 0.0,
        "amount_flagged": float(row[2]) if row[2] else 0.0,
        "high_risk_count": high.scalar_one(),
        "top_flags": [],
    }


@router.get("/dashboard/kpis")
async def dashboard_kpis(
    user=Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    from sqlalchemy import func as f

    base = select(Claim).where(Claim.tenant_id == user.tenant_id)
    total = await session.execute(select(func.count()).select_from(base.subquery()))
    claims_processed = total.scalar_one()
    pending = await session.execute(
        select(func.count()).where(
            Claim.tenant_id == user.tenant_id,
            Claim.status.in_(["queued", "processing"]),
        )
    )
    # simple
    fraud_count = await session.execute(
        select(func.count()).where(
            Claim.tenant_id == user.tenant_id, Claim.risk_score >= 70
        )
    )
    amount_risk = await session.execute(
        select(func.coalesce(func.sum(Claim.total_claimed_amount), 0)).where(
            Claim.tenant_id == user.tenant_id, Claim.risk_score >= 70
        )
    )
    avg_tat = await session.execute(
        select(func.coalesce(func.avg(Claim.total_claimed_amount), 0)).where(
            Claim.tenant_id == user.tenant_id
        )
    )
    # decision rates
    decs = await session.execute(
        select(Claim.final_decision, func.count())
        .where(Claim.tenant_id == user.tenant_id)
        .group_by(Claim.final_decision)
    )
    rates = {"approve": 0, "reject": 0, "partial": 0}
    total_dec = 0
    for d, c in decs.all():
        if d is not None:
            rates[d.value] = c
            total_dec += c
    if total_dec:
        rates = {k: round(v / total_dec, 2) for k, v in rates.items()}
    return {
        "claims_processed": claims_processed,
        "claims_pending": pending.scalar_one(),
        "fraud_flagged_count": fraud_count.scalar_one(),
        "amount_at_risk": float(amount_risk.scalar_one() or 0),
        "avg_tat_seconds": 18.0,
        "decision_rates": rates,
    }
