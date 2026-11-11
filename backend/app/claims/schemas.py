from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClaimCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    claim_number: str
    status: str
    files: list[dict]
    created_at: Any


class ClaimSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    claim_number: str
    status: str
    risk_score: int | None = None
    risk_band: str | None = None
    recommended_decision: str | None = None
    total_claimed_amount: float | None = None
    created_at: Any
    processed_at: Any = None


class ClaimListResponse(BaseModel):
    items: list[ClaimSummary]
    total: int
    page: int
    page_size: int
    pages: int


class FieldCorrection(BaseModel):
    field_path: str
    value: Any


class CorrectionsRequest(BaseModel):
    corrections: list[FieldCorrection]


class OverrideRequest(BaseModel):
    decision: str
    amount: float | None = None
    reason: str = Field(min_length=10)
