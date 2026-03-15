#!/usr/bin/env python3
"""
Ezviz Device Configuration Script
萤石设备配置脚本 - 支持 11 个配置 API

根据文档 ID: 701,702,703,706,707,712,713,714,715,722,723
"""

import os
import sys
import json
from datetime import datetime

import requests

# ============================================================================
# Configuration
# ============================================================================

# API endpoints (verified against Ezviz Open Platform docs)
CONFIG_APIS = {
    # 701: 设置布撤防
    "defence_set": {
        "url": "/api/lapp/device/defence/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "isDefence"]
    },
    # 702: 获取布撤防时间计划
    "defence_plan_get": {
        "url": "/api/lapp/device/defence/plan/get",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo"]
    },
    # 703: 设置布撤防计划
    "defence_plan_set": {
        "url": "/api/lapp/device/defence/plan/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "startTime", "stopTime", "period", "enable"]
    },
    # 706: 获取镜头遮蔽开关状态 (使用 scene/switch API)
    "shelter_get": {
        "url": "/api/lapp/device/scene/switch/status",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 707: 设置镜头遮蔽开关 (使用 scene/switch API)
    "shelter_set": {
        "url": "/api/lapp/device/scene/switch/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo", "enable"]
    },
    # 712: 获取全天录像开关状态
    "fullday_record_get": {
        "url": "/api/lapp/device/fullday/record/switch/status",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 713: 设置全天录像开关状态
    "fullday_record_set": {
        "url": "/api/lapp/device/fullday/record/switch/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "enable"]
    },
    # 714: 获取移动侦测灵敏度配置 (使用 algorithm/config API)
    "motion_detect_sensitivity_get": {
        "url": "/api/lapp/device/algorithm/config/get",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 715: 设置移动侦测灵敏度 (使用 algorithm/config API)
    "motion_detect_sensitivity_set": {
        "url": "/api/lapp/device/algorithm/config/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo", "type", "value"]
    },
    # Note: motion_track (722/723) removed - device capability not widely supported
}

# Environment variables
APP_KEY = os.getenv("EZVIZ_APP_KEY", "")
APP_SECRET = os.getenv("EZVIZ_APP_SECRET", "")
DEVICE_SERIAL = os.getenv("EZVIZ_DEVICE_SERIAL", "")
CHANNEL_NO = os.getenv("EZVIZ_CHANNEL_NO", "1")

# ============================================================================
# Helper Functions
# ============================================================================

def get_access_token(app_key, app_secret):
    """Get access token from Ezviz Open Platform."""
    url = "https://open.ys7.com/api/lapp/token/get"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "appKey": app_key,
        "appSecret": app_secret
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            token_data = result.get("data", {})
            access_token = token_data.get("accessToken")
            expire_time = token_data.get("expireTime")
            return {
                "success": True,
                "token": access_token,
                "expire_time": expire_time
            }
        else:
            return {
                "success": False,
                "error": result.get("msg", "Failed to get token"),
                "code": result.get("code")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def execute_config(access_token, device_serial, config_type, value=None, extra_params=None):
    """
    Execute device configuration.
    
    Args:
        access_token: Ezviz access token
        device_serial: Device serial number
        config_type: Configuration type (defence_set, shelter_get, etc.)
        value: Configuration value (for set actions: isDefence, enable, sensitivity)
        extra_params: Additional parameters (for defence_plan_set: startTime, stopTime, period)
    
    Returns:
        dict: Configuration result
    """
    if config_type not in CONFIG_APIS:
        return {
            "success": False,
            "error": f"Unknown config type: {config_type}",
            "available_types": list(CONFIG_APIS.keys())
        }
    
    api_info = CONFIG_APIS[config_type]
    api_url = f"https://open.ys7.com{api_info['url']}"
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper()
    }
    
    # Add channelNo for APIs that support it
    if "channelNo" in api_info["params"]:
        data["channelNo"] = "1"  # Default channel
    
    # Add action-specific parameters based on API docs
    if value is not None:
        if config_type == "defence_set":
            # 701: isDefence - 0:睡眠，8:在家，16:外出 (普通 IPC: 0-撤防，1-布防)
            data["isDefence"] = str(value)
        elif config_type == "shelter_set":
            # 707: enable - 0:关闭，1:开启 (镜头遮蔽)
            data["enable"] = str(value)
            data["channelNo"] = "1"
        elif config_type == "fullday_record_set":
            # 713: enable - 0:关闭，1:开启
            data["enable"] = str(value)
        elif config_type == "motion_detect_sensitivity_set":
            # 715: type=0 (移动侦测), value=0-6 (0 最低灵敏度)
            data["type"] = "0"
            data["value"] = str(value)
            data["channelNo"] = "1"
        elif config_type == "defence_plan_set":
            # 703: Multiple parameters needed
            if extra_params:
                data["startTime"] = extra_params.get("startTime", "00:00")
                data["stopTime"] = extra_params.get("stopTime", "00:00")
                data["period"] = extra_params.get("period", "0,1,2,3,4,5,6")
                data["enable"] = str(extra_params.get("enable", 1))
            else:
                # Default values
                data["startTime"] = "00:00"
                data["stopTime"] = "00:00"
                data["period"] = "0,1,2,3,4,5,6"
                data["enable"] = "1"
    
    print(f"[INFO] Calling API: {api_url}")
    print(f"[INFO] Device: {device_serial}, Type: {config_type}")
    if value:
        print(f"[INFO] Value: {value}")
    
    try:
        response = requests.post(api_url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            print(f"[SUCCESS] Config executed successfully!")
            return {
                "success": True,
                "data": result.get("data", {}),
                "message": result.get("msg", "Success")
            }
        else:
            error_msg = result.get("msg", "Config failed")
            print(f"[ERROR] Config failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "code": result.get("code")
            }
    
    except Exception as e:
        print(f"[ERROR] Config failed: {type(e).__name__}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    print("=" * 70)
    print("Ezviz Device Config (萤石设备配置)")
    print("=" * 70)
    print(f"[Time] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    app_key = APP_KEY or sys.argv[1] if len(sys.argv) > 1 else ""
    app_secret = APP_SECRET or sys.argv[2] if len(sys.argv) > 2 else ""
    device_serial = DEVICE_SERIAL or sys.argv[3] if len(sys.argv) > 3 else ""
    config_type = sys.argv[4] if len(sys.argv) > 4 else "defence_set"
    value = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Validate
    if not app_key or not app_secret:
        print("[ERROR] APP_KEY and APP_SECRET required.")
        print("[INFO] Set EZVIZ_APP_KEY and EZVIZ_APP_SECRET env vars.")
        sys.exit(1)
    
    if not device_serial:
        print("[ERROR] DEVICE_SERIAL required.")
        print("[INFO] Set EZVIZ_DEVICE_SERIAL env var.")
        sys.exit(1)
    
    print(f"[INFO] Device: {device_serial}")
    print(f"[INFO] Config Type: {config_type}")
    if value:
        print(f"[INFO] Value: {value}")
    
    # Parse extra_params for defence_plan_set
    extra_params = None
    if config_type == "defence_plan_set" and value:
        try:
            # Try to parse as JSON
            extra_params = json.loads(value)
            print(f"[INFO] Parsed extra_params: {extra_params}")
        except json.JSONDecodeError:
            print("[WARN] Failed to parse value as JSON, using as-is")
    
    # Step 1: Get access token
    print("\n" + "=" * 70)
    print("[Step 1] Getting access token...")
    print("=" * 70)
    
    token_result = get_access_token(app_key, app_secret)
    
    if not token_result["success"]:
        print(f"[ERROR] Failed to get token: {token_result.get('error')}")
        sys.exit(1)
    
    access_token = token_result["token"]
    expire_time = token_result["expire_time"]
    print(f"[SUCCESS] Token obtained, expires: {expire_time}")
    
    # Step 2: Execute config
    print("\n" + "=" * 70)
    print("[Step 2] Executing config...")
    print("=" * 70)
    
    config_result = execute_config(
        access_token, device_serial, config_type, value, extra_params
    )
    
    # Output result
    print("\n" + "=" * 70)
    print("CONFIG RESULT")
    print("=" * 70)
    
    if config_result["success"]:
        print(f"  Device:     {device_serial}")
        print(f"  Type:       {config_type}")
        print(f"  Value:      {value}")
        print(f"  Status:     success")
        if config_result.get("data"):
            print(f"  Data:       {json.dumps(config_result['data'], ensure_ascii=False)}")
    else:
        print(f"  Device:     {device_serial}")
        print(f"  Type:       {config_type}")
        print(f"  Status:     failed")
        print(f"  Error:      {config_result.get('error')}")
        if config_result.get("code"):
            print(f"  Code:       {config_result['code']}")
    
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if config_result["success"] else 1)

if __name__ == "__main__":
    main()
