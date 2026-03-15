#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Algorand anchor v2: Full on-chain memory backup.
Stores complete event content (semantic/procedural/self_model) encrypted in blockchain notes.
Uses multi-tx for large payloads (>992 bytes usable per tx).
"""
import base64
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from algosdk import account, mnemonic
from algosdk.transaction import PaymentTxn
from algosdk.v2client import algod
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MEM_ROOT = Path('/home/molty/.openclaw/workspace/memory')
LEDGER = MEM_ROOT / 'ledger.jsonl'
ANCHORS = MEM_ROOT / 'onchain-anchors.jsonl'
WALLET = Path('/home/molty/.openclaw/workspace/.secrets/algorand-wallet-nox.json')
NOTE_KEY = Path('/home/molty/.openclaw/workspace/.secrets/algorand-note-key.bin')
ALGOD_URL = os.getenv('ALGORAND_ALGOD_URL', 'https://mainnet-api.algonode.cloud')
ALGOD_TOKEN = os.getenv('ALGORAND_ALGOD_TOKEN', '')

MAX_NOTE_SIZE = 1024
OVERHEAD = 32  # NXP1(4) + nonce(12) + auth_tag(16)
USABLE_PER_TX = MAX_NOTE_SIZE - OVERHEAD  # 992 bytes


def read_ledger_tip_and_count(path: Path):
    """Read last ledger hash and total entry count."""
    if not path.exists() or path.stat().st_size == 0:
        return 'GENESIS', 0
    count = 0
    last = None
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            count += 1
            last = line
    if not last:
        return 'GENESIS', 0
    return json.loads(last)['chain_hash'], count


def read_layer_events_for_date(layer_path: Path, date_key: str) -> list:
    """Read all events from a layer file (semantic/procedural/self_model) for a specific date."""
    if not layer_path.exists() or layer_path.stat().st_size == 0:
        return []
    events = []
    with layer_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                # Match entries created on the target date
                if entry.get('ts', '').startswith(date_key):
                    events.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
    return events


def already_anchored(date_key: str, ledger_tip: str) -> bool:
    """Check if this date+ledger_tip combination is already anchored."""
    if not ANCHORS.exists() or ANCHORS.stat().st_size == 0:
        return False
    with ANCHORS.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('date') == date_key and row.get('ledger_tip') == ledger_tip:
                return True
    return False


def append_anchor(row: dict):
    """Append anchor record to onchain-anchors.jsonl."""
    with ANCHORS.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def encrypt_note(payload: bytes, key: bytes) -> bytes:
    """Encrypt payload with AES-GCM and prepend NXP1 header."""
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, payload, None)
    return b'NXP2' + nonce + ciphertext  # v2 = full content


def send_tx(client, sender, sk, note: bytes, sp) -> str:
    """Send 0-ALGO self-transfer with encrypted note."""
    txn = PaymentTxn(sender=sender, sp=sp, receiver=sender, amt=0, note=note)
    stx = txn.sign(sk)
    return client.send_transaction(stx)


def main():
    MEM_ROOT.mkdir(parents=True, exist_ok=True)
    if not ANCHORS.exists():
        ANCHORS.touch()

    ledger_tip, entries = read_ledger_tip_and_count(LEDGER)
    now = datetime.now()
    date_key = now.date().isoformat()

    # Read full content of promoted events for this date
    semantic = read_layer_events_for_date(MEM_ROOT / 'semantic.jsonl', date_key)
    procedural = read_layer_events_for_date(MEM_ROOT / 'procedural.jsonl', date_key)
    self_model = read_layer_events_for_date(MEM_ROOT / 'self_model.jsonl', date_key)
    
    # ALSO read raw events layer for complete recovery
    events_raw = read_layer_events_for_date(MEM_ROOT / 'events.jsonl', date_key)

    semantic_count = len(semantic)
    procedural_count = len(procedural)
    self_model_count = len(self_model)
    events_count = len(events_raw)

    # Check if already anchored
    if already_anchored(date_key, ledger_tip):
        print(json.dumps({
            'ok': True,
            'status': 'noop_already_anchored',
            'date': date_key,
            'ledger_tip': ledger_tip,
            'entries': entries,
            'events': events_count,
            'semantic': semantic_count,
            'procedural': procedural_count,
            'self_model': self_model_count
        }))
        return

    # Load wallet
    if not WALLET.exists() or not NOTE_KEY.exists():
        raise SystemExit('Missing wallet or note key in .secrets')

    wallet = json.loads(WALLET.read_text(encoding='utf-8'))
    addr = wallet['address']
    sk = mnemonic.to_private_key(wallet['mnemonic'])
    if account.address_from_private_key(sk) != addr:
        raise SystemExit('Wallet mismatch: mnemonic/address invalid')

    note_key = NOTE_KEY.read_bytes()
    if len(note_key) != 32:
        raise SystemExit('Invalid note key length (must be 32 bytes)')

    # Build full content payload (raw events + consolidated layers)
    content = {
        'events': events_raw,
        'semantic': semantic,
        'procedural': procedural,
        'self_model': self_model
    }
    content_json = json.dumps(content, separators=(',', ':'), ensure_ascii=False)
    content_bytes = content_json.encode('utf-8')
    content_hash = hashlib.sha256(content_bytes).hexdigest()

    # Base metadata
    base_meta = {
        'v': 2,
        'mode': 'daily-consolidation',
        'date': date_key,
        'ledger_tip': ledger_tip,
        'entries': entries,
        'events_count': events_count,
        'semantic_count': semantic_count,
        'procedural_count': procedural_count,
        'self_model_count': self_model_count,
        'root_hash': hashlib.sha256(f'{date_key}:{ledger_tip}:{entries}'.encode('utf-8')).hexdigest(),
        'content_hash': content_hash,
    }

    # Check if single-tx or multi-tx needed
    test_payload = base_meta.copy()
    test_payload['multi_tx'] = False
    test_payload['content'] = content
    test_payload_bytes = json.dumps(test_payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

    client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)
    sp = client.suggested_params()

    if len(test_payload_bytes) <= USABLE_PER_TX:
        # SINGLE TX: everything fits
        encrypted_note = encrypt_note(test_payload_bytes, note_key)
        txid = send_tx(client, addr, sk, encrypted_note, sp)

        row = {
            'ts': now.isoformat(),
            'date': date_key,
            'txid': txid,
            'ledger_tip': ledger_tip,
            'entries': entries,
            'root_hash': base_meta['root_hash'],
            'content_hash': content_hash,
            'multi_tx': False,
            'note_b64': base64.b64encode(encrypted_note).decode('ascii'),
            'status': 'anchored',
        }
        append_anchor(row)

        print(json.dumps({
            'ok': True,
            'status': 'anchored',
            'date': date_key,
            'txid': txid,
            'entries': entries,
            'events': events_count,
            'semantic': semantic_count,
            'procedural': procedural_count,
            'self_model': self_model_count,
            'multi_tx': False,
            'note_bytes': len(encrypted_note)
        }))

    else:
        # MULTI TX: split content into chunks
        # First TX: metadata + first chunk
        # Subsequent TXs: continuation chunks
        # Raw chunk size must account for base64 expansion (~4/3) + JSON metadata.
        # Use conservative fixed size to guarantee note <= 1024 bytes.
        chunk_size = 200
        chunks = []
        offset = 0
        while offset < len(content_bytes):
            chunks.append(content_bytes[offset:offset + chunk_size])
            offset += chunk_size

        total_parts = len(chunks)
        txids = []

        for i, chunk in enumerate(chunks):
            part_num = i + 1
            chunk_hash = hashlib.sha256(chunk).hexdigest()

            if i == 0:
                # First part: full metadata + first chunk
                payload = base_meta.copy()
                payload['multi_tx'] = True
                payload['total_parts'] = total_parts
                payload['part'] = part_num
                payload['chunk_hash'] = chunk_hash
                payload['chunk'] = base64.b64encode(chunk).decode('ascii')
            else:
                # Continuation parts: minimal metadata + chunk
                payload = {
                    'v': 2,
                    'mode': 'daily-consolidation-part',
                    'date': date_key,
                    'part': part_num,
                    'total_parts': total_parts,
                    'chunk_hash': chunk_hash,
                    'chunk': base64.b64encode(chunk).decode('ascii')
                }

            payload_bytes = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
            encrypted_note = encrypt_note(payload_bytes, note_key)
            txid = send_tx(client, addr, sk, encrypted_note, sp)
            txids.append(txid)

            # Record each part
            row = {
                'ts': now.isoformat(),
                'date': date_key,
                'txid': txid,
                'ledger_tip': ledger_tip,
                'entries': entries,
                'root_hash': base_meta['root_hash'],
                'content_hash': content_hash,
                'multi_tx': True,
                'part': part_num,
                'total_parts': total_parts,
                'note_b64': base64.b64encode(encrypted_note).decode('ascii'),
                'status': 'anchored',
            }
            append_anchor(row)

        print(json.dumps({
            'ok': True,
            'status': 'anchored',
            'date': date_key,
            'txids': txids,
            'entries': entries,
            'events': events_count,
            'semantic': semantic_count,
            'procedural': procedural_count,
            'self_model': self_model_count,
            'multi_tx': True,
            'total_parts': total_parts,
            'total_bytes': len(content_bytes)
        }))


if __name__ == '__main__':
    main()
