"""Asynchronous Flight Arrival Delay Inference API backed by PostgreSQL.

Expected model artifacts in the same working directory:
- flight_arrdelay_model_10.onnx
- flight_arrdelay_model_50.onnx
- flight_arrdelay_model_90.onnx

Database setup:
- Set DATABASE_URL to your PostgreSQL async SQLAlchemy URL.
- Run the DDL in flight_inference_jobs.sql before starting the API.

Run:
    uvicorn flights_inference_api_main:app --reload
"""

from datetime import datetime
from typing import Literal
from uuid import uuid4

import httpx
import numpy as np
import onnxruntime as rt
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from database import AsyncSessionLocal, get_db
from schemas import FlightDelayPredictionOutput, FlightInferenceFeatures

api_description = """
This API lets clients submit flight arrival delay inference jobs,
track their status, retrieve results when processing is complete,
and optionally receive webhook notifications.

The models predict three quantiles of `ArrDelayMinutes` using the
`Marketing_Airline_Network` feature:

- 10th percentile arrival delay
- 50th percentile arrival delay (median)
- 90th percentile arrival delay

The endpoints are grouped into the following categories:

## Analytics
Get information about the health of the API.

## Inference Jobs
Submit inference jobs, check job status, inspect the original request,
and retrieve completed results.
"""

MODEL_10_PATH = "flight_arrdelay_model_10.onnx"
MODEL_50_PATH = "flight_arrdelay_model_50.onnx"
MODEL_90_PATH = "flight_arrdelay_model_90.onnx"

sess_10 = None
sess_50 = None
sess_90 = None

input_name_10 = None
label_name_10 = None
input_name_50 = None
label_name_50 = None
input_name_90 = None
label_name_90 = None


class InferenceJobRequest(BaseModel):
    features: FlightInferenceFeatures
    webhook_url: HttpUrl | None = None


class InferenceJobAccepted(BaseModel):
    job_id: str
    status: Literal["queued"]


class InferenceJobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    webhook_url: str | None = None
    webhook_sent: bool
    webhook_status_code: int | None = None
    error_text: str | None = None
    webhook_error_text: str | None = None


class InferenceJobResult(BaseModel):
    job_id: str
    status: Literal["succeeded"]
    result: FlightDelayPredictionOutput
    completed_at: str


