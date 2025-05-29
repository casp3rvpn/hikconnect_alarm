# Hik-Connect Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

This integration allows Home Assistant to monitor alarm status from Hik-Connect devices.

## Features
- Automatically detects Hik-Connect devices linked to your account
- No need to manually enter `app_key` and `app_secret`
- Real-time alarm status updates
- Shows additional details like alarm type and last trigger time

## Installation via HACS
1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click **⋮ (3 dots) → Custom repositories**
4. Add repository URL: `https://github.com/your-username/hikconnect-homeassistant`
5. Select **Integration** category
6. Click **Install**
7. Restart Home Assistant

## Manual Installation
1. Copy the `hikconnect` folder to `custom_components` in your Home Assistant config
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for **Hik-Connect Alarm** and follow the setup

## Configuration
After installation:
1. Enter your Hik-Connect username and password
2. Select your device from the list
3. The integration will automatically track alarm status

## Support
For issues, please [open an issue on GitHub](https://github.com/your-username/hikconnect-homeassistant/issues).