import hashlib
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AuditEvent


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


async def append_event(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    claim_id: uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    payload: dict | None = None,
) -> AuditEvent:
    payload = payload or {}
    # advisory lock to serialize chain per tenant
    await session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:t))"), {"t": str(tenant_id)}
    )
    result = await session.execute(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == tenant_id)
        .order_by(AuditEvent.chain_seq.desc())
        .limit(1)
    )
    prev = result.scalar_one_or_none()
    prev_hash = prev.payload_hash if prev else None
    chain_seq = (prev.chain_seq + 1) if prev else 1
    created_at = datetime.now(timezone.utc)
    hash_input = {
        "tenant_id": str(tenant_id),
        "chain_seq": chain_seq,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id) if entity_id else None,
        "actor_user_id": str(actor_user_id) if actor_user_id else None,
        "claim_id": str(claim_id) if claim_id else None,
        "payload": payload,
        "prev_hash": prev_hash,
        "created_at": created_at.isoformat(),
    }
    payload_hash = hashlib.sha256(_canonical(hash_input).encode()).hexdigest()
    ev = AuditEvent(
        tenant_id=tenant_id,
        claim_id=claim_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        chain_seq=chain_seq,
        created_at=created_at,
    )
    session.add(ev)
    await session.flush()
    return ev


async def verify_chain(session: AsyncSession, tenant_id: uuid.UUID) -> dict:
    result = await session.execute(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == tenant_id)
        .order_by(AuditEvent.chain_seq.asc())
    )
    events = list(result.scalars().all())
    prev_hash = None
    expected_seq = 1
    for ev in events:
        if ev.chain_seq != expected_seq:
            return {
                "ok": False,
                "broken_at_seq": ev.chain_seq,
                "reason": "sequence gap",
            }
        hash_input = {
            "tenant_id": str(tenant_id),
            "chain_seq": ev.chain_seq,
            "action": ev.action,
            "entity_type": ev.entity_type,
            "entity_id": str(ev.entity_id) if ev.entity_id else None,
            "actor_user_id": str(ev.actor_user_id) if ev.actor_user_id else None,
            "claim_id": str(ev.claim_id) if ev.claim_id else None,
            "payload": ev.payload,
            "prev_hash": ev.prev_hash,
            "created_at": ev.created_at.isoformat(),
        }
        recomputed = hashlib.sha256(_canonical(hash_input).encode()).hexdigest()
        if recomputed != ev.payload_hash:
            return {
                "ok": False,
                "broken_at_seq": ev.chain_seq,
                "reason": "hash mismatch",
            }
        if ev.prev_hash != prev_hash:
            return {
                "ok": False,
                "broken_at_seq": ev.chain_seq,
                "reason": "prev_hash mismatch",
            }
        prev_hash = ev.payload_hash
        expected_seq += 1
    return {"ok": True, "broken_at_seq": None, "reason": None}
