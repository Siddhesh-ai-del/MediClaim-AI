import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role
from app.audit.writer import verify_chain
from app.db import get_session
from app.models.entities import AuditEvent

router = APIRouter(prefix="/claims", tags=["audit"])
admin_router = APIRouter(prefix="/admin", tags=["admin-audit"])


@router.get("/{claim_id}/audit")
async def list_audit(
    claim_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(AuditEvent)
        .where(AuditEvent.claim_id == claim_id)
        .order_by(AuditEvent.chain_seq.asc())
    )
    result = await session.execute(q)
    events = list(result.scalars().all())
    items = [
        {
            "seq": e.chain_seq,
            "action": e.action,
            "actor": {"id": str(e.actor_user_id) if e.actor_user_id else None},
            "created_at": e.created_at,
            "payload": e.payload,
        }
        for e in events
    ]
    return {"items": items, "total": len(items)}


@router.get("/{claim_id}/export")
async def export_audit(
    claim_id: uuid.UUID,
    format: str = Query("json"),
    user=Depends(require_role("manager")),
    session: AsyncSession = Depends(get_session),
):
    import csv
    import io

    q = (
        select(AuditEvent)
        .where(AuditEvent.claim_id == claim_id)
        .order_by(AuditEvent.chain_seq.asc())
    )
    result = await session.execute(q)
    events = list(result.scalars().all())
    if format == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["seq", "action", "actor_id", "created_at", "payload"])
        for e in events:
            # sanitize cells (H-10)
            def san(v):
                s = str(v)
                if s and s[0] in ("=", "+", "-", "@"):
                    return "\t" + s
                return s

            w.writerow(
                [
                    e.chain_seq,
                    san(e.action),
                    san(str(e.actor_user_id)),
                    e.created_at,
                    san(str(e.payload)),
                ]
            )
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=audit_{claim_id}.csv"
            },
        )
    import json as _j

    data = _j.dumps(
        [
            {
                "seq": e.chain_seq,
                "action": e.action,
                "created_at": str(e.created_at),
                "payload": e.payload,
            }
            for e in events
        ]
    )
    return StreamingResponse(
        iter([data]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=audit_{claim_id}.json"},
    )

@admin_router.get("/audit/verify")
async def verify_tenant_audit(user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await verify_chain(session, user.tenant_id)
    return result
