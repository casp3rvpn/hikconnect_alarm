from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass
)
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    device_info = await hass.async_add_executor_job(device.get_device_info)
    
    async_add_entities([
        HikVisionAlarmSensor(device, device_info)
    ], True)

class HikVisionAlarmSensor(BinarySensorEntity):
    """Representation of a HikVision alarm sensor."""
    
    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_should_poll = True

    def __init__(self, device, device_info):
        self._device = device
        self._attr_name = f"HikVision Alarm {device_info.get('deviceName', 'Unknown')}"
        self._attr_unique_id = device_info.get("serialNumber", "unknown")
        self._attr_is_on = False

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            status = await self.hass.async_add_executor_job(
                self._device.get_alarm_status
            )
            self._attr_is_on = status.get("triggered", False)
        except Exception:
            self._attr_available = False