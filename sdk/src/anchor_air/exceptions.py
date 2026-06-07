class AnchorAirError(Exception):
    """Base exception for the Anchor Air SDK."""


class AnchorAirRequestError(AnchorAirError):
    """Raised when the API request fails before receiving a response."""


class AnchorAirAPIError(AnchorAirError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"HTTP ERROR {status_code}: {response_text}")