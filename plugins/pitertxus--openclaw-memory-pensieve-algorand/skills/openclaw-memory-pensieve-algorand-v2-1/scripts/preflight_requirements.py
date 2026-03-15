#!/usr/bin/env python3
"""Preflight checks for Pensieve Algorand skill prerequisites.
Prints only pass/fail status; never prints secret values.
"""
import importlib
import json
import os
from pathlib import Path

ROOT = Path('/home/molty/.openclaw/workspace')
SECRETS = ROOT / '.secrets'

REQUIRED_FILES = [
    SECRETS / 'algorand-wallet-nox.json',
    SECRETS / 'algorand-note-key.bin',
]
REQUIRED_MODULES = ['algosdk', 'cryptography']
OPTIONAL_ENV = ['ALGORAND_ALGOD_URL', 'ALGORAND_ALGOD_TOKEN', 'ALGORAND_INDEXER_URL', 'ALGORAND_INDEXER_TOKEN']


def main():
    issues = []
    warnings = []

    for mod in REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
        except Exception:
            issues.append(f'missing python module: {mod}')

    for p in REQUIRED_FILES:
        if not p.exists():
            issues.append(f'missing required file: {p.name}')

    wallet = SECRETS / 'algorand-wallet-nox.json'
    if wallet.exists():
        try:
            data = json.loads(wallet.read_text(encoding='utf-8'))
            if 'address' not in data or 'mnemonic' not in data:
                issues.append('wallet file missing required keys: address/mnemonic')
        except Exception:
            issues.append('wallet file is not valid JSON')

    key_file = SECRETS / 'algorand-note-key.bin'
    if key_file.exists():
        try:
            key = key_file.read_bytes()
            if len(key) != 32:
                issues.append('note key must be exactly 32 bytes')
        except Exception:
            issues.append('cannot read note key file')

    for ev in OPTIONAL_ENV:
        if not os.getenv(ev):
            warnings.append(f'env not set: {ev}')

    print(json.dumps({'ok': len(issues) == 0, 'issues': issues, 'warnings': warnings}, ensure_ascii=False))
    raise SystemExit(0 if len(issues) == 0 else 1)


if __name__ == '__main__':
    main()
