#!/usr/bin/env python3
"""
EIP-681 Payment Link Generator (v0.3.3)

Generate EIP-681 compliant payment links and QR codes for MetaMask.

EIP-681 Format:
    ethereum:<to>@<chainId>/transfer?address=<recipient>&uint256=<amount>

Usage:
    python3 eip681_payment.py generate \
      --token USDC \
      --to 0x1F3A9A450428BbF161C4C33f10bd7AA1b2599a3e \
      --amount 10 \
      --network base
    
    # With QR code (for desktop users)
    python3 eip681_payment.py generate \
      --token USDC \
      --to 0x... \
      --amount 10 \
      --network base \
      --qr-output /tmp/payment_qr.png
"""

import argparse
import json
import os
import sys
import subprocess
from typing import Optional, Dict, Any

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# Token addresses by chain
TOKEN_ADDRESSES = {
    "base": {
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "USDT": "0xfde4C96c8593536E11F39842a902aB0E47ec4E54",
        "WETH": "0x4200000000000000000000000000000000000006",
        "ETH": "0x0000000000000000000000000000000000000000",  # Native
    },
    "ethereum": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2",
        "ETH": "0x0000000000000000000000000000000000000000",  # Native
    }
}

# Chain IDs
CHAIN_IDS = {
    "base": 8453,
    "ethereum": 1,
}

# Token decimals
TOKEN_DECIMALS = {
    "USDC": 6,
    "USDT": 6,
    "WETH": 18,
    "ETH": 18,
}

# QR Code options
QR_SKILL_PATH = os.path.expanduser("~/.openclaw/workspace/skills/qrcode-gen-yn/agent.py")
# Try npm qrcode as fallback


# ============================================================================
# EIP-681 Link Generation
# ============================================================================

def generate_eip681_link(
    token: str,
    to: str,
    amount: float,
    network: str = "base"
) -> Dict[str, Any]:
    """
    Generate EIP-681 compliant payment link.
    
    Args:
        token: Token symbol (USDC, USDT, WETH, ETH)
        to: Recipient address
        amount: Amount to send (human readable, e.g., 10.5)
        network: Network name (base, ethereum)
    
    Returns:
        Dict with link, calldata, and transaction details
    """
    # Validate inputs
    if network not in CHAIN_IDS:
        return {
            "success": False,
            "error": f"Unsupported network: {network}. Supported: {list(CHAIN_IDS.keys())}"
        }
    
    if token.upper() not in TOKEN_ADDRESSES.get(network, {}):
        return {
            "success": False,
            "error": f"Unsupported token: {token} on {network}. Supported: {list(TOKEN_ADDRESSES.get(network, {}).keys())}"
        }
    
    token = token.upper()
    chain_id = CHAIN_IDS[network]
    token_address = TOKEN_ADDRESSES[network][token]
    decimals = TOKEN_DECIMALS.get(token, 18)
    
    # Convert amount to smallest unit
    amount_smallest = int(amount * (10 ** decimals))
    
    # Check if native token (ETH)
    is_native = token == "ETH"
    
    if is_native:
        # Native ETH transfer - simpler format
        link = f"ethereum:{to}@{chain_id}?value={amount_smallest}"
        calldata = None
    else:
        # ERC20 transfer
        # Transfer function: 0xa9059cbb(to, amount)
        to_padded = to[2:].lower().zfill(64)
        amount_hex = hex(amount_smallest)[2:].zfill(64)
        calldata = f"0xa9059cbb{to_padded}{amount_hex}"
        
        # EIP-681 format for ERC20
        link = f"ethereum:{token_address}@{chain_id}/transfer?address={to}&uint256={amount_smallest}"
    
    # MetaMask deep link
    metamask_link = f"https://metamask.app.link/send/{token_address}@{chain_id}/transfer?address={to}&uint256={amount_smallest}"
    
    return {
        "success": True,
        "network": network,
        "chain_id": chain_id,
        "token": token,
        "token_address": token_address,
        "recipient": to,
        "amount": amount,
        "amount_smallest": amount_smallest,
        "calldata": calldata,
        "eip681_link": link,
        "metamask_link": metamask_link,
        "transaction": {
            "to": token_address if not is_native else to,
            "value": f"0x{hex(amount_smallest)[2:]}" if is_native else "0x0",
            "data": calldata if calldata else "0x",
            "chain_id": chain_id
        }
    }


