from datetime import date

from pydantic import BaseModel, ConfigDict


class FlightBase(BaseModel):
    flight_date: date
    iata_code_marketing_airline: str | None = None
    flight_number_marketing_airline: str | None = None

    origin: str | None = None
    origin_city_name: str | None = None
    dest: str | None = None
    dest_city_name: str | None = None

    crs_dep_time: str | None = None
    dep_time: str | None = None
    crs_arr_time: str | None = None
    arr_time: str | None = None

    dep_delay_minutes: float | None = None
    arr_delay_minutes: float | None = None

    cancelled: float | None = None
    diverted: float | None = None

    operating_airline: str | None = None
    iata_code_operating_airline: str | None = None
    tail_number: str | None = None


class Flight(FlightBase):
    id: int

    model_config = ConfigDict(from_attributes=True)