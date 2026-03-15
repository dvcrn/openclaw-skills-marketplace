# Nutrigenomics — Personalised Nutrition from Genetic Data

**Skill ID**: `nutrigenomics`  
**Platform**: OpenClaw  
**Version**: 0.2.0-openclaw  
**Status**: Ready for Community  
**Author**: David de Lorenzo  
**License**: MIT  

---

## What This Skill Does

The Nutrigenomics generates a **personalised nutrition report** from consumer genetic data. Upload your DNA file (23andMe, AncestryDNA, or VCF format), and receive:

✅ **Personalised nutrition recommendations** based on your genetic profile  
✅ **Risk assessment** for nutrient absorption and metabolism  
✅ **Gene-nutrient interaction analysis** covering 40+ nutritionally-relevant SNPs  
✅ **Visual reports** (radar charts, heatmaps) showing your nutrient risk profile  
✅ **Actionable guidance** on dietary optimisation and supplementation  

All analysis runs **locally** — your genetic data never leaves your device.

---

## How to Use

### Step 1: Prepare Your Genetic Data

You'll need raw genetic data from one of these sources:

- **23andMe**: Download your raw DNA data file (`.txt` or `.csv`)
- **AncestryDNA**: Download your raw DNA file (`.csv`)
- **Generic VCF**: Standard VCF format files

**Not sure where to get your data?**
- 23andMe: Account → Download your DNA → Raw Data → Download
- AncestryDNA: Account → Settings → Download DNA → Download your DNA

### Step 2: Upload Your File

1. Click **"Upload Genetic Data"** in OpenClaw
2. Select your 23andMe, AncestryDNA, or VCF file
3. The system will auto-detect your file format

### Step 3: Get Your Report

The Nutrigenomics will:

1. Parse your genetic data securely (locally, no uploads to external servers)
2. Extract relevant SNPs from your genome
3. Compute nutrient risk scores
4. Generate your personalised report with visualisations
5. Provide downloadable results

**Expected output:**
- `nutrigenomics_report.md` — Full nutrition report (Markdown)
- `nutrigenomics_radar.png` — Nutrient risk profile chart
- `nutrigenomics_heatmap.png` — Gene-nutrient interaction matrix
- `commands.sh` — Reproducibility documentation

---

## What Genes Does It Analyse?

The skill examines 40+ nutritionally-relevant genes including:

### Key Nutrient Metabolisers
- **MTHFR** → Folate & B12 metabolism
- **APOE** → Saturated fat response
- **FTO** → Energy balance & carb sensitivity
- **FADS1/2** → Omega-3 & PUFA metabolism
- **VDR** → Vitamin D absorption
- **BCMO1** → Beta-carotene → Vitamin A conversion
- **CYP1A2** → Caffeine metabolism
- **MCM6** → Lactose tolerance

### Plus: Antioxidant pathways, detoxification genes, food sensitivities, and more

See the complete SNP panel in `data/snp_panel.json`.

---

## Understanding Your Results

### Nutrient Risk Scores (0–10 scale)

- **0–3**: Low risk — Standard dietary advice applies
- **3–6**: Moderate risk — Dietary optimisation recommended
- **6–10**: Elevated risk — Consider testing and targeted supplementation

### Example Interpretation

If your **MTHFR risk score is 8.5**:
- You carry genetic variants affecting folate metabolism
- You may benefit from methylfolate supplementation
- Regular homocysteine testing is advisable
- Consider increasing folate-rich foods (leafy greens, legumes)

---

## Privacy & Security

✅ **All processing is local** — Your genetic data stays on your device  
✅ **No data transmission** — Nothing is uploaded to external servers  
✅ **No registration required** — Use anonymously  
✅ **Reports contain no raw genotypes** — Only gene names, SNP IDs, and risk categories  

The skill is designed with privacy-first principles. Even if you wanted to share your report with a healthcare provider, sensitive raw genotype data is never exposed.

---

## Important Limitations & Disclaimer

