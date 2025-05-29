"""Config flow for Hik-Connect integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_SERIAL,
    CONF_DEVICE_NAME,
    DEFAULT_APP_KEY,
    DEFAULT_APP_SECRET,
    LOGIN_URL,
    DEVICES_URL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

async def authenticate_client(
    hass: HomeAssistant, username: str, password: str
) -> tuple[str, list[dict]]:
    """Authenticate with Hik-Connect and get devices list."""
    session = async_get_clientsession(hass)
    
    # Step 1: Get access token
    auth_data = {
        "client_id": DEFAULT_APP_KEY,
        "client_secret": DEFAULT_APP_SECRET,
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    try:
        async with session.post(LOGIN_URL, data=auth_data) as response:
            if response.status != 200:
                raise InvalidAuth
            auth_info = await response.json()
            access_token = auth_info["access_token"]

        # Step 2: Get devices list
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get(DEVICES_URL, headers=headers) as response:
            if response.status != 200:
                raise CannotConnect
            devices_info = await response.json()
            return access_token, devices_info["devices"]

    except aiohttp.ClientError as err:
        _LOGGER.error("Connection error: %s", err)
        raise CannotConnect from err

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hik-Connect."""

    VERSION = 1
    reauth_entry: ConfigEntry | None = None

    def __init__(self):
        """Initialize the config flow."""
        self.devices = []
        self.access_token = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                self.access_token, self.devices = await authenticate_client(
                    self.hass, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                return await self.async_step_device()

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_device(self, user_input=None):
        """Handle the device selection step."""
        if user_input is None:
            # Show device selection form
            device_options = {
                device["deviceSerial"]: f"{device['deviceName']} ({device['deviceSerial']})"
                for device in self.devices
            }

            if not device_options:
                return self.async_abort(reason="no_devices")

            return self.async_show_form(
                step_id="device",
                data_schema=vol.Schema({
                    vol.Required(CONF_DEVICE_SERIAL): vol.In(device_options)
                }),
            )

        # Get selected device details
        selected_device = next(
            device for device in self.devices
            if device["deviceSerial"] == user_input[CONF_DEVICE_SERIAL]
        )

        # Check if already configured
        await self.async_set_unique_id(user_input[CONF_DEVICE_SERIAL])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{selected_device['deviceName']}",
            data={
                CONF_USERNAME: self.hass.data[DOMAIN].get(CONF_USERNAME),
                CONF_PASSWORD: self.hass.data[DOMAIN].get(CONF_PASSWORD),
                CONF_DEVICE_SERIAL: user_input[CONF_DEVICE_SERIAL],
                CONF_DEVICE_NAME: selected_device["deviceName"],
            },
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""