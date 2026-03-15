# Nutrigenomics — OpenClaw Implementation Guide

This document provides step-by-step instructions for submitting and deploying Nutrigenomics to the OpenClaw platform.

---

## Pre-Submission Checklist

- [ ] Python 3.11+ available
- [ ] All dependencies in `requirements.txt` installable
- [ ] `openclaw_adapter.py` entry point functional
- [ ] `openclaw.json` manifest complete and valid
- [ ] Documentation files present:
  - [ ] `SKILL_OPENCLAW.md` (user-facing)
  - [ ] `README_OPENCLAW.md` (comprehensive guide)
  - [ ] This file (`IMPLEMENTATION.md`)
- [ ] Example genetic data in `tests/` for validation
- [ ] MIT license included (`LICENSE`)

---

## File Structure for Submission

```
nutrigenomics-openclaw/
├── openclaw.json                 ← Skill manifest (REQUIRED)
├── openclaw_adapter.py           ← Entry point (REQUIRED)
├── SKILL_OPENCLAW.md             ← User documentation (REQUIRED)
├── README_OPENCLAW.md            ← Comprehensive guide
├── IMPLEMENTATION.md             ← This file
├── LICENSE                       ← MIT License
├── requirements.txt              ← Python dependencies
├── nutrigenomics.py            ← Core analysis engine
├── parse_input.py                ← Input parser (23andMe, AncestryDNA, VCF)
├── extract_genotypes.py          ← SNP lookup
├── score_variants.py             ← Risk scoring algorithm
├── generate_report.py            ← Report generation
├── repro_bundle.py               ← Reproducibility export
├── data/
│   └── snp_panel.json            ← 58 SNP definitions
├── tests/
│   ├── synthetic_patient.csv     ← Test data
│   └── test_nutrigenomics.py           ← Unit tests
└── examples/
    ├── generate_patient.py       ← Demo patient generator
    └── output/                   ← Pre-rendered example outputs
```

---

## Installation & Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Validate Core Functionality

```bash
# Test with synthetic patient
python examples/generate_patient.py --run

# Run unit tests
pytest tests/test_nutrigenomics.py -v
```

### 3. Test OpenClaw Adapter

```bash
# Generate a test patient
python examples/generate_patient.py --output tests/test_patient.csv

# Run analysis via adapter
python openclaw_adapter.py --input tests/test_patient.csv --format 23andme --output /tmp/test_results

# Check output
ls -la /tmp/test_results/
cat /tmp/test_results/nutrigenomics_report.md
```

### 4. Validate Manifest

```bash
# Ensure openclaw.json is valid JSON
python -m json.tool openclaw.json > /dev/null && echo "✓ Valid JSON"
```

---

## OpenClaw Platform Integration

### Step 1: Register with OpenClaw

1. Create account at https://openclaw.ai
2. Navigate to "Skills" → "Submit Skill"
3. Choose "Upload from GitHub" or "Manual Upload"

### Step 2: Upload Files

OpenClaw requires:
- **Main entry point**: `openclaw_adapter.py`
- **Manifest**: `openclaw.json`
- **Documentation**: `SKILL_OPENCLAW.md`, `README_OPENCLAW.md`
- **All supporting modules**: `parse_input.py`, `extract_genotypes.py`, etc.

### Step 3: Configure Entry Point

In `openclaw.json`, the entry point is:
```json
"entry_point": "openclaw_adapter:run_analysis"
```

This calls the `run_analysis()` function in `openclaw_adapter.py`.

### Step 4: Set Input Schema

Users upload files via:
```json
"input_schema": {
  "type": "object",
  "properties": {
    "input_file": {
      "type": "string",
      "description": "Path to genetic data file"
    }
  }
}
```

OpenClaw handles file upload and provides the path to `input_file`.

### Step 5: Configure Output Handling

