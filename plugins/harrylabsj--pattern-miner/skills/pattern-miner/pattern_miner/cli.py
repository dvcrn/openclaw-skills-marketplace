#!/usr/bin/env python3
"""CLI interface for Pattern Miner."""

import argparse
import json
import sys
from pathlib import Path
from datetime import timedelta

from .analyzer import CodeAnalyzer
from .history import HistoryAnalyzer, get_default_history_path
from .template import TemplateGenerator, ScriptGenerator


def cmd_analyze(args):
    """Analyze code files for duplicate patterns."""
    analyzer = CodeAnalyzer(min_lines=args.min_lines)
    
    print(f"Analyzing directory: {args.directory}")
    patterns = analyzer.analyze_directory(args.directory, args.extensions.split(','))
    
    if not patterns:
        print("No duplicate patterns found.")
        return 0
    
    print(f"\nFound {len(patterns)} duplicate pattern(s):\n")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}:")
        print(f"  Language: {pattern.language}")
        print(f"  Occurrences: {pattern.count}")
        print(f"  Hash: {pattern.hash}")
        print(f"  Locations:")
        for file_path, line_num in pattern.occurrences[:5]:
            print(f"    - {file_path}:{line_num}")
        if len(pattern.occurrences) > 5:
            print(f"    ... and {len(pattern.occurrences) - 5} more")
        
        if pattern.variables:
            print(f"  Variables: {', '.join(pattern.variables[:10])}")
        
        print(f"  Code preview:")
        for line in pattern.code.split('\n')[:5]:
            print(f"    {line}")
        print()
    
    if args.output:
        output_data = {
            'patterns': [
                {
                    'hash': p.hash,
                    'language': p.language,
                    'count': p.count,
                    'occurrences': p.occurrences,
                    'variables': p.variables,
                    'code': p.code
                }
                for p in patterns
            ]
        }
        Path(args.output).write_text(json.dumps(output_data, indent=2))
        print(f"Results saved to: {args.output}")
    
    return 0


def cmd_history(args):
    """Analyze command history for repeated sequences."""
    analyzer = HistoryAnalyzer()
    
    if args.history_file:
        count = analyzer.load_history(args.history_file)
    else:
        default_path = get_default_history_path()
        if default_path:
            count = analyzer.load_history(default_path)
        else:
            print("No history file found. Use --history-file to specify.")
            return 1
    
    print(f"Loaded {count} commands from history")
    
    if args.db_path:
        db_count = analyzer.load_from_sqlite(args.db_path)
        print(f"Loaded {db_count} additional commands from database")
    
    time_window = None
    if args.days:
        time_window = timedelta(days=args.days)
    
    patterns = analyzer.analyze(time_window=time_window)
    
    if not patterns:
        print("No repeated command sequences found.")
        return 0
    
    print(f"\nFound {len(patterns)} repeated command sequence(s):\n")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}:")
        print(f"  Occurrences: {pattern.count}")
        print(f"  Commands:")
        for cmd in pattern.commands:
            print(f"    - {cmd[:80]}{'...' if len(cmd) > 80 else ''}")
        print(f"  Example usage:")
        if pattern.occurrences:
            print(f"    {pattern.occurrences[0][0][:100]}")
        print()
    
    # Show frequent commands
    frequent = analyzer.get_frequent_commands(min_count=args.min_count)
    if frequent:
        print("\nFrequent individual commands:")
        for cmd, count in sorted(frequent, key=lambda x: -x[1])[:10]:
            print(f"  {cmd}: {count} times")
    
    return 0


