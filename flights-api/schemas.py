#region imports
from datetime import date

from pydantic import BaseModel, ConfigDict
#endregion

#region schemas
class Flight(BaseModel):
    id: int
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

    model_config = ConfigDict(from_attributes=True)

# https://www.bts.gov/topics/airlines-and-airports/airline-codes
class Airline(BaseModel):
    carrier: str
    carrier_name: str


#endregion