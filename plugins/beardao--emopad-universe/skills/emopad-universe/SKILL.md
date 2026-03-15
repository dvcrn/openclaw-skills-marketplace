---
name: emoPAD-universe
description: "emoPAD Universe - Emotion Universe Skill\n\n Helps users locate emotions in the PAD (Pleasure-Arousal-Dominance) coordinate system,\n and provides emoNebula feature: continuous real-time emotion PAD monitoring, with a popup window\n displaying the emotion nebula chart every 5 minutes.\n\n ## Cross-Platform Support\n \n Supports Linux and Windows operating systems:\n - **Linux**: Uses eog (Eye of GNOME) to display image windows\n - **Windows**: Uses the system default image viewer to display\n\n ## Auto-Start\n \n After installing this skill, the emoPAD service and emoNebula will start automatically, no manual operation needed.\n\n ## Supported Hardware\n \n - EEG: KSEEG102 (Bluetooth BLE)\n - PPG: Cheez PPG Sensor (Serial)\n - GSR: Sichiray GSR V2 (Serial)\n \n Theoretically, similar devices should also work. Future versions will gradually add support for mainstream brands, including:\n - Muse series EEG devices\n - Emotiv EEG devices\n - Oura Ring smart ring\n - Whoop smart wristband\n - Other mainstream EEG devices and wearable devices\n\n ## Dependency Installation\n \n Dependencies will be checked and installed automatically when installing the skill, no manual operation needed.\n\n ## Usage\n \n - `openclaw emopad status` - Get current PAD status\n - `openclaw emopad snapshot` - Manually generate emotion nebula chart\n - `openclaw emopad stop` - Stop service\n - `openclaw emopad start` - Restart service\n\n ## Important Notes\n \n **About Emotion PAD Calculation**: Currently based on heuristic methods, mapping relationships summarized from extensive literature.\n This method temporarily cannot reflect individual differences. Future versions will introduce personalized calibration training modules to truly achieve personalized emotion recognition."
---

# emoPAD Universe

## Cross-Platform Support

emoPAD Universe supports the following operating systems:

| OS | Image Viewer | Notes |
|---------|-----------|------|
| Linux | eog (Eye of GNOME) | Window mode, closable |
| Windows | System default image viewer | Window mode, closable |

## Auto-Start

After installing this skill, the following operations will be performed automatically:
1. Check and install required Python dependencies
2. Start emoPAD service (listening on http://127.0.0.1:8766)
3. Start emoNebula auto-report (popup window displaying emotion nebula chart every 5 minutes)

No manual start needed, ready to use after installation.

## Tools

### emopad_status

Get current emotion PAD status and sensor connection status

**Description**: Returns values for three dimensions: Pleasure, Arousal, Dominance, and connection status of EEG, PPG, GSR sensors

**Parameters**: None

**Returns**: Formatted emotion status text, including sensor connection status

---

### emopad_snapshot

Generate current emotion nebula chart

**Description**: Generate 3D PAD cube visualization screenshot

**Parameters**: None

**Returns**: 
- Status message
- PNG image data

---

### emopad_start_nebula

Start emoNebula auto-report

**Description**: Automatically generate and display emotion nebula chart in popup window every 5 minutes. Requires at least 2 sensors connected to display image, otherwise shows data missing reminder.

**Parameters**: None

**Returns**: Status message

---

### emopad_stop_nebula

Stop emoNebula auto-report

**Description**: Stop automatically displaying emotion nebula chart

**Parameters**: None

**Returns**: Status message

## Configuration

```yaml
serial_port: /dev/ttyACM0      # Serial device path (Linux)
# serial_port: COM3            # Serial device path (Windows)
baudrate: 115200               # Serial baudrate
eeg_window_sec: 2              # EEG data window (seconds)
ppg_gsr_window_sec: 60         # PPG/GSR data window (seconds)
hop_sec: 2                     # Calculation interval (seconds)
history_length: 120            # Number of historical data points
nebula_interval: 300           # Send interval (seconds)
service_host: 127.0.0.1        # Service listening address
service_port: 8766             # Service listening port
```

## Dependencies

- mne
- heartpy
- neurokit2
- bleak
- pyvista
- pyserial
- scipy
- numpy
- PyWavelets
- fastapi
- uvicorn
- pillow
- requests
- pyyaml

## Hardware Support

### Currently Supported Devices

| Type | Model | Connection |
|------|------|----------|
| EEG | KSEEG102 | Bluetooth BLE |
| PPG | Cheez PPG Sensor | Serial |
| GSR | Sichiray GSR V2 | Serial |

### Future Planned Support

- Muse series EEG devices
- Emotiv EEG devices
- Oura Ring smart ring
- Whoop smart wristband
- Other mainstream EEG devices and wearable devices

## About Emotion PAD Calculation

**Important Note**: Currently, emotion PAD calculation is based on heuristic methods, mapping relationships summarized from extensive literature.

Characteristics of this method:
- ✅ Based on statistical patterns from scientific literature
- ✅ Suitable for emotion recognition in general population
- ⚠️ Temporarily cannot reflect individual differences

**Future Improvements**: Will introduce personalized calibration training modules in new versions, through user-specific data training, to achieve true personalized emotion recognition.
