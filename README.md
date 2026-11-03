# Liquidity Map

A multi-timeframe liquidity visualization project.

## Visual design references

- [Orb tier identity and selectable styles](docs/ORB_DESIGN_SPEC.md)
- [Tier and style reference sheet](assets/orb-tier-reference.svg)
- [Solar Crown style close-up](assets/orb-aaa-reference.svg)
- [Ten premium cosmetic movement trails with seven-tier heatmap colors](assets/trail-effect-reference.svg)

**Terminology:** Liquidity tiers are SSS, SS, S, A, B, C, and D. "AAA" refers only to optional premium game-quality rendering, never to a liquidity tier or signal grade. The Solar Crown artwork is a selectable orb skin.

Trail hue follows the tier heatmap: SSS white, SS red, S orange, A yellow, B light blue, C blue, and D deep blue. The heatmap recolors trails only; orb core colors remain unchanged. The trail reference is a premium cosmetic VFX direction sheet, not a production sprite atlas. Final in-app effects require layered shader/sprite implementation and measured performance tuning. Final sprites should use transparent backgrounds, separable core/ring/aura layers, and multiple resolution or level-of-detail variants.
