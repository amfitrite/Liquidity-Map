# Liquidity Orb Visual Design Specification

**Status:** Visual reference / implementation guidance  
**Scope:** Orb rendering and user-selectable appearance only. This document does not define liquidity detection, scoring, mitigation calculations, or probability logic.

## Core separation: tier, style, quality

These are three independent settings:

- **Liquidity tier** communicates the model's assessed level strength and tier label. The orb core keeps its existing tier palette; the trail uses a separate heatmap palette defined below.
- **Orb style** is a user-selectable finishing skin. It controls secondary surface treatment, highlights, decorative rings, aura, and particles. It must preserve each tier's defining silhouette, core material family, and base color. Trail appearance is controlled independently by Trail Effect.
- **Render quality** controls visual fidelity and performance cost. "AAA quality" means premium game-quality rendering; it is not a liquidity tier and must never appear as a signal grade.

Changing style or quality must never change detection, tier, score, lifecycle, coordinates, or probabilities.

## Liquidity tier identity

The tier hierarchy contains exactly seven tiers:

| Tier | Color | Core / material | Signature |
|---|---|---|---|
| SSS | Royal gold `#E8B84D` | Golden Sovereign | Imperial crown silhouette, gold core, 3 royal orbits, jeweled highlights |
| SS | Cyan `#22D3EE` | Vortex / liquid energy | Smooth energy core, 2 orbit rings, vortex arcs |
| S | Blue `#3B82F6` | Sapphire / prism | Geometric faceted core, 1 segmented orbit |
| A | Violet `#A78BFA` | Arcane / ethereal | Soft spherical core, 1 fine ring, faint aura |
| B | Silver `#A1A1AA` | Brushed metal | Metallic bead, partial ring, controlled specular highlight |
| C | Slate `#64748B` | Rough mineral | Small irregular/faceted stone core, minimal outline |
| D | Earth / worn clay `#80634B` | Humble Earthen Seed | Rough unadorned clay-stone nucleus, uneven facets, no aura or jewels |

Suggested nominal diameters at 1x: SSS 36 px, SS 31 px, S 26 px, A 21 px, B 17 px, C 13 px, D 10 px. These are starting values only. Size must not be the sole strength cue.

### Per-tier orb geometry and material construction

Each tier must have its own recognizable base object. The reference SVG is an enlarged inspection sheet, not a claim that every orb renders at the same size in the chart.

| Tier | Named identity | Required geometry and material cues |
|---|---|---|
| SSS | Golden Sovereign | The unmistakable ruler of all seven tiers: rich royal-gold core, a clearly readable crown silhouette, three precise royal orbit rings, engraved regalia, and restrained jewel-like highlights. It must look prestigious, commanding, and expensive without becoming visually noisy. Gold is the SSS orb identity; the separate trail heatmap remains white for SSS. |
| SS | Vortex Energy | A smooth, rounded liquid-energy nucleus with a visible internal spiral/swirl, two intersecting elliptical orbit rings, and flowing energy arcs. Cyan luminous-fluid material; less angular than SSS. |
| S | Sapphire Prism | A sharply cut polygonal sapphire nucleus with distinct triangular facet planes and one segmented orbital ring. Strong blue glass, crisp edges, and geometric symmetry. |
| A | Arcane Sphere | A soft spherical violet nucleus with a single fine orbit ring, a faint diffuse aura, and subtle internal light. Keep the silhouette calm and less ornamented than the upper tiers. |
| B | Brushed Silver | A metallic bead with fine brushed surface grooves, a controlled specular highlight, and one partial machined ring. Silver-gray material; avoid excessive glow. |
| C | Rough Mineral | A small irregular stone/mineral nucleus with uneven facets, low-reflective slate material, and only a minimal outline. The silhouette should feel naturally fractured, not polished. |
| D | Humble Earthen Seed | The lowest/commoner identity: a small worn clay-and-stone nucleus with uneven rough facets, muted earth-brown material, no crown, no jewelry, no orbit ornament, and no aura. It should feel ordinary and unadorned, while retaining enough edge contrast to remain visible. |

