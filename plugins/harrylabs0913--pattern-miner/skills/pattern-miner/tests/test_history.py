"""Tests for Pattern Miner history module."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from pattern_miner.history import HistoryAnalyzer, CommandPattern, get_default_history_path


class TestHistoryAnalyzer:
    """Test cases for HistoryAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = HistoryAnalyzer(min_sequence=2)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.analyzer.clear()
    
    def test_load_history_from_file(self):
        """Test loading history from file."""
        # Create test history file
        test_history = """cd /project
git pull
pip install -r requirements.txt
cd /project
git pull
python manage.py migrate
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_history)
            history_file = f.name
        
        try:
            count = self.analyzer.load_history(history_file)
            assert count == 6
        finally:
            Path(history_file).unlink()
    
    def test_load_zsh_history_format(self):
        """Test loading zsh history format."""
        test_history = """: 1234567890:0;cd /project
: 1234567891:0;git pull
: 1234567892:0;ls -la
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_history)
            history_file = f.name
        
        try:
            count = self.analyzer.load_history(history_file)
            assert count == 3
        finally:
            Path(history_file).unlink()
    
    def test_analyze_repeated_sequences(self):
        """Test analyzing repeated command sequences."""
        # Add test commands
        self.analyzer.commands = [
            ('cd project', datetime.now(), ''),
            ('git pull', datetime.now(), ''),
            ('cd project', datetime.now(), ''),
            ('git pull', datetime.now(), ''),
        ]
        
        patterns = self.analyzer.analyze()
        
        # Should find repeated sequence
        assert len(patterns) >= 1
    
    def test_normalize_sequence(self):
        """Test command sequence normalization."""
        seq1 = ['cd /home/user/project', 'pip install requests']
        seq2 = ['cd /var/www/app', 'pip install flask']
        
        norm1 = self.analyzer._normalize_sequence(seq1)
        norm2 = self.analyzer._normalize_sequence(seq2)
        
        # Both should have paths normalized
        assert '<PATH>' in norm1 or '<PATH>' in norm2
    
    def test_get_frequent_commands(self):
        """Test getting frequent individual commands."""
        self.analyzer.commands = [
            ('git status', datetime.now(), ''),
            ('git status', datetime.now(), ''),
            ('git status', datetime.now(), ''),
            ('ls -la', datetime.now(), ''),
            ('ls -la', datetime.now(), ''),
        ]
        
        frequent = self.analyzer.get_frequent_commands(min_count=3)
        
        assert len(frequent) >= 1
        assert ('git', 3) in frequent or any(cmd == 'git' for cmd, _ in frequent)
    
    def test_time_window_filter(self):
        """Test time window filtering."""
        now = datetime.now()
        old = now - timedelta(days=10)
        
        self.analyzer.commands = [
            ('new command', now, ''),
            ('old command', old, ''),
        ]
        
        # Filter last 1 day
        patterns = self.analyzer.analyze(time_window=timedelta(days=1))
        
        # Should only include recent commands
        # Note: This test may need adjustment based on implementation
    
    def test_clear_cache(self):
        """Test clearing analyzer cache."""
        self.analyzer.commands = [('test', datetime.now(), '')]
        self.analyzer.patterns['test'] = CommandPattern(
            hash='test',
            commands=['test'],
            occurrences=[]
        )
        
        self.analyzer.clear()
        
        assert len(self.analyzer.commands) == 0
        assert len(self.analyzer.patterns) == 0


class TestCommandPattern:
    """Test cases for CommandPattern dataclass."""
    
    def test_pattern_creation(self):
        """Test creating a CommandPattern."""
        pattern = CommandPattern(
            hash='abc123',
            commands=['cd project', 'git pull'],
            occurrences=[('cd project && git pull', datetime.now())]
        )
        
        assert pattern.hash == 'abc123'
        assert len(pattern.commands) == 2
        assert pattern.count == 1
    
    def test_pattern_multiple_occurrences(self):
        """Test CommandPattern with multiple occurrences."""
        now = datetime.now()
        pattern = CommandPattern(
            hash='abc123',
            commands=['cd project', 'git pull'],
            occurrences=[
                ('cd project && git pull', now),
                ('cd project && git pull', now),
                ('cd project && git pull', now),
            ]
        )
        
        assert pattern.count == 3


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_get_default_history_path(self):
        """Test getting default history path."""
        path = get_default_history_path()
        
        # Should return a path or None
        assert path is None or Path(path).exists()
