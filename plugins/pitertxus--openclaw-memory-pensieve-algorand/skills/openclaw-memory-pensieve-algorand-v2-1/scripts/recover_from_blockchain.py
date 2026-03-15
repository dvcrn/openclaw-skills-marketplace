#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Recover memory from Algorand blockchain.
Reads onchain-anchors.jsonl, fetches/decrypts notes, reconstructs full content.
Supports both single-tx (v1/v2) and multi-tx (v2) formats.
"""
import base64
import hashlib
import json
import os
from pathlib import Path

from algosdk.v2client import indexer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ANCHORS = Path('/home/molty/.openclaw/workspace/memory/onchain-anchors.jsonl')
NOTE_KEY = Path('/home/molty/.openclaw/workspace/.secrets/algorand-note-key.bin')
OUTPUT_DIR = Path('/home/molty/.openclaw/workspace/memory/recovered')
INDEXER_URL = os.getenv('ALGORAND_INDEXER_URL', 'https://mainnet-idx.algonode.cloud')
INDEXER_TOKEN = os.getenv('ALGORAND_INDEXER_TOKEN', '')


def decrypt_note(note_b64: str, key: bytes) -> dict:
    raw = base64.b64decode(note_b64)
    header = raw[:4]
    if header not in (b'NXP1', b'NXP2'):
        raise ValueError(f'Invalid note format: {header}')
    nonce = raw[4:16]
    ct = raw[16:]
    pt = AESGCM(key).decrypt(nonce, ct, None)
    return json.loads(pt.decode('utf-8'))


def fetch_note_b64_by_txid(txid: str, idx: indexer.IndexerClient) -> str:
    tx = idx.transaction(txid)
    note_b64 = tx.get('transaction', {}).get('note')
    if not note_b64:
        raise ValueError(f'No note found on-chain for txid={txid}')
    return note_b64


def select_latest_anchor_set(records: list[dict]) -> list[dict]:
    """Select coherent latest anchor batch (same timestamp), sorted by part."""
    latest_ts = max(r.get('ts', '') for r in records)
    latest = [r for r in records if r.get('ts') == latest_ts]
    latest.sort(key=lambda r: int(r.get('part', 0) or 0))
    return latest


def recover_date(date_key: str, key: bytes) -> dict:
    if not ANCHORS.exists() or ANCHORS.stat().st_size == 0:
        raise SystemExit('No anchors found')

    records = []
    with ANCHORS.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('date') == date_key and row.get('status') == 'anchored':
                records.append(row)

    if not records:
        raise SystemExit(f'No anchors found for date {date_key}')

    selected = select_latest_anchor_set(records)
    idx = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_URL)

    # Prefer on-chain note fetch by txid. Fallback to local cached note_b64 only if needed.
    def get_note_b64(row: dict) -> str:
        txid = row.get('txid')
        if txid:
            try:
                return fetch_note_b64_by_txid(txid, idx)
            except Exception:
                pass
        note_b64 = row.get('note_b64')
        if note_b64:
            return note_b64
        raise ValueError('No usable note source (txid fetch failed and note_b64 missing)')

    first_note = get_note_b64(selected[0])
    first_payload = decrypt_note(first_note, key)

    is_multi = bool(first_payload.get('multi_tx', False))

    if not is_multi:
        payload = first_payload

        if payload.get('v') == 1:
            return {
                'date': date_key,
                'version': 1,
                'metadata': payload,
                'content': None,
                'note': 'v1 format: no content stored on-chain',
            }

        if payload.get('v') == 2 and 'content' in payload:
            content = payload['content']
            content_bytes = json.dumps(content, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
            computed_hash = hashlib.sha256(content_bytes).hexdigest()
            return {
                'date': date_key,
                'version': 2,
                'multi_tx': False,
                'metadata': payload,
                'content': content,
                'verified': computed_hash == payload.get('content_hash'),
                'anchor_ts': selected[0].get('ts'),
            }

        raise ValueError(f'Unknown payload format for {date_key}')

    # MULTI TX coherent reconstruction from selected batch only
    expected_total = int(first_payload.get('total_parts', 0) or 0)
    if expected_total <= 0:
        raise ValueError('Invalid total_parts in first payload')

    if len(selected) != expected_total:
        raise ValueError(
            f'Incomplete latest anchor set for {date_key}: found {len(selected)} rows, expected {expected_total}'
        )

    chunks_by_part = {}
    metadata = first_payload

    for row in selected:
        note_b64 = get_note_b64(row)
        part_payload = decrypt_note(note_b64, key)
        part_num = int(part_payload.get('part', 0) or 0)

        if part_num <= 0:
            raise ValueError('Invalid part number in payload')

        chunk_b64 = part_payload.get('chunk')
        if not chunk_b64:
            raise ValueError(f'Missing chunk in part {part_num}')

        chunk_bytes = base64.b64decode(chunk_b64)
        chunk_hash = part_payload.get('chunk_hash')
        computed_hash = hashlib.sha256(chunk_bytes).hexdigest()
        if computed_hash != chunk_hash:
            raise ValueError(f'Chunk hash mismatch in part {part_num}')

        if part_num in chunks_by_part:
            raise ValueError(f'Duplicate part {part_num} in latest anchor set')
        chunks_by_part[part_num] = chunk_bytes

    missing_parts = [p for p in range(1, expected_total + 1) if p not in chunks_by_part]
    if missing_parts:
        raise ValueError(f'Missing parts in latest anchor set: {missing_parts}')

    full_content_bytes = b''.join(chunks_by_part[p] for p in range(1, expected_total + 1))
    full_content_hash = hashlib.sha256(full_content_bytes).hexdigest()

    if full_content_hash != metadata.get('content_hash'):
        raise ValueError(
            f'Full content hash mismatch: {full_content_hash} != {metadata.get("content_hash")}'
        )

    content = json.loads(full_content_bytes.decode('utf-8'))

    return {
        'date': date_key,
        'version': 2,
        'multi_tx': True,
        'total_parts': expected_total,
        'metadata': metadata,
        'content': content,
        'verified': True,
        'anchor_ts': selected[0].get('ts'),
    }


def main():
    import sys

    if len(sys.argv) < 2:
        print('Usage: recover_from_blockchain.py <date> [--restore]')
        print('  date: YYYY-MM-DD')
        print('  --restore: write recovered content to memory/*.jsonl files')
        sys.exit(1)

    date_key = sys.argv[1]
    restore = '--restore' in sys.argv

    if not NOTE_KEY.exists():
        raise SystemExit('Note key not found in .secrets')

    key = NOTE_KEY.read_bytes()

    print(f'Recovering data for {date_key}...')
    result = recover_date(date_key, key)

    print('\nRecovery successful!')
    print(f'  Version: {result["version"]}')
    print(f'  Multi-TX: {result.get("multi_tx", False)}')
    if result.get('total_parts'):
        print(f'  Total parts: {result["total_parts"]}')
    print(f'  Verified: {result.get("verified", "N/A")}')

    if result['content']:
        events_raw = result['content'].get('events', [])
        semantic = result['content'].get('semantic', [])
        procedural = result['content'].get('procedural', [])
        self_model = result['content'].get('self_model', [])

        print('\nRecovered content:')
        print(f'  Events (raw): {len(events_raw)} events')
        print(f'  Semantic: {len(semantic)} events')
        print(f'  Procedural: {len(procedural)} events')
        print(f'  Self-model: {len(self_model)} events')

        if restore:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for layer_name, events in [
                ('events', events_raw),
                ('semantic', semantic),
                ('procedural', procedural),
                ('self_model', self_model),
            ]:
                if events:
                    out_file = OUTPUT_DIR / f'{layer_name}_recovered_{date_key}.jsonl'
                    with out_file.open('w', encoding='utf-8') as f:
                        for event in events:
                            f.write(json.dumps(event, ensure_ascii=False) + '\n')
                    print(f'  Wrote {out_file}')
            print(f'\nRecovered files written to {OUTPUT_DIR}/')
    else:
        print('\nNo content recovered (v1 format or empty day)')

    output_file = OUTPUT_DIR / f'recovery_{date_key}.json'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'\nFull recovery data: {output_file}')


if __name__ == '__main__':
    main()