- The tier identity owns the base silhouette, base material family, and base hue. The user-selected Orb Style may decorate or finish that object but must not turn every tier into the same orb geometry.
- Preserve the signature cues at all supported zoom levels: imperial gold crown and three royal orbits for SSS, double-orbit vortex for SS, segmented sapphire prism for S, fine-ring sphere for A, brushed partial-ring metal for B, rough mineral for C, and unadorned earthen commoner seed for D.
- At the chart's nominal 1x size, simplify micro-details through LOD rather than removing the defining silhouette. SSS/SS may carry more fine detail; C/D must remain compact and readable without invented glow.
- The showcase SVG enlarges all seven identities for inspection. Use the 1x nominal size row as the implementation size reference.


## User-selectable orb styles

Provide a visible Orb Style setting with a live preview. The selected style applies consistently to every tier while preserving each tier's core silhouette, material family, and color identity. Initial presets:

1. **Celestial Crystal** — faceted luminous core, precision rings, restrained star glints.
2. **Solar Crown** — white-hot center, six short crown rays, two offset elliptical orbits, floating sparks. This is the former gold concept; it is a style preset, not an AAA tier.
3. **Vortex Energy** — fluid energy core, flowing orbit arcs, subtle internal motion.
4. **Prismatic Core** — crystalline facets, sharp specular edges, segmented orbit.
5. **Arcane Aura** — smooth orb, fine rune-like ring, soft controlled aura.
6. **Minimal / Clean** — compact solid core, thin outline, no particles, minimal glow.

The style changes secondary finishing and embellishment only; it must not erase the tier-specific base geometry or material signature. Tier identity remains the source of truth: SSS is royal gold and D is humble earth/clay. A style may add lighter/darker shades and surface finishing, but must not replace these identities with a fixed style color.

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

## Trail Effect — ten selectable premium cosmetic trails

A trail is the **visual residue left behind an object as it moves**, like a premium MOBA skin cosmetic. It is not a slash, attack arc, projectile, skill cast, or directional blade. The orb is the moving head; the trail remains behind it and gradually dissipates.

Provide exactly ten user-selectable options:

1. **No Effect (Straight Line)** — one plain, straight, unadorned line. No glow, particles, texture, animation, distortion, taper decoration, or bloom. Its line color still follows the tier heatmap. This is the lightweight default.
2. **Aurora Flow** — a luxury pearlescent silk trail: a broad translucent ribbon, two or three fine interwoven filaments, refractive edge highlights, and subtle iridescent color separation. The trailing end dissolves into fine light dust.
3. **Stardust Wake** — a dense but art-directed particle field with multiple particle scales, jewel-bright star glints, tiny bokeh, and depth layering. Particle density and brightness taper smoothly toward the oldest trail section.
4. **Nebula Veil** — layered volumetric-looking clouds, fine internal filaments, softly illuminated vapor edges, and sparse embedded star points. The cloud must remain connected to the historic path and gently dissipate, not look like an impact explosion.
5. **Spectral Afterimage** — a procession of glossy, semi-transparent orb echoes with individual soft halos and subtle refraction. Older echoes become progressively smaller, dimmer, and more diffuse.
6. **Prismatic Serpentine** — multiple glass-like filaments braided around a soft central flow, with refractive edges, controlled chromatic highlights, and fine connecting threads. The silhouette must feel fluid and continuous, never like a blade.
7. **Astral Filigree** — delicate ornamental geometry embedded along the wake: fine arcs, jeweled nodes, tiny star points, and elegant repeating motifs. Treat it like a costly cosmetic ornament, not readable text, runes for attack, or a weapon effect.
8. **Frosted Crystal Drift** — small faceted crystal motes with translucent surfaces, icy caustics, micro highlights, and gently drifting frost dust. Keep fragments small and soft-edged; do not form large sharp shards or projectiles.
9. **Blooming Petals** — opalescent petal fragments and miniature floral clusters floating along a soft luminous thread. Petals rotate and drift subtly, then fade; avoid a sharp slash or a one-time burst.
10. **Celestial Rings** — a series of translucent elliptical echoes deposited along the path, with subtle refraction, double outlines, fine luminous nodes, and fading arcs. These are stationary residues along the recorded history, not expanding shockwaves.

### Premium cosmetic / gacha-quality visual standard

The previous simple line-and-dot sketches are not the target. Enabled effects must feel like a premium, unlockable game cosmetic: composed, layered, distinctive, and richly finished rather than merely brighter or blurrier.

