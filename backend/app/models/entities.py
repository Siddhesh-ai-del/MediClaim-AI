import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    officer = "officer"
    manager = "manager"
    admin = "admin"


class ClaimStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    extracted = "extracted"
    scored = "scored"
    adjudicated = "adjudicated"
    reviewed = "reviewed"
    failed = "failed"


class FileStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class DecisionType(str, enum.Enum):
    approve = "approve"
    reject = "reject"
    partial = "partial"


class FlagType(str, enum.Enum):
    upcoding = "upcoding"
    phantom_billing = "phantom_billing"
    unbundling = "unbundling"
    duplicate_claim = "duplicate_claim"
    inflated_charge = "inflated_charge"
    diagnosis_procedure_mismatch = "diagnosis_procedure_mismatch"
    provider_outlier = "provider_outlier"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class FraudSource(str, enum.Enum):
    rule = "rule"
    stat = "stat"
    ml = "ml"


class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    retrying = "retrying"


class JobType(str, enum.Enum):
    ocr = "ocr"
    extraction = "extraction"
    scoring = "scoring"
    adjudication = "adjudication"


def _uuid():
    return uuid.uuid4()


class Tenant(Base):
    __tablename__ = "tenant"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserAccount(Base):
    __tablename__ = "user_account"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.officer
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
    )


class Provider(Base):
    __tablename__ = "provider"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    provider_code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    provider_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("tenant_id", "provider_code", name="uq_provider_tenant_code"),
    )


class Claim(Base):
    __tablename__ = "claim"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    claim_number: Mapped[str] = mapped_column(Text, nullable=False)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("provider.id"), nullable=True
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=False
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=True
    )
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus, name="claim_status"),
        nullable=False,
        default=ClaimStatus.queued,
    )
    total_claimed_amount: Mapped[float | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(Text, nullable=False, default="INR")
    patient_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    patient_gender: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    admission_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    discharge_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_confidence_low: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_confidence_high: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended_decision: Mapped[DecisionType | None] = mapped_column(
        Enum(DecisionType, name="decision_type"), nullable=True
    )
    recommended_amount: Mapped[float | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    recommended_reasons: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )
    override_decision: Mapped[DecisionType | None] = mapped_column(
        Enum(DecisionType, name="decision_type"), nullable=True
    )
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=True
    )
    override_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    final_decision: Mapped[DecisionType | None] = mapped_column(
        Enum(DecisionType, name="decision_type"), nullable=True
    )
    extraction_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    __table_args__ = (
        UniqueConstraint("tenant_id", "claim_number", name="uq_claim_tenant_number"),
    )


class ClaimFile(Base):
    __tablename__ = "claim_file"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id", ondelete="CASCADE"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status"), nullable=False, default=FileStatus.queued
    )
    error_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_engine: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sha256: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class OcrResult(Base):
    __tablename__ = "ocr_result"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claim_file.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    engine: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("claim_file_id", "page_number", name="uq_ocr_file_page"),
    )


class Extraction(Base):
    __tablename__ = "extraction"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    extractor_model: Mapped[str] = mapped_column(Text, nullable=False)
    raw_llm_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("claim_id", "version", name="uq_extraction_claim_version"),
    )


class ExtractionField(Base):
    __tablename__ = "extraction_field"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    extraction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extraction.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_path: Mapped[str] = mapped_column(Text, nullable=False)
    value_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    source_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_corrected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    corrected_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=True
    )
    corrected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    corrected_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("extraction_id", "field_path", name="uq_ef_extraction_path"),
    )


class FraudFlag(Base):
    __tablename__ = "fraud_flag"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id", ondelete="CASCADE"), nullable=False
    )
    flag_type: Mapped[FlagType] = mapped_column(
        Enum(FlagType, name="flag_type"), nullable=False
    )
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="severity"), nullable=False
    )
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[FraudSource] = mapped_column(
        Enum(FraudSource, name="fraud_source"), nullable=False
    )
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_impact: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Adjudication(Base):
    __tablename__ = "adjudication"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[DecisionType] = mapped_column(
        Enum(DecisionType, name="decision_type"), nullable=False
    )
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    reasons: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    engine_version: Mapped[str] = mapped_column(Text, nullable=False)
    is_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    override_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=True
    )
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ProcessingJob(Base):
    __tablename__ = "processing_job"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type"), nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), nullable=False, default=JobStatus.queued
    )
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TariffReference(Base):
    __tablename__ = "tariff_reference"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_rate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, default="INR")
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(Date, nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_event"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    claim_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id"), nullable=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    payload_hash: Mapped[str] = mapped_column(Text, nullable=False)
    prev_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    chain_seq: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint("tenant_id", "chain_seq", name="uq_audit_tenant_seq"),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("refresh_token.id"), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
