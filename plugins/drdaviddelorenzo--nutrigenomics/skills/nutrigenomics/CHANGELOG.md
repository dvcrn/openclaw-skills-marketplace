# Changelog

All notable changes to Nutrigenomics are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-02-28

### Added

#### OpenClaw Integration
- **`openclaw_adapter.py`** — Function-based entry point for OpenClaw platform
  - `NutrigenomicsOpenClaw` class wraps analysis engine
  - `run_analysis()` entry point for web-based deployment
  - Structured JSON output with status, summary, risk scores, and file paths
  - Comprehensive error handling with user-friendly messages
  
- **`openclaw.json`** — Skill manifest for OpenClaw platform
  - Entry point registration
  - Input/output schema definitions
  - Dependency specifications
  - Metadata for platform discovery

#### Documentation
- **`SKILL.md`** — OpenClaw skill instructions
  - User-facing documentation optimised for web platform
  - "How to get your genetic data" guide
  - Quick start workflow
  - Detailed gene descriptions with examples
  - Privacy & security emphasis
  - Comprehensive FAQ and troubleshooting
  
- **`README.md`** — Main documentation
  - Step-by-step tutorial
  - Input file format specifications with examples
  - Understanding results section
  - Support and contribution information
  
- **`IMPLEMENTATION.md`** — Technical deployment guide
  - Installation and testing procedures
  - Platform integration steps
  - Environment configuration
  - Performance benchmarks
  - Security verification checklist

- **`ATTRIBUTION.md`** — Attribution and acknowledgments
  - Author and maintainer information
  - Links to authoritative scientific sources
  - Software and library acknowledgments
  - Citation formats (BibTeX, APA, Chicago)
  - Transparency about AI-assisted development

#### Licensing & Community
- **`LICENSE`** — MIT License
  - Open-source, permissive licensing
  - Copyright © 2026 David de Lorenzo
  - Allows commercial and private use

- **`CONTRIBUTORS.md`** — Community contribution framework
  - How to report bugs
  - How to suggest SNPs
  - Code contribution guidelines
  - Recognition pathways for contributors
  - Code of conduct

#### Core Features
- **SNP Panel**: 58 SNPs across 40+ genes
- **Nutrient Categories**: 8 categories (micronutrients, macronutrients, omega-3s, caffeine, alcohol, sensitivities, antioxidants, detoxification)
- **File Format Support**: 23andMe, AncestryDNA, VCF
- **Risk Scoring**: 0-10 scale per nutrient
- **Visualisations**: Radar charts and interaction heatmaps
- **Privacy**: 100% local processing, no data transmission
- **Reproducibility**: Complete analysis bundles with documentation

### Changed
- Rebranded as Nutrigenomics for consumer-focused OpenClaw platform
- Web-based interface accessible to general users
- Simplified installation (direct GitHub or ClawHub registry)
- Updated all documentation for OpenClaw users

### Fixed
- `.DS_Store` files excluded from version control
- Removed unverified scientific citations
- Improved error messages for common issues
- Better handling of incomplete file formats

---

## Known Issues & Limitations

### About This Project

**Nutrigenomics** is the consumer-focused, web-based version of nutrigenomics analysis for OpenClaw. 

For healthcare professionals and researchers, a professional-grade command-line tool (**NutriGx Advisor**) is available for ClawBio platform, offering advanced features and integration capabilities for clinical and research workflows.

### Current Limitations (v0.2.0)

1. **Common Variants Only**
   - SNP panel limited to MAF > 1% in major populations
   - Rare pathogenic variants not detected
   - Primarily based on European GWAS data

2. **Gene × Environment Not Modeled**
   - Current analysis is genotype-only
   - Doesn't account for diet, lifestyle, environment
   - Future versions will integrate these factors

3. **File Size Limits**
   - VCF files should be <100MB
   - Large genomic files may timeout
   - Consider splitting very large datasets

4. **Population Context**
   - SNP effects derived from European ancestry studies
   - May not apply equally to other populations
   - Users encouraged to consult healthcare providers

5. **Educational Use Only**
   - Not a medical diagnostic tool
   - Cannot diagnose nutrient deficiencies
   - Cannot prescribe treatments
   - Should supplement, not replace, professional advice

### Recommendations for Users

- **Consult Healthcare Providers** — Always verify findings with qualified professionals
- **Biomarker Testing** — Confirm nutrient status with blood tests
- **Dietary Assessment** — Combine genetic findings with actual dietary intake analysis
- **Professional Guidance** — Work with dietitians for personalised meal planning

---

## Future Directions

Community feedback and contributions welcome! Areas of interest for future development:

- **Microbiome Integration** — Understand how gut bacteria interact with your genetics
- **Dietary Tracking** — Sync nutrition data with genetic recommendations
- **Population Expansion** — Include non-European ancestry populations
- **Advanced Analytics** — Machine learning for personalized predictions
- **Healthcare Integration** — Connect with medical professionals for clinical use

---

## Contributing

We welcome contributions from:
- **Researchers** — Suggest new SNPs or analysis methods
- **Developers** — Improve code, add features, fix bugs
- **Translators** — Help make documentation available in other languages
- **Users** — Share feedback and use cases

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for guidelines.

---

## Citation

If you use Nutrigenomics in research or education:

### BibTeX
```bibtex
@software{delorenzo2026nutrigenomics,
  author = {de Lorenzo, David},
  title = {Nutrigenomics: Personalised Nutrition from Genetic Data},
  year = {2026},
  url = {https://github.com/drdaviddelorenzo/nutrigenomics},
  version = {0.2.0}
}
```

### APA
de Lorenzo, D. (2026). *Nutrigenomics: Personalised nutrition from genetic data* (Version 0.2.0) [Software]. Retrieved from https://github.com/drdaviddelorenzo/nutrigenomics

### Chicago
de Lorenzo, David. "Nutrigenomics: Personalised Nutrition from Genetic Data." Version 0.2.0. Accessed [Date]. https://github.com/drdaviddelorenzo/nutrigenomics.

---

## Resources

- **GitHub**: https://github.com/drdaviddelorenzo/nutrigenomics
- **Author**: [@drdaviddelorenzo](https://github.com/drdaviddelorenzo)
- **Website**: https://drdaviddelorenzo.github.io
- **Email**: david@drdaviddelorenzo.dev
- **OpenClaw**: https://openclaw.ai
- **ClawHub**: https://clawhub.ai

---

## License

MIT License — See [LICENSE](LICENSE) for full details.

© 2026 David de Lorenzo
