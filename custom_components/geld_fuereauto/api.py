"""Read-only cookie-authenticated API client for Geld für eAuto."""

from __future__ import annotations

from aiohttp import ClientError, CookieJar
from homeassistant.helpers.aiohttp_client import async_create_clientsession

BASE_URL = "https://geld-fuer-eauto.de"


class GeldFuerEautoAuthError(Exception):
    """Login rejected or the authenticated session expired."""


class GeldFuerEautoApi:
    """Keep the account's cookies isolated from all other integrations."""

    def __init__(self, hass, email: str, password: str) -> None:
        self._session = async_create_clientsession(hass, cookie_jar=CookieJar())
        self._email = email
        self._password = password
        self._authenticated = False

    def _has_session_cookie(self) -> bool:
        """Only inspect cookie names; never log or persist their values."""
        from yarl import URL

        cookies = self._session.cookie_jar.filter_cookies(URL(BASE_URL))
        return bool(cookies.get("sid"))

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        async with self._session.get(
            f"{BASE_URL}{endpoint}",
            params=params,
            timeout=25,
            headers={"Accept": "application/json, text/plain, */*"},
        ) as response:
            if response.status in (401, 403):
                self._authenticated = False
                raise GeldFuerEautoAuthError(f"Session expired (HTTP {response.status})")
            response.raise_for_status()
            result = await response.json(content_type=None)
            if not isinstance(result, dict):
                raise ValueError(f"Unexpected API response from {endpoint}")
            return result

    async def login(self) -> dict:
        """Start a new cookie session and verify it against account details."""
        self._authenticated = False
        self._session.cookie_jar.clear()
        async with self._session.post(
            f"{BASE_URL}/api/login",
            json={"email": self._email, "password": self._password},
            headers={
                "Accept": "application/json, text/plain, */*",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/login?redirect=/dashboard/vehicles",
            },
            timeout=25,
        ) as response:
            if response.status in (400, 401, 403):
                raise GeldFuerEautoAuthError(f"Login rejected (HTTP {response.status})")
            response.raise_for_status()

        if not self._has_session_cookie():
            raise GeldFuerEautoAuthError("Login did not return a sid cookie")

        account = await self._get("/api/getAccountDetails")
        # The returned account structure may not include an email at top level.
        if account.get("email") and str(account["email"]).casefold() != self._email.casefold():
            raise GeldFuerEautoAuthError("Login returned a different account")
        self._authenticated = True
        return account

    async def fetch(self) -> dict:
        """Read personal data with automatic first login and expiry retry."""
        if not self._authenticated or not self._has_session_cookie():
            await self.login()
        try:
            return await self._fetch_authenticated()
        except GeldFuerEautoAuthError:
            await self.login()
            return await self._fetch_authenticated()

    async def _fetch_authenticated(self) -> dict:
        account = await self._get("/api/getAccountDetails")
        cars_result = await self._get(
            "/api/getCars",
            {"limit": 100, "page": 1, "order_by": "uploaded"},
        )
        cars = list(cars_result.get("cars") or [])
        count = int(cars_result.get("count") or len(cars))
        page = 1
        while len(cars) < count and page < 50:
            page += 1
            batch = await self._get(
                "/api/getCars",
                {"limit": 100, "page": page, "order_by": "uploaded"},
            )
            more = batch.get("cars") or []
            if not more:
                break
            cars.extend(more)
        summary = await self._get(
            "/api/profile/getPaymentSummary", {"payment_type": "All"}
        )
        return {"account": account, "cars": cars, "payment_summary": summary}
