# Changelog

All notable changes to the PRISM-Gen Demo skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-03-09
### Security & Compliance
- **ClawHub security scan fixes**: Addressed all issues identified in security scan report
- **Documentation accuracy**: Corrected misleading claims about "11 real PRISM files" and "no network dependencies"
- **Transparent network usage**: Clearly distinguishes between offline basic functions and network-required Python installation

### Added
- **Security verification tools**: 
  - `SECURITY.md`: Comprehensive security statement document
  - `scripts/verify_skill.sh`: Skill integrity verification with dry-run mode
  - `scripts/list_scripts_info.sh`: Detailed script information listing
  - `scripts/pre_package_check.sh`: Pre-upload integrity checker
- **Enhanced installation safety**:
  - Security warning banner in `setup.sh`
  - User confirmation for Python package installation
  - Option to skip Python installation for offline basic functions
- **Improved documentation**:
  - Accurate file listing (example + real data files)
  - Clear network dependency explanations
  - Complete security guidelines

### Fixed
- **Setup script improvements**: Added safety checks and user controls
- **Documentation consistency**: Updated all SKILL.md files and READMEs
- **Version consistency**: Unified version numbering across all files
- **Script self-check issue**: Fixed verification script detecting its own patterns

### Changed
- **User experience**: More transparent installation process
- **Security posture**: Proactive security verification before use
- **Compliance**: Meets ClawHub security standards for skill packages

### Compatibility
- **Backward compatible**: All existing functionality remains unchanged
- **Enhanced safety**: Added verification tools without breaking existing workflows
- **User control**: Optional Python installation preserves offline functionality

## [1.0.1] - 2026-03-07
### Fixed
- **Windows compatibility**: Removed all Zone.Identifier NTFS alternate data streams that caused upload failures on ClawHub
- **File cleanup**: Eliminated Windows-specific metadata files from the release package

### Changed
- **Bilingual documentation**: Updated SKILL.md to include both English and Chinese descriptions (English-first)
- **Documentation structure**: Implemented hybrid documentation scheme (concise README + detailed technical docs)
- **User experience**: Optimized environment check logic to reduce redundant output
- **Code cleanup**: Removed unnecessary backup files and streamlined scripts

### Compatibility
- **Backward compatible**: All existing functionality remains unchanged
- **Data format**: Fully compatible with previous version
- **API stability**: All command interfaces remain the same

## [1.0.0] - 2026-03-06
### Added
- Initial release of PRISM-Gen Demo skill
- Complete data analysis pipeline for drug discovery results
- 6 core functional modules:
  - Data source listing and inspection
  - Filtering and searching
  - Sorting and ranking
  - Merging and aggregation
  - Visualization (distribution plots, scatter plots)
  - Profile summarization
- 10 pre-calculated CSV data files covering all PRISM-Gen stages
- Comprehensive documentation in Chinese and English
- Automated environment setup script
- Package script for distribution

### Features
- **Zero computational dependency**: Only processes pre-calculated CSV files
- **High portability**: Works offline without HPC connection
- **Rich visualization**: Multiple chart types for data exploration
- **Structured output**: Clear, organized analysis reports
- **Drug discovery focus**: Specialized analysis for molecular screening

### Data Coverage
- Stage 3a: Proxy model optimized molecules (200 molecules)
- Stage 3b: xTB+DFT electronic screening results
- Stage 3c: GEM re-ranking results
- Stage 4a: ADMET filtered results
- Stage 4b: DFT validation (PySCF) results
- Stage 4c: Master summary table
- Stage 5a: Broad-spectrum docking results
- Stage 5b: Final candidate molecules

### Technical Specifications
- Language: Bash + Python
- Dependencies: pandas, numpy, matplotlib, seaborn, scipy, scikit-learn
- Platform: Linux, macOS, WSL
- Data format: CSV with standardized columns
- Output: PNG images, CSV files, text reports

### Fixed
- Variable scope issues in visualization scripts
- Bash to Python variable passing problems
- Missing module imports in Python code
- File path handling in scripts

### Security
- No external network calls
- Local file operations only
- No sensitive data in example files
- MIT license for open source use

## [0.1.0] - 2026-03-05
### Development Phase
- Initial skill structure design
- Core script development
- Data preparation and validation
- Documentation writing
- Testing and bug fixing

---

## Release Notes for Users

### For First-Time Users
1. Run `bash setup.sh` to install dependencies
2. Explore data with `bash scripts/demo_list_sources.sh`
3. Try the quick start examples in TUTORIAL.md

### For Advanced Users
1. Customize analysis in `config/` directory
2. Add your own CSV files to `data/` directory
3. Extend functionality by modifying scripts

### Known Issues
- Chinese font rendering may show warnings on some systems
- Large datasets (>10,000 rows) may require memory optimization
- Some visualization options are still being optimized

### Upgrade Instructions
When upgrading from previous versions:
1. Backup your custom configurations
2. Install new version
3. Run `bash setup.sh` to update dependencies
4. Test with example commands

---

## Future Roadmap

### Planned for v1.1.0
- [ ] Interactive web interface option
- [ ] Additional visualization types (heatmaps, radar charts)
- [ ] Batch processing capabilities
- [ ] Export to multiple formats (Excel, JSON, PDF)
- [ ] Performance optimization for large datasets

### Planned for v1.2.0
- [ ] Integration with other drug discovery tools
- [ ] Machine learning-based analysis
- [ ] Custom scoring functions
- [ ] Plugin system for extended functionality

### Long-term Goals
- Real-time collaboration features
- Cloud deployment options
- Mobile app interface
- Integration with laboratory information systems

---

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check the documentation in docs/
- Contact the maintainer

## License

This project is licensed under the MIT License - see LICENSE file for details.