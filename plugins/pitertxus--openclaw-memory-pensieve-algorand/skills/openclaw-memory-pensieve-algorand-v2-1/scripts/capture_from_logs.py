#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Capture important events from OpenClaw logs and session files.
Manual extraction for backfilling events.jsonl.
"""
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

MEM_ROOT = Path('/home/molty/.openclaw/workspace/memory')
EVENTS = MEM_ROOT / 'events.jsonl'
LEDGER = MEM_ROOT / 'ledger.jsonl'

def read_ledger_tip():
    """Get current ledger tip hash."""
    if not LEDGER.exists() or LEDGER.stat().st_size == 0:
        return 'GENESIS'
    with LEDGER.open('r', encoding='utf-8') as f:
        lines = [l for l in f if l.strip()]
        if not lines:
            return 'GENESIS'
        return json.loads(lines[-1])['chain_hash']

def append_event(content, source, importance=0.5, tags=None):
    """Append event to events.jsonl with hash chain."""
    prev_hash = read_ledger_tip()
    
    event = {
        'id': hashlib.sha256(f'{datetime.now().isoformat()}{content}'.encode()).hexdigest()[:36],
        'ts': datetime.now(timezone.utc).isoformat(),
        'type': 'events',
        'source': source,
        'importance': importance,
        'tags': tags or [],
        'content': content
    }
    
    # Hash chain
    event_str = json.dumps(event, sort_keys=True, separators=(',', ':'))
    entry_hash = hashlib.sha256(event_str.encode('utf-8')).hexdigest()
    chain_hash = hashlib.sha256(f'{prev_hash}{entry_hash}'.encode('utf-8')).hexdigest()
    
    event['entry_hash'] = entry_hash
    event['prev_hash'] = prev_hash
    event['chain_hash'] = chain_hash
    
    # Append to events
    with EVENTS.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    # Append to ledger
    ledger_entry = {
        'ts': event['ts'],
        'entry_hash': entry_hash,
        'prev_hash': prev_hash,
        'chain_hash': chain_hash,
        'source': source
    }
    with LEDGER.open('a', encoding='utf-8') as f:
        f.write(json.dumps(ledger_entry, ensure_ascii=False) + '\n')
    
    return event['id']

def capture_today_manual(date_str='2026-03-05'):
    """Capture important events from today's work (manual extraction)."""
    
    events_added = []
    
    # Event 1: Pensieve v2 implementation
    eid = append_event(
        content="Implemented Pensieve v2 with full on-chain memory backup. Upgraded anchor system from metadata-only to full content (semantic/procedural/self-model events). Single-TX if <992 bytes, Multi-TX if larger. Complete disaster recovery now possible from blockchain alone (mnemonic + encryption key). Scripts: anchor_daily_algorand.py (v2), read_anchor_latest.py (v2), recover_from_blockchain.py. Cost: ~2.19 ALGO/year (~$0.44/year). Current balance: 1.994 ALGO = 332 days remaining.",
        source='manual_capture',
        importance=0.95,
        tags=['pensieve', 'blockchain', 'algorand', 'memory', 'infrastructure']
    )
    events_added.append(eid)
    
    # Event 2: Tech Watch bulletproof system
    eid = append_event(
        content="Rebuilt Tech Watch system with mandatory deduplication. Implemented: (1) Zotero library export (2236 items, 2145 DOIs), (2) sent-papers.jsonl log, (3) TECH_WATCH_PROTOCOL.md with mandatory pre-flight checks, (4) bestEffort=false for visible errors, (5) EN-only enforcement via nox-grupo.md. Scope: papers from 2025-2026 highly relevant to ALL MHBI projects. Format fixed: 1-4 items max, no commentary. Root cause: previous system sent Pedro's own paper (Nature Comms 2025) and had silent delivery failures.",
        source='manual_capture',
        importance=0.9,
        tags=['tech-watch', 'zotero', 'deduplication', 'mission-critical', 'mhbi']
    )
    events_added.append(eid)
    
    # Event 3: HFSP metabolic memory proposal
    eid = append_event(
        content="Created HFSP Research Grant proposal structure for metabolic memory project. Generated 5 documents (1564 lines total): 00_EXECUTIVE_SUMMARY.md, QUICK_START.md, literature review (40+ papers), experimental battery (5 Aims), collaborator strategy. Core idea: Does Legionella infection create metabolic memory in macrophages that biases response to Salmonella? Single-cell imaging + ML to predict and manipulate memory nodes. Identified consortium: Pedro (France) + Erika Pearce (Johns Hopkins, USA) as critical first partner. Calibrated against HFSP 2025 awarded projects for 'frontierness' requirement.",
        source='manual_capture',
        importance=0.85,
        tags=['hfsp', 'grant', 'proposal', 'metabolic-memory', 'collaboration']
    )
    events_added.append(eid)
    
    # Event 4: Algorand secrets backup
    eid = append_event(
        content="Sent critical Algorand wallet secrets via WhatsApp for backup: (1) mnemonic (24 words), (2) note encryption key (32 bytes base64). Without these, blockchain transactions are public but notes permanently unreadable. Wallet address: WARHPKTGAJM75YFSR442JXJRAV6BKOEWPUSAK5O7LHPTNB7Y2QMNOU7SUY. User instructed to save in password manager + paper backup.",
        source='manual_capture',
        importance=0.9,
        tags=['security', 'backup', 'algorand', 'secrets']
    )
    events_added.append(eid)
    
    # Event 5: Checkpoint 18:30 tokens fix
    eid = append_event(
        content="Fixed checkpoint 18:30 cron to ALWAYS include token stats at end of report. Updated prompt with 'IMPORTANT: The Tokens line is MANDATORY' and explicit examples for all cases (active tasks, no tasks, no changes). Previous behavior: sometimes omitted tokens despite user request.",
        source='manual_capture',
        importance=0.6,
        tags=['checkpoint', 'tokens', 'reporting', 'cron']
    )
    events_added.append(eid)
    
    # Event 6: Zotero export optimization
    eid = append_event(
        content="Optimized Zotero library export from daily (7x/week) to 3x/week (Mon/Thu/Sat 07:30, 30 min before Tech Watch). Reduces API calls without compromising data freshness. Export contains 2236 items for deduplication.",
        source='manual_capture',
        importance=0.5,
        tags=['zotero', 'optimization', 'api']
    )
    events_added.append(eid)
    
    # Event 7: Date reasoning error identified
    eid = append_event(
        content="Self-identified reasoning error: confused 'mañana jueves 06-03' when today is jueves 05-03 (tomorrow is viernes 06-03). Root cause: lazy association between 'jueves' (Tech Watch day) and '06-03' (tomorrow) without verifying day-of-week. Lesson: always verify dates with `date` command before stating specific weekdays.",
        source='manual_capture',
        importance=0.7,
        tags=['self-correction', 'reasoning', 'lesson']
    )
    events_added.append(eid)
    
    print(f"✓ Captured {len(events_added)} events from {date_str}")
    for eid in events_added:
        print(f"  - {eid}")
    
    return events_added

if __name__ == '__main__':
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else '2026-03-05'
    capture_today_manual(date)
