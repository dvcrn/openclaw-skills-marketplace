#!/usr/bin/env python3
"""
Quick lottery status checker for Agent Lottery
Returns a concise summary of current lottery status
"""

import json
import os
from datetime import datetime

CONFIG_DIR = os.path.expanduser("~/.agent-lottery")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PID_FILE = os.path.join(CONFIG_DIR, "miner.pid")


def get_status():
    """Get quick lottery status"""
    
    # Check if mining is running
    is_running = False
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        is_running = True
    except:
        is_running = False
    
    # Load config
    if not os.path.exists(CONFIG_FILE):
        return "No wallet configured. Start with: wallet.py --generate"
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    stats = config.get('stats', {})
    best_diff = stats.get('best_difficulty', 0)
    shares = stats.get('total_shares', 0)
    cpu = config.get('cpu_percent', 50)
    
    # Calculate runtime
    runtime = "N/A"
    if stats.get('start_time'):
        start = datetime.fromisoformat(stats['start_time'])
        elapsed = datetime.now() - start
        hours = elapsed.total_seconds() / 3600
        if hours < 1:
            runtime = f"{elapsed.total_seconds()/60:.0f} min"
        elif hours < 24:
            runtime = f"{hours:.1f} hrs"
        else:
            runtime = f"{hours/24:.1f} days"
    
    # Status emoji
    status_emoji = "🟢" if is_running else "🔴"
    
    return f"""
{status_emoji} **Agent Lottery**

🎫 Tickets: {shares}
🏆 Best Diff: {best_diff:.4f}
⏱️ Runtime: {runtime}
💪 CPU: {cpu}%
"""


if __name__ == '__main__':
    print(get_status())
