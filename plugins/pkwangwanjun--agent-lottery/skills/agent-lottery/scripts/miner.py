#!/usr/bin/env python3
"""
Mining Controller for Agent Lottery
Start/stop cpuminer with CPU limit and track statistics
"""

import subprocess
import argparse
import json
import os
import re
import time
import signal
import sys
import urllib.request
from datetime import datetime

# Config file path (store in skill directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(SKILL_DIR, "data")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PID_FILE = os.path.join(CONFIG_DIR, "miner.pid")
STATS_FILE = os.path.join(CONFIG_DIR, "stats.json")


def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def check_cpuminer():
    """Check if cpuminer-opt is installed"""
    try:
        result = subprocess.run(['cpuminer-opt', '--help'], capture_output=True, text=True, timeout=5)
        return True
    except FileNotFoundError:
        return False
    except:
        return True  # Installed but --help may not work


def check_cpulimit():
    """Check if cpulimit is installed"""
    try:
        subprocess.run(['cpulimit', '--help'], capture_output=True, timeout=5)
        return True
    except FileNotFoundError:
        return False
    except:
        return True


def get_network_difficulty():
    """Fetch current BTC network difficulty from public API"""
    try:
        with urllib.request.urlopen('https://blockchain.info/q/getdifficulty', timeout=10) as resp:
            return float(resp.read().decode().strip())
    except:
        # Fallback to recent estimate if API fails
        return 1.44e14


def format_difficulty(diff):
    """Format difficulty with trillion/billion suffix"""
    if diff >= 1e12:
        return f"{diff/1e12:.2f}T"
    elif diff >= 1e9:
        return f"{diff/1e9:.2f}B"
    elif diff >= 1e6:
        return f"{diff/1e6:.2f}M"
    else:
        return f"{diff:.2f}"


def get_mining_status():
    """Check if mining is currently running"""
    if not os.path.exists(PID_FILE):
        return False, None
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)
        return True, pid
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return False, None


def parse_difficulty(line):
    """Parse difficulty from cpuminer output"""
    # Match patterns like "accepted: 1/1 (diff 0.001), ..."
    # or "Diff 1234.56"
    diff_match = re.search(r'diff\s+([\d.]+)', line, re.IGNORECASE)
    if diff_match:
        return float(diff_match.group(1))
    return None


def update_stats(difficulty, is_share=True):
    """Update mining statistics"""
    config = load_config()
    if not config:
        return
    
    stats = config.get('stats', {
        'best_difficulty': 0,
        'total_shares': 0,
        'start_time': None,
        'last_update': None
    })
    
    if stats['start_time'] is None:
        stats['start_time'] = datetime.now().isoformat()
    
    stats['last_update'] = datetime.now().isoformat()
    
    if difficulty and difficulty > stats.get('best_difficulty', 0):
        stats['best_difficulty'] = difficulty
        print(f"\n🎰 NEW BEST DIFFICULTY: {difficulty:.2f}!\n")
    
    if is_share:
        stats['total_shares'] = stats.get('total_shares', 0) + 1
    
    config['stats'] = stats
    save_config(config)


def start_mining(cpu_percent=None, pool_url=None, address=None):
    """Start mining process"""
    is_running, pid = get_mining_status()
    if is_running:
        print(f"Mining already running (PID: {pid})")
        return
    
    config = load_config()
    if not config:
        print("No wallet configured. Run wallet.py --generate first.")
        return
    
    pool = pool_url or config.get('pool_url', 'btc.casualmine.com:20001')
    addr = address or config['wallet']['address']
    cpu = cpu_percent or config.get('cpu_percent', 10)
    
    # Check dependencies
    if not check_cpuminer():
        print("Error: cpuminer-opt not found. Install with:")
        print("  sudo apt install cpuminer-opt")
        print("Or build from source: https://github.com/JayDDee/cpuminer-opt")
        return
    
    print(f"=== Starting Agent Lottery Mining ===")
    print(f"Pool: {pool}")
    print(f"Address: {addr}")
    print(f"CPU Limit: {cpu}%")
    print(f"\n⚠️  This is lottery mining - extremely low chance of finding a block!")
    print(f"    Current BTC block difficulty: ~1e12 (one in a trillion chance per share)")
    print()
    
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Preserve existing stats or initialize new ones
    if 'stats' not in config or not config['stats'].get('start_time'):
        config['stats'] = {
            'best_difficulty': 0,
            'total_shares': 0,
            'start_time': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat()
        }
        save_config(config)
    
    # Build cpuminer command
    # -a sha256d for Bitcoin
    # -o stratum+tcp://pool:port
    # -u address
    # -p x (password, usually ignored for solo)
    pool_protocol = pool
    if not pool.startswith('stratum+tcp://'):
        pool_protocol = f'stratum+tcp://{pool}'
    
    miner_cmd = [
        'cpuminer-opt',
        '-a', 'sha256d',
        '-o', pool_protocol,
        '-u', addr,
        '-p', 'x',
        '--no-color'
    ]
    
    # Log file for cpuminer output
    log_file = os.path.join(CONFIG_DIR, "miner.log")
    
    # Clear log file before starting (to avoid confusion with old logs)
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Start miner process with output to log file
    # Keep file handle open to avoid buffering issues
    try:
        log_f = open(log_file, 'w')
        miner_proc = subprocess.Popen(
            miner_cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Save PID
        with open(PID_FILE, 'w') as f:
            f.write(str(miner_proc.pid))
        
        print(f"Mining started (PID: {miner_proc.pid})")
        print(f"Log file: {log_file}")
        print("Press Ctrl+C to stop mining\n")
        print("-" * 50)
        
        # If cpulimit is available and cpu < 100, wrap the process
        if cpu < 100 and check_cpulimit():
            # Wait a moment for process to start
            time.sleep(1)
            limit_proc = subprocess.Popen([
                'cpulimit', '-p', str(miner_proc.pid), '-l', str(cpu), '-q'
            ])
        
        # Track last submitted difficulty for when Accepted comes
        last_submitted_diff = None
        last_processed_line = 0  # Track which lines we've already processed
        
        # Monitor log file for shares
        while miner_proc.poll() is None:
            # Flush log buffer to ensure data is written to disk
            try:
                log_f.flush()
                os.fsync(log_f.fileno())
            except:
                pass
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                    # Only process new lines since last check
                    new_lines = lines[last_processed_line:]
                    last_processed_line = len(lines)
                    
                    for line in new_lines:
                        # cpuminer-opt format:
                        # [timestamp] 1 Submitted Diff 2.6377, Block 939354, Job xxx
                        # [timestamp] 1 Accepted 1 S0 R0 B0, 9.750 sec (171ms)
                        # 
                        # NOTE: Periodic reports also contain "Submitted" and "Accepted" but:
                        # - Reports: "Submitted             0            0" (no timestamp, padded columns)
                        # - Real: "[2026-03-05 11:45:38] 1 Submitted Diff 2.6377" (has timestamp, "Diff X.XX")
                        
                        # Only match real share submissions (must have "Diff" keyword and timestamp)
                        if 'submitted' in line.lower() and 'diff' in line.lower() and line.strip().startswith('['):
                            diff = parse_difficulty(line)
                            if diff:
                                last_submitted_diff = diff
                                print(f"[SHARE] Submitted Diff: {diff:.4f}")
                        
                        # Only match real acceptances (must have timestamp and S0 pattern)
                        # Real: "[timestamp] 1 Accepted 1 S0 R0 B0"
                        # Report: "Accepted              0            0        0.0%"
                        if 'accepted' in line.lower() and ' S0 ' in line and line.strip().startswith('['):
                            update_stats(last_submitted_diff)
                            print(f"[ACCEPTED] Share confirmed! Diff: {last_submitted_diff}")
                            last_submitted_diff = None
                            
            time.sleep(2)  # Check every 2 seconds
        
    except KeyboardInterrupt:
        print("\n\nStopping mining...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close log file handle
        try:
            if 'log_f' in locals():
                log_f.close()
        except:
            pass
        stop_mining()


def stop_mining():
    """Stop mining process"""
    is_running, pid = get_mining_status()
    
    if not is_running:
        print("Mining not running")
        return
    
    try:
        # Kill the process group
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError:
        pass
    except:
        # Try direct kill
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass
    
    # Kill cpuminer processes
    try:
        subprocess.run(['pkill', '-f', 'cpuminer-opt'], capture_output=True)
    except:
        pass
    
    # Kill cpulimit processes
    try:
        subprocess.run(['pkill', '-f', 'cpulimit'], capture_output=True)
    except:
        pass
    
    # Kill the miner.py monitoring script (started with nohup)
    try:
        subprocess.run(['pkill', '-f', 'miner.py start'], capture_output=True)
    except:
        pass
    
    # Remove PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    
    print("Mining stopped")


def show_status():
    """Show current mining status and statistics"""
    is_running, pid = get_mining_status()
    config = load_config()
    
    print("=== Agent Lottery Status ===\n")
    
    if is_running:
        print(f"🟢 Mining: ACTIVE (PID: {pid})")
    else:
        print("🔴 Mining: STOPPED")
    
    if config:
        stats = config.get('stats', {})
        print(f"\n📊 Statistics:")
        print(f"   Best Difficulty: {stats.get('best_difficulty', 0):.4f}")
        print(f"   Total Shares: {stats.get('total_shares', 0)}")
        
        if stats.get('start_time'):
            start = datetime.fromisoformat(stats['start_time'])
            elapsed = datetime.now() - start
            hours = elapsed.total_seconds() / 3600
            print(f"   Running Time: {hours:.2f} hours")
        
        print(f"\n💰 Wallet:")
        print(f"   Address: {config['wallet']['address']}")
        print(f"   Pool: {config.get('pool_url', 'N/A')}")
        print(f"   CPU Limit: {config.get('cpu_percent', 10)}%")
        
        # Lottery context
        best_diff = stats.get('best_difficulty', 0)
        network_diff = get_network_difficulty()
        network_diff_fmt = format_difficulty(network_diff)
        print(f"\n🎰 Lottery Context:")
        print(f"   BTC Network Difficulty: {network_diff_fmt} ({network_diff:.2e})")
        print(f"   Your Best Share: {best_diff:.4f}")
        if best_diff > 0:
            ratio = network_diff / best_diff
            print(f"   You're ~{ratio:.2e}x away from a block!")
        
        # Fun comparison
        print(f"\n📝 Fun Facts:")
        print(f"   - Finding a block with CPU: ~1 in 10^15 hashes")
        print(f"   - Powerball jackpot odds: ~1 in 3x10^8")
        print(f"   - Lightning strike odds: ~1 in 15,300/year")
    else:
        print("No wallet configured. Run: python wallet.py --generate")


def adjust_cpu(new_percent):
    """Dynamically adjust CPU limit while mining is running"""
    is_running, pid = get_mining_status()
    
    if not is_running:
        print("Mining not running. CPU limit will be applied on next start.")
        config = load_config()
        if config:
            config['cpu_percent'] = new_percent
            save_config(config)
            print(f"CPU limit set to {new_percent}% for future sessions.")
        return
    
    # Kill existing cpulimit processes for this PID
    try:
        subprocess.run(['pkill', '-f', f'cpulimit.*{pid}'], capture_output=True)
        time.sleep(0.5)
    except:
        pass
    
    # Start new cpulimit if not 100%
    if new_percent < 100 and check_cpulimit():
        subprocess.Popen([
            'cpulimit', '-p', str(pid), '-l', str(new_percent), '-q'
        ])
        print(f"✅ CPU limit adjusted to {new_percent}%")
    elif new_percent >= 100:
        print("✅ CPU limit removed (100%)")
    else:
        print("cpulimit not installed, cannot limit CPU")
        return
    
    # Update config
    config = load_config()
    if config:
        config['cpu_percent'] = new_percent
        save_config(config)


def lottery_summary():
    """Generate a lottery-style summary"""
    config = load_config()
    
    if not config:
        return "No lottery in progress. Use 'start' to begin mining."
    
    stats = config.get('stats', {})
    is_running, _ = get_mining_status()
    
    best_diff = stats.get('best_difficulty', 0)
    shares = stats.get('total_shares', 0)
    
    # Calculate running time
    running_time = ""
    if stats.get('start_time'):
        start = datetime.fromisoformat(stats['start_time'])
        elapsed = datetime.now() - start
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        running_time = f"{hours}h {minutes}m"
    else:
        running_time = "N/A"
    
    status = "🎫 ACTIVE" if is_running else "⏸️ PAUSED"
    
    # Format shares with commas for readability
    shares_str = f"{shares:,}"
    best_diff_str = f"{best_diff:.4f}"
    
    # Get real-time network difficulty
    network_diff = get_network_difficulty()
    network_diff_str = format_difficulty(network_diff)
    
    summary = f"""
🎰 AGENT LOTTERY STATUS: {status}

┌──────────────────────────────────────┐
│  📊 SHARES (Tickets): {shares_str:>14}  │
│  🏆 BEST DIFFICULTY:  {best_diff_str:>14}  │
│  ⏱️  RUNNING TIME:     {running_time:>14}  │
│  🎯 NETWORK DIFF:      {network_diff_str:>14}  │
└──────────────────────────────────────┘

💡 What this means:
   Each share = one lottery ticket
   Higher difficulty = closer to winning
   Block needs diff ~10^14 (very rare!)

📝 Log file: {CONFIG_DIR}/miner.log
"""
    
    if best_diff > 0:
        # Calculate how "close" they are
        ratio = network_diff / best_diff
        if ratio < 1e10:
            # Extremely unlikely but handle it
            summary += f"\n🔥 Incredible! You're only {ratio:.2e}x away!"
        elif ratio < 1e12:
            summary += f"\n📈 Great progress! You're {ratio:.2e}x away"
        else:
            summary += f"\n🎲 Keep going! Odds: 1 in {ratio:.2e}"
    else:
        summary += "\n⏳ No shares yet - mining just started or waiting..."
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='Agent Lottery Mining Controller')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'lottery', 'setcpu'], 
                        help='Command to execute')
    parser.add_argument('--cpu', type=int, help='CPU usage percentage (1-100)')
    parser.add_argument('--pool', type=str, help='Mining pool URL:port')
    parser.add_argument('--address', type=str, help='Bitcoin address to mine to')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_mining(args.cpu, args.pool, args.address)
    elif args.command == 'stop':
        stop_mining()
    elif args.command == 'status':
        show_status()
    elif args.command == 'lottery':
        print(lottery_summary())
    elif args.command == 'setcpu':
        if args.cpu:
            adjust_cpu(args.cpu)
        else:
            print("Usage: miner.py setcpu --cpu <1-100>")


if __name__ == '__main__':
    main()
