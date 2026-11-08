
#region imports
import json

#endregion


#region setup
API_BASE_URL = "http://127.0.0.1:8000/"


#endregion

#region tools


@mcp.tool
async def get_airline_codes() -> str:
    """
    Get the list of airline carrier codes and names.

    Use this tool to translate a common airline name into the carrier code
    needed by get_flights. For example, use it to find that
    "United Airlines" corresponds to "UA" before calling get_flights.
    """
    data = await get_client().airlines()

    return json.dumps(data)


#endregion

# region Resources

# endregion

# region Prompts

# endregion

#region entrypoint
#endregion