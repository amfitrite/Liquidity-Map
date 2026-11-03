# Liquidity Orb Visual Design Specification

**Status:** Visual reference / implementation guidance  
**Scope:** Orb rendering and user-selectable appearance only. This document does not define liquidity detection, scoring, mitigation calculations, or probability logic.

## Core separation: tier, style, quality

These are three independent settings:

- **Liquidity tier** communicates the model's assessed level strength. It controls the tier color and tier label.
- **Orb style** is a user-selectable visual skin. It controls core geometry, material, rings, aura, particles, and trail treatment.
- **Render quality** controls visual fidelity and performance cost. "AAA quality" means premium game-quality rendering; it is not a liquidity tier and must never appear as a signal grade.

Changing style or quality must never change detection, tier, score, lifecycle, coordinates, or probabilities.

## Liquidity tier identity

The tier hierarchy contains exactly seven tiers:

| Tier | Color | Core / material | Signature |
|---|---|---|---|
| SSS | Ice cyan-white `#E0F7FF` | Celestial crystal | Faceted crystal core, 3 concentric rings, radial glints |
| SS | Cyan `#22D3EE` | Vortex / liquid energy | Smooth energy core, 2 orbit rings, vortex arcs |
| S | Blue `#3B82F6` | Sapphire / prism | Geometric faceted core, 1 segmented orbit |
| A | Violet `#A78BFA` | Arcane / ethereal | Soft spherical core, 1 fine ring, faint aura |
| B | Silver `#A1A1AA` | Brushed metal | Metallic bead, partial ring, controlled specular highlight |
| C | Slate `#64748B` | Rough mineral | Small irregular/faceted stone core, minimal outline |
| D | Graphite `#475569` | Shadow seed | Dark compact core, broken outline, no aura |

Suggested nominal diameters at 1x: SSS 36 px, SS 31 px, S 26 px, A 21 px, B 17 px, C 13 px, D 10 px. These are starting values only. Size must not be the sole strength cue.

## User-selectable orb styles

Provide a visible Orb Style setting with a live preview. The selected style applies consistently to every tier while preserving each tier's color identity. Initial presets:

1. **Celestial Crystal** — faceted luminous core, precision rings, restrained star glints.
2. **Solar Crown** — white-hot center, six short crown rays, two offset elliptical orbits, floating sparks. This is the former gold concept; it is a style preset, not an AAA tier.
3. **Vortex Energy** — fluid energy core, flowing orbit arcs, subtle internal motion.
4. **Prismatic Core** — crystalline facets, sharp specular edges, segmented orbit.
5. **Arcane Aura** — smooth orb, fine rune-like ring, soft controlled aura.
6. **Minimal / Clean** — compact solid core, thin outline, no particles, minimal glow.

The style changes geometry and material only. Tier hue remains the source of truth; a style may use lighter/darker shades of that hue for highlights and shadows but must not replace it with a fixed style color.

## AAA game-quality rendering option

"AAA" is a **render-quality preset**, not a tier or signal grade. Offer these quality levels:

- **Performance:** static core, simple ring, no real-time particles; suitable for dense charts and integrated GPUs.
- **Balanced:** layered core, soft glow, limited particles on selected active objects.
- **High:** multi-layer material, refined specular lighting, smooth orbit animation, selective bloom and particle effects.
- **Ultra / AAA:** premium game-like finish with layered materials, high-resolution sprites or shaders, physically-inspired highlights, soft bloom, subtle refraction, fine particles, and smooth temporal animation. Apply strict object/particle budgets and automatic fallback under load.

Allow Auto quality to adapt to visible object count and frame rate. Quality changes only rendering fidelity; it must not affect market calculations. Provide reduced-motion and disable-animation options.

## Lifecycle styling (orthogonal to tier and style)

- **Unmitigated:** full tier color and normal selected-style detail.
- **Approaching:** preserve tier color; optional slow, subtle pulse.
- **Partially mitigated:** preserve the tier-colored core; reduce glow and partially fade/segment rings.
- **Fully mitigated:** retain original geometry and hue in a desaturated, low-opacity form; stop active animation.
- **Reclaimed:** preserve tier identity and add a small amber event marker. Amber is a state marker, not a replacement tier color.
- **Expired/archived:** preserve tier identity at very low opacity, static.

Do not imply a precise mitigation percentage unless the detection model defines and validates it.

## Trail options

Trail is independently selectable from orb style. Initial trail families: Minimal Line, Soft Glow, Particle, Comet, Energy Ribbon, Chinese Ink Brush, Dry Brush, Silk Flow, Miasma, Spirit Wisp, Arcane Rune, Cosmic Nebula, Lightning Arc, Windstream, Ember, Frost Shard, Blade Slash, Energy Pulse, Spectral Flame, Sakura/Petal, Liquid Mercury, Digital Glitch, Fiber Optic, and Prism Flow.

Trail represents the object's age/history from formation to now, not a price path or forecast. Active trails extend to NOW; swept/mitigated trails end at event time; historical trails remain static and fade. Trail color follows tier identity. Trail style must not change data or calculations.

## Overlap and multi-timeframe handling

- Keep one orb per liquidity object, including objects at nearly identical prices.
- Never replace nearby objects with one aggregate orb.
- At crowded zoom levels, use a small visual fan/stack offset or depth layering for presentation only.
- Preserve the true underlying price/time coordinates and make every object individually selectable.
- A proximity cluster may be shown as metadata or a subtle bracket, never as a replacement orb.

## Sprite and renderer guidance

- Keep core, ring, aura/glow, particles, and lifecycle overlays separable where practical.
- Recommended source canvas: 128x128 or 256x256 transparent sprites; export 1x/2x/3x or use vector/shaders.
- Do not bake trails into orb sprites.
- Use premultiplied alpha correctly and test against the actual dark chart background.
- Use low-detail LOD when zoomed out; reserve expensive effects for visible, high-priority objects.
- Bake or simplify historical trails; animate only active/replay-window objects.
- Keep renderer separate from detection/scoring so effects cannot block or modify market calculations.

## Settings and acceptance checklist

User settings should include Orb Style, Render Quality (Auto/Performance/Balanced/High/Ultra-AAA), Trail Style, effect intensity, particle density, motion intensity, and reduced-motion/disable-animation.

- [ ] Exactly seven liquidity tiers: SSS, SS, S, A, B, C, D.
- [ ] No "AAA" liquidity tier or signal grade is introduced by the visual system.
- [ ] Orb Style can be changed with a live preview.
- [ ] Render Quality can be changed independently from Orb Style.
- [ ] Tier hue and lifecycle identity persist across all styles and quality levels.
- [ ] Nearby liquidity objects remain individually selectable with true price/time coordinates.
- [ ] Visual effects never alter data, scoring, or probabilities.
- [ ] Dense historical regions remain performant.

## Reference artwork

- [Tier identity and style examples](../assets/orb-tier-reference.svg)
- [Solar Crown style close-up](../assets/orb-aaa-reference.svg) — the filename is retained for compatibility; this image is a style/quality reference, not an AAA tier.
