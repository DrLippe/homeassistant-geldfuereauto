"""Personal account entities, constructed only from observed response fields."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, NAME

ACCOUNT_FIELDS = {
    "pending_amount": ("Ausstehende Auszahlungen", "€"),
    "paid_amount": ("Ausgezahlte Prämien", "€"),
    "pending_car_amount_next_year": ("Ausstehend nächstes Quotenjahr", "€"),
}


def make_account_entities(coordinator, entry):
    """Create a basic personal account and one device per returned car."""
    entities = [
        AccountSummarySensor(coordinator, entry, key, name, unit)
        for key, (name, unit) in ACCOUNT_FIELDS.items()
    ]
    entities.append(CarCountSensor(coordinator, entry))
    for car in coordinator.data.get("cars", []):
        car_id = car.get("docid")
        if not car_id:
            continue
        for payout in car.get("payouts", []):
            year = payout.get("year")
            if year is not None:
                entities.extend([
                    CarPayoutSensor(coordinator, entry, car_id, year, "value", "Prämie", "€"),
                    CarPayoutSensor(coordinator, entry, car_id, year, "paid", "Ausgezahlt", None),
                    CarPayoutSensor(coordinator, entry, car_id, year, "status", "Status", None),
                ])
    return entities


class BasePersonalSensor(CoordinatorEntity, SensorEntity):
    """Base class for customer sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME + " – Kundenkonto",
            manufacturer="ZusammenStromen GmbH",
            configuration_url="https://geld-fuer-eauto.de/de/dashboard",
        )


class AccountSummarySensor(BasePersonalSensor):
    """Account payment summary value."""

    def __init__(self, coordinator, entry, key, label, unit):
        super().__init__(coordinator, entry)
        self._key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.entry_id}_summary_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:cash"

    @property
    def native_value(self):
        return self.coordinator.data.get("payment_summary", {}).get(self._key)


class CarCountSensor(BasePersonalSensor):
    """Number of registered vehicles."""

    _attr_name = "Registrierte Fahrzeuge"
    _attr_icon = "mdi:car-multiple"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_cars_count"

    @property
    def native_value(self):
        return len(self.coordinator.data.get("cars", []))


class CarPayoutSensor(BasePersonalSensor):
    """One payout field for one car and quota year."""

    def __init__(self, coordinator, entry, car_id, year, field, label, unit):
        super().__init__(coordinator, entry)
        self._car_id = car_id
        self._year = year
        self._field = field
        car = next((car for car in coordinator.data.get("cars", []) if car.get("docid") == car_id), {})
        plate = car.get("plate") or "Fahrzeug"
        self._attr_name = f"{year} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{car_id}_{year}_{field}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:cash-check" if field == "paid" else "mdi:cash"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{car_id}")},
            name=f"{NAME} – {plate}",
            manufacturer="ZusammenStromen GmbH",
            via_device=(DOMAIN, entry.entry_id),
            configuration_url="https://geld-fuer-eauto.de/de/dashboard/vehicles",
        )

    @property
    def native_value(self):
        for car in self.coordinator.data.get("cars", []):
            if car.get("docid") == self._car_id:
                for payout in car.get("payouts", []):
                    if str(payout.get("year")) == str(self._year):
                        value = payout.get(self._field)
                        if self._field == "paid" and isinstance(value, bool):
                            return "Ja" if value else "Nein"
                        return value
        return None
