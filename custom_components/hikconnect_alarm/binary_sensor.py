from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    api = hass.data[DOMAIN][entry.entry_id]
    
    # Get device info
    device_info = await hass.async_add_executor_job(api.get_device_info)
    
    async_add_entities([
        HikConnectAlarmSensor(api, device_info)
    ], True)

class HikConnectAlarmSensor(BinarySensorEntity):
    """Representation of a Hik-Connect alarm sensor."""
    
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_should_poll = True

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = f"Hik-Connect Alarm {device_info['name']}"
        self._attr_unique_id = f"hikconnect_{device_info['serial']}"
        self._attr_is_on = False

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            status = await self.hass.async_add_executor_job(
                self._api.get_alarm_status
            )
            self._attr_is_on = status.get("alarm_active", False)
        except Exception:
            self._attr_available = False