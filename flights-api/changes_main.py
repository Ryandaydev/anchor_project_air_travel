
#region imports
from schemas import Flight, Airline
#endregion


#region setup

AIRLINE_CODES = [
    {"carrier": "AA", "carrier_name": "American Airlines"},
    {"carrier": "DL", "carrier_name": "Delta Air Lines"},
    {"carrier": "UA", "carrier_name": "United Airlines"},
    {"carrier": "WN", "carrier_name": "Southwest Airlines"},
]


#endregion

#region endpoints
@app.get(
        "/v0/airlines", 
        description="""Return list of airlines with carrier code and carrier name.""",
        operation_id="v0_get_airlines",
        tags=["airline"],
        response_model=list[Airline])
async def get_airlines():
    return AIRLINE_CODES
#endregion