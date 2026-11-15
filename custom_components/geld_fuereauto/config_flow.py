"""Config flow for Geld für eAuto."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, NAME


class GeldFuerEautoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure the public price feed."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Set up the public standard price feed."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})

        return self.async_show_form(step_id="user")
