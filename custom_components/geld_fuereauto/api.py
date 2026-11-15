"""Read-only client for the customer endpoints observed in a browser HAR.

The login endpoint was observed, but the HAR did not contain session headers.
The login implementation therefore verifies authentication by requesting account
details rather than assuming HTTP 200 means authenticated.
"""

from __future__ import annotations

from aiohttp import ClientError, ClientResponseError

from homeassistant.helpers.aiohttp_client import async_get_clientsession

BASE_URL = "https://geld-fuer-eauto.de"


class GeldFuerEautoAuthError(Exception):
    """Login rejected or session expired."""


class GeldFuerEautoApi:
    """API calls use one Home Assistant-managed cookie session."""

    def __init__(self, hass, email: str, password: str) -> None:
        self._session = async_get_clientsession(hass)
        self._email = email
        self._password = password

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        async with self._session.get(
            f"{BASE_URL}{endpoint}", params=params, timeout=25
        ) as response:
            if response.status in (401, 403):
                raise GeldFuerEautoAuthError("Session expired")
            response.raise_for_status()
            return await response.json(content_type=None)

    async def login(self) -> dict:
        """Log in, and independently verify the resulting authenticated session."""
        async with self._session.post(
            f"{BASE_URL}/api/login",
            json={"email": self._email, "password": self._password},
            timeout=25,
        ) as response:
            if response.status in (400, 401, 403):
                raise GeldFuerEautoAuthError("Login rejected")
            response.raise_for_status()
        data = await self._get("/api/getAccountDetails")
        if not isinstance(data, dict) or data.get("email", "").casefold() != self._email.casefold():
            raise GeldFuerEautoAuthError("Could not verify authenticated account")
        return data

    async def fetch(self) -> dict:
        """Fetch read-only customer information; do not expose private fields."""
        account = await self._get("/api/getAccountDetails")
        cars_result = await self._get(
            "/api/getCars",
            {"limit": 100, "page": 1, "order_by": "uploaded"},
        )
        cars = list(cars_result.get("cars", []))
        count = int(cars_result.get("count", len(cars)))
        page = 1
        while len(cars) < count and page < 50:
            page += 1
            batch = await self._get(
                "/api/getCars",
                {"limit": 100, "page": page, "order_by": "uploaded"},
            )
            more = batch.get("cars", [])
            if not more:
                break
            cars.extend(more)
        summary = await self._get(
            "/api/profile/getPaymentSummary", {"payment_type": "all"}
        )
        return {"account": account, "cars": cars, "payment_summary": summary}
