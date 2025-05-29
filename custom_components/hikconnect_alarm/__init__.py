from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from hikconnect.api import HikConnectAPI

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hik-Connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    api = HikConnectAPI(
        host=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"]
    )
    
    hass.data[DOMAIN][entry.entry_id] = api
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])
    
    return True