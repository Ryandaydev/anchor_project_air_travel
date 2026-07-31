from urllib.parse import urljoin

import httpx

from air_travel.exceptions import AirTravelAPIError, AirTravelRequestError

DEFAULT_BASE_URL = "https://api.airtravelsource.com/"


class AirTravelClient:
    """Client for the Air Travel API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self.base_url = base_url
        self.timeout = timeout

    def build_url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    def health(self) -> dict:
        """Check API health status."""
        try:
            response = httpx.get(
                self.build_url("/"),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise AirTravelAPIError(
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.HTTPError as e:
            raise AirTravelRequestError(str(e)) from e

    def carriers(self, code: str | None = None) -> list[dict]:
        """List DOT/BTS airline carrier codes and names."""
        params: dict[str, str] = {}

        if code:
            params["code"] = code

        try:
            response = httpx.get(
                self.build_url("/v0/carriers"),
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise AirTravelAPIError(
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.HTTPError as e:
            raise AirTravelRequestError(str(e)) from e

    def flights(
        self,
        carrier: str | None = None,
        flightnumber: str | None = None,
        flight_date: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """Search for flights based on carrier, flight number, and flight date."""
        params: dict[str, str | int] = {
            "skip": skip,
            "limit": limit,
        }

        if carrier:
            params["carrier"] = carrier
        if flightnumber:
            params["flightnumber"] = flightnumber
        if flight_date:
            params["flight_date"] = flight_date

        try:
            response = httpx.get(
                self.build_url("/v0/flights"),
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise AirTravelAPIError(
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.HTTPError as e:
            raise AirTravelRequestError(str(e)) from e