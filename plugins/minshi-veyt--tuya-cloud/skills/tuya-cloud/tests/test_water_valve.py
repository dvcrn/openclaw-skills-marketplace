#!/usr/bin/env python3
"""Test switching the left water valve of the greenhouse water valve device.
Uses device IDs from test_data.env.
Left valve is controlled via switch_1 (first channel).
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load private device IDs from test_data.env in the same folder
_TEST_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_TEST_DIR / "test_data.env")

WATER_VALVE_DEVICE_ID = os.environ["WATER_VALVE_DEVICE_ID"]
WATER_VALVE_GATEWAY_ID = os.environ["WATER_VALVE_GATEWAY_ID"]

# Add scripts directory to path
sys.path.insert(0, str(_TEST_DIR.parent / "scripts"))

from tuya_controller import load_tuya_client, get_device_status, send_device_commands

# Left water valve = first channel (switch_1)
LEFT_VALVE_DP = "switch_1"

def test_left_water_valve_on_off():
    """Switch the left water valve ON, then OFF."""
    print("=" * 50)
    print("Test: Left water valve ON/OFF")
    print("=" * 50)
    print(f"Device (water valve): {WATER_VALVE_DEVICE_ID}")
    print(f"Gateway:             {WATER_VALVE_GATEWAY_ID}")
    print(f"DP code (left valve): {LEFT_VALVE_DP}")
    print()

    client = load_tuya_client()
    print("✅ API client connected")
    print()

    # Optional: show current state before changing
    try:
        status = get_device_status(client, WATER_VALVE_DEVICE_ID)
        print("Current device status (before):", status)
        print()
    except Exception as e:
        print("⚠️  Could not read current status:", e)
        print()

    # Turn left valve ON
    print("Sending: left water valve ON...")
    try:
        send_device_commands(
            client,
            WATER_VALVE_DEVICE_ID,
            [{"code": LEFT_VALVE_DP, "value": True}],
        )
        print("✅ Left water valve ON command sent")
    except Exception as e:
        print(f"❌ Failed to turn ON: {e}")
        return False

    time.sleep(2)

    # Turn left valve OFF
    print("Sending: left water valve OFF...")
    try:
        send_device_commands(
            client,
            WATER_VALVE_DEVICE_ID,
            [{"code": LEFT_VALVE_DP, "value": False}],
        )
        print("✅ Left water valve OFF command sent")
    except Exception as e:
        print(f"❌ Failed to turn OFF: {e}")
        return False

    print()
    print("=" * 50)
    print("✅ Test completed: left water valve ON then OFF")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_left_water_valve_on_off()
    sys.exit(0 if success else 1)
