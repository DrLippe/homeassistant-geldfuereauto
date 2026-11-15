"""Geld für eAuto sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .account_sensor import make_account_entities
from .const import DOMAIN, NAME, PRICE_URL
from .coordinator import GeldFuerEautoAccountCoordinator, GeldFuerEautoCoordinator

TARIFF_LABELS = {
    "garantie": "Garantie",
    "risiko": "Risikoanteil",
    "express": "Express",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create entities based on the selected feed."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if isinstance(coordinator, GeldFuerEautoAccountCoordinator):
        async_add_entities(make_account_entities(coordinator, entry))
    else:
        async_add_entities(
            GeldFuerEautoSensor(coordinator, entry, year, vehicle_class, tariff)
            for year, vehicle_class, tariff in sorted(coordinator.data)
        )


class GeldFuerEautoSensor(CoordinatorEntity[GeldFuerEautoCoordinator], SensorEntity):
    """An unpersonalized published THG premium or risk share."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, year, vehicle_class, tariff):
        super().__init__(coordinator)
        self._key = (year, vehicle_class, tariff)
        self._attr_unique_id = f"{entry.entry_id}_{year}_{vehicle_class}_{tariff}"
        self._attr_name = f"{year} {vehicle_class} {TARIFF_LABELS[tariff]}"
        self._attr_native_unit_of_measurement = "%" if tariff == "risiko" else "€"
        self._attr_icon = "mdi:percent" if tariff == "risiko" else "mdi:cash"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "standard_preise")},
            name=f"{NAME} – Standardprämien",
            manufacturer="ZusammenStromen GmbH",
            configuration_url=PRICE_URL,
        )
        self._attr_extra_state_attributes = {
            "quotenjahr": year,
            "fahrzeugklasse": vehicle_class,
            "tarif": tariff,
            "preisart": "Unverbindliche öffentliche Standardprämie",
            "quelle": PRICE_URL,
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)
