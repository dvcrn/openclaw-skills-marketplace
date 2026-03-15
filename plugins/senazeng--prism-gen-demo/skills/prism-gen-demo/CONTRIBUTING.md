# Contributing to PRISM-Gen Demo

Thank you for your interest in contributing to PRISM-Gen Demo! This document provides guidelines and instructions for contributors.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How Can I Contribute?

### Reporting Bugs
- Check if the bug has already been reported in Issues
- Use the bug report template
- Include steps to reproduce, expected behavior, and actual behavior
- Include system information and error messages

### Suggesting Enhancements
- Check if the enhancement has already been suggested
- Use the feature request template
- Explain why this enhancement would be useful
- Provide examples of how it would work

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

### Prerequisites
- Python 3.8+
- Bash shell
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/prism-gen-demo.git
cd prism-gen-demo

# Install dependencies
bash setup.sh

# Run tests
bash scripts/test_basic.sh
bash scripts/test_full_functionality.sh
```

### Project Structure
```
prism-gen-demo/
├── data/           # Example data files
├── scripts/        # Core scripts
├── config/         # Configuration files
├── docs/           # Documentation
├── examples/       # Usage examples
├── tests/          # Test scripts
├── output/         # Generated output
└── plots/          # Generated plots
```

## Coding Standards

### Bash Scripts
- Use `#!/bin/bash` shebang
- Set `set -euo pipefail` for error handling
- Use meaningful variable names
- Add comments for complex logic
- Follow shellcheck recommendations

### Python Code
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for functions
- Handle exceptions gracefully
- Use logging instead of print for production code

### Documentation
- Update README.md for user-facing changes
- Update CHANGELOG.md for all releases
- Add comments in code for complex algorithms
- Keep SKILL.md up to date

## Testing

### Test Categories
1. **Unit Tests**: Individual script functionality
2. **Integration Tests**: Script interactions
3. **Data Tests**: Data format and integrity
4. **Performance Tests**: Large dataset handling

### Running Tests
```bash
# Basic functionality tests
bash scripts/test_basic.sh

# Full functionality tests
bash scripts/test_full_functionality.sh

# Visualization tests
bash scripts/test_visualization.sh

# Paper-ready tests (comprehensive)
bash scripts/paper_ready_test.sh
```

### Adding Tests
1. Create test script in `tests/` directory
2. Follow naming convention: `test_*.sh`
3. Include setup, execution, and cleanup
4. Provide clear pass/fail criteria

## Documentation

### Required Documentation
- **SKILL.md**: Main skill documentation
- **README.md**: Project overview
- **TUTORIAL.md**: Step-by-step guide
- **CHANGELOG.md**: Release history
- **CONTRIBUTING.md**: This file
- **LICENSE**: License information

### Writing Documentation
- Use clear, concise language
- Include examples where helpful
- Use markdown formatting
- Keep documentation up to date with code changes

## Release Process

### Versioning
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Release Checklist
1. Update version in SKILL.md
2. Update CHANGELOG.md
3. Run all tests
4. Update documentation
5. Create release package
6. Tag release in git
7. Publish to ClawHub

## Areas Needing Contribution

### High Priority
- Performance optimization for large datasets
- Additional visualization types
- More example datasets
- Improved error handling

### Medium Priority
- Web interface development
- Additional export formats
- More analysis algorithms
- Extended documentation

### Low Priority
- Theming and customization
- Additional language support
- Advanced configuration options

## Getting Help

- Check existing documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md
- README.md
- Release notes

Thank you for contributing to PRISM-Gen Demo!