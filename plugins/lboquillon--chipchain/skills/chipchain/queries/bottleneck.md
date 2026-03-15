# Bottleneck / Chokepoint Identification Workflow

**Question pattern:** "What's the chokepoint in X supply chain?" / "Who's the single-source risk?"

## Known Top-10 Global Chokepoints (all Japanese)

> **ALL share figures are APPROXIMATE estimates (~2023-2024 training data). Treat as directional, not precise. Verify with current SEMI, TechCET, or Yole data.**

| Rank | Company | Material/Equipment | Approx. Share (unverified) | Substitutability |
|------|---------|-------------------|------------|-----------------|
| 1 | Ajinomoto Fine-Techno | ABF film (FC-BGA substrate insulation) | ~100% | Near-zero |
| 2 | Lasertec (6920.T) | EUV mask inspection equipment | ~100% | Near-zero |
| 3 | NuFlare (Toshiba sub) | E-beam mask writers | ~90% | Very low |
| 4 | DISCO (6146.T) | Dicing saws | ~80% | Low |
| 5 | Shin-Etsu Chemical (4063.T) | Photomask blanks | ~70% | Low |
| 6 | Toyo Gosei (4970.T) | Photoacid generators (PAGs) | ~60-70% | Low |
| 7 | SCREEN Holdings (7735.T) | Wafer cleaning equipment | ~60% | Moderate |
| 8 | HORIBA (6856.T) | Mass flow controllers | ~60% | Moderate |
| 9 | Shin-Etsu + SUMCO | Silicon wafers (combined) | ~55% | Moderate |
| 10 | Stella Chemifa + Morita | Electronic-grade HF (combined) | ~50-60% | Low |

## Raw Material Chokepoints (upstream)

> **Share figures are approximate estimates. Verify with current USGS, ITC, or industry data.**

| Material | Source (approx.) | Geography risk |
|----------|--------|---------------|
| Fluorspar (CaF2) | China ~60% of acid-grade | Feeds into HF, NF3, all fluorine chemistry |
| Rare earths (Ce for CMP) | China ~60-70% processing | Ceria for CMP slurry |
| High-purity quartz | Spruce Pine, NC (USA) — unique geological deposit | No substitute for CZ crucibles |
| Tantalum (for sputtering targets) | DRC ~60% artisanal coltan | Conflict mineral |
| Tungsten | China ~80% of mining | Sputtering targets, CVD |
| Hafnium | CEZUS/Framatome (France) #1 | Nuclear industry byproduct — linked to nuclear fuel demand |

## Investigation Method

1. **Map the supply chain node** — What material/equipment is in question?
2. **Count the suppliers** — How many companies globally can provide this at semiconductor grade?
3. **Assess concentration** — What % does the top supplier hold? Top 2? Top 3?
4. **Check geographic concentration** — Are all suppliers in one country/region?
5. **Evaluate substitutability** — Can a fab switch suppliers? How long does qualification take? (typically 6-24 months for materials)
6. **Identify tier-2 dependencies** — Even if there are multiple tier-1 suppliers, do they all depend on the same tier-2 input?
7. **Check for active diversification** — Is anyone investing to break the chokepoint? (Korean 국산화 push, Chinese 国产替代)

## Multilingual Search Queries

### Korean (집중도 / 독점):
```
[소재명] 독점 공급                → "[material] monopoly supply"
[소재명] 단일 공급원              → "[material] single source"
[소재명] 공급 집중                → "[material] supply concentration"
[소재명] 공급 리스크              → "[material] supply risk"
[소재명] 대체 불가                → "[material] irreplaceable"
[소재명] 공급선 다변화 필요       → "[material] needs supply diversification"
```

### Japanese (寡占 / 独占):
```
{材料名} 独占                    → "[material] monopoly"
{材料名} 寡占                    → "[material] oligopoly"
{材料名} 供給リスク              → "[material] supply risk"
{材料名} シェア 集中             → "[material] share concentration"
{材料名} 代替困難                → "[material] hard to substitute"
{材料名} ボトルネック            → "[material] bottleneck"
```

### Chinese — Mainland (垄断 / 卡脖子):
```
[材料名] 垄断                    → "[material] monopoly"
[材料名] 供应集中度              → "[material] supply concentration"
[材料名] 卡脖子                  → "[material] chokepoint/stranglehold"
[材料名] 单一供应商风险          → "[material] single-supplier risk"
[材料名] 不可替代                → "[material] irreplaceable"
[材料名] 供应链安全              → "[material] supply chain security"
```

### Chinese — Taiwan (壟斷 / 供應集中):
```
[材料名] 壟斷                    → "[material] monopoly"
[材料名] 供應集中                → "[material] supply concentration"
[材料名] 單一供應商              → "[material] single supplier"
[材料名] 供應風險                → "[material] supply risk"
[材料名] 替代方案                → "[material] alternatives"
[材料名] 供應鏈韌性              → "[material] supply chain resilience"
```

## Output: Chokepoint Assessment

```
Material: [X]
Current suppliers: [list with market share estimates]
Geographic concentration: [country/region breakdown]
Substitution difficulty: [Low/Medium/High/Near-impossible]
Qualification time: [months]
Active diversification efforts: [who's trying to enter]
Upstream dependencies: [tier-2 chokepoints]
Risk scenario: [what happens if supply is disrupted]
Confidence: [level + sources]
```
