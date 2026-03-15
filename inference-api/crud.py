from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import InferenceJob


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def create_job_record(
    db: AsyncSession,
    job_id: str,
    request_json: dict,
    webhook_url: Optional[str],
) -> InferenceJob:
    job = InferenceJob(
        job_id=job_id,
        status="queued",
        request_json=request_json,
        result_json=None,
        error_text=None,
        webhook_url=webhook_url,
        webhook_sent=False,
        webhook_status_code=None,
        webhook_error_text=None,
        created_at=utc_now(),
        started_at=None,
        completed_at=None,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job_record(db: AsyncSession, job_id: str) -> Optional[InferenceJob]:
    result = await db.execute(
        select(InferenceJob).where(InferenceJob.job_id == job_id)
    )
    return result.scalar_one_or_none()


async def update_job_running(db: AsyncSession, job_id: str) -> None:
    await db.execute(
        update(InferenceJob)
        .where(InferenceJob.job_id == job_id)
        .values(status="running", started_at=utc_now())
    )
    await db.commit()


async def update_job_succeeded(db: AsyncSession, job_id: str, result_json: dict) -> None:
    await db.execute(
        update(InferenceJob)
        .where(InferenceJob.job_id == job_id)
        .values(
            status="succeeded",
            result_json=result_json,
            error_text=None,
            completed_at=utc_now(),
        )
    )
    await db.commit()


async def update_job_failed(db: AsyncSession, job_id: str, error_text: str) -> None:
    await db.execute(
        update(InferenceJob)
        .where(InferenceJob.job_id == job_id)
        .values(
            status="failed",
            error_text=error_text,
            completed_at=utc_now(),
        )
    )
    await db.commit()


async def update_webhook_delivery(
    db: AsyncSession,
    job_id: str,
    sent: bool,
    status_code: Optional[int] = None,
    error_text: Optional[str] = None,
) -> None:
    await db.execute(
        update(InferenceJob)
        .where(InferenceJob.job_id == job_id)
        .values(
            webhook_sent=sent,
            webhook_status_code=status_code,
            webhook_error_text=error_text,
        )
    )
    await db.commit()
