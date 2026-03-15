"""Command history analyzer for detecting repeated command sequences."""

import hashlib
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import os


@dataclass
class CommandPattern:
    """Represents a detected command pattern."""
    hash: str
    commands: List[str]
    occurrences: List[Tuple[str, datetime]]  # (full_command, timestamp)
    count: int = 0
    context: str = ""  # Working directory or context
    
    def __post_init__(self):
        self.count = len(self.occurrences)


class HistoryAnalyzer:
    """Analyzes shell command history to detect repeated patterns."""
    
    def __init__(self, db_path: str = None, min_sequence: int = 2):
        self.min_sequence = min_sequence
        self.db_path = db_path
        self.patterns: Dict[str, CommandPattern] = {}
        self.commands: List[Tuple[str, datetime, str]] = []  # (command, timestamp, cwd)
        
    def load_history(self, history_file: str = None) -> int:
        """Load command history from shell history file."""
        if history_file is None:
            # Try common history file locations
            candidates = [
                Path.home() / '.bash_history',
                Path.home() / '.zsh_history',
                Path.home() / '.fish_history',
            ]
            for candidate in candidates:
                if candidate.exists():
                    history_file = str(candidate)
                    break
                    
        if not history_file or not Path(history_file).exists():
            return 0
            
        content = Path(history_file).read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle zsh history format (timestamp:command)
            if line.startswith(':'):
                match = re.match(r':\d+:\d+;(.+)', line)
                if match:
                    self.commands.append((match.group(1), datetime.now(), ''))
            else:
                self.commands.append((line, datetime.now(), ''))
        
        return len(self.commands)
    
    def load_from_sqlite(self, db_path: str = None) -> int:
        """Load command history from SQLite database."""
        db_path = db_path or self.db_path
        if not db_path or not Path(db_path).exists():
            return 0
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Try common table structures
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if 'history' in table.lower() or 'command' in table.lower():
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        # Try to extract command and timestamp
                        cmd = None
                        ts = datetime.now()
                        cwd = ''
                        
                        for item in row:
                            if isinstance(item, str) and ('/' in item or ' ' in item):
                                cmd = item
                            elif isinstance(item, (int, float)):
                                try:
                                    ts = datetime.fromtimestamp(item)
                                except (ValueError, OSError):
                                    pass
                        
                        if cmd:
                            self.commands.append((cmd, ts, cwd))
        except sqlite3.Error:
            pass
        finally:
            conn.close()
            
        return len(self.commands)
    
    def analyze(self, time_window: timedelta = None) -> List[CommandPattern]:
        """Analyze loaded history for repeated command sequences."""
        if not self.commands:
            return []
            
        # Filter by time window if specified
        commands = self.commands
        if time_window:
            cutoff = datetime.now() - time_window
            commands = [(cmd, ts, cwd) for cmd, ts, cwd in commands if ts >= cutoff]
        
        # Find repeated sequences using sliding window
        sequence_hashes: Dict[str, List[Tuple[str, datetime, str]]] = defaultdict(list)
        
        for seq_len in range(self.min_sequence, min(self.min_sequence + 4, len(commands) // 2 + 1)):
            for i in range(len(commands) - seq_len + 1):
                sequence = commands[i:i + seq_len]
                
                # Normalize commands
                normalized = self._normalize_sequence([cmd for cmd, _, _ in sequence])
                seq_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]
                
                # Store with context
                full_cmd = ' && '.join([cmd for cmd, _, _ in sequence])
                timestamp = sequence[0][1]
                cwd = sequence[0][2] if sequence[0][2] else ''
                
                sequence_hashes[seq_hash].append((full_cmd, timestamp, cwd))
        
        # Create patterns for repeated sequences
        for seq_hash, occurrences in sequence_hashes.items():
            if len(occurrences) >= 2:
                commands_list = occurrences[0][0].split(' && ')
                self.patterns[seq_hash] = CommandPattern(
                    hash=seq_hash,
                    commands=commands_list,
                    occurrences=[(occ[0], occ[1]) for occ in occurrences],
                    context=occurrences[0][2]
                )
        
        return self.get_patterns(min_count=2)
    
    def _normalize_sequence(self, commands: List[str]) -> str:
        """Normalize a command sequence for comparison."""
        normalized = []
        for cmd in commands:
            # Remove specific paths and values
            cmd = re.sub(r'/[^\s]+', '<PATH>', cmd)
            cmd = re.sub(r'\b\d+\b', '<NUM>', cmd)
            cmd = re.sub(r'-[a-zA-Z]+', '<FLAG>', cmd)
            cmd = re.sub(r'"[^"]*"', '<STR>', cmd)
            cmd = re.sub(r"'[^']*'", '<STR>', cmd)
            normalized.append(cmd.strip())
        return ' || '.join(normalized)
    
    def get_patterns(self, min_count: int = 2) -> List[CommandPattern]:
        """Get all detected patterns with minimum occurrence count."""
        return [p for p in self.patterns.values() if p.count >= min_count]
    
    def get_frequent_commands(self, min_count: int = 3) -> List[Tuple[str, int]]:
        """Get frequently used individual commands."""
        cmd_counts: Dict[str, int] = defaultdict(int)
        
        for cmd, _, _ in self.commands:
            # Extract base command
            base = cmd.split()[0] if cmd.split() else cmd
            base = base.split('/')[-1]  # Get command name from path
            cmd_counts[base] += 1
        
        return [(cmd, count) for cmd, count in cmd_counts.items() if count >= min_count]
    
    def clear(self):
        """Clear all cached data."""
        self.patterns.clear()
        self.commands.clear()


def get_default_history_path() -> Optional[str]:
    """Get the default shell history file path."""
    candidates = [
        Path.home() / '.bash_history',
        Path.home() / '.zsh_history',
        Path.home() / '.fish_history',
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None
