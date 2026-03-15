#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
"""
Auto-capture significant events from daily memory files.
Runs daily at checkpoint (18:30) to extract and append events to events.jsonl.
"""
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

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

def already_captured(content_text):
    """Check if exact content already captured (avoid accidental false positives)."""
    if not EVENTS.exists():
        return False

    target_hash = hashlib.sha256(content_text.strip().encode('utf-8')).hexdigest()

    with EVENTS.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                existing = event.get('content', '').strip()
                existing_hash = hashlib.sha256(existing.encode('utf-8')).hexdigest()
                if existing_hash == target_hash:
                    return True
            except Exception:
                continue
    return False

def append_event(content, source, importance=0.5, tags=None):
    """Append event to events.jsonl with hash chain."""
    if already_captured(content):
        return None  # Skip duplicate
    
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

def extract_from_daily_log(date_str):
    """Extract significant events from memory/YYYY-MM-DD.md."""
    log_file = MEM_ROOT / f'{date_str}.md'
    
    if not log_file.exists():
        return []
    
    content = log_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    events = []
    current_section = None
    buffer = []
    
    for line in lines:
        # Section headers
        if line.startswith('## '):
            # Flush buffer
            if buffer and current_section:
                event_content = '\n'.join(buffer).strip()
                if len(event_content) > 50:  # Minimum content length
                    events.append({
                        'content': f'{current_section}: {event_content}',
                        'importance': 0.7,
                        'tags': ['daily-log', 'auto-capture']
                    })
            
            current_section = line[3:].strip()
            buffer = []
        
        # Capture significant patterns
        elif any(marker in line for marker in ['✅', 'Implemented', 'Created', 'Fixed', 'Updated', 'Completed']):
            buffer.append(line)
        
        # Decision markers
        elif line.startswith('**') and any(word in line.lower() for word in ['decision', 'key', 'important', 'critical']):
            buffer.append(line)
    
    # Flush last buffer
    if buffer and current_section:
        event_content = '\n'.join(buffer).strip()
        if len(event_content) > 50:
            events.append({
                'content': f'{current_section}: {event_content}',
                'importance': 0.7,
                'tags': ['daily-log', 'auto-capture']
            })
    
    return events

def main():
    """Run daily auto-capture."""
    today = datetime.now().date().isoformat()
    
    # Extract from today's log
    events = extract_from_daily_log(today)
    
    captured = 0
    for event_data in events:
        eid = append_event(
            content=event_data['content'],
            source='auto_capture',
            importance=event_data['importance'],
            tags=event_data['tags']
        )
        if eid:
            captured += 1
    
    # Output for cron logging
    print(json.dumps({'ok': True, 'date': today, 'captured': captured, 'scanned': len(events)}))

if __name__ == '__main__':
    main()
