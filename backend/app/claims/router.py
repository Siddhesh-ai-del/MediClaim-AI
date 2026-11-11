import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role, tenant_id_from_request
from app.claims import repo, service
from app.claims.schemas import (
    ClaimCreateResponse,
    ClaimListResponse,
    ClaimSummary,
    CorrectionsRequest,
    OverrideRequest,
)
from app.common.errors import (
    ClaimNotFound,
    Forbidden,
    InvalidStatusTransition,
    OverrideReasonRequired,
)
from app.db import get_session
from app.models.entities import (
    Claim,
    ClaimStatus,
    UserAccount,
    Extraction,
    ExtractionField,
    FraudFlag,
    Adjudication,
    ClaimFile,
)

router = APIRouter(prefix="/claims", tags=["claims"])


def _risk_band(score):
    if score is None:
        return None
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


@router.post("", status_code=202)
async def create_claim(
    claim_number: str = Form(...),
    provider_code: str | None = Form(None),
    files: list[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    tenant_id = user.tenant_id
    # resolve provider
    provider_id = None
    if provider_code:
        from app.models.entities import Provider

        r = await session.execute(
            select(Provider).where(
                Provider.tenant_id == user.tenant_id,
                Provider.provider_code == provider_code,
            )
        )
        p = r.scalar_one_or_none()
        if p:
            provider_id = p.id
    claim, file_rows = await service.create_claim_with_files(
        session, user.tenant_id, user.id, claim_number, files, provider_id
    )
    from app.audit.writer import append_event

    await append_event(
        session,
        user.tenant_id,
        "claim.created",
        "claim",
        claim.id,
        claim_id=claim.id,
        actor_user_id=user.id,
        payload={"claim_number": claim_number},
    )
    await session.commit()
    from app.claims.processing import process_claim

    background_tasks.add_task(process_claim, claim.id)
    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "status": claim.status.value,
        "files": [
            {"id": str(f.id), "filename": f.original_filename, "status": f.status.value}
            for f in file_rows
        ],
        "created_at": claim.created_at,
    }


@router.get("")
async def list_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    provider_id: uuid.UUID | None = None,
    sort: str = "created_at:desc",
    search: str | None = None,
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    claims, total = await repo.list_claims(
        session,
        user.tenant_id,
        user,
        status,
        provider_id,
        None,
        None,
        sort,
        search,
        page,
        page_size,
    )
    items = []
    for c in claims:
        items.append(
            {
                "id": c.id,
                "claim_number": c.claim_number,
                "provider_name": None,
                "status": c.status.value,
                "risk_score": c.risk_score,
                "risk_band": _risk_band(c.risk_score),
                "recommended_decision": c.recommended_decision.value
                if c.recommended_decision
                else None,
                "total_claimed_amount": float(c.total_claimed_amount)
                if c.total_claimed_amount is not None
                else None,
                "created_at": c.created_at,
                "processed_at": c.processed_at,
            }
        )
    pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/{claim_id}")
async def get_claim(
    claim_id: uuid.UUID,
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    claim = await repo.get_claim(session, claim_id, user.tenant_id)
    if claim is None or (
        user.role.value == "officer"
        and claim.submitted_by != user.id
        and claim.assigned_to != user.id
    ):
        raise ClaimNotFound("claim not found")
    # provider
    provider = None
    if claim.provider_id:
        from app.models.entities import Provider

        r = await session.execute(
            select(Provider).where(Provider.id == claim.provider_id)
        )
        p = r.scalar_one_or_none()
        if p:
            provider = {"id": str(p.id), "name": p.name, "code": p.provider_code}
    # files
    fr = await session.execute(select(ClaimFile).where(ClaimFile.claim_id == claim.id))
    files = [
        {
            "id": str(f.id),
            "filename": f.original_filename,
            "status": f.status.value,
            "ocr_engine": f.ocr_engine,
            "page_count": f.page_count,
        }
        for f in fr.scalars().all()
    ]
    # extraction latest
    extraction_payload = None
    er = await session.execute(
        select(Extraction)
        .where(Extraction.claim_id == claim.id)
        .order_by(Extraction.version.desc())
    )
    ext = er.scalars().first()
    if ext:
        fr2 = await session.execute(
            select(ExtractionField).where(ExtractionField.extraction_id == ext.id)
        )
        fields = [
            {
                "field_path": f.field_path,
                "value": f.value_json,
                "confidence": float(f.confidence) if f.confidence is not None else None,
                "human_corrected": f.human_corrected,
                "source_quote": f.source_quote,
            }
            for f in fr2.scalars().all()
        ]
        extraction_payload = {
            "version": ext.version,
            "model": ext.extractor_model,
            "fields": fields,
        }
    # flags
    fr3 = await session.execute(select(FraudFlag).where(FraudFlag.claim_id == claim.id))
    flags = [
        {
            "type": f.flag_type.value,
            "severity": f.severity.value,
            "evidence": f.evidence,
            "source": f.source.value,
            "rule_id": f.rule_id,
        }
        for f in fr3.scalars().all()
    ]
    # adjudication latest
    ar = await session.execute(
        select(Adjudication)
        .where(Adjudication.claim_id == claim.id)
        .order_by(Adjudication.created_at.desc())
    )
    adj = ar.scalars().first()
    adjudication_payload = None
    if adj:
        adjudication_payload = {
            "decision": adj.decision.value,
            "amount": float(adj.amount) if adj.amount is not None else None,
            "reasons": adj.reasons,
            "created_at": adj.created_at,
        }
    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "status": claim.status.value,
        "provider": provider,
        "patient": {
            "name": claim.patient_name,
            "age": claim.patient_age,
            "gender": claim.patient_gender,
        },
        "policy_number": claim.policy_number,
        "admission_date": claim.admission_date,
        "discharge_date": claim.discharge_date,
        "total_claimed_amount": float(claim.total_claimed_amount)
        if claim.total_claimed_amount is not None
        else None,
        "currency": claim.currency,
        "risk_score": claim.risk_score,
        "risk_confidence_low": claim.risk_confidence_low,
        "risk_confidence_high": claim.risk_confidence_high,
        "recommended_decision": claim.recommended_decision.value
        if claim.recommended_decision
        else None,
        "recommended_amount": float(claim.recommended_amount)
        if claim.recommended_amount is not None
        else None,
        "recommended_reasons": claim.recommended_reasons,
        "override_decision": claim.override_decision.value
        if claim.override_decision
        else None,
        "final_decision": claim.final_decision.value if claim.final_decision else None,
        "extraction": extraction_payload,
        "flags": flags,
        "files": files,
        "adjudication": adjudication_payload,
        "error_reason": claim.error_reason,
        "created_at": claim.created_at,
        "processed_at": claim.processed_at,
        "reviewed_at": claim.reviewed_at,
    }


@router.patch("/{claim_id}/fields")
async def patch_fields(
    claim_id: uuid.UUID,
    body: CorrectionsRequest,
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    claim = await repo.get_claim(session, claim_id, user.tenant_id)
    if claim is None or (
        user.role.value == "officer"
        and claim.submitted_by != user.id
        and claim.assigned_to != user.id
    ):
        raise ClaimNotFound("claim not found")
    # find latest extraction
    er = await session.execute(
        select(Extraction)
        .where(Extraction.claim_id == claim.id)
        .order_by(Extraction.version.desc())
    )
    ext = er.scalars().first()
    if ext is None:
        raise ClaimNotFound("no extraction")
    for corr in body.corrections:
        fr = await session.execute(
            select(ExtractionField).where(
                ExtractionField.extraction_id == ext.id,
                ExtractionField.field_path == corr.field_path,
            )
        )
        f = fr.scalar_one_or_none()
        if f is not None:
            f.corrected_value = f.value_json
            f.value_json = corr.value
            f.human_corrected = True
            f.corrected_by = user.id
            f.corrected_at = datetime.now(timezone.utc)
    await session.commit()
    return {"status": "ok"}


@router.post("/{claim_id}/override")
async def override_claim(
    claim_id: uuid.UUID,
    body: OverrideRequest,
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    claim = await repo.get_claim(session, claim_id, user.tenant_id)
    if claim is None or (
        user.role.value == "officer"
        and claim.submitted_by != user.id
        and claim.assigned_to != user.id
    ):
        raise ClaimNotFound("claim not found")
    if not body.reason or len(body.reason) < 10:
        raise OverrideReasonRequired("reason required")
    from app.models.entities import Adjudication, DecisionType

    dec = DecisionType(body.decision)
    adj = Adjudication(
        claim_id=claim.id,
        decision=dec,
        amount=body.amount,
        reasons=[{"text": body.reason, "evidence": "human override"}],
        engine_version="human",
        is_override=True,
        override_by=user.id,
        override_reason=body.reason,
    )
    session.add(adj)
    claim.override_decision = dec
    claim.override_reason = body.reason
    claim.override_by = user.id
    claim.override_at = datetime.now(timezone.utc)
    claim.final_decision = dec
    claim.reviewed_at = datetime.now(timezone.utc)
    await session.commit()
    return {"status": "ok"}


@router.post("/{claim_id}/retry", status_code=202)
async def retry_claim(
    claim_id: uuid.UUID,
    user: UserAccount = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    claim = await repo.get_claim(session, claim_id, user.tenant_id)
    if claim is None:
        raise ClaimNotFound("claim not found")
    return {"status": "queued"}