def cmd_template(args):
    """Generate templates from detected patterns."""
    # Load patterns from analysis
    if not args.input:
        print("Error: --input required (JSON output from analyze command)")
        return 1
    
    try:
        data = json.loads(Path(args.input).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading input: {e}")
        return 1
    
    generator = TemplateGenerator(output_dir=args.output_dir or './templates')
    
    patterns = data.get('patterns', [])
    print(f"Generating templates for {len(patterns)} pattern(s)...")
    
    for i, pattern_data in enumerate(patterns):
        # Create a simple pattern object
        class PatternObj:
            def __init__(self, data):
                self.hash = data['hash']
                self.code = data['code']
                self.language = data['language']
                self.variables = data.get('variables', [])
                self.count = data['count']
        
        pattern = PatternObj(pattern_data)
        template = generator.generate_from_pattern(
            pattern,
            name=f"pattern_{pattern.hash[:8]}"
        )
        print(f"  Generated: {template.name} ({template.language})")
    
    # Save templates
    if args.output_dir:
        paths = generator.save_all_templates()
        print(f"\nSaved {len(paths)} template(s) to: {args.output_dir}")
    
    return 0


def cmd_script(args):
    """Generate automation scripts from patterns."""
    # Load patterns from analysis
    if not args.input:
        print("Error: --input required (JSON output from analyze command)")
        return 1
    
    try:
        data = json.loads(Path(args.input).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading input: {e}")
        return 1
    
    script_gen = ScriptGenerator(output_dir=args.output_dir or './scripts')
    
    patterns = data.get('patterns', [])
    print(f"Generating scripts for {len(patterns)} pattern(s)...")
    
    for i, pattern_data in enumerate(patterns):
        class PatternObj:
            def __init__(self, data):
                self.hash = data['hash']
                self.code = data['code']
                self.language = data['language']
                self.variables = data.get('variables', [])
                self.count = data['count']
        
        pattern = PatternObj(pattern_data)
        
        if pattern.language in ('shell', 'bash'):
            script = script_gen.generate_from_commands(
                pattern.code.split('\n'),
                name=f"automation_{pattern.hash[:8]}"
            )
            
            if args.output_dir:
                filename = f"automation_{pattern.hash[:8]}.sh"
                path = script_gen.save_script(script, filename)
                print(f"  Generated: {path}")
            else:
                print(f"\n# Script for pattern {pattern.hash[:8]}")
                print(script)
    
    return 0


def cmd_full(args):
    """Run full analysis and generate templates/scripts."""
    print("=" * 60)
    print("Pattern Miner - Full Analysis")
    print("=" * 60)
    
    # Step 1: Code analysis
    print("\n[1/4] Analyzing code files...")
    code_analyzer = CodeAnalyzer(min_lines=args.min_lines)
    code_patterns = code_analyzer.analyze_directory(
        args.directory,
        args.extensions.split(',') if args.extensions else ['.py', '.sh', '.bash']
    )
    print(f"  Found {len(code_patterns)} code pattern(s)")
    
    # Step 2: History analysis
    print("\n[2/4] Analyzing command history...")
    history_analyzer = HistoryAnalyzer()
    history_file = args.history_file or get_default_history_path()
    if history_file:
        history_analyzer.load_history(history_file)
        history_patterns = history_analyzer.analyze()
        print(f"  Found {len(history_patterns)} history pattern(s)")
    else:
        history_patterns = []
        print("  No history file found, skipping")
    
    # Step 3: Generate templates
    print("\n[3/4] Generating templates...")
    template_gen = TemplateGenerator(output_dir=args.output_dir or './pattern-miner-output')
    
    all_patterns = code_patterns + history_patterns
    for pattern in all_patterns:
        template_gen.generate_from_pattern(pattern)
    
    if args.output_dir:
        template_paths = template_gen.save_all_templates()
        print(f"  Saved {len(template_paths)} template(s)")
    
    # Step 4: Generate scripts
    print("\n[4/4] Generating scripts...")
    script_gen = ScriptGenerator(output_dir=args.output_dir or './pattern-miner-output')
    
    script_count = 0
    for pattern in all_patterns:
        if pattern.language in ('shell', 'bash'):
            script = script_gen.generate_from_commands(
                pattern.code.split('\n'),
                name=f"automation_{pattern.hash[:8]}"
            )
            if args.output_dir:
                script_gen.save_script(script, f"automation_{pattern.hash[:8]}.sh")
                script_count += 1
    
    print(f"  Generated {script_count} script(s)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Code patterns: {len(code_patterns)}")
    print(f"History patterns: {len(history_patterns)}")
    print(f"Total patterns: {len(all_patterns)}")
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
    
    # Save summary JSON
    if args.output_dir:
        summary = {
            'code_patterns': len(code_patterns),
            'history_patterns': len(history_patterns),
            'total_patterns': len(all_patterns),
            'patterns': [
                {
                    'hash': p.hash,
                    'language': p.language,
                    'count': p.count,
                    'type': 'code' if p in code_patterns else 'history'
                }
                for p in all_patterns
            ]
        }
        summary_path = Path(args.output_dir) / 'summary.json'
        summary_path.write_text(json.dumps(summary, indent=2))
        print(f"Summary saved to: {summary_path}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Pattern Miner - Detect duplicate patterns in code and commands',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pattern-miner analyze ./my-project
  pattern-miner history --days 30
  pattern-miner full ./my-project --output-dir ./templates
  pattern-miner template --input patterns.json --output-dir ./templates
        """
    )
    
    parser.add_argument('--version', action='version', version='pattern-miner 0.1.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code for duplicate patterns')
    analyze_parser.add_argument('directory', help='Directory to analyze')
    analyze_parser.add_argument('-e', '--extensions', default='.py,.sh,.bash',
                               help='File extensions to analyze (comma-separated)')
    analyze_parser.add_argument('-m', '--min-lines', type=int, default=3,
                               help='Minimum lines for pattern detection')
    analyze_parser.add_argument('-o', '--output', help='Output JSON file')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # History command
    history_parser = subparsers.add_parser('history', help='Analyze command history')
    history_parser.add_argument('-f', '--history-file', help='History file path')
    history_parser.add_argument('-d', '--db-path', help='SQLite database path')
    history_parser.add_argument('--days', type=int, help='Analyze last N days')
    history_parser.add_argument('--min-count', type=int, default=3,
                               help='Minimum occurrences for frequent commands')
    history_parser.set_defaults(func=cmd_history)
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Generate templates')
    template_parser.add_argument('-i', '--input', required=True,
                                help='Input JSON file from analyze command')
    template_parser.add_argument('-o', '--output-dir', help='Output directory for templates')
    template_parser.set_defaults(func=cmd_template)
    
    # Script command
    script_parser = subparsers.add_parser('script', help='Generate scripts')
    script_parser.add_argument('-i', '--input', required=True,
                              help='Input JSON file from analyze command')
    script_parser.add_argument('-o', '--output-dir', help='Output directory for scripts')
    script_parser.set_defaults(func=cmd_script)
    
    # Full command
    full_parser = subparsers.add_parser('full', help='Run full analysis and generation')
    full_parser.add_argument('directory', help='Directory to analyze')
    full_parser.add_argument('-e', '--extensions', default='.py,.sh,.bash',
                            help='File extensions to analyze')
    full_parser.add_argument('-f', '--history-file', help='History file path')
    full_parser.add_argument('-m', '--min-lines', type=int, default=3,
                            help='Minimum lines for pattern detection')
    full_parser.add_argument('-o', '--output-dir', help='Output directory')
    full_parser.set_defaults(func=cmd_full)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
