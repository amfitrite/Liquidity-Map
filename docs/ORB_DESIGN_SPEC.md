# Liquidity Orb Visual Design Specification

**Status:** Visual reference / implementation guidance  
**Scope:** Orb appearance only. This document does not define liquidity detection, scoring, mitigation calculations, or probability logic.

## Design goals

1. Every detected liquidity object remains an individual orb. Never merge nearby liquidity objects into one orb.
2. Nearby objects may be visually fanned/offset at crowded zoom levels to prevent occlusion, but their true price/time coordinates must remain unchanged and recoverable.
3. Tier identity must be recognizable from more than diameter: use distinct core geometry, material, ring structure, and restrained VFX.
4. Tier color is persistent across orb and trail. Mitigation must not overwrite the tier identity.
5. The orb is a marker for a candle-derived liquidity hypothesis, not a measurement of actual resting order-book size.

## Tier identity system

| Tier | Color | Core / material | Signature geometry | Visual intensity |
|---|---|---|---|---|
| SSS | Ice cyan-white `#E0F7FF` | Celestial crystal | Faceted crystal core, 3 concentric rings, four small radial glints | Highest |
| SS | Cyan `#22D3EE` | Vortex / liquid energy | Smooth energy core, 2 orbit rings, subtle vortex arcs | High |
| S | Blue `#3B82F6` | Sapphire / prism | Geometric faceted core, 1 segmented orbit | Medium-high |
| A | Violet `#A78BFA` | Arcane / ethereal | Soft spherical core, 1 fine ring, faint aura | Medium |
| B | Silver `#A1A1AA` | Brushed metal | Metallic bead, thin partial ring, controlled specular highlight | Low |
| C | Slate `#64748B` | Rough mineral | Small irregular/faceted stone core, minimal outline | Very low |
| D | Graphite `#475569` | Shadow seed | Dark compact core, broken outline, no aura | Minimal |

### Suggested standard-size reference

These are starting values for a 1x UI scale, not fixed limits:

| Tier | Nominal diameter |
|---|---:|
| SSS | 36 px |
| SS | 31 px |
| S | 26 px |
| A | 21 px |
| B | 17 px |
| C | 13 px |
| D | 10 px |

Allow modest within-tier size variation from the structural-strength score. Do not let size alone encode the full score.

## State styling (orthogonal to tier)

Tier and lifecycle are separate dimensions.

- **Unmitigated:** full tier color, normal material detail, active glow.
- **Approaching:** preserve tier color; optional slow, subtle pulse on the outer aura.
- **Partially mitigated:** preserve the tier-colored core; reduce glow and show a segmented/partially faded ring.
- **Fully mitigated:** retain the original tier geometry and hue in a desaturated, low-opacity form; stop active animation.
- **Reclaimed:** preserve tier identity and add a small amber event marker/outline. Amber is a state marker, not a replacement tier color.
- **Expired/archived:** preserve tier identity at very low opacity; no continuous animation.

Do not imply a precise mitigation percentage unless the detection model defines and validates that percentage.

## Stacking and overlap

- Keep one orb per liquidity object, including objects at nearly identical prices.
- Never replace a group with a single aggregate orb.
- When objects overlap, use a small visual fan/stack offset or depth layering only for presentation.
- Provide hover/click selection so each underlying object remains individually inspectable.
- Do not alter stored price/time coordinates to create the visual offset.
- A cluster may be indicated by proximity or a subtle bracket/halo, but its members remain separate.

## Trail relationship

Trail is a separate user-selectable renderer style. Orb tier color and trail tier color must match.

Supported trail families include Minimal Line, Soft Glow, Particle Trail, Comet Trail, Energy Ribbon, Chinese Ink Brush, Dry Brush, Silk Flow, Miasma, Spirit Wisp, Arcane Rune, Cosmic Nebula, Lightning Arc, Windstream, Ember Trail, Frost Shard, Blade Slash, Energy Pulse, Spectral Flame, Sakura/Petal, Liquid Mercury, Digital Glitch, Fiber Optic, and Prism Flow.

The chosen effect may change shape, texture, and animation, but must not change tier, lifecycle state, object coordinates, or any calculation. For dense historical regions, bake or simplify static trails; animate only the current/replay window.

## Sprite production guidance

- Produce each tier as an independent transparent sprite or layered vector asset.
- Recommended source canvas: 128x128 or 256x256, centered with safe padding for glow.
- Export at 1x, 2x, and 3x (or use resolution-independent vector assets).
- Keep core, ring, aura/glow, and state overlay separable where practical.
- Use premultiplied alpha correctly; avoid dark fringes on transparent edges.
- Include a low-detail fallback for zoomed-out views and a high-detail version for close zoom.
- Do not bake trail effects into the orb sprite. Trail is rendered independently.
- Provide a reduced-motion / no-animation mode.
- Test against the actual dark chart background and at small sizes; tiers C and D must remain distinguishable.

## Acceptance checklist

- [ ] Seven tiers are visually distinguishable when displayed at equal diameter.
- [ ] Tier color remains identifiable in all lifecycle states.
- [ ] Individual nearby liquidity objects can be selected independently.
- [ ] Visual offsets never modify underlying price/time coordinates.
- [ ] Trail style can be changed without changing liquidity data or calculations.
- [ ] Historical objects can render statically without continuous particle updates.
- [ ] Low-detail fallback remains legible at zoomed-out scales.
- [ ] Orb sprites have transparent backgrounds and no baked-in chart grid.

## Reference artwork

See [orb-tier-reference.svg](../assets/orb-tier-reference.svg). It is an illustrative design sheet for discussion and sprite production, not a final production atlas.
