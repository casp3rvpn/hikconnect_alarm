from hikconnect.api import HikConnectAPI

class HikConnectBinarySensor(BinarySensorEntity):
    def __init__(self, api: HikConnectAPI, device_info):
        self._api = api
        self._attr_name = f"Hik-Connect Alarm {device_info['name']}"
        self._attr_unique_id = device_info["serial"]

    async def async_update(self):
        """Fetch alarm status."""
        status = await self.hass.async_add_executor_job(
            self._api.get_alarm_status
        )
        self._attr_is_on = status["alarm_active"]