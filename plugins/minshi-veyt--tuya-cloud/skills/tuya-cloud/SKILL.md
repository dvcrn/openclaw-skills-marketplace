---
name: tuya-cloud
description: "Read sensor data and control Tuya IoT devices via Tuya Cloud API. Use when the user wants to list devices, read temperature, humidity, soil moisture, battery or other sensor data, or send commands to switches and valves. Requires TUYA_ACCESS_ID, TUYA_ACCESS_SECRET, and optionally TUYA_API_ENDPOINT in .env."
---

# Tuya Cloud Controller

Read sensor data and control Tuya IoT devices via `scripts/tuya_controller.py`.

## Device registry

Known controllable devices are defined in `scripts/config.py` as `CONTROLLABLE_DEVICES` (OPTIONAL).  
**Always consult this list first if exist** to resolve a device name to its `device_id`.  
For valve devices the `valve` key gives the DP code (e.g. `switch_1`) to use as the command `code`.  
Only call `tuya_list_devices` if the device is not listed in the config.

## Setup

Add credentials to `.env`:

```bash
TUYA_ACCESS_ID=your_access_id
TUYA_ACCESS_SECRET=your_access_secret
TUYA_API_ENDPOINT=https://openapi.tuyaeu.com  # default: tuyaus.com (US)
```

Regional endpoints: EU `tuyaeu.com` · US `tuyaus.com` · CN `tuyacn.com` · IN `tuyain.com`

Enable **IoT Core** service in your Tuya IoT Platform project, and grant devices controllable permission (read-only by default).

## Tools

### `tuya_list_devices`

List all Tuya devices linked to the cloud project.

```bash
python scripts/tuya_controller.py list_devices
python scripts/tuya_controller.py list_devices --output_format json --output_path devices.json
```

### `tuya_read_sensor`

Read all sensor data from a Tuya device (temperature, humidity, battery, motion, door state, switch state).

```bash
python scripts/tuya_controller.py read_sensor <device_id>
python scripts/tuya_controller.py read_sensor <device_id> --output_format text
```

`parse_sensor_data()` interprets raw API keys:

| Sensor | Raw keys | Notes |
|---|---|---|
| Temperature | `va_temperature`, `temp_current`, `temp_set` | Divided by 10 (e.g. 245 → 24.5°C) |
| Humidity | `va_humidity`, `humidity_value` | Percentage as-is |
| Battery | `battery_percentage`, `battery` | Good >80% / Medium >20% / Low ≤20% |
| Motion | `pir` | `"pir"` value = detected |
| Door | `doorcontact_state` | Boolean → Open/Closed |
| State | `state` | Boolean → On/Off |
| Soil moisture | `soil_moisture`, `humidity`, `va_humidity` | Percentage as-is |

### `tuya_control_device`

Send commands to a Tuya device (switch, valve, countdown timer). Pass a JSON array of `{"code", "value"}` pairs.

```bash
# Turn switch/valve on or off
python scripts/tuya_controller.py control_device <device_id> '[{"code":"switch_1","value":true}]'
python scripts/tuya_controller.py control_device <device_id> '[{"code":"switch_2","value":false}]'

# Open valve for a fixed duration — send switch ON + countdown in ONE call
# countdown_1 / countdown_2 values are in MINUTES — do NOT multiply by 60
python scripts/tuya_controller.py control_device <device_id> '[{"code":"switch_1","value":true},{"code":"countdown_1","value":10}]'
```

> ⚠️ `countdown_1` / `countdown_2` are in **minutes**. `10` = 10 min, `60` = 1 hour.

## API Endpoints (internal)

- Device list: `GET /v2.0/cloud/thing/device` (`page_size=20`)
- Device info: `GET /v2.0/cloud/thing/{device_id}`
- Device status: `GET /v2.0/cloud/thing/{device_id}/state`
- Send commands: `POST /v1.0/iot-03/devices/{device_id}/commands`

## Dependencies

```bash
pip install tinytuya python-dotenv
```

## Troubleshooting

| Error | Fix |
|---|---|
| "Data center is not enabled" | Enable IoT Core in Tuya IoT Platform → Service API |
| "Permission denied" | Subscribe to IoT Core and enable Device Status Notification |
| Device offline | `online: false`; soil moisture returns `null` |
| Wrong endpoint | Match `TUYA_API_ENDPOINT` to your account region |
