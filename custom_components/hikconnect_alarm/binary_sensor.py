"""Hik-Connect Alarm binary sensor."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import aiohttp
import async_timeout

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    CONF_DEVICE_SERIAL,
    CONF_DEVICE_NAME,
    DEFAULT_APP_KEY,
    DEFAULT_APP_SECRET,
    LOGIN_URL,
    ALARM_STATUS_URL,
    ATTR_ALARM_TYPE,
    ATTR_ALARM_TIME,
    ATTR_DEVICE_MODEL,
    ATTR_DEVICE_STATUS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hik-Connect binary sensor from a config entry."""
    coordinator = HikConnectDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([HikConnectBinarySensor(coordinator, entry)])

class HikConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Hik-Connect data API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        self._entry = entry
        self._session = hass.helpers.aiohttp_client.async_get_clientsession()
        self._access_token = None
        self._token_expires = None

    async def _async_update_data(self) -> dict:
        """Update data via API."""
        try:
            async with async_timeout.timeout(10):
                # Refresh access token if needed
                if not self._access_token or datetime.now() >= self._token_expires:
                    await self._refresh_access_token()

                # Get alarm status
                return await self._get_alarm_status()
        except Exception as error:
            raise UpdateFailed(f"Error updating Hik-Connect data: {error}") from error

    async def _refresh_access_token(self) -> None:
        """Refresh Hik-Connect access token."""
        auth_data = {
            "client_id": DEFAULT_APP_KEY,
            "client_secret": DEFAULT_APP_SECRET,
            "grant_type": "password",
            "username": self._entry.data[CONF_USERNAME],
            "password": self._entry.data[CONF_PASSWORD],
        }

        async with self._session.post(LOGIN_URL, data=auth_data) as response:
            if response.status != 200:
                raise UpdateFailed("Failed to refresh access token")
            
            auth_info = await response.json()
            self._access_token = auth_info["access_token"]
            self._token_expires = datetime.now() + timedelta(
                seconds=auth_info["expires_in"] - 60  # 1 minute buffer
            )

    async def _get_alarm_status(self) -> dict:
        """Get alarm status from Hik-Connect API."""
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        params = {
            "deviceSerial": self._entry.data[CONF_DEVICE_SERIAL],
        }

        async with self._session.get(
            ALARM_STATUS_URL, headers=headers, params=params
        ) as response:
            if response.status != 200:
                raise UpdateFailed(f"Failed to get alarm status: {response.status}")

            data = await response.json()
            return {
                "alarm_status": data.get("alarmStatus", False),
                "alarm_type": data.get("alarmType", "unknown"),
                "alarm_time": data.get("alarmTime"),
                "device_model": data.get("deviceModel"),
                "device_status": data.get("deviceStatus"),
            }

class HikConnectBinarySensor(BinarySensorEntity):
    """Representation of a Hik-Connect alarm status."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(
        self, coordinator: HikConnectDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__()
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = entry.data.get(CONF_DEVICE_NAME, DEFAULT_NAME)
        self._attr_unique_id = f"hikconnect_{entry.data[CONF_DEVICE_SERIAL]}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data[CONF_DEVICE_SERIAL])},
            "name": entry.data.get(CONF_DEVICE_NAME, DEFAULT_NAME),
            "manufacturer": "Hikvision",
        }

    @property
    def is_on(self) -> bool:
        """Return true if alarm is triggered."""
        if not self._coordinator.data:
            return False
        return self._coordinator.data.get("alarm_status", False)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional alarm attributes."""
        if not self._coordinator.data:
            return {}
        
        return {
            ATTR_ALARM_TYPE: self._coordinator.data.get("alarm_type"),
            ATTR_ALARM_TIME: self._coordinator.data.get("alarm_time"),
            ATTR_DEVICE_MODEL: self._coordinator.data.get("device_model"),
            ATTR_DEVICE_STATUS: self._coordinator.data.get("device_status"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update the entity."""
        await self._coordinator.async_request_refresh()