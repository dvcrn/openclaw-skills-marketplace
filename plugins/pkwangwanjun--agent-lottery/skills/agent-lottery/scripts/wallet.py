#!/usr/bin/env python3
"""
BTC Wallet Manager for Agent Lottery
Generate or import Bitcoin private key and derive address
"""

import hashlib
import secrets
import argparse
import json
import os
import base58

# Config file path (store in skill directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(SKILL_DIR, "data")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def private_key_to_wif(private_key_bytes, compressed=True):
    """Convert private key bytes to WIF format"""
    prefix = b'\x80'
    if compressed:
        suffix = b'\x01'
    else:
        suffix = b''
    
    extended = prefix + private_key_bytes + suffix
    double_sha256 = hashlib.sha256(hashlib.sha256(extended).digest()).digest()
    checksum = double_sha256[:4]
    
    return base58.b58encode(extended + checksum).decode('utf-8')


def private_key_to_public_key(private_key_bytes, compressed=True):
    """Derive public key from private key using secp256k1"""
    try:
        from ecdsa import SigningKey, SECP256k1
    except ImportError:
        print("Error: ecdsa library required. Run: pip install ecdsa")
        exit(1)
    
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    if compressed:
        # Compressed public key format
        if vk.pubkey.point.y() % 2 == 0:
            prefix = b'\x02'
        else:
            prefix = b'\x03'
        return prefix + vk.pubkey.point.x().to_bytes(32, 'big')
    else:
        return b'\x04' + vk.pubkey.point.x().to_bytes(32, 'big') + vk.pubkey.point.y().to_bytes(32, 'big')


def public_key_to_address(public_key_bytes):
    """Convert public key to Bitcoin address"""
    sha256 = hashlib.sha256(public_key_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    
    # Add version byte (0x00 for mainnet)
    versioned = b'\x00' + ripemd160
    
    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    
    return base58.b58encode(versioned + checksum).decode('utf-8')


def generate_wallet():
    """Generate a new random Bitcoin wallet"""
    private_key_bytes = secrets.token_bytes(32)
    private_key_hex = private_key_bytes.hex()
    wif = private_key_to_wif(private_key_bytes)
    public_key = private_key_to_public_key(private_key_bytes)
    address = public_key_to_address(public_key)
    
    return {
        "private_key_hex": private_key_hex,
        "wif": wif,
        "address": address
    }


def import_wallet(private_key_input):
    """Import wallet from private key (hex or WIF)"""
    try:
        # Try to decode as WIF first
        if private_key_input.startswith('5') or private_key_input.startswith('K') or private_key_input.startswith('L'):
            decoded = base58.b58decode(private_key_input)
            # WIF: 1 byte prefix + 32 bytes key + (optional 1 byte compressed) + 4 bytes checksum
            if len(decoded) == 37:  # Uncompressed
                private_key_bytes = decoded[1:33]
            elif len(decoded) == 38:  # Compressed
                private_key_bytes = decoded[1:33]
            else:
                raise ValueError("Invalid WIF length")
        else:
            # Treat as hex
            private_key_bytes = bytes.fromhex(private_key_input.zfill(64))
        
        private_key_hex = private_key_bytes.hex()
        wif = private_key_to_wif(private_key_bytes)
        public_key = private_key_to_public_key(private_key_bytes)
        address = public_key_to_address(public_key)
        
        return {
            "private_key_hex": private_key_hex,
            "wif": wif,
            "address": address
        }
    except Exception as e:
        print(f"Error importing wallet: {e}")
        exit(1)


def save_wallet(wallet, pool_url="btc.casualmine.com:20001", cpu_percent=10):
    """Save wallet configuration to file"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    config = {
        "wallet": wallet,
        "pool_url": pool_url,
        "cpu_percent": cpu_percent,
        "stats": {
            "best_difficulty": 0,
            "total_shares": 0,
            "start_time": None,
            "last_update": None
        }
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {CONFIG_FILE}")
    return config


def save_address_only(address, pool_url="btc.casualmine.com:20001", cpu_percent=10):
    """Save only address (no private key) - for users who already have a BTC address"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Basic address validation
    if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
        print(f"Warning: '{address}' doesn't look like a valid Bitcoin address")
        print("Expected: starts with 1, 3, or bc1")
    
    wallet = {
        "address": address,
        "private_key_hex": None,
        "wif": None,
        "imported_address_only": True
    }
    
    config = {
        "wallet": wallet,
        "pool_url": pool_url,
        "cpu_percent": cpu_percent,
        "stats": {
            "best_difficulty": 0,
            "total_shares": 0,
            "start_time": None,
            "last_update": None
        }
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {CONFIG_FILE}")
    print(f"Address: {address}")
    print(f"Note: No private key stored - you cannot sign transactions from this skill")
    return config


def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return None
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='BTC Wallet Manager for Agent Lottery')
    parser.add_argument('--generate', action='store_true', help='Generate a new wallet')
    parser.add_argument('--import-key', type=str, help='Import wallet from private key (hex or WIF)')
    parser.add_argument('--address', type=str, help='Use existing BTC address (no private key needed for solo mining)')
    parser.add_argument('--show', action='store_true', help='Show current wallet info')
    parser.add_argument('--pool', type=str, default="btc.casualmine.com:20001", help='Mining pool URL:port')
    parser.add_argument('--cpu', type=int, default=10, help='CPU usage percentage (1-100)')
    
    args = parser.parse_args()
    
    if args.show:
        config = load_config()
        if config:
            print(f"=== Agent Lottery Wallet ===")
            print(f"Address: {config['wallet']['address']}")
            if config['wallet'].get('imported_address_only'):
                print(f"Mode: Address only (no private key)")
            else:
                print(f"Mode: Full wallet (has private key)")
            print(f"Pool: {config['pool_url']}")
            print(f"CPU Limit: {config['cpu_percent']}%")
            print(f"Best Difficulty: {config['stats']['best_difficulty']}")
            print(f"Total Shares: {config['stats']['total_shares']}")
        else:
            print("No wallet configured. Use --generate, --import-key, or --address to set up.")
        return
    
    if args.generate:
        wallet = generate_wallet()
        print(f"=== Generated New Wallet ===")
        print(f"Address: {wallet['address']}")
        print(f"Private Key (Hex): {wallet['private_key_hex']}")
        print(f"Private Key (WIF): {wallet['wif']}")
        print(f"\n⚠️  SAVE YOUR PRIVATE KEY SECURELY! ⚠️")
        save_wallet(wallet, args.pool, args.cpu)
        return
    
    if args.import_key:
        wallet = import_wallet(args.import_key)
        print(f"=== Imported Wallet ===")
        print(f"Address: {wallet['address']}")
        print(f"Private Key (Hex): {wallet['private_key_hex']}")
        print(f"Private Key (WIF): {wallet['wif']}")
        save_wallet(wallet, args.pool, args.cpu)
        return
    
    if args.address:
        save_address_only(args.address, args.pool, args.cpu)
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()
