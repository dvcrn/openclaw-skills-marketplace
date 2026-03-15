# Contributing to Linux Kernel Crash Debug Skill

First off, thank you for considering contributing to this project! It's people like you that make this tool better for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Description**: A clear description of the bug
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, crash version, kernel version
- **Additional context**: Any other context, logs, or screenshots

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Summary**: A clear title for the suggestion
- **Motivation**: Why this enhancement would be useful
- **Detailed description**: How you envision it working
- **Alternatives**: Any alternative solutions you've considered

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Improving Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos or unclear sentences
- Adding examples or use cases
- Translating documentation
- Improving the skill content

## Development Guidelines

### Skill File Structure

```
linux-kernel-crash-debug/
├── SKILL.md                 # Main skill (keep under 500 lines)
├── references/              # Detailed documentation
│   ├── advanced-commands.md
│   ├── vmcore-format.md
│   └── case-studies.md
└── README*.md              # Documentation
```

### Writing Guidelines

1. **Keep SKILL.md concise**: It should be a quick reference, not a textbook
2. **Put details in references/**: Advanced content goes in separate files
3. **Use examples**: Real command examples help understanding
4. **Link to sources**: Reference official documentation

### Commit Message Format

Use clear, descriptive commit messages:

```
<type>: <subject>

<body (optional)>
```

Types:
- `Add`: New feature or content
- `Fix`: Bug fix
- `Update`: Update existing content
- `Refactor`: Restructure without changing content
- `Docs`: Documentation only changes

## Code of Conduct

Be respectful and inclusive. We're all here to learn and help each other debug kernel crashes!

## Questions?

Feel free to open an issue with the "question" label, or reach out to the maintainers.

---

Thank you for your contributions!