# Trail VFX Design & Implementation Specification

**Status:** Premium visual reference and renderer contract  
**Repository:** `amfitrite/Liquidity-Map`  
**Visual reference:** [`assets/trail-effect-premium-reference.svg`](../assets/trail-effect-premium-reference.svg)  
**Legacy reference:** [`assets/trail-effect-reference.svg`](../assets/trail-effect-reference.svg) — retained for comparison; the premium reference is the current art direction.

## 1. Purpose and separation of concerns

A trail is the **residual visual history behind a moving liquidity orb**. It is not a forecast path, target, projected movement, weapon slash, projectile, attack arc, or one-time impact burst.

Keep these dimensions independent:

- **Liquidity tier** chooses the trail's base hue.
- **Trail preset** chooses silhouette, material, geometry, and particle motif.
- **Trail age** controls opacity, scale, thickness, blur, and detail dissipation.
- **Render quality** controls implementation fidelity and GPU cost.
- **Liquidity model** owns all detection, score, price/time coordinates, state, and probabilities. Rendering must never modify these.

The orb is the live head. The trail must remain behind the head on recorded samples only. Do not extrapolate points in front of the latest sample.

## 2. Fixed tier heatmap palette

Use exactly this categorical mapping. Preserve the tier's recognizable hue for the entire trail; age may fade or soften it but must not turn it into a universal rainbow or white-to-blue temperature gradient.

| Liquidity tier | Heat rank | Base hue | Hex |
|---|---|---|---|
| SSS | Hottest | White | `#FFFFFF` |
| SS | Very hot | Red | `#FF303B` |
| S | Hot | Orange | `#FF7900` |
| A | Warm | Yellow | `#FFD52A` |
| B | Cool | Light blue | `#73E6FF` |
| C | Colder | Blue | `#2787E5` |
| D | Coldest | Deep blue | `#092B68` |

The reference SVG uses B / light blue as its artwork preview tint. At runtime, derive highlights and shadows from the tier hue while preserving the same tier identity. Do not change the orb core palette to match the trail heatmap.

## 3. Ten selectable trail presets

Expose exactly ten choices in the Trail Effect setting. Presets 02–10 are premium VFX. Preset 01 is a deliberately plain baseline and must remain plain at every render-quality setting.

| ID | Preset | Required visual identity | Animation character |
|---|---|---|---|
| 01 | **No Effect** | One thin, straight, tier-colored line. No bloom, glow, particles, texture, distortion, taper decoration, or ornamental geometry. | Static; zero animation. |
| 02 | **Aurora Flow** | Pearlescent silk ribbon, translucent body, two or three fine filaments, refractive edge highlights, sparse light dust. | Slow UV drift and subtle ribbon undulation; never turbulent. |
| 03 | **Stardust Wake** | Art-directed multi-scale particles, tiny jewel sparks, occasional star glints, sparse soft bokeh. Avoid a generic dense particle cloud. | Particles drift gently and fade individually; density grows toward the live head. |
| 04 | **Nebula Veil** | Layered soft cloud envelope, vapor-edge lighting, delicate internal filaments, sparse embedded star points. | Low-amplitude cloud flow/noise; stay attached to the historical path. |
| 05 | **Spectral Afterimage** | Repeated glossy orb echoes with distinct halos and glassy outlines. | Echoes stay at past sampled positions; older echoes shrink, dim, and soften. |
| 06 | **Prismatic Serpentine** | Interwoven glass ribbons and braided filaments with refractive seams. It must look fluid, not blade-like. | Filaments move slowly around the path with restrained phase offset. |
| 07 | **Astral Filigree** | Elegant repeating geometric ornaments, fine connecting arcs, jeweled nodes, small star glints. No readable text or combat runes. | Motifs are deposited along the path; small highlights shimmer subtly. |
| 08 | **Frosted Crystal Drift** | Small faceted translucent crystals, icy caustic glints, frost dust. Never use large sharp projectile-like shards. | Motes rotate and drift slightly, then fade; no explosive burst. |
| 09 | **Blooming Petals** | Opalescent petal pairs or small botanical clusters riding a fine light thread. | Petals rotate slowly and drift slightly while remaining visually attached to the wake. |
| 10 | **Celestial Rings** | Nested elliptical echoes, subtle double outlines, refractive arcs, tiny luminous nodes. | Rings are deposited along old positions and remain as fading history marks; never expand like shockwaves. |

### Quality bar

The premium options must be recognizable by **material and silhouette**, not merely by stronger glow or a different particle overlay. Use refined curves, antialiased geometry, layered alpha, controlled bloom, restrained specular accents, and clean negative space. The result should resemble a premium game cosmetic while remaining legible over a dense trading chart.

Avoid:
- generic dotted lines presented as separate presets;
- excessive bloom that washes out the tier hue;
- noisy particle clouds or random decorative clutter;
- sharp slashes, weapon arcs, projectiles, explosions, and forward-moving bursts;
- all nine premium effects sharing the same ribbon silhouette.

## 4. Motion and temporal model