### 1. Not Medical Diagnosis
This skill provides **educational, research-oriented nutrigenomics analysis**. It does not constitute medical advice, diagnosis, or treatment recommendations. Always consult with a qualified healthcare provider before making significant dietary changes or starting supplements.

### 2. Common Variants Only
The panel covers SNPs with minor allele frequency (MAF) > 1% in major populations. **Rare pathogenic variants are not detected** and require clinical genetic testing.

### 3. Population Context
Effect sizes are predominantly derived from European GWAS cohorts. Risk estimates may vary across different ancestries and genetic backgrounds.

### 4. Gene × Environment Interaction
A "high risk" genetic score does **not** mean you have a nutrient deficiency. Genetic risk scores represent *potential* — they interact with:
- Your current diet
- Lifestyle & physical activity
- Stress & sleep
- Microbiome composition
- Medications
- Life stage (pregnancy, ageing, etc.)

### 5. Simpson's Paradox
Population-level genetic associations used to derive risk weights may not perfectly reflect your individual trajectory. Use this report as a **starting point for informed discussion** with a registered dietitian or nutrigenomics specialist.

---

## File Format Examples

### 23andMe Format
```
rsid	chromosome	position	genotype
rs3094315	1	742429	AA
rs12562034	1	758311	AG
rs12124819	1	776546	AA
```

### AncestryDNA Format
```
rsid,chromosome,position,allele1,allele2
rs3094315,1,742429,A,A
rs12562034,1,758311,A,G
```

### VCF Format
```
##fileformat=VCFv4.1
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
1	742429	rs3094315	A	.	.	.	.	GT	0/0
1	758311	rs12562034	A	G	.	.	.	GT	0/1
```

---

## Roadmap & Future Versions

- [ ] **v0.3**: Microbiome × genotype interaction (16S input)
- [ ] **v0.4**: Longitudinal tracking (compare reports over time)
- [ ] **v0.5**: HLA typing for immune-mediated food reactions
- [ ] **v1.0**: Multi-omics integration (metabolomics + genomics + dietary intake)

---

## Key References

This skill incorporates knowledge from the nutrigenomics research field. For scientific details about specific genes and nutrients:

- Consult **PubMed** (https://pubmed.ncbi.nlm.nih.gov/) for peer-reviewed publications
- Check **GWAS Catalog** (https://www.ebi.ac.uk/gwas/) for genetic associations
- Review **ClinVar** (https://www.ncbi.nlm.nih.gov/clinvar/) for variant interpretations
- Always verify with qualified healthcare providers before making dietary decisions

This skill is educational and research-oriented, not a medical diagnostic tool.

---

## Troubleshooting

### "File format not recognised"
- Ensure your file is truly 23andMe, AncestryDNA, or VCF format
- Check for unexpected line breaks or special characters
- Try re-downloading your raw data file from your test provider

### "Panel coverage low (< 50% SNPs found)"
- This is normal — not all SNPs are tested by every genotyping chip
- The report will flag "NOT_TESTED" where data is absent
- Low coverage still provides valuable insights for well-covered pathways

### "No recommendations generated"
- This means your genetic profile shows low risk across all nutrients
- You may still benefit from standard nutrition guidance
- Consider a registered dietitian for personalised advice unrelated to genetics

---

## Support & Contribution

Have suggestions for SNPs to add? Found a bug? Want to contribute?

- **GitHub**: [ClawBio/nutrigenomics](https://github.com/clawbio/nutrigenomics)
- **GitHub**: [@drdaviddelorenzo](https://github.com/drdaviddelorenzo)
- **Website**: https://drdaviddelorenzo.github.io
- **Email**: david@drdaviddelorenzo.dev
- **License**: MIT — free to use, modify, and distribute

---

## Version History

**v0.2.0-openclaw** (Feb 2026)
- Adapted for OpenClaw platform
- Improved file upload handling
- Enhanced user-facing documentation
- Simplified report generation for non-technical users

**v0.1.0** (Initial release)
- Core nutrigenomics analysis
- 40+ SNP panel
- Report generation with visualisations

---

*Nutrigenomics: Democratising personalised nutrition through open science and genetic literacy.*
