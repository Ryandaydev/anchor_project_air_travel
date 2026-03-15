from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InferenceJob


VALID_JOB_STATUSES = {"queued", "running", "succeeded", "failed"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def create_job_record(
    db: AsyncSession,
    job_id: str,
    request_payload: dict,
    webhook_url: str | None,
) -> InferenceJob:
    job = InferenceJob(
        job_id=job_id,
        status="queued",
        request_json=request_payload,
        webhook_url=webhook_url,
        created_at=utc_now(),
        webhook_sent=False,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def fetch_job(db: AsyncSession, job_id: str) -> InferenceJob | None:
    result = await db.execute(
        select(InferenceJob).where(InferenceJob.job_id == job_id)
    )
    return result.scalar_one_or_none()


async def update_job_running(db: AsyncSession, job_id: str) -> InferenceJob | None:
    job = await fetch_job(db, job_id)
    if job is None:
        return None

    job.status = "running"
    job.started_at = utc_now()
    await db.commit()
    await db.refresh(job)
    return job


async def update_job_succeeded(
    db: AsyncSession,
    job_id: str,
    result_payload: dict,
) -> InferenceJob | None:
    job = await fetch_job(db, job_id)
    if job is None:
        return None

    job.status = "succeeded"
    job.result_json = result_payload
    job.completed_at = utc_now()
    job.error_text = None
    await db.commit()
    await db.refresh(job)
    return job


async def update_job_failed(
    db: AsyncSession,
    job_id: str,
    error_text: str,
) -> InferenceJob | None:
    job = await fetch_job(db, job_id)
    if job is None:
        return None

    job.status = "failed"
    job.error_text = error_text
    job.completed_at = utc_now()
    await db.commit()
    await db.refresh(job)
    return job


async def update_webhook_delivery(
    db: AsyncSession,
    job_id: str,
    sent: bool,
    status_code: int | None = None,
    error_text: str | None = None,
) -> InferenceJob | None:
    job = await fetch_job(db, job_id)
    if job is None:
        return None

    job.webhook_sent = sent
    job.webhook_status_code = status_code
    job.webhook_error_text = error_text
    await db.commit()
    await db.refresh(job)
    return job


async def delete_job_record(db: AsyncSession, job_id: str) -> bool:
    result = await db.execute(
        delete(InferenceJob).where(InferenceJob.job_id == job_id)
    )
    await db.commit()
    return result.rowcount > 0


async def reset_job_store(db: AsyncSession) -> None:
    await db.execute(delete(InferenceJob))
    await db.commit()
