"""Code analyzer for detecting duplicate patterns in Python and Shell code."""

import hashlib
import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field


@dataclass
class CodePattern:
    """Represents a detected code pattern."""
    hash: str
    code: str
    language: str
    occurrences: List[Tuple[str, int]]  # (file_path, line_number)
    count: int = 0
    variables: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.count = len(self.occurrences)


class CodeAnalyzer:
    """Analyzes code files to detect duplicate patterns."""
    
    def __init__(self, min_lines: int = 3, similarity_threshold: float = 0.8):
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.patterns: Dict[str, CodePattern] = {}
        self.file_cache: Dict[str, List[str]] = {}
        
    def analyze_directory(self, directory: str, extensions: List[str] = None) -> List[CodePattern]:
        """Analyze all code files in a directory."""
        if extensions is None:
            extensions = ['.py', '.sh', '.bash']
            
        dir_path = Path(directory)
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {directory}")
            
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                self.analyze_file(str(file_path))
                
        return self.get_patterns(min_count=2)
    
    def analyze_file(self, file_path: str) -> List[CodePattern]:
        """Analyze a single file for duplicate patterns."""
        path = Path(file_path)
        if not path.exists():
            return []
            
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        self.file_cache[file_path] = lines
        
        language = self._detect_language(file_path)
        
        if language == 'python':
            patterns = self._analyze_python(lines, file_path)
        elif language in ('shell', 'bash'):
            patterns = self._analyze_shell(lines, file_path)
        else:
            patterns = self._analyze_generic(lines, file_path)
            
        for pattern in patterns:
            key = pattern.hash
            if key in self.patterns:
                self.patterns[key].occurrences.extend(pattern.occurrences)
                self.patterns[key].count = len(self.patterns[key].occurrences)
            else:
                self.patterns[key] = pattern
                
        return patterns
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        path = Path(file_path)
        suffix = path.suffix.lower()
        name = path.name.lower()
        
        if suffix == '.py':
            return 'python'
        elif suffix in ('.sh', '.bash') or name.startswith('shebang'):
            return 'shell'
        elif suffix == '.bash':
            return 'bash'
        else:
            return 'generic'
    
    def _analyze_python(self, lines: List[str], file_path: str) -> List[CodePattern]:
        """Analyze Python code for patterns."""
        patterns = []
        
        # Try AST-based analysis for function-level patterns
        try:
            content = '\n'.join(lines)
            tree = ast.parse(content)
            patterns.extend(self._extract_ast_patterns(tree, file_path))
        except SyntaxError:
            pass  # Fall back to line-based analysis
        
        # Line-based pattern detection
        patterns.extend(self._find_repeated_blocks(lines, file_path, 'python'))
        
        return patterns
    
    def _extract_ast_patterns(self, tree: ast.AST, file_path: str) -> List[CodePattern]:
        """Extract patterns from Python AST."""
        patterns = []
        
        # Find similar function bodies
        function_bodies: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function body code
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                
                # Extract variables used in function
                variables = self._extract_function_variables(node)
                
                # Create normalized code (replace variable names with placeholders)
                normalized = self._normalize_python_node(node)
                code_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]
                
                function_bodies[code_hash].append((
                    file_path,
                    start_line,
                    ast.unparse(node) if hasattr(ast, 'unparse') else normalized
                ))
        
        # Create patterns for repeated function bodies
        for code_hash, occurrences in function_bodies.items():
            if len(occurrences) >= 2:
                patterns.append(CodePattern(
                    hash=code_hash,
                    code=occurrences[0][2][:500],  # Truncate for storage
                    language='python',
                    occurrences=[(occ[0], occ[1]) for occ in occurrences],
                    variables=list(set(v for occ in occurrences for v in self._extract_variables(occ[2])))
                ))
                
        return patterns
    
    def _normalize_python_node(self, node: ast.AST) -> str:
        """Normalize Python AST node for comparison."""
        # Create a structural representation
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            return f"func({len(args)}, {len(node.body)} statements)"
        elif isinstance(node, ast.ClassDef):
            return f"class({len(node.body)} members)"
        return str(type(node).__name__)
    
    def _extract_function_variables(self, node: ast.FunctionDef) -> List[str]:
        """Extract variable names from a function."""
        variables = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                variables.add(child.id)
        return list(variables)
    
    def _analyze_shell(self, lines: List[str], file_path: str) -> List[CodePattern]:
        """Analyze Shell code for patterns."""
        patterns = []
        
        # Find function definitions
        patterns.extend(self._find_shell_functions(lines, file_path))
        
        # Find repeated command sequences
        patterns.extend(self._find_repeated_blocks(lines, file_path, 'shell'))
        
        return patterns
    
    def _find_shell_functions(self, lines: List[str], file_path: str) -> List[CodePattern]:
        """Find shell function definitions."""
        patterns = []
        functions: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
        
        func_pattern = re.compile(r'^(\w+)\s*\(\s*\)\s*\{?$')
        current_func = None
        current_body = []
        start_line = 0
        
        for i, line in enumerate(lines):
            match = func_pattern.match(line.strip())
            if match:
                if current_func and current_body:
                    body_text = '\n'.join(current_body)
                    func_hash = hashlib.md5(body_text.encode()).hexdigest()[:12]
                    functions[func_hash].append((file_path, start_line, body_text))
                
                current_func = match.group(1)
                current_body = []
                start_line = i + 1
            elif current_func:
                if line.strip() == '}':
                    body_text = '\n'.join(current_body)
                    func_hash = hashlib.md5(body_text.encode()).hexdigest()[:12]
                    functions[func_hash].append((file_path, start_line, body_text))
                    current_func = None
                    current_body = []
                else:
                    current_body.append(line)
        
        # Create patterns for similar functions
        for func_hash, occurrences in functions.items():
            if len(occurrences) >= 2:
                patterns.append(CodePattern(
                    hash=func_hash,
                    code=occurrences[0][2][:500],
                    language='shell',
                    occurrences=[(occ[0], occ[1]) for occ in occurrences]
                ))
        
        return patterns
    
    def _find_repeated_blocks(self, lines: List[str], file_path: str, language: str) -> List[CodePattern]:
        """Find repeated code blocks using sliding window."""
        patterns = []
        block_hashes: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
        
        # Sliding window approach
        for window_size in range(self.min_lines, min(self.min_lines + 5, len(lines) // 2 + 1)):
            for i in range(len(lines) - window_size + 1):
                block = lines[i:i + window_size]
                
                # Skip blocks with too many empty lines
                non_empty = [l for l in block if l.strip()]
                if len(non_empty) < self.min_lines:
                    continue
                
                # Normalize and hash
                normalized = self._normalize_block(block, language)
                block_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]
                block_text = '\n'.join(block)
                
                block_hashes[block_hash].append((file_path, i + 1, block_text))
        
        # Create patterns for repeated blocks
        seen_hashes = set()
        for block_hash, occurrences in block_hashes.items():
            if len(occurrences) >= 2 and block_hash not in seen_hashes:
                # Check if this is not a subset of an already found pattern
                is_subset = False
                for existing in patterns:
                    if self._is_subset(occurrences, existing.occurrences):
                        is_subset = True
                        break
                
                if not is_subset:
                    seen_hashes.add(block_hash)
                    patterns.append(CodePattern(
                        hash=block_hash,
                        code=occurrences[0][2],
                        language=language,
                        occurrences=[(occ[0], occ[1]) for occ in occurrences],
                        variables=self._extract_variables(occurrences[0][2])
                    ))
        
        return patterns
    
    def _normalize_block(self, block: List[str], language: str) -> str:
        """Normalize a code block for comparison."""
        normalized = []
        for line in block:
            # Remove comments
            if language == 'python':
                line = re.sub(r'#.*$', '', line)
            elif language in ('shell', 'bash'):
                line = re.sub(r'#.*$', '', line)
            
            # Normalize whitespace
            line = ' '.join(line.split())
            
            # Replace literals with placeholders
            line = re.sub(r'\b\d+\b', '<NUM>', line)
            line = re.sub(r'"[^"]*"', '<STR>', line)
            line = re.sub(r"'[^']*'", '<STR>', line)
            
            normalized.append(line)
        
        return '\n'.join(normalized)
    
    def _extract_variables(self, code: str) -> List[str]:
        """Extract potential variable names from code."""
        variables = set()
        
        # Python variables
        python_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code)
        variables.update(python_vars)
        
        # Shell variables
        shell_vars = re.findall(r'\b([A-Z_][A-Z0-9_]*)=', code)
        variables.update(shell_vars)
        
        # Filter out keywords
        keywords = {'if', 'else', 'elif', 'for', 'while', 'def', 'class', 
                   'return', 'import', 'from', 'in', 'with', 'try', 'except',
                   'echo', 'cd', 'ls', 'grep', 'awk', 'sed'}
        variables -= keywords
        
        return list(variables)
    
    def _is_subset(self, occurrences1: List[Tuple], occurrences2: List[Tuple]) -> bool:
        """Check if occurrences1 is a subset of occurrences2."""
        set1 = set((o[0], o[1]) for o in occurrences1)
        set2 = set((o[0], o[1]) for o in occurrences2)
        return set1.issubset(set2) and len(set1) < len(set2)
    
    def get_patterns(self, min_count: int = 2) -> List[CodePattern]:
        """Get all detected patterns with minimum occurrence count."""
        return [p for p in self.patterns.values() if p.count >= min_count]
    
    def clear(self):
        """Clear all cached data."""
        self.patterns.clear()
        self.file_cache.clear()
