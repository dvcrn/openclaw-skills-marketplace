#!/usr/bin/env python3
"""
Preflight Check Module for Web3 Investor

Purpose: Check execution readiness before attempting transactions.
Returns available payment methods and recommendations.

Usage:
    python preflight.py check
    python preflight.py check --network base
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from enum import Enum

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "..", "config", "config.json")

class PaymentMethod(Enum):
    """Available payment methods."""
    KEYSTORE_SIGNER = "keystore_signer"
    EIP681_PAYMENT_LINK = "eip681_payment_link"
    NONE = "none"


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load config: {e}", file=sys.stderr)
        return {}


# ============================================================================
# Signer API Check
# ============================================================================

def check_signer_api(network: str = "base", timeout: int = 5) -> Dict[str, Any]:
    """
    Check if local signer API is available.
    
    Returns:
        Dict with status, message, and details
    """
    config = load_config()
    api_config = config.get("api", {})
    base_url = api_config.get("url", "http://localhost:3000/api")
    api_timeout = api_config.get("timeout_seconds", timeout)
    
    # Try to reach the balances endpoint
    url = f"{base_url}/wallet/balances?chain={network}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Web3-Investor-Preflight/0.5.0"},
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=api_timeout) as response:
            data = json.loads(response.read().decode())
            
            if data.get("success"):
                return {
                    "available": True,
                    "status": "online",
                    "message": "Signer API is available",
                    "url": base_url,
                    "network": network
                }
            else:
                return {
                    "available": False,
                    "status": "error",
                    "message": f"Signer API returned error: {data.get('error', 'Unknown')}",
                    "url": base_url
                }
                
    except urllib.error.URLError as e:
        return {
            "available": False,
            "status": "offline",
            "message": f"Signer API unreachable: {e.reason}",
            "url": base_url
        }
    except Exception as e:
        return {
            "available": False,
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "url": base_url
        }


# ============================================================================
# Execution Readiness Check
# ============================================================================

def check_execution_readiness(network: str = "base") -> Dict[str, Any]:
    """
    Check what payment methods are available for transaction execution.
    
    This function should be called BEFORE asking user for transaction details.
    
    Args:
        network: Network to check (default: base)
    
    Returns:
        Dict with recommended payment method and details
    """
    result = {
        "network": network,
        "methods": [],
        "recommended": None,
        "message": ""
    }
    
    # 1. Check local signer API
    signer_status = check_signer_api(network)
    
    if signer_status["available"]:
        result["methods"].append({
            "method": PaymentMethod.KEYSTORE_SIGNER.value,
            "status": "available",
            "description": "Local keystore signer (preview → approve → execute)",
            "details": signer_status
        })
        result["recommended"] = PaymentMethod.KEYSTORE_SIGNER.value
        result["message"] = "✅ Local signer available. Use preview → approve → execute flow."
    else:
        result["methods"].append({
            "method": PaymentMethod.KEYSTORE_SIGNER.value,
            "status": "unavailable",
            "description": "Local keystore signer",
            "details": signer_status
        })
        
        # 2. Fallback to EIP-681
        result["methods"].append({
            "method": PaymentMethod.EIP681_PAYMENT_LINK.value,
            "status": "available",
            "description": "EIP-681 payment link (MetaMask mobile)",
            "details": {
                "supported_wallets": ["MetaMask", "Rainbow", "Trust Wallet"],
                "requires": "Mobile wallet with USDT on the target chain"
            }
        })
        result["recommended"] = PaymentMethod.EIP681_PAYMENT_LINK.value
        result["message"] = "⚠️ No local signer. Use EIP-681 payment link for mobile wallet payment."
    
    return result


def format_readiness_report(readiness: Dict[str, Any]) -> str:
    """Format execution readiness as human-readable report."""
    lines = [
        "=" * 60,
        "🔍 Execution Readiness Check",
        "=" * 60,
        "",
        f"Network: {readiness['network'].upper()}",
        f"Recommended: {readiness['recommended']}",
        "",
        "Available Payment Methods:",
        "-" * 40,
    ]
    
    for method in readiness["methods"]:
        status_icon = "✅" if method["status"] == "available" else "❌"
        lines.append(f"  {status_icon} {method['method']}: {method['status']}")
        lines.append(f"      {method['description']}")
    
    lines.extend([
        "",
        "-" * 60,
        readiness["message"],
        ""
    ])
    
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Preflight check for Web3 Investor execution readiness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python preflight.py check
    python preflight.py check --network ethereum
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check execution readiness")
    check_parser.add_argument("--network", default="base", help="Network to check")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.command == "check":
        readiness = check_execution_readiness(args.network)
        
        if args.json:
            # Convert Enum to string for JSON serialization
            output = {
                "network": readiness["network"],
                "methods": readiness["methods"],
                "recommended": readiness["recommended"],
                "message": readiness["message"]
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_readiness_report(readiness))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()