- Build each enabled effect from multiple composited layers where appropriate: a soft base envelope, a signature material/motif layer, fine filaments or secondary geometry, micro-particles, and controlled bloom/specular accents.
- Give each preset a recognizable silhouette and material identity. Do not make all nine presets the same ribbon with a different particle overlay.
- Use high-resolution gradients, smooth curves, antialiased edges, layered alpha, subtle refraction/caustics, and carefully distributed detail. Avoid flat primitives, generic dotted lines, noisy particle clouds, and overexposed bloom.
- Details should be richest near the live orb and gradually become sparse, smaller, softer, and more transparent toward the old trail end. The transition must feel intentional, not like a hard cutoff.
- Premium detail must remain legible at normal chart zoom. Add level-of-detail variants so detail reduces gracefully when zoomed out or when many trails overlap.
- Do not use a static decorative slash or forward-moving projectile as a substitute for a movement trail. Every flourish remains behind the orb along its recorded path.

### Trail tier heatmap palette

Trail color is assigned by liquidity tier, not by Orb Style or Trail Effect. This is a **categorical visual heat scale** for tier strength, not a measured temperature, order-book heat, volatility reading, or live liquidity intensity.

| Tier | Heat level | Trail color | Hex |
|---|---|---|---|
| SSS | Hottest | White | `#FFFFFF` |
| SS | Very hot | Red | `#FF303B` |
| S | Hot | Orange | `#FF7900` |
| A | Warm | Yellow | `#FFD52A` |
| B | Cool | Light blue | `#73E6FF` |
| C | Colder | Blue | `#2787E5` |
| D | Coldest | Deep blue | `#092B68` |

- Each tier has its own fixed trail hue. The seven hues must remain visually distinguishable.
- Preserve that tier hue along the entire trail; age/fade changes opacity and softness only, not the hue. Do not turn every trail into a white-to-blue thermal gradient.
- The heatmap colors apply to all nine VFX options and to the plain No Effect line.
- Orb core colors are unchanged. Do not recolor orb bodies to match the trail heatmap.
- Style and effect control shape/material; tier controls trail hue. These dimensions must remain independent.

### Movement-trail behavior and technical rules

- The live orb is the head of the effect. Every visible trail element must remain behind it along the object's recorded path; never project the effect forward.
- Trail residue fades progressively with age/distance from the live head. Use smooth alpha dissipation, not abrupt cut-offs.
- The nine effect presets meet the premium cosmetic standard above while preserving distinct visual identities.
- Use the fixed Trail Tier Heatmap palette above. Lighter/darker shades of the assigned tier hue may add depth, but the tier's base hue must remain recognizable.
- Trail Effect is independent of Orb Style and Render Quality. Any orb skin can be combined with any trail option.
- The trail records the object's age/history from formation to now; it is not a price forecast, target path, or directional trading signal.
- Active trails extend to NOW. Swept/mitigated trails end at the event time. Historical trails become static and gradually fade.
- **No Effect stays a literal plain straight line**, regardless of Render Quality. Ultra / AAA must not secretly add glow or particles to it.
- Reduced-motion and disable-animation modes must preserve a clean static representation of the selected trail.
- Use LOD and particle budgets. Animate only visible active/replay-window trails; simplify or bake historical trails.
- Visual trail settings must never alter liquidity detection, tier, score, lifecycle, coordinates, or probability calculations.

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
- [ ] Trail Effect selector contains exactly ten options, including No Effect.
- [ ] Nine premium cosmetic presets have distinct silhouettes/material identities and read as movement residue, not slashes or projectiles.
- [ ] Enabled presets have layered materials, signature detail, and a deliberate fade profile; not just a line with dots.
- [ ] Trail hue maps SSS white → SS red → S orange → A yellow → B light blue → C blue → D deep blue.
- [ ] Trail hue remains fixed per tier; trail age changes opacity only. Orb body colors remain unchanged.
- [ ] No Effect renders only a plain straight line, regardless of Render Quality.
- [ ] Trail residue fades progressively behind the orb and never projects forward.
- [ ] Tier hue and lifecycle identity persist across all styles and quality levels.
- [ ] Nearby liquidity objects remain individually selectable with true price/time coordinates.
- [ ] Visual effects never alter data, scoring, or probabilities.
- [ ] Dense historical regions remain performant.

## Reference artwork

- [Seven tier-specific orb designs](../assets/orb-tier-reference.svg)
- [Five trail-effect visual options](../assets/trail-effect-reference.svg)
- [Solar Crown style close-up](../assets/orb-aaa-reference.svg) — the filename is retained for compatibility; this image is a style/quality reference, not an AAA tier.
