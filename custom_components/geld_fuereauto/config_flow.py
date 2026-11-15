"""Config flow for Geld für eAuto."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, NAME

SCHEMA = vol.Schema({
    vol.Optional("email", default=""): str,
    vol.Optional("password", default=""): str,
})


class GeldFuerEautoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up public prices or a personal customer account."""

    VERSION = 2

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Use credentials only when both values are supplied."""
        errors = {}
        if user_input is not None:
            email = user_input.get("email", "").strip()
            password = user_input.get("password", "")
            if bool(email) != bool(password):
                errors["base"] = "credentials_incomplete"
            else:
                await self.async_set_unique_id(email.casefold() if email else DOMAIN)
                self._abort_if_unique_id_configured()
                data = {"email": email, "password": password} if email else {}
                return self.async_create_entry(
                    title=f"{NAME} ({email})" if email else NAME,
                    data=data,
                )
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)
