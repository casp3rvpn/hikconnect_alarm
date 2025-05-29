from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from hikconnect import HikConnect
from .const import DOMAIN, DEFAULT_PORT

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hik-Connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    device = HikConnect(
        ip=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"],
        port=entry.data.get("port", DEFAULT_PORT)
    )
    
    hass.data[DOMAIN][entry.entry_id] = device
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, ["binary_sensor"]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok