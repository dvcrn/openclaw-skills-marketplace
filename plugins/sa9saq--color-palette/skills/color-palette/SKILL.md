---
name: color-palette
description: "Generate color palettes and check WCAG accessibility compliance for UI design."
---

# Color Palette

Generate harmonious color palettes and verify accessibility compliance.

## Instructions

1. **Generate palette** from a base color (hex, RGB, HSL, or name):
   - **Complementary**: Opposite on color wheel (+180°)
   - **Analogous**: Adjacent colors (±30°)
   - **Triadic**: Three evenly spaced (120° apart)
   - **Split-complementary**: Base + two adjacent to complement
   - **Monochromatic**: Shades/tints of one hue

2. **Brand palette**: From brand description or existing colors, suggest:
   - Primary, Secondary, Accent, Background, Text, Error, Success

3. **WCAG Accessibility Check**: For any fg/bg pair, calculate contrast ratio:
   ```
   Linearize: c ≤ 0.04045 → c/12.92, else ((c+0.055)/1.055)^2.4
   Luminance: L = 0.2126*R + 0.7152*G + 0.0722*B
   Ratio: (L_light + 0.05) / (L_dark + 0.05)
   ```
   - AA normal text: ≥ 4.5:1
   - AA large text: ≥ 3:1
   - AAA normal text: ≥ 7:1

4. **Output format**:
   ```
   🎨 Palette: Analogous from #3B82F6
   | Role      | Hex     | RGB           | Name       |
   |-----------|---------|---------------|------------|
   | Primary   | #3B82F6 | 59, 130, 246  | Blue       |
   | Secondary | #6366F1 | 99, 102, 241  | Indigo     |
   | Accent    | #22D3EE | 34, 211, 238  | Cyan       |

   ✅ #1E293B on #F8FAFC → 15.4:1 (AAA Pass)
   ❌ #94A3B8 on #F8FAFC → 2.8:1 (AA Fail — try #64748B)
   ```

5. **Export**: Generate CSS custom properties or Tailwind config:
   ```css
   :root { --color-primary: #3B82F6; --color-secondary: #6366F1; }
   ```

## Edge Cases

- **Dark mode**: Generate both light and dark variants
- **Color blindness**: Warn if palette relies on red/green distinction alone
- **Near-failing contrast**: Suggest nearest passing alternative

## Requirements

- No dependencies — pure calculation
- No API keys needed
