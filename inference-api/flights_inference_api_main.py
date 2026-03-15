"""Asynchronous Flight Arrival Delay Inference API.

This API adapts the asynchronous job architecture from the example API to the
Anchor Project's flight arrival delay quantile models.

Expected model artifacts in the same working directory:
- flight_arrdelay_model_10.onnx
- flight_arrdelay_model_50.onnx
- flight_arrdelay_model_90.onnx

Run:
    uvicorn flights_inference_api_main:app --reload
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

import httpx
import numpy as np
import onnxruntime as rt
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from crud import (
    create_job_record,
    get_job_record,
    update_job_failed,
    update_job_running,
    update_job_succeeded,
    update_webhook_delivery,
)
from database import AsyncSessionLocal, get_db
from schemas import FlightDelayPredictionOutput, FlightInferenceFeatures

api_description = """
This API lets clients submit flight arrival delay inference jobs,
track job status, retrieve completed results, and optionally receive
webhook notifications when processing finishes.

The models predict three quantiles of `ArrDelayMinutes` using the
`Marketing_Airline_Network` feature:
- 10th percentile arrival delay
- 50th percentile arrival delay (median)
- 90th percentile arrival delay

The endpoints are grouped into the following categories:

## Analytics
Health and service information.

## Inference Jobs
Submit inference jobs, check their status, inspect the original request,
and retrieve completed results.
"""

MODEL_10_PATH = "flight_arrdelay_model_10.onnx"
MODEL_50_PATH = "flight_arrdelay_model_50.onnx"
MODEL_90_PATH = "flight_arrdelay_model_90.onnx"

sess_10: rt.InferenceSession | None = None
sess_50: rt.InferenceSession | None = None
sess_90: rt.InferenceSession | None = None

input_name_10: str | None = None
output_name_10: str | None = None
input_name_50: str | None = None
output_name_50: str | None = None
input_name_90: str | None = None
output_name_90: str | None = None


class InferenceJobRequest(BaseModel):
    features: FlightInferenceFeatures
    webhook_url: Optional[HttpUrl] = None


class InferenceJobAccepted(BaseModel):
    job_id: str
    status: Literal["queued"]


class InferenceJobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_sent: bool
    webhook_status_code: Optional[int] = None
    error_text: Optional[str] = None


class InferenceJobResult(BaseModel):
    job_id: str
    status: Literal["succeeded"]
    result: FlightDelayPredictionOutput
    completed_at: str


class InferenceJobRequestView(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    request: FlightInferenceFeatures
    webhook_url: Optional[str] = None
    created_at: str


app = FastAPI(
    description=api_description,
    title="Asynchronous Flight Arrival Delay Inference API",
    version="0.1.0",
)


def dt_to_iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value is not None else None


def load_model(model_path: str) -> rt.InferenceSession:
    session_options = rt.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    return rt.InferenceSession(
        model_path,
        session_options,
        providers=["CPUExecutionProvider"],
    )


@app.on_event("startup")
def load_models() -> None:
    global sess_10, sess_50, sess_90
    global input_name_10, output_name_10
    global input_name_50, output_name_50
    global input_name_90, output_name_90

    sess_10 = load_model(MODEL_10_PATH)
    sess_50 = load_model(MODEL_50_PATH)
    sess_90 = load_model(MODEL_90_PATH)

    input_name_10 = sess_10.get_inputs()[0].name
    output_name_10 = sess_10.get_outputs()[0].name
    input_name_50 = sess_50.get_inputs()[0].name
    output_name_50 = sess_50.get_outputs()[0].name
    input_name_90 = sess_90.get_inputs()[0].name
    output_name_90 = sess_90.get_outputs()[0].name


@app.get(
    "/",
    summary="Check API health",
    description="Use this endpoint to check whether the inference API is running.",
    response_description="A JSON record with a simple health message.",
    operation_id="v0_health_check",
    tags=["analytics"],
)
async def root() -> dict[str, str]:
    return {"message": "Flight arrival delay inference API is running"}


@app.get(
    "/model-info",
    summary="Get model metadata",
    description="Returns a concise description of the currently loaded flight delay models.",
    operation_id="v0_model_info",
    tags=["analytics"],
)
async def model_info() -> dict[str, object]:
    return {
        "target": "ArrDelayMinutes",
        "feature": "Marketing_Airline_Network",
        "quantiles": [0.1, 0.5, 0.9],
        "model_files": {
            "10th_percentile": MODEL_10_PATH,
            "50th_percentile": MODEL_50_PATH,
            "90th_percentile": MODEL_90_PATH,
        },
    }


def run_prediction(features: FlightInferenceFeatures) -> FlightDelayPredictionOutput:
    if not all([sess_10, sess_50, sess_90, input_name_10, input_name_50, input_name_90, output_name_10, output_name_50, output_name_90]):
        raise RuntimeError("Model sessions are not initialized")

    airline_value = features.marketing_airline_network.strip()
    input_data = np.array([[airline_value]], dtype=str)

    pred_10 = sess_10.run([output_name_10], {input_name_10: input_data})[0]
    pred_50 = sess_50.run([output_name_50], {input_name_50: input_data})[0]
    pred_90 = sess_90.run([output_name_90], {input_name_90: input_data})[0]

    return FlightDelayPredictionOutput(
        arrival_delay_10th_percentile_minutes=round(float(np.asarray(pred_10).reshape(-1)[0]), 2),
        arrival_delay_50th_percentile_minutes=round(float(np.asarray(pred_50).reshape(-1)[0]), 2),
        arrival_delay_90th_percentile_minutes=round(float(np.asarray(pred_90).reshape(-1)[0]), 2),
    )


async def send_webhook(job_id: str, webhook_url: str, result: FlightDelayPredictionOutput) -> None:
    payload = {
        "job_id": job_id,
        "status": "succeeded",
        "result": result.model_dump(),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(webhook_url, json=payload)

        async with AsyncSessionLocal() as db:
            await update_webhook_delivery(
                db,
                job_id,
                response.is_success,
                response.status_code,
                None if response.is_success else response.text[:1000],
            )
    except Exception as exc:
        async with AsyncSessionLocal() as db:
            await update_webhook_delivery(
                db,
                job_id,
                False,
                None,
                str(exc),
            )


async def process_job(job_id: str, features: FlightInferenceFeatures, webhook_url: Optional[str]) -> None:
    async with AsyncSessionLocal() as db:
        await update_job_running(db, job_id)

    try:
        result = await run_in_threadpool(run_prediction, features)

        async with AsyncSessionLocal() as db:
            await update_job_succeeded(db, job_id, result.model_dump())

        if webhook_url is not None:
            await send_webhook(job_id, webhook_url, result)
    except Exception as exc:
        async with AsyncSessionLocal() as db:
            await update_job_failed(db, job_id, str(exc))


@app.post(
    "/inference-jobs",
    response_model=InferenceJobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a flight delay inference job",
    description="Submit a job that predicts 10th, 50th, and 90th percentile arrival delays for a marketing airline.",
    response_description="A JSON record containing the job ID and initial queued status.",
    operation_id="v0_submit_inference_job",
    tags=["inference jobs"],
)
async def submit_inference_job(
    request: InferenceJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> InferenceJobAccepted:
    job_id = str(uuid4())

    await create_job_record(
        db,
        job_id,
        request.features.model_dump(by_alias=True),
        str(request.webhook_url) if request.webhook_url is not None else None,
    )

    background_tasks.add_task(
        process_job,
        job_id,
        request.features,
        str(request.webhook_url) if request.webhook_url is not None else None,
    )

    return InferenceJobAccepted(job_id=job_id, status="queued")


@app.get(
    "/inference-jobs/{job_id}",
    response_model=InferenceJobStatus,
    summary="Get inference job status",
    description="Return the current status of a previously submitted inference job.",
    operation_id="v0_get_inference_job_status",
    tags=["inference jobs"],
)
async def get_inference_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> InferenceJobStatus:
    job = await get_job_record(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    return InferenceJobStatus(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at.isoformat(),
        started_at=dt_to_iso(job.started_at),
        completed_at=dt_to_iso(job.completed_at),
        webhook_url=job.webhook_url,
        webhook_sent=job.webhook_sent,
        webhook_status_code=job.webhook_status_code,
        error_text=job.error_text,
    )


@app.get(
    "/inference-jobs/{job_id}/request",
    response_model=InferenceJobRequestView,
    summary="Get the original request for a submitted job",
    description="Return the stored request payload for a previously submitted inference job.",
    operation_id="v0_get_inference_job_request",
    tags=["inference jobs"],
)
async def get_inference_job_request(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> InferenceJobRequestView:
    job = await get_job_record(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    return InferenceJobRequestView(
        job_id=job.job_id,
        status=job.status,
        request=FlightInferenceFeatures.model_validate(job.request_json),
        webhook_url=job.webhook_url,
        created_at=job.created_at.isoformat(),
    )


@app.get(
    "/inference-jobs/{job_id}/result",
    response_model=InferenceJobResult,
    summary="Get completed inference job result",
    description="Return prediction output for a completed inference job.",
    operation_id="v0_get_inference_job_result",
    tags=["inference jobs"],
)
async def get_inference_job_result(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> InferenceJobResult:
    job = await get_job_record(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    if job.status in {"queued", "running"}:
        raise HTTPException(status_code=409, detail="Inference job is not complete yet")

    if job.status == "failed":
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Inference job failed",
                "error_text": job.error_text,
            },
        )

    if job.result_json is None:
        raise HTTPException(status_code=500, detail="Completed job has no stored result")

    return InferenceJobResult(
        job_id=job.job_id,
        status="succeeded",
        result=FlightDelayPredictionOutput.model_validate(job.result_json),
        completed_at=job.completed_at.isoformat() if job.completed_at else "",
    )


@app.post(
    "/predict-sync",
    response_model=FlightDelayPredictionOutput,
    summary="Run synchronous flight delay inference",
    description="Run the three quantile models immediately for quick local testing.",
    operation_id="v0_predict_sync",
    tags=["analytics"],
)
async def predict_sync(features: FlightInferenceFeatures) -> FlightDelayPredictionOutput:
    return await run_in_threadpool(run_prediction, features)