class InferenceJobRequestView(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    request: FlightInferenceFeatures
    webhook_url: str | None = None
    created_at: str


class DeleteJobResponse(BaseModel):
    job_id: str
    deleted: bool


app = FastAPI(
    description=api_description,
    title="Asynchronous Flight Arrival Delay Inference API",
    version="0.3.0",
)


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@app.on_event("startup")
def load_models() -> None:
    global sess_10, sess_50, sess_90
    global input_name_10, label_name_10
    global input_name_50, label_name_50
    global input_name_90, label_name_90

    sess_options = rt.SessionOptions()
    sess_options.intra_op_num_threads = 1
    sess_options.inter_op_num_threads = 1

    sess_10 = rt.InferenceSession(
        MODEL_10_PATH,
        sess_options,
        providers=["CPUExecutionProvider"],
    )
    sess_50 = rt.InferenceSession(
        MODEL_50_PATH,
        sess_options,
        providers=["CPUExecutionProvider"],
    )
    sess_90 = rt.InferenceSession(
        MODEL_90_PATH,
        sess_options,
        providers=["CPUExecutionProvider"],
    )

    input_name_10 = sess_10.get_inputs()[0].name
    label_name_10 = sess_10.get_outputs()[0].name
    input_name_50 = sess_50.get_inputs()[0].name
    label_name_50 = sess_50.get_outputs()[0].name
    input_name_90 = sess_90.get_inputs()[0].name
    label_name_90 = sess_90.get_outputs()[0].name


@app.get(
    "/",
    summary="Check to see if the inference API is running",
    description="""Use this endpoint to check if the API is running.""",
    response_description="A JSON record with a message in it.",
    operation_id="v0_health_check",
    tags=["analytics"],
)
async def root() -> dict[str, str]:
    return {"message": "Flight arrival delay inference API is running"}


@app.get(
    "/model-info",
    summary="Get model metadata",
    description="Return a concise description of the flight delay models currently loaded.",
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
    airline_value = features.marketing_airline_network.strip()
    input_data = np.array([[airline_value]], dtype=str)

    pred_10 = sess_10.run([label_name_10], {input_name_10: input_data})[0]
    pred_50 = sess_50.run([label_name_50], {input_name_50: input_data})[0]
    pred_90 = sess_90.run([label_name_90], {input_name_90: input_data})[0]

    return FlightDelayPredictionOutput(
        arrival_delay_10th_percentile_minutes=round(float(np.asarray(pred_10).reshape(-1)[0]), 2),
        arrival_delay_50th_percentile_minutes=round(float(np.asarray(pred_50).reshape(-1)[0]), 2),
        arrival_delay_90th_percentile_minutes=round(float(np.asarray(pred_90).reshape(-1)[0]), 2),
    )


async def send_webhook(
    job_id: str,
    webhook_url: str,
    result: FlightDelayPredictionOutput,
) -> None:
    payload = {
        "job_id": job_id,
        "status": "succeeded",
        "result": result.model_dump(),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(webhook_url, json=payload)

        async with AsyncSessionLocal() as db:
            await crud.update_webhook_delivery(
                db=db,
                job_id=job_id,
                sent=response.is_success,
                status_code=response.status_code,
                error_text=None if response.is_success else response.text[:1000],
            )
    except Exception as exc:
        async with AsyncSessionLocal() as db:
            await crud.update_webhook_delivery(
                db=db,
                job_id=job_id,
                sent=False,
                status_code=None,
                error_text=str(exc),
            )


async def process_job(
    job_id: str,
    features: FlightInferenceFeatures,
    webhook_url: str | None,
) -> None:
    async with AsyncSessionLocal() as db:
        await crud.update_job_running(db=db, job_id=job_id)

    try:
        result = run_prediction(features)

        async with AsyncSessionLocal() as db:
            await crud.update_job_succeeded(
                db=db,
                job_id=job_id,
                result_payload=result.model_dump(),
            )

        if webhook_url is not None:
            await send_webhook(job_id, webhook_url, result)

    except Exception as exc:
        async with AsyncSessionLocal() as db:
            await crud.update_job_failed(db=db, job_id=job_id, error_text=str(exc))


@app.post(
    "/inference-jobs",
    response_model=InferenceJobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a flight delay inference job",
    description="Submit a job that predicts 10th, 50th, and 90th percentile arrival delays for a marketing airline.",
    response_description="A JSON record containing the job ID and queued status.",
    operation_id="v0_submit_inference_job",
    tags=["inference jobs"],
)
async def submit_inference_job(
    request: InferenceJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> InferenceJobAccepted:
    job_id = str(uuid4())

    await crud.create_job_record(
        db=db,
        job_id=job_id,
        request_payload=request.features.model_dump(by_alias=True),
        webhook_url=str(request.webhook_url) if request.webhook_url is not None else None,
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
    job = await crud.fetch_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    return InferenceJobStatus(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at.isoformat(),
        started_at=_iso_or_none(job.started_at),
        completed_at=_iso_or_none(job.completed_at),
        webhook_url=job.webhook_url,
        webhook_sent=job.webhook_sent,
        webhook_status_code=job.webhook_status_code,
        error_text=job.error_text,
        webhook_error_text=job.webhook_error_text,
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
    job = await crud.fetch_job(db=db, job_id=job_id)
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
    job = await crud.fetch_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    if job.status in {"queued", "running"}:
        raise HTTPException(
            status_code=409,
            detail="Inference job is not complete yet",
        )

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
        completed_at=job.completed_at.isoformat(),
    )


@app.delete(
    "/inference-jobs/{job_id}",
    response_model=DeleteJobResponse,
    summary="Delete a stored inference job",
    description="Delete a stored inference job record from PostgreSQL.",
    operation_id="v0_delete_inference_job",
    tags=["inference jobs"],
)
async def delete_inference_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> DeleteJobResponse:
    deleted = await crud.delete_job_record(db=db, job_id=job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Inference job not found")
    return DeleteJobResponse(job_id=job_id, deleted=True)


@app.get(
    "/predict-sync",
    response_model=FlightDelayPredictionOutput,
    summary="Run a synchronous prediction",
    description="Convenience endpoint for local development. The asynchronous job endpoints are still the primary interface.",
    operation_id="v0_predict_sync",
    tags=["inference jobs"],
)
async def predict_sync(features: FlightInferenceFeatures) -> FlightDelayPredictionOutput:
    return run_prediction(features)


@app.delete(
    "/reset-job-store",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all stored job records",
    description="Convenience endpoint for demos and testing. Removes all rows from the PostgreSQL tracking table.",
    operation_id="v0_reset_job_store",
    tags=["analytics"],
)
async def reset_job_store(db: AsyncSession = Depends(get_db)) -> Response:
    await crud.reset_job_store(db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
