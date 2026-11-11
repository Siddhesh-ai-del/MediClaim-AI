import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import ValidationFailed
from app.models.entities import JobStatus, JobType, ProcessingJob


async def enqueue_job(
    session: AsyncSession, claim_id: uuid.UUID, job_type: JobType, idempotency_key: str
) -> ProcessingJob:
    existing = await session.execute(
        select(ProcessingJob).where(ProcessingJob.idempotency_key == idempotency_key)
    )
    job = existing.scalar_one_or_none()
    if job is not None:
        return job
    job = ProcessingJob(
        claim_id=claim_id, job_type=job_type, idempotency_key=idempotency_key
    )
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> ProcessingJob | None:
    result = await session.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    return result.scalar_one_or_none()


async def update_job_status(
    session: AsyncSession,
    job: ProcessingJob,
    status: JobStatus,
    error: str | None = None,
) -> None:
    job.status = status
    if status == JobStatus.running:
        job.started_at = datetime.now(timezone.utc)
        job.attempts += 1
    if status in (JobStatus.succeeded, JobStatus.failed):
        job.finished_at = datetime.now(timezone.utc)
    if error:
        job.last_error = error
    await session.flush()