The adapter returns:
```python
{
    "status": "success",
    "message": "Analysis complete",
    "report_path": "/path/to/nutrigenomics_report.md",
    "figures": {
        "radar": "/path/to/nutrigenomics_radar.png",
        "heatmap": "/path/to/nutrigenomics_heatmap.png"
    },
    "summary": "Executive summary...",
    "risk_scores": {...}
}
```

OpenClaw will:
- Display the summary to the user
- Provide download links for report and figures
- Show risk scores in structured format

---

## API Usage (for OpenClaw Integration)

### Python Function Call

```python
from openclaw_adapter import NutrigenomicsOpenClaw

adapter = NutrigenomicsOpenClaw()
result = adapter.analyse_file(
    input_file="/path/to/genome.csv",
    file_format="auto",
    output_dir="/tmp/results"
)

if result["status"] == "success":
    print(f"Report: {result['report_path']}")
    print(f"Summary: {result['summary']}")
    print(f"Risk Scores: {result['risk_scores']}")
```

### CLI Usage (for testing)

```bash
python openclaw_adapter.py \
    --input /path/to/genome.csv \
    --format auto \
    --output /tmp/results
```

Returns JSON output on stdout.

---

## Environment & Dependencies

### Python Version
- Minimum: Python 3.11
- Recommended: Python 3.12

### Dependencies (from `requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥1.5.0 | Data parsing and manipulation |
| numpy | ≥1.24.0 | Numerical computations |
| matplotlib | ≥3.7.0 | Report visualisations (radar chart) |
| seaborn | ≥0.12.0 | Advanced visualisations (heatmap) |
| reportlab | ≥4.0.0 | PDF report generation (optional) |

### Installation Command

```bash
pip install pandas>=1.5.0 numpy>=1.24.0 matplotlib>=3.7.0 seaborn>=0.12.0 reportlab>=4.0.0
```

---

## Troubleshooting Deployment

### Issue: "Module not found: parse_input"

**Solution**: Ensure all Python files are in the same directory. OpenClaw needs:
```
openclaw_adapter.py
parse_input.py
extract_genotypes.py
score_variants.py
generate_report.py
repro_bundle.py
```

### Issue: "SNP panel not found"

**Solution**: The `data/snp_panel.json` file must be included. OpenClaw should preserve directory structure.

### Issue: "PNG figures not generating"

**Solution**: Matplotlib requires display backend. The adapter handles this by setting:
```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

### Issue: Timeout on large files

**Solution**: Test with files up to 50 MB. Larger files may timeout. Consider:
- Implementing streaming parser
- Compressing input (`.gz`)
- Splitting analysis by chromosome

---

## Security & Privacy Verification

Before submission, verify:

- [ ] **No external API calls** — All processing is local
- [ ] **No data persistence** — Genetic data not saved after analysis
- [ ] **No network transmission** — Check with `strace` or network monitoring
- [ ] **Input sanitisation** — File paths validated, no path traversal
- [ ] **Error messages safe** — No sensitive data in exceptions
- [ ] **Temp files cleaned** — Using `tempfile` with auto-cleanup

### Verification Commands

```bash
# Check for network calls
python -c "
import openclaw_adapter
import unittest.mock as mock

with mock.patch('urllib.request.urlopen') as mock_urlopen:
    adapter = openclaw_adapter.NutrigenomicsOpenClaw()
    # Run analysis
    # Assert mock_urlopen not called
"

