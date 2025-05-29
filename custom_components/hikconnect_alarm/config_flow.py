from hikconnect.api import HikConnectAPI, AuthenticationError
import voluptuous as vol

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            try:
                api = HikConnectAPI(
                    host=user_input["host"],
                    username=user_input["username"],
                    password=user_input["password"]
                )
                await self.hass.async_add_executor_job(api.get_device_info)
                
                return self.async_create_entry(
                    title=f"Hik-Connect {user_input['host']}",
                    data=user_input
                )
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str
            }),
            errors=errors
        )