The renderer should consume recorded trail samples, not infer market movement.

Recommended logical sample shape:

```python
TrailSample(
    timestamp: float,
    x: float,
    y: float,
    tier: str,
    state: str,
)
```

The actual repository data model may use different names; adapt at the renderer boundary instead of forcing market-model changes.

For each visible trail segment:

1. Preserve chronological order from oldest to newest.
2. Place the newest sample at the orb head.
3. Interpolate between recorded samples for smooth curves; interpolation must not create a forward projection.
4. Compute normalized age along the visible trail, where 0 is oldest and 1 is newest.
5. Increase opacity, line thickness, particle density, and detail toward the newest section.
6. Progressively reduce opacity, scale, thickness, contrast, and detail toward the oldest section.
7. Keep the tier base hue constant while varying only its lightness/alpha for material shading.

A suitable starting dissipation curve is:

```text
age_alpha = pow(normalized_age, 1.6)
```

Use this as a visual starting point, not a market parameter. Each preset may adjust the curve slightly, but the old end must always dissolve smoothly.

### Lifecycle

- **Active / live:** trail extends to the current orb head using recorded positions up to now.
- **Swept / mitigated:** stop adding samples at the event timestamp; preserve the completed trail as a static historical residue.
- **Expired / archived:** static, low-opacity history; do not continue animation as though the orb were still moving.
- **Replay:** reconstruct the trail only from samples available at the replay time. Never show future samples.

## 5. Animation model

Use a monotonic frame clock for presentation and deterministic per-object seeds for repeatable particle placement. Avoid randomizing every particle on every frame; that causes visual flicker.

Suggested animation channels:

- **Ribbon UV drift:** move texture coordinates slowly along the ribbon.
- **Ribbon deformation:** apply a low-amplitude wave to the offset from the recorded path.
- **Particle drift:** advance each particle using its own birth time, velocity, and lifetime.
- **Echo fade:** derive each afterimage's alpha and scale from age, not arbitrary per-frame opacity changes.
- **Ornament shimmer:** modulate highlights slightly; keep the geometry anchored to the recorded path.
- **Cloud noise:** animate low-frequency noise only; do not displace the path centerline substantially.

A paused chart, historical chart, reduced-motion mode, or disabled animation setting must render a stable static frame.

## 6. Renderer architecture

Recommended hybrid 2D + GPU approach for the Python application:

- **Path builder:** converts timestamp/price samples into screen-space path segments and performs smoothing/interpolation.
- **Trail material layer:** draws ribbon, cloud, rings, glass, and other preset-specific base geometry.
- **Particle layer:** manages deterministic particles and individual lifetimes.
- **Tier palette resolver:** provides the fixed seven-color mapping.
- **Dissipation layer:** applies age-based alpha, scale, width, and detail reduction.
- **Compositor:** blends layers and applies restrained bloom/glow where supported.
- **LOD/performance manager:** selects lower-detail representations based on zoom, visible trail count, and frame budget.

Prefer GPU shaders for high-quality active effects. A CPU/QPainter fallback should preserve path shape, tier hue, and dissipation without attempting expensive blur/particle simulation.

Do not force a renderer migration if the project already has a stable drawing backend. Add the effect system behind a small renderer interface so presets can be implemented incrementally.

## 7. Performance and readability constraints

- Animate only visible active trails and the current replay window.
- Bake or simplify historical trails.
- Cap particles per trail and globally; use deterministic thinning when the cap is reached.
- Use level-of-detail: at zoomed-out scales, retain the silhouette and hue while removing tiny ornaments and particles.
- Reduce bloom before reducing path accuracy.
- Do not allow one premium trail to obscure nearby candles, price labels, or other liquidity orbs.
- Prefer additive blending only for highlights; use normal alpha compositing for the main ribbon/cloud body.
- Provide **Performance**, **Balanced**, and **High** quality modes plus **Auto**.
- Provide **Reduced Motion** and **Disable Trail Animation** controls.
- No Effect remains a literal plain line in every quality mode.

## 8. Acceptance checklist

- [ ] Exactly ten selectable presets are exposed.
- [ ] The new premium SVG is the visual source of truth for preset silhouettes.
- [ ] SSS/SS/S/A/B/C/D use the exact fixed heatmap colors above.
- [ ] Changing tier changes trail hue but not preset geometry.
- [ ] Changing preset changes visual material/shape but not liquidity data.
- [ ] No trail geometry appears in front of the live orb.
- [ ] Older trail sections dissipate progressively without a hard cutoff.
- [ ] Swept/mitigated and archived trails stop moving.
- [ ] No Effect remains a plain straight line with no hidden glow.
- [ ] Reduced-motion and static modes produce stable frames.
- [ ] LOD and particle budgets prevent chart overload.
- [ ] Visual work does not change detection, tier scoring, coordinates, lifecycle, or probabilities.

## 9. Scope boundary

This is a visual design and renderer specification only. It does not authorize changes to liquidity detection, tier calculation, price/time data, signal generation, or trading logic.
