#!/home/molty/.openclaw/workspace/.venv-algo/bin/python
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('/home/molty/.openclaw/workspace/memory')
EVENTS = ROOT / 'events.jsonl'
SEM = ROOT / 'semantic.jsonl'
PROC = ROOT / 'procedural.jsonl'
SELF = ROOT / 'self_model.jsonl'
LOG = ROOT / 'consolidation-log.jsonl'


def read_jsonl(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    out = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: Path, row: dict):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def norm(s: str) -> str:
    return ' '.join((s or '').strip().lower().split())


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for p in (EVENTS, SEM, PROC, SELF, LOG):
        if not p.exists():
            p.touch()

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)

    events = []
    for e in read_jsonl(EVENTS):
        try:
            ts = datetime.fromisoformat(e.get('ts'))
        except Exception:
            continue
        if ts >= cutoff:
            events.append(e)

    tag_counts = Counter(t for e in events for t in e.get('tags', []))
    source_counts = Counter(e.get('source', 'unknown') for e in events)

    promoted_sem = []
    promoted_proc = []
    promoted_self = []

    # semantic: recurring tags in last 24h
    for tag, n in tag_counts.items():
        if n >= 3:
            row = {
                'id': f'sem-{int(now.timestamp())}-{tag}',
                'ts': now.isoformat(),
                'type': 'semantic',
                'source': 'dream_cycle_daily',
                'importance': 0.7,
                'tags': [tag],
                'content': f'Recurring focus: {tag} ({n} events/24h).',
                'status': 'active'
            }
            append_jsonl(SEM, row)
            promoted_sem.append({'tag': tag, 'count': n})

    # procedural: repeated source pattern as workflow hint
    for src, n in source_counts.items():
        if src not in ('unknown', 'manual') and n >= 3:
            row = {
                'id': f'proc-{int(now.timestamp())}-{src}',
                'ts': now.isoformat(),
                'type': 'procedural',
                'source': 'dream_cycle_daily',
                'importance': 0.65,
                'tags': ['workflow', src],
                'content': f'Repeated workflow signal: source={src} appears {n} times/24h.',
                'status': 'active'
            }
            append_jsonl(PROC, row)
            promoted_proc.append({'source': src, 'count': n})

    # self-model: only very stable recurring behavioral tag
    if tag_counts.get('memory', 0) >= 5:
        row = {
            'id': f'self-{int(now.timestamp())}-memory',
            'ts': now.isoformat(),
            'type': 'self_model',
            'source': 'dream_cycle_daily',
            'importance': 0.8,
            'tags': ['identity', 'memory'],
            'content': 'Prioritize durable memory consistency and append-only integrity checks.',
            'status': 'active'
        }
        append_jsonl(SELF, row)
        promoted_self.append({'rule': 'memory-consistency'})

    # contradiction flags (simple heuristic): same normalized content with both active+superseded statuses in semantic
    contradictions = []
    sem_rows = read_jsonl(SEM)
    by_content = defaultdict(set)
    for r in sem_rows[-500:]:
        c = norm(r.get('content', ''))
        if not c:
            continue
        by_content[c].add(r.get('status', 'active'))
    for c, statuses in by_content.items():
        if 'active' in statuses and 'superseded' in statuses:
            contradictions.append({'content': c[:120], 'statuses': sorted(statuses)})

    log = {
        'ts': now.isoformat(),
        'source': 'dream_cycle_daily',
        'window_hours': 24,
        'events_scanned': len(events),
        'promoted': {
            'semantic': promoted_sem,
            'procedural': promoted_proc,
            'self_model': promoted_self,
        },
        'contradictions': contradictions,
        'status': 'ok'
    }
    append_jsonl(LOG, log)

    print(json.dumps({
        'ok': True,
        'events_scanned': len(events),
        'promoted_semantic': len(promoted_sem),
        'promoted_procedural': len(promoted_proc),
        'promoted_self_model': len(promoted_self),
        'contradictions': len(contradictions)
    }))


if __name__ == '__main__':
    main()
