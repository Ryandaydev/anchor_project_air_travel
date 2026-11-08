#region imports
#endregion

#region schemas

# https://www.bts.gov/topics/airlines-and-airports/airline-codes
class Airline(BaseModel):
    carrier: str
    carrier_name: str


#endregion