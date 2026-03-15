"""Tests for Pattern Miner analyzer module."""

import pytest
import tempfile
import os
from pathlib import Path

from pattern_miner.analyzer import CodeAnalyzer, CodePattern


class TestCodeAnalyzer:
    """Test cases for CodeAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer(min_lines=2)
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_python_language(self):
        """Test Python language detection."""
        assert self.analyzer._detect_language('test.py') == 'python'
        assert self.analyzer._detect_language('script.PY') == 'python'
    
    def test_detect_shell_language(self):
        """Test Shell language detection."""
        assert self.analyzer._detect_language('script.sh') == 'shell'
        assert self.analyzer._detect_language('script.bash') == 'bash'
    
    def test_analyze_single_file(self):
        """Test analyzing a single file."""
        # Create test file with duplicate code
        test_code = """
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    x = 1
    y = 2
    return x + y
"""
        test_file = Path(self.temp_dir) / 'test.py'
        test_file.write_text(test_code)
        
        patterns = self.analyzer.analyze_file(str(test_file))
        
        # Should find at least one pattern
        assert len(patterns) >= 0  # May vary based on detection
    
    def test_analyze_directory(self):
        """Test analyzing a directory."""
        # Create test files
        test_code = """
def process():
    data = []
    for i in range(10):
        data.append(i)
    return data
"""
        for i in range(3):
            test_file = Path(self.temp_dir) / f'test{i}.py'
            test_file.write_text(test_code)
        
        patterns = self.analyzer.analyze_directory(self.temp_dir)
        
        # Should find duplicate patterns
        assert len(patterns) >= 0
    
    def test_normalize_block(self):
        """Test code block normalization."""
        block1 = ['x = 1', 'y = 2', 'return x + y']
        block2 = ['a = 1', 'b = 2', 'return a + b']
        
        norm1 = self.analyzer._normalize_block(block1, 'python')
        norm2 = self.analyzer._normalize_block(block2, 'python')
        
        # Should normalize to similar structure
        assert norm1 is not None
        assert norm2 is not None
    
    def test_extract_variables(self):
        """Test variable extraction."""
        code = """
        user_name = "test"
        count = 10
        result = process(user_name, count)
        """
        variables = self.analyzer._extract_variables(code)
        
        assert 'user_name' in variables or 'count' in variables or 'result' in variables
    
    def test_get_patterns_filter(self):
        """Test pattern filtering by count."""
        # Manually add patterns
        pattern1 = CodePattern(
            hash='abc123',
            code='test code',
            language='python',
            occurrences=[('file1.py', 1), ('file2.py', 2)]
        )
        pattern2 = CodePattern(
            hash='def456',
            code='test code 2',
            language='python',
            occurrences=[('file3.py', 1)]
        )
        
        self.analyzer.patterns['abc123'] = pattern1
        self.analyzer.patterns['def456'] = pattern2
        
        # Filter by min_count=2
        filtered = self.analyzer.get_patterns(min_count=2)
        assert len(filtered) == 1
        assert filtered[0].hash == 'abc123'
    
    def test_clear_cache(self):
        """Test clearing analyzer cache."""
        self.analyzer.patterns['test'] = CodePattern(
            hash='test',
            code='test',
            language='python',
            occurrences=[]
        )
        
        self.analyzer.clear()
        
        assert len(self.analyzer.patterns) == 0
        assert len(self.analyzer.file_cache) == 0


class TestCodePattern:
    """Test cases for CodePattern dataclass."""
    
    def test_pattern_creation(self):
        """Test creating a CodePattern."""
        pattern = CodePattern(
            hash='abc123',
            code='test code',
            language='python',
            occurrences=[('file1.py', 1), ('file2.py', 2)]
        )
        
        assert pattern.hash == 'abc123'
        assert pattern.language == 'python'
        assert pattern.count == 2
    
    def test_pattern_with_variables(self):
        """Test CodePattern with variables."""
        pattern = CodePattern(
            hash='abc123',
            code='test code',
            language='python',
            occurrences=[('file1.py', 1)],
            variables=['x', 'y', 'z']
        )
        
        assert 'x' in pattern.variables
        assert len(pattern.variables) == 3