def generate_qr_code(link: str, output_path: str) -> Dict[str, Any]:
    """
    Generate QR code for payment link.
    
    Tries multiple methods in order:
    1. npm qrcode (if available)
    2. Python qrcode-gen-yn skill (if installed)
    
    Args:
        link: EIP-681 link or MetaMask link
        output_path: Path to save QR code PNG
    
    Returns:
        Dict with success status and path (or error with fallback)
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Method 1: Try npm qrcode (preferred, faster)
    try:
        result = subprocess.run(
            ["npx", "qrcode", "-t", "png", "-o", output_path, link],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            return {
                "success": True,
                "qr_path": output_path,
                "method": "npm-qrcode",
                "link": link
            }
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        pass
    except Exception:
        pass
    
    # Method 2: Try Python qrcode-gen-yn skill
    if os.path.exists(QR_SKILL_PATH):
        try:
            result = subprocess.run(
                ["python3", QR_SKILL_PATH, link, output_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "qr_path": output_path,
                    "method": "python-skill",
                    "link": link
                }
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
    
    # All methods failed - return fallback
    return {
        "success": False,
        "error": "QR code generation unavailable",
        "fallback": "Please display the link directly for mobile users",
        "link": link
    }


def format_output(result: Dict, include_qr: bool = False, qr_path: str = None) -> str:
    """Format result for display."""
    if not result.get("success"):
        return f"❌ Error: {result.get('error', 'Unknown error')}"
    
    lines = [
        "=" * 60,
        "EIP-681 Payment Link Generated",
        "=" * 60,
        "",
        f"Network: {result['network'].upper()} (Chain ID: {result['chain_id']})",
        f"Token: {result['token']} ({result['token_address']})",
        f"Recipient: {result['recipient']}",
        f"Amount: {result['amount']} {result['token']}",
        "",
        "-" * 60,
        "For Mobile Users (MetaMask)",
        "-" * 60,
        f"Click this link: {result['metamask_link']}",
        "",
        "-" * 60,
        "For Desktop Users",
        "-" * 60,
        "Scan QR code with MetaMask mobile app,",
        "or manually copy the transaction details below.",
        "",
        "Transaction Details:",
        f"  To: {result['transaction']['to']}",
        f"  Value: {result['transaction']['value']}",
        f"  Data: {result['calldata'][:30]}..." if result.get('calldata') else "  Data: (none - native transfer)",
        "",
        "-" * 60,
        "Raw EIP-681 Link",
        "-" * 60,
        result['eip681_link'],
    ]
    
    if include_qr and qr_path:
        lines.extend([
            "",
            "-" * 60,
            "QR Code",
            "-" * 60,
            f"Generated at: {qr_path}",
        ])
    
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="EIP-681 Payment Link Generator (v0.3.3)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate EIP-681 payment link")
    gen_parser.add_argument("--token", required=True, help="Token symbol (USDC, USDT, WETH, ETH)")
    gen_parser.add_argument("--to", required=True, help="Recipient address")
    gen_parser.add_argument("--amount", type=float, required=True, help="Amount to send")
    gen_parser.add_argument("--network", default="base", choices=["base", "ethereum"], help="Network")
    gen_parser.add_argument("--qr-output", help="Path to save QR code PNG (optional)")
    gen_parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        # Generate EIP-681 link
        result = generate_eip681_link(
            token=args.token,
            to=args.to,
            amount=args.amount,
            network=args.network
        )
        
        # Generate QR code if requested
        if args.qr_output and result.get("success"):
            qr_result = generate_qr_code(result['metamask_link'], args.qr_output)
            result["qr"] = qr_result
        
        # Output
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result, include_qr=bool(args.qr_output), qr_path=args.qr_output))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()