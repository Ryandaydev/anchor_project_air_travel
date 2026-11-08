#region imports

#endregion

#region setup

#endregion

#region client

    async def airlines(self) -> list[dict]:
        """Get the list of airline codes."""
        try:
            response = await self._client.get(
                self.build_url("/v0/airlines"),
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

#endregion