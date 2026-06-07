from urllib.parse import urljoin

import httpx

from anchor_air.exceptions import AnchorAirAPIError, AnchorAirRequestError

DEFAULT_BASE_URL = "https://air-travel.fastapicloud.dev"


class AnchorAirClient:
    """Client for the Anchor Air API."""

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
            raise AnchorAirAPIError(
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.HTTPError as e:
            raise AnchorAirRequestError(str(e)) from e

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
            raise AnchorAirAPIError(
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e

        except httpx.HTTPError as e:
            raise AnchorAirRequestError(str(e)) from e