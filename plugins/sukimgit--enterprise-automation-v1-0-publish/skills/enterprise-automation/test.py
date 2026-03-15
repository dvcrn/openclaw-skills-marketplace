# Test script for enterprise-automation
print("Testing enterprise-automation modules...")
print()

# Test 1: Import modules
print("[TEST 1] Importing modules...")
try:
    from modules.file_search import search_files
    from modules.email_send import send_email
    from modules.feishu_notify import send_feishu_message
    print("[OK] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    exit(1)

print()

# Test 2: Check config template
print("[TEST 2] Checking config template...")
import json
from pathlib import Path

config_path = Path("config.example.json")
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check for placeholders
    if "YOUR_" in json.dumps(config):
        print("[OK] Config template uses placeholders")
    else:
        print("[FAIL] Config template should use placeholders (YOUR_*)")
        exit(1)
else:
    print("[FAIL] config.example.json not found")
    exit(1)

print()

# Test 3: Privacy check
print("[TEST 3] Running privacy check...")
import subprocess
result = subprocess.run(["python", "check_privacy.py", "."], capture_output=True, text=True)
if result.returncode == 0:
    print("[OK] Privacy check passed")
else:
    print("[FAIL] Privacy check failed")
    print(result.stdout)
    print(result.stderr)
    exit(1)

print()
print("=" * 60)
print("All tests passed! Ready for deployment.")
print("=" * 60)
