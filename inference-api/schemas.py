"""Pydantic schemas for the flight delay inference API."""

from pydantic import BaseModel, Field


class FlightInferenceFeatures(BaseModel):
    marketing_airline_network: str = Field(
        ...,
        alias="Marketing_Airline_Network",
        min_length=1,
        description=(
            "Marketing airline code or name used by the trained model, "
            "for example DL, UA, AA, or WN."
        ),
        examples=["DL"],
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {"Marketing_Airline_Network": "DL"},
                {"Marketing_Airline_Network": "UA"},
                {"Marketing_Airline_Network": "AA"},
            ]
        },
    }


class FlightDelayPredictionOutput(BaseModel):
    arrival_delay_10th_percentile_minutes: float
    arrival_delay_50th_percentile_minutes: float
    arrival_delay_90th_percentile_minutes: float
