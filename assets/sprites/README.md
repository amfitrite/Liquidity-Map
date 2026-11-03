# Liquidity Map — Orb Sprite Assets Specification & Catalog

This directory contains the production-grade vector sprite assets and texture atlases for the **Liquidity Map** rendering engine, structured according to the royal social hierarchy defined in [`docs/ORB_DESIGN_SPEC.md`](../../docs/ORB_DESIGN_SPEC.md) and [`docs/MTF_LIQUIDITY_TIER_RENDER_SPEC.md`](../../docs/MTF_LIQUIDITY_TIER_RENDER_SPEC.md).

---

## 1. Directory Structure

```text
assets/sprites/
├── orbs/
│   ├── tier_sss_sovereign.svg       # SSS Sovereign (Golden Emperor) - 256x256
│   ├── tier_ss_dynast.svg          # SS Dynast (Royal Heir Ruby) - 256x256
│   ├── tier_s_duke.svg             # S Duke (High Nobility Violet/Sapphire) - 256x256
│   ├── tier_a_knight.svg           # A Knight (Azure Knightly Order) - 256x256
│   ├── tier_b_merchant.svg         # B Merchant (Jade Guild Bead & Seal) - 256x256
│   ├── tier_c_crafter.svg          # C Crafter (Forged Iron Slag) - 256x256
│   ├── tier_d_peasant.svg          # D Peasant (Humble Clay Nucleus) - 256x256
│   └── spritesheet_orbs_matrix.svg # Master 7x4 Grid (All Tiers x 4 Lifecycle States)
├── layers/
│   ├── cores.svg                   # Decomposed orb body nuclei
│   └── crowns_regalia.svg          # Decomposed crowns, coronets, heraldic crests & seals
├── orb_viewer.html                 # Interactive WebGL/Canvas/SVG laboratory & inspector
└── README.md                       # This document
```

---

## 2. Sprite Canvas & Dimension Standards

| Tier | Named Identity | Frame | Base Hue | 1x Nominal Chart Diameter | Sprite Canvas | Distinguishing Geometry |
|---|---|---|---|---:|---:|---|
| **SSS** | **Golden Sovereign** | MN1 | `#D6A332` | **36 px** | 256 × 256 | Dominant 5-point imperial crown, triple celestial orbits, heart gem |
| **SS** | **Crimson Dynast** | W1 | `#C02645` | **31 px** | 256 × 256 | 3-spire royal coronet, ceremonial elliptical orbit, marquise ruby gem |
| **S** | **Sapphire Duke** | D1 | `#7251C8` | **26 px** | 256 × 256 | Hexagonal heraldic shield cut, dual crescent half-orbits, sapphire inset |
| **A** | **Azure Knight** | H4 | `#1D4ED8` | **21 px** | 256 × 256 | Octagonal armored prism, disciplined single circular steel halo |
| **B** | **Jade Merchant** | H1 | `#16866B` | **17 px** | 256 × 256 | Smooth polished jade cabochon, prosperity knot trade seal, simple hoop |
| **C** | **Iron Crafter** | M15 | `#64748B` | **13 px** | 256 × 256 | Rough forged iron slag, worn chisel facets, **zero orbit/aura/gem** |
| **D** | **Earthen Peasant** | M5, M1 | `#9A7658` | **10 px** | 256 × 256 | Handmade asymmetric clay nodule, thumb indents, **zero ornament/halo** |

---

## 3. Layer Separation Architecture

Each standalone SVG is modularized with standardized `<g>` tag IDs to allow dynamic GPU shader animation and layer toggling:

- `layer-aura`: Ambient soft radial bloom (disabled in Performance mode or on Tiers C & D).
- `layer-orbits` / `layer-halo`: Kinetic orbital rings (can be independently rotated via CSS / Canvas `ctx.rotate`).
- `layer-core`: Base solid geometric structure and radial material gradient.
- `layer-crown` / `layer-coronet` / `layer-emblem`: Social hierarchy insignia.
- `layer-highlights`: Specular caustics and sharp facet reflections.
- `layer-particles`: Orbiting stellar glints (managed within GPU particle budget).

---

## 4. Lifecycle States (Matrix Atlas Mapping)

In `spritesheet_orbs_matrix.svg`, the columns represent the 4 active lifecycle states:

1. **State 1: FRESH (Active)** — Full color luminance, 100% orbit presence, high-gloss specular highlight.
2. **State 2: TESTED (Pulsing)** — Excited outer ring, resonant halo pulse (+20% radius breathing effect).
3. **State 3: PARTIALLY MITIGATED** — 60% opacity, fragmented orbit arcs, amber mitigation marker.
4. **State 4: SWEPT (Extinguished)** — Desaturated (grayscale feColorMatrix), 35% opacity, static extinguished stone/slag residue.

---

## 5. Level of Detail (LOD) Rules

1. **LOD 0 (Macro View / Tooltip Inspection / 2x - 8x)**: Full layers active, multi-point gradients, fine particles, animated orbital paths.
2. **LOD 1 (1x Chart Nominal View)**: Subtle aura, primary orbit line, solid core with primary crown/seal silhouette.
3. **LOD 2 (Zoomed Out / Dense View)**: Preserve each individual orb's tier-specific silhouette/core and state cue; remove orbits, particles, and fine facet lines. LOD must never merge separate liquidity objects into a cluster orb. Any screen-space overlap handling must preserve each object's exact world coordinates and unique ID.


## 6. Centered live-price world integration

The orb atlas is an asset library, not a chart layout. In the application, the Dukascopy live-price marker stays at the center of the main viewport; historical liquidity objects occupy the past/left world and future projections the right/future world. Do not render candles or OHLC bars. Orb sprite positions must be computed from immutable world coordinates through the centered camera transform.

## 7. Lifecycle and identity

Tier (SSS through D) is independent from lifecycle (FRESH, TESTED, PARTIALLY_SWEPT, SWEPT, INVALIDATED, EXPIRED). State overlays must not destroy tier silhouette. LOD may simplify ornamentation but may not merge or delete independent liquidity objects. See [Orb & Trail Production Integration Specification](../../docs/ORB_TRAIL_PRODUCTION_INTEGRATION_SPEC.md).
