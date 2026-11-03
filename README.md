# Liquidity Map

A multi-timeframe liquidity visualization project.

## Visual design references

- [Seven tier-specific orb designs and selectable styles](docs/ORB_DESIGN_SPEC.md)
- [Seven distinct orb tier designs (SVG)](assets/orb-tier-reference.svg)
- [Solar Crown style close-up](assets/orb-aaa-reference.svg)
- [Premium trail VFX reference — 10 distinct effects](assets/trail-effect-premium-reference.svg)
- [Trail VFX implementation and animation specification](docs/TRAIL_VFX_IMPLEMENTATION_SPEC.md)
- [Legacy trail reference — retained for comparison](assets/trail-effect-reference.svg)

**Terminology:** Liquidity tiers are SSS, SS, S, A, B, C, and D. "AAA" refers only to optional premium game-quality rendering, never to a liquidity tier or signal grade. The Solar Crown artwork is a selectable orb skin.

Trail hue follows the tier heatmap: SSS white, SS red, S orange, A yellow, B light blue, C blue, and D deep blue. The heatmap recolors trails only; orb core colors remain unchanged. The premium trail sheet is a visual design reference, not a production sprite atlas. Final in-app effects require layered shader/sprite implementation and measured performance tuning. Final sprites should use transparent backgrounds, separable material layers, and multiple resolution or level-of-detail variants.
