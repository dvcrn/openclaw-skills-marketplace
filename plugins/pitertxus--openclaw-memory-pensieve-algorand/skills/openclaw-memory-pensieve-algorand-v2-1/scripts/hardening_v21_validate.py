#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Pensieve hardening v2.1 validator.
Runs integrity and recoverability checks for a target date (default=today).
"""
import base64
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from algosdk.v2client import indexer
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path('/home/molty/.openclaw/workspace/memory')
EVENTS = ROOT / 'events.jsonl'
LEDGER = ROOT / 'ledger.jsonl'
ANCHORS = ROOT / 'onchain-anchors.jsonl'
NOTE_KEY = Path('/home/molty/.openclaw/workspace/.secrets/algorand-note-key.bin')
INDEXER_URL = os.getenv('ALGORAND_INDEXER_URL', 'https://mainnet-idx.algonode.cloud')
INDEXER_TOKEN = os.getenv('ALGORAND_INDEXER_TOKEN', '')


def read_jsonl(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def canonical_event_hash(event_without_hashes: dict) -> str:
    event_str = json.dumps(event_without_hashes, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(event_str.encode('utf-8')).hexdigest()


def date_rows(rows, date_key: str):
    return [r for r in rows if str(r.get('ts', '')).startswith(date_key)]


def validate_ledger_chain(events_rows):
    issues = []
    prev_chain = None
    for i, e in enumerate(events_rows):
        base = {k: e[k] for k in ['id', 'ts', 'type', 'source', 'importance', 'tags', 'content'] if k in e}
        expected_entry_hash = canonical_event_hash(base)
        if e.get('entry_hash') != expected_entry_hash:
            issues.append(f'event[{i}] entry_hash mismatch')

        if i == 0:
            prev_chain = e.get('prev_hash')
        else:
            if e.get('prev_hash') != events_rows[i - 1].get('chain_hash'):
                issues.append(f'event[{i}] prev_hash not linked to previous chain_hash')

        expected_chain = sha256_text(f"{e.get('prev_hash', '')}{e.get('entry_hash', '')}")
        if e.get('chain_hash') != expected_chain:
            issues.append(f'event[{i}] chain_hash mismatch')

    return issues


def load_anchor_payload_for_date(date_key: str, key: bytes):
    anchors = read_jsonl(ANCHORS)
    day = [r for r in anchors if r.get('date') == date_key and r.get('status') == 'anchored']
    if not day:
        return None, ['no anchored rows for date']

    # Select latest coherent anchor set only
    latest_ts = max(r.get('ts', '') for r in day)
    latest = [r for r in day if r.get('ts') == latest_ts]
    latest.sort(key=lambda r: int(r.get('part', 0) or 0))

    idx = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_URL)

    def fetch_note_b64(row: dict) -> str:
        txid = row.get('txid')
        if txid:
            try:
                tx = idx.transaction(txid)
                note = tx.get('transaction', {}).get('note')
                if note:
                    return note
            except Exception:
                pass
        note_local = row.get('note_b64')
        if note_local:
            return note_local
        raise ValueError('missing note data (tx fetch failed and local note_b64 absent)')

    def decrypt(note_b64: str):
        raw = base64.b64decode(note_b64)
        hdr = raw[:4]
        if hdr not in (b'NXP1', b'NXP2'):
            raise ValueError('invalid note header')
        nonce = raw[4:16]
        ct = raw[16:]
        pt = AESGCM(key).decrypt(nonce, ct, None)
        return json.loads(pt.decode('utf-8'))

    issues = []

    first_payload = decrypt(fetch_note_b64(latest[0]))
    is_multi = bool(first_payload.get('multi_tx', False))

    if not is_multi:
        return first_payload, issues

    expected_total = int(first_payload.get('total_parts', 0) or 0)
    if expected_total <= 0:
        issues.append('invalid total_parts in first payload')
        return None, issues

    if len(latest) != expected_total:
        issues.append(f'incomplete latest anchor set: got {len(latest)} expected {expected_total}')

    chunks_by_part = {}
    meta = first_payload

    for row in latest:
        payload = decrypt(fetch_note_b64(row))
        pnum = int(payload.get('part', 0) or 0)
        chunk_b64 = payload.get('chunk')
        if not chunk_b64:
            issues.append(f'missing chunk at part {pnum}')
            continue
        chunk = base64.b64decode(chunk_b64)
        if hashlib.sha256(chunk).hexdigest() != payload.get('chunk_hash'):
            issues.append(f'chunk hash mismatch at part {pnum}')
        if pnum in chunks_by_part:
            issues.append(f'duplicate part {pnum} in latest anchor set')
            continue
        chunks_by_part[pnum] = chunk

    missing = [p for p in range(1, expected_total + 1) if p not in chunks_by_part]
    if missing:
        issues.append(f'missing parts: {missing}')

    if missing:
        return None, issues

    content_bytes = b''.join(chunks_by_part[p] for p in range(1, expected_total + 1))
    full_hash = hashlib.sha256(content_bytes).hexdigest()
    if meta and full_hash != meta.get('content_hash'):
        issues.append('content_hash mismatch')

    content = json.loads(content_bytes.decode('utf-8')) if content_bytes else {}
    payload = dict(meta or {})
    payload['content'] = content
    return payload, issues


def detect_probable_truncation(text: str):
    # heuristic only: likely clipped if it ends mid-token or explicit truncation marker
    t = (text or '').strip()
    if not t:
        return False
    if t.endswith('...'):
        return True
    if t.endswith(' re') or t.endswith(' im') or t.endswith(' au'):
        return True
    return False


def main():
    date_key = sys.argv[1] if len(sys.argv) > 1 else datetime.now().date().isoformat()

    events_all = read_jsonl(EVENTS)
    events_day = date_rows(events_all, date_key)
    issues = []
    warnings = []

    # Local integrity
    issues.extend(validate_ledger_chain(events_day))

    # Anchor recoverability
    if not NOTE_KEY.exists():
        print(json.dumps({'ok': False, 'date': date_key, 'error': 'note key missing'}))
        sys.exit(2)

    payload, anchor_issues = load_anchor_payload_for_date(date_key, NOTE_KEY.read_bytes())
    issues.extend(anchor_issues)

    anchored_events = []
    if payload is None:
        issues.append('no recoverable anchor payload')
    else:
        content = payload.get('content', payload.get('content') or {})
        anchored_events = content.get('events', []) if isinstance(content, dict) else []

        # Count parity
        if len(anchored_events) != len(events_day):
            issues.append(f'events count mismatch local={len(events_day)} onchain={len(anchored_events)}')

        # Event hash parity by entry_hash
        local_by_hash = {e.get('entry_hash'): e for e in events_day}
        onchain_by_hash = {e.get('entry_hash'): e for e in anchored_events}
        if set(local_by_hash.keys()) != set(onchain_by_hash.keys()):
            issues.append('entry_hash set mismatch local vs onchain')

        # Content-level truncation heuristics
        trunc_count = 0
        for ev in anchored_events:
            if detect_probable_truncation(ev.get('content', '')):
                trunc_count += 1
        if trunc_count:
            warnings.append(f'probable truncated events={trunc_count}')

    result = {
        'ok': len(issues) == 0,
        'date': date_key,
        'local_events': len(events_day),
        'onchain_events': len(anchored_events),
        'issues': issues,
        'warnings': warnings,
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
