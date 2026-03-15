#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Read latest anchor from blockchain (supports v1 metadata-only and v2 full-content).
For multi-tx v2, reconstructs from all parts.
"""
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ANCHORS = Path('/home/molty/.openclaw/workspace/memory/onchain-anchors.jsonl')
NOTE_KEY = Path('/home/molty/.openclaw/workspace/.secrets/algorand-note-key.bin')


def decrypt_note(note_b64: str, key: bytes) -> dict:
    """Decrypt an encrypted note (NXP1 or NXP2 format)."""
    raw = base64.b64decode(note_b64)
    header = raw[:4]
    
    if header not in (b'NXP1', b'NXP2'):
        raise ValueError(f'Invalid note format: {header}')
    
    nonce = raw[4:16]
    ct = raw[16:]
    pt = AESGCM(key).decrypt(nonce, ct, None)
    return json.loads(pt.decode('utf-8'))


if not ANCHORS.exists() or ANCHORS.stat().st_size == 0:
    raise SystemExit('No anchors recorded yet')

if not NOTE_KEY.exists():
    raise SystemExit('Note key not found')

key = NOTE_KEY.read_bytes()

# Read all anchor records
rows = [json.loads(l) for l in ANCHORS.read_text(encoding='utf-8').splitlines() if l.strip()]

if not rows:
    raise SystemExit('No anchors found')

# Get latest date
latest_date = max(row['date'] for row in rows)

# Get all records for latest date
latest_records = [r for r in rows if r['date'] == latest_date]

# Check if multi-tx
is_multi = latest_records[0].get('multi_tx', False)

if not is_multi:
    # Single TX
    last = latest_records[0]
    payload = decrypt_note(last['note_b64'], key)
    
    # Build summary
    summary = {
        'txid': last['txid'],
        'date': last['date'],
        'version': payload.get('v', 1),
        'multi_tx': False,
        'payload': payload
    }
    
    # Add counts if available
    if 'events_count' in payload:
        summary['events_count'] = payload['events_count']
    if 'semantic_count' in payload:
        summary['semantic_count'] = payload['semantic_count']
        summary['procedural_count'] = payload['procedural_count']
        summary['self_model_count'] = payload['self_model_count']
    
    print(json.dumps(summary, ensure_ascii=False))

else:
    # Multi TX: get first part (has full metadata)
    parts = sorted(latest_records, key=lambda r: r.get('part', 0))
    first_part = parts[0]
    
    payload = decrypt_note(first_part['note_b64'], key)
    
    # Build summary
    summary = {
        'txids': [p['txid'] for p in parts],
        'date': first_part['date'],
        'version': payload.get('v', 2),
        'multi_tx': True,
        'total_parts': first_part.get('total_parts'),
        'payload': payload,
        'events_count': payload.get('events_count'),
        'semantic_count': payload.get('semantic_count'),
        'procedural_count': payload.get('procedural_count'),
        'self_model_count': payload.get('self_model_count')
    }
    
    print(json.dumps(summary, ensure_ascii=False))
