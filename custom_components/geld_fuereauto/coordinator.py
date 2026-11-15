"""Fetch public standard premiums from Geld für eAuto."""

from __future__ import annotations

import re
from datetime import timedelta
from html.parser import HTMLParser

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PRICE_URL, VEHICLE_CLASSES


class _PriceTableParser(HTMLParser):
    """Read year headings and standard-price table rows from public HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.year: int | None = None
        self.prices: dict[tuple[int, str, str], float] = {}
        self._heading = False
        self._heading_parts: list[str] = []
        self._in_row = False
        self._in_cell = False
        self._cells: list[str] = []
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h2":
            self._heading = True
            self._heading_parts = []
        elif tag == "tr":
            self._in_row = True
            self._cells = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._heading:
            self._heading_parts.append(data)
        if self._in_cell:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self._heading:
            text = " ".join(self._heading_parts)
            match = re.search(r"Quotenjahr\s+(20\d{2})", text, re.I)
            if match:
                self.year = int(match.group(1))
            self._heading = False
        elif tag in ("td", "th") and self._in_cell:
            self._cells.append(" ".join(self._parts).strip())
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            self._parse_row()
            self._in_row = False

    def _parse_row(self) -> None:
        if self.year is None or len(self._cells) < 4:
            return
        match = re.search(r"\b(M1|N1|N2|N3|M3)\b", self._cells[0])
        if not match:
            return
        vehicle_class = match.group(1)
        for index, tariff in enumerate(("garantie", "risiko", "express"), 1):
            value = self._parse_number(self._cells[index])
            if value is not None:
                self.prices[(self.year, vehicle_class, tariff)] = value

    @staticmethod
    def _parse_number(text: str) -> float | None:
        match = re.search(r"\d[\d\s.\u00a0]*(?:,\d+)?", text)
        if not match:
            return None
        raw = re.sub(r"[\s.\u00a0]", "", match.group()).replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None


def parse_prices(html: str) -> dict[tuple[int, str, str], float]:
    """Parse public price table without inventing missing values."""
    parser = _PriceTableParser()
    parser.feed(html)
    if not parser.prices:
        raise ValueError("No standard premiums found in public price page")
    # Skip incomplete years instead of publishing a misleading partial matrix.
    years = {key[0] for key in parser.prices}
    complete_years = {
        year for year in years
        if all((year, cls, tariff) in parser.prices
               for cls in VEHICLE_CLASSES
               for tariff in ("garantie", "risiko", "express"))
    }
    if not complete_years:
        raise ValueError("Public premium table incomplete or structure changed")
    return {
        key: value for key, value in parser.prices.items()
        if key[0] in complete_years
    }


class GeldFuerEautoCoordinator(DataUpdateCoordinator[dict]):
    """Poll the public premium table daily."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(hours=24),
        )

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                PRICE_URL,
                timeout=20,
                headers={"Accept": "text/html"},
            ) as response:
                response.raise_for_status()
                html = await response.text()
            return parse_prices(html)
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Unable to retrieve public premiums: {err}") from err


class GeldFuerEautoAccountCoordinator(DataUpdateCoordinator[dict]):
    """Poll the customer's vehicles and payout summary."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        from .api import GeldFuerEautoApi
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}_account",
            update_interval=timedelta(hours=6),
        )
        self.api = GeldFuerEautoApi(hass, entry.data["email"], entry.data["password"])

    async def _async_update_data(self) -> dict:
        from .api import GeldFuerEautoAuthError
        try:
            return await self.api.fetch()
        except GeldFuerEautoAuthError as err:
            # Do not retry a rejected login. The API client already retries once
            # when an existing session expires.
            raise UpdateFailed(f"Customer authentication failed: {err}") from err
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(
                f"Customer API request failed: {type(err).__name__}"
            ) from err
