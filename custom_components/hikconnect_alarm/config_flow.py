from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from hikconnect.api import HikConnectAPI, AuthenticationError
from .const import DOMAIN, DEFAULT_PORT

class HikConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                api = HikConnectAPI(
                    host=user_input["host"],
                    username=user_input["username"],
                    password=user_input["password"],
                    port=user_input.get("port", DEFAULT_PORT)
                )
                
                # Проверка подключения
                await self.hass.async_add_executor_job(api.get_device_info)
                
                return self.async_create_entry(
                    title=f"Hik-Connect {user_input['host']}",
                    data=user_input
                )
            except AuthenticationError:
                errors["base"] = "invalid_auth"
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