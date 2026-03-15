# Contributing to guard-scanner

First off, thank you for considering contributing to `guard-scanner`! It's people like you that make open-source such a great community to learn, inspire, and create. 

We are building this tool to provide a lightweight, evidence-driven safety net for developers exploring agentic AI. We rely heavily on the community to help identify new threat vectors, false positives, and missing context validators.

## How to Contribute

### Adding Threat Patterns

The easiest way to contribute is adding or refining detection patterns in `src/patterns.js`, then adding semantic validation or scoring updates where needed.

```javascript
{
    id: 'YOUR_ID',           // Unique ID (CATEGORY_NAME format)
    cat: 'category-name',    // Threat category
    regex: /your-pattern/gi, // Detection regex
    severity: 'HIGH',        // CRITICAL | HIGH | MEDIUM | LOW
    desc: 'Description',     // Human-readable description
    codeOnly: true           // or docOnly: true, or all: true
}
```

### Adding IoCs

Add known malicious indicators to `src/ioc-db.js`:
- IPs, domains, URLs, usernames, filenames, or typosquat names

### Development

```bash
# Run the full project gate
npm test

# Scan the test fixtures
node src/cli.js test/fixtures/ --verbose --check-deps

# Run with all output formats
node src/cli.js test/fixtures/ --json --sarif --html --verbose
```

### Pull Request Checklist

- [ ] Tests pass (`npm test` — currently 342 tests / 84 suites)
- [ ] New patterns have test coverage in `test/scanner.test.js`
- [ ] No false positives against `test/fixtures/clean-skill/`
- [ ] Severity level is appropriate (see `docs/THREAT_TAXONOMY.md`)
- [ ] Description is clear and references source (Snyk, OWASP, CVE, etc.)
- [ ] Documentation and capability counts stay in sync (`docs/spec/capabilities.json`)
- [ ] Corpus and perf baselines remain green (`npm run test:corpus`, `npm run test:perf`)

## Reporting Security Issues

See [SECURITY.md](SECURITY.md) for responsible disclosure procedures.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Be respectful. We're all here to make AI agents safer.

## License

By contributing, you agree your contributions will be licensed under the MIT License.
