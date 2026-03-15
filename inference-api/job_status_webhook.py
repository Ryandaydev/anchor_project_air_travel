"""
Webhook receiver for Flight Delay Inference API
Receives completion notifications when inference jobs finish.
"""

from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI(
    title="Flight Inference Webhook Receiver",
    description="Receives webhook callbacks from the flight delay inference API.",
    version="0.1",
)


@app.get("/")
async def health_check():
    return {"message": "Flight inference webhook receiver running"}


@app.post("/flight-inference-webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    print("\n========== FLIGHT INFERENCE WEBHOOK ==========")

    job_id = payload.get("job_id")
    airline = payload.get("request", {}).get("Marketing_Airline_Network")
    status = payload.get("status")

    print(f"Job ID: {job_id}")
    print(f"Airline: {airline}")
    print(f"Status: {status}")

    if status == "succeeded":
        result = payload.get("result", {})

        p10 = result.get("p10_delay_minutes")
        p50 = result.get("p50_delay_minutes")
        p90 = result.get("p90_delay_minutes")

        print("\nPredicted Arrival Delay Distribution")
        print("------------------------------------")
        print(f"10th percentile delay : {p10} minutes")
        print(f"50th percentile delay : {p50} minutes")
        print(f"90th percentile delay : {p90} minutes")

    if payload.get("error"):
        print("\nERROR:")
        print(payload["error"])

    created_at = payload.get("created_at")
    completed_at = payload.get("completed_at")

    if created_at:
        print(f"\nCreated at: {created_at}")

    if completed_at:
        print(f"Completed at: {completed_at}")

    print("======================================\n")

    return {"message": "Flight inference webhook received"}