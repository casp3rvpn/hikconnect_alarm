from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from hikconnect.hikconnect import HikVisionDevice
from .const import DOMAIN, DEFAULT_PORT

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hik-Connect Local."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                device = HikVisionDevice(
                    host=user_input["host"],
                    username=user_input["username"],
                    password=user_input["password"],
                    port=user_input.get("port", DEFAULT_PORT)
                )
                
                # Test connection
                await self.hass.async_add_executor_job(device.get_device_info)

                return self.async_create_entry(
                    title=f"HikVision {user_input['host']}",
                    data=user_input
                )
            except Exception as err:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Optional("port", default=DEFAULT_PORT): int
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )