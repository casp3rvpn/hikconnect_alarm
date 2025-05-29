"""Constants for Hik-Connect integration."""
DOMAIN = "hikconnectAlarm"
DEFAULT_NAME = "Hik-Connect Alarm"
DEFAULT_SCAN_INTERVAL = 15  # seconds
VERSION = "0.1.1"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_SERIAL = "device_serial"
CONF_DEVICE_NAME = "device_name"
CONF_CAMERA_IDX = "camera_index"

# Default API credentials (from official Hik-Connect app)
DEFAULT_APP_KEY = "27400483"
DEFAULT_APP_SECRET = "4c12b3e5b6a74b5d9e5337d5c1f6a7d1"

# API endpoints
API_BASE_URL = "https://api.hik-connect.com"
LOGIN_URL = f"{API_BASE_URL}/v3/users/login/v2"
DEVICES_URL = f"{API_BASE_URL}/api/v3/devices"
ALARM_STATUS_URL = f"{API_BASE_URL}/api/v3/alarm/device/status"

# Attributes
ATTR_ALARM_TYPE = "alarm_type"
ATTR_ALARM_TIME = "alarm_time"
ATTR_DEVICE_MODEL = "device_model"
ATTR_DEVICE_STATUS = "device_status"