# Monitor file system
strace -e openat python openclaw_adapter.py --input tests/synthetic_patient.csv
```

---

## Performance Benchmarks

Expected performance on typical consumer genetic data:

| Operation | Time | Notes |
|-----------|------|-------|
| Parse 500k variants | 2-5 sec | Depends on file I/O speed |
| Extract SNPs (58 panel) | <1 sec | Fast dictionary lookup |
| Score variants | <1 sec | Vectorized numpy operations |
| Generate report + figures | 3-8 sec | Matplotlib rendering |
| **Total time** | **5-15 sec** | Full end-to-end analysis |

### Optimisation Tips

- **Parser**: Already optimised with pandas vectorisation
- **Scorer**: Uses numpy broadcasting
- **Figures**: Use `plt.imsave()` for faster PNG export
- **Async**: Consider async file I/O for large batches

---

## Monitoring & Logging

### Logging Configuration

The adapter writes to stdout:
```
[Nutrigenomics] Parsing genetic file: genome.csv
[Nutrigenomics] Loaded 500,000 variants
[Nutrigenomics] Extracting SNP genotypes from panel...
[Nutrigenomics] Panel coverage: 58/58 SNPs (100.0%)
```

OpenClaw should capture these for user feedback.

### Error Logging

Exceptions are caught and returned in result dict:
```python
{
    "status": "error",
    "message": "User-friendly error message",
    "report_path": None
}
```

Never expose stack traces to users.

---

## Version Management

### Versioning Scheme

`MAJOR.MINOR.PATCH-platform`

Examples:
- `0.2.0-openclaw` — First OpenClaw release
- `0.3.0-openclaw` — Bug fixes, new SNP additions
- `1.0.0-openclaw` — Production-ready release

### Updating SNP Panel

The `data/snp_panel.json` is the versioned source of truth. To add SNPs:

1. Edit `data/snp_panel.json`
2. Add new SNP entry with structure:
   ```json
   "rs12345678": {
       "gene": "GENE_NAME",
       "nutrient": "Nutrient Category",
       "effect": "Description of risk allele",
       "weight": 0.5,
       "evidence": "Source (e.g., GWAS Catalog)"
   }
   ```
3. Update `SKILL_OPENCLAW.md` documentation
4. Increment version in `openclaw.json`
5. Update `CHANGELOG.md`

---

## Support & Maintenance

### Issue Reporting

Users can report issues via:
- OpenClaw platform: In-app feedback
- GitHub: [nutrigenomics/issues](https://github.com/clawbio/nutrigenomics/issues)
- Email: david@nutrigenomics.dev

### Regular Maintenance

- [ ] Monthly: Review user feedback and error logs
- [ ] Quarterly: Update SNP panel with new research
- [ ] Annually: Major version release with new features

---

## OpenClaw Submission Checklist

### Functional Requirements
- [ ] `openclaw_adapter.py` runs without errors
- [ ] `run_analysis()` function signature matches schema
- [ ] Handles all three input formats (23andMe, AncestryDNA, VCF)
- [ ] Generates Markdown report
- [ ] Generates PNG figures (radar, heatmap)
- [ ] Returns JSON result with expected keys

### Documentation Requirements
- [ ] `SKILL_OPENCLAW.md` explains user-facing functionality
- [ ] `README_OPENCLAW.md` provides comprehensive guide
- [ ] `openclaw.json` manifest is complete and valid
- [ ] Includes examples of input data
- [ ] Includes disclaimer about medical/educational nature

### Code Quality
- [ ] Python code passes `pylint` or `flake8`
- [ ] No hardcoded paths (uses relative paths)
- [ ] Error handling for edge cases
- [ ] Logging for debugging

### Legal & Compliance
- [ ] MIT license included
- [ ] Privacy policy clear (no data transmission)
- [ ] Disclaimer present (not medical advice)
- [ ] Attribution to source papers included

---

## Post-Submission

### Analytics to Monitor

Track via OpenClaw analytics:
- Number of analyses run per day/week/month
- Popular nutrients/genes users are interested in
- Error rates (file format issues, etc.)
- User feedback and ratings

### Feature Requests to Consider

Based on user feedback:
- Microbiome integration (16S rRNA input)
- Longitudinal tracking (compare reports over time)
- HLA typing for immune-mediated food reactions
- Integration with dietary apps

---

## Contact & Support

- **Author**: David de Lorenzo (@drdaviddelorenzo)
- **GitHub**: [nutrigenomics](https://github.com/clawbio/nutrigenomics)
- **Email**: david@nutrigenomics.dev
- **OpenClaw**: In-app support channel

---

*Last updated: February 2026*
*For OpenClaw v1.x+*
