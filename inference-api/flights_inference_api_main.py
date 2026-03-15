"""Asynchronous Flight Arrival Delay Inference API.

This API adapts the async job architecture from the earlier example API
to the Anchor Project's flight arrival delay quantile models.

Expected model artifacts in the same working directory:
- flight_arrdelay_model_10.onnx
- flight_arrdelay_model_50.onnx
- flight_arrdelay_model_90.onnx

Run:
    uvicorn flights_inference_api_main:app --reload
"""

from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import uuid4
import json
import sqlite3

import httpx
import numpy as np
import onnxruntime as rt
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, HttpUrl
from starlette.concurrency import run_in_threadpool

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

DB_PATH = "flight_inference_jobs.db"
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


class DeleteJobResponse(BaseModel):
    job_id: str
    deleted: bool


app = FastAPI(
    description=api_description,
    title="Asynchronous Flight Arrival Delay Inference API",
    version="0.2.0",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inference_jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                request_json TEXT NOT NULL,
                result_json TEXT,
                error_text TEXT,
                webhook_url TEXT,
                webhook_sent INTEGER NOT NULL DEFAULT 0,
                webhook_status_code INTEGER,
                webhook_error_text TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT
            )
            """
        )
        conn.commit()


def create_job_record(
    job_id: str,
    request_json: str,
    webhook_url: Optional[str],
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO inference_jobs (
                job_id, status, request_json, webhook_url, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (job_id, "queued", request_json, webhook_url, utc_now_iso()),
        )
        conn.commit()


def update_job_running(job_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE inference_jobs
            SET status = ?, started_at = ?
            WHERE job_id = ?
            """,
            ("running", utc_now_iso(), job_id),
        )
        conn.commit()


def update_job_succeeded(job_id: str, result_json: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE inference_jobs
            SET status = ?, result_json = ?, completed_at = ?, error_text = NULL
            WHERE job_id = ?
            """,
            ("succeeded", result_json, utc_now_iso(), job_id),
        )
        conn.commit()


def update_job_failed(job_id: str, error_text: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE inference_jobs
            SET status = ?, error_text = ?, completed_at = ?
            WHERE job_id = ?
            """,
            ("failed", error_text, utc_now_iso(), job_id),
        )
        conn.commit()


def update_webhook_delivery(
    job_id: str,
    sent: bool,
    status_code: Optional[int] = None,
    error_text: Optional[str] = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE inference_jobs
            SET webhook_sent = ?, webhook_status_code = ?, webhook_error_text = ?
            WHERE job_id = ?
            """,
            (1 if sent else 0, status_code, error_text, job_id),
        )
        conn.commit()


def fetch_job(job_id: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                job_id,
                status,
                request_json,
                result_json,
                error_text,
                webhook_url,
                webhook_sent,
                webhook_status_code,
                webhook_error_text,
                created_at,
                started_at,
                completed_at
            FROM inference_jobs
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()
        return row


def delete_job_record(job_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM inference_jobs WHERE job_id = ?", (job_id,))
        conn.commit()
        return cursor.rowcount > 0


@app.on_event("startup")
def load_models_and_initialize_db() -> None:
    global sess_10, sess_50, sess_90
    global input_name_10, label_name_10
    global input_name_50, label_name_50
    global input_name_90, label_name_90

    initialize_database()

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
        await run_in_threadpool(
            update_webhook_delivery,
            job_id,
            response.is_success,
            response.status_code,
            None if response.is_success else response.text[:1000],
        )
    except Exception as exc:
        await run_in_threadpool(
            update_webhook_delivery,
            job_id,
            False,
            None,
            str(exc),
        )


async def process_job(
    job_id: str,
    features: FlightInferenceFeatures,
    webhook_url: Optional[str],
) -> None:
    await run_in_threadpool(update_job_running, job_id)

    try:
        result = await run_in_threadpool(run_prediction, features)
        await run_in_threadpool(update_job_succeeded, job_id, json.dumps(result.model_dump()))

        if webhook_url is not None:
            await send_webhook(job_id, webhook_url, result)

    except Exception as exc:
        await run_in_threadpool(update_job_failed, job_id, str(exc))


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
) -> InferenceJobAccepted:
    job_id = str(uuid4())

    await run_in_threadpool(
        create_job_record,
        job_id,
        request.features.model_dump_json(by_alias=True),
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
async def get_inference_job_status(job_id: str) -> InferenceJobStatus:
    row = await run_in_threadpool(fetch_job, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    return InferenceJobStatus(
        job_id=row["job_id"],
        status=row["status"],
        created_at=row["created_at"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        webhook_url=row["webhook_url"],
        webhook_sent=bool(row["webhook_sent"]),
        webhook_status_code=row["webhook_status_code"],
        error_text=row["error_text"],
    )


@app.get(
    "/inference-jobs/{job_id}/request",
    response_model=InferenceJobRequestView,
    summary="Get the original request for a submitted job",
    description="Return the stored request payload for a previously submitted inference job.",
    operation_id="v0_get_inference_job_request",
    tags=["inference jobs"],
)
async def get_inference_job_request(job_id: str) -> InferenceJobRequestView:
    row = await run_in_threadpool(fetch_job, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    request_payload = json.loads(row["request_json"])
    return InferenceJobRequestView(
        job_id=row["job_id"],
        status=row["status"],
        request=FlightInferenceFeatures.model_validate(request_payload),
        webhook_url=row["webhook_url"],
        created_at=row["created_at"],
    )


@app.get(
    "/inference-jobs/{job_id}/result",
    response_model=InferenceJobResult,
    summary="Get completed inference job result",
    description="Return prediction output for a completed inference job.",
    operation_id="v0_get_inference_job_result",
    tags=["inference jobs"],
)
async def get_inference_job_result(job_id: str) -> InferenceJobResult:
    row = await run_in_threadpool(fetch_job, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Inference job not found")

    if row["status"] in {"queued", "running"}:
        raise HTTPException(
            status_code=409,
            detail="Inference job is not complete yet",
        )

    if row["status"] == "failed":
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Inference job failed",
                "error_text": row["error_text"],
            },
        )

    if row["result_json"] is None:
        raise HTTPException(status_code=500, detail="Completed job has no stored result")

    return InferenceJobResult(
        job_id=row["job_id"],
        status="succeeded",
        result=FlightDelayPredictionOutput.model_validate(json.loads(row["result_json"])),
        completed_at=row["completed_at"],
    )


@app.delete(
    "/inference-jobs/{job_id}",
    response_model=DeleteJobResponse,
    summary="Delete a stored inference job",
    description="Delete a stored inference job record from the local tracking database.",
    operation_id="v0_delete_inference_job",
    tags=["inference jobs"],
)
async def delete_inference_job(job_id: str) -> DeleteJobResponse:
    deleted = await run_in_threadpool(delete_job_record, job_id)
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
    return await run_in_threadpool(run_prediction, features)


@app.delete(
    "/reset-job-store",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all stored job records",
    description="Convenience endpoint for demos and testing. Removes all rows from the local SQLite tracking table.",
    operation_id="v0_reset_job_store",
    tags=["analytics"],
)
async def reset_job_store() -> Response:
    def _reset() -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM inference_jobs")
            conn.commit()

    await run_in_threadpool(_reset)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
