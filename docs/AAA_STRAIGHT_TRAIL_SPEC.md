# AAA Straight-Line Liquidity Trail Specification

**Status:** Corrected renderer contract  
**Master artwork:** [Trail Effects Showcase](../assets/sprites/trails/trail_effects_showcase.svg)  
**Interactive laboratory:** [Centered Live-Price Trail Studio](../assets/sprites/trails/trail_studio.html)  
**Integration rules:** [Orb & Trail Production Integration](ORB_TRAIL_PRODUCTION_INTEGRATION_SPEC.md)

## 1. Core model

Liquidity is anchored to an exact price or price zone. A trail is a rendering of temporal/spatial context, not a liquidity object and not a chart series.

The application is a centered live-price world:
- No candlesticks, OHLC bars, candle bodies, or wicks are rendered.
- Dukascopy's accepted live price is the central screen-space anchor.
- Historical objects and historical traces map to the left/past side.
- Forecast/scenario projections map to the right/future side and use a distinct visual grammar.
- Higher prices render above the live price; lower prices below.
- Camera transforms may move the world, but never mutate source timestamps, exact prices, IDs, or lifecycle.

Do not hard-code the orb head at the right edge. The screen position of every trail/orb is computed from its world coordinates and the centered camera transform. The studio is explicitly simulated; it is not a Dukascopy connection.

## 2. Trail categories

### Historical / observed trail
Represents the recorded history or lifetime of an observed liquidity object. It must remain attached to that object's real price and timestamp. In the centered world, the historical portion appears on the left side. A liquidity orb is not automatically the live-price orb.

### Future projection
Represents an uncertain scenario beyond the live timestamp. Use dashed/segmented lines, uncertainty ribbons, quantile fans, or horizon markers. It must not look like an observed trail or imply confirmed resting orders. Display issue time, horizon, model version, and validation state.

### Cosmetic animation
Glow, particles, shimmer, and moving packets are decorative only. They cannot create source ticks, price touches, liquidity, order flow, or probability updates.

## 3. Tier heatmap palette

| Tier | Hue | Hex |
|---|---|---|
| SSS | Sovereign white/gold highlight | `#FFFFFF` |
| SS | Crimson ruby | `#FF303B` |
| S | Solar orange | `#FF7900` |
| A | Cyber yellow | `#FFD52A` |
| B | Neon cyan | `#73E6FF` |
| C | Cobalt blue | `#2787E5` |
| D | Deep blue | `#244F91` |

Tier hue controls trail heat only. Orb body material remains tier-specific (gold, ruby, sapphire, azure, jade, iron, clay/stone). Do not collapse tier, lifecycle, direction, and probability into one color channel.

## 4. Material presets

- Quantum Hyper-Beam — sharp white-hot core, restrained volumetric envelope.
- Fusion Plasma Conduit — layered hot core and containment rails.
- Astral Constellation — sparse fixed-seed photonic nodes.
- Cyber Neon Data Rail — segmented telemetry and clean parallel rails.
- Cryo-Prismatic — cool refraction and narrow crystalline highlights.
- Heavy Flux Channel — broad low-frequency envelope, low particle count.
- Minimal Horizon — thin core with almost no bloom.

A preset changes material, not liquidity semantics or price geometry.

## 5. Layer stack

1. Atmosphere envelope: broad low-opacity glow.
2. Containment rails: parallel thin lines.
3. Telemetry ticks: optional calibrated marks; explicitly decorative unless sourced.
4. Photonic nodes: sparse particles, deterministic where practical.
5. Incandescent core: sharp central line.

Do not use glow so strong that nearby orbs, exact price levels, or state markers become unreadable. SVG Gaussian filters are artwork references; benchmark them before large-scale production use.

## 6. Dissipation and direction

For a historical trail parameterized from origin (x_0) to attached object position (x_1), normalized progress is (u=(x-x_0)/(x_1-x_0)). A candidate fade curve is (alpha(u)=alpha_{max}u^{1.8}), where (uin[0,1]).

This is a visual profile only. The renderer must derive (x_0) and (x_1) from the camera/world transform and object semantics; never assume the current live price is the trail head or always on the right edge. Future projections use a separate opacity/uncertainty profile and must not reuse historical decay as if they were observations.

## 7. Lifecycle presentation

- FRESH: active material, restrained glow.
- TESTED: subtle pulse/ring, still active.
- PARTIALLY_SWEPT: segmented/partial rim; preserve only model-supported residual geometry.
- SWEPT: freeze at confirmed sweep event time, then desaturate/fade.
- INVALIDATED/EXPIRED: stop active animation and show muted archive style.
- FUTURE_PROJECTION: separate forecast styling, no historical sweep lifecycle until an observed event actually occurs.

Lifecycle is provided by the model. Visual effects never decide it. Do not refer to a "sweep candle"; the UI has no candles.

## 8. Performance

120 simultaneous trail objects is a provisional design budget, not a measured capacity. 60–120 FPS is a target, not a guarantee.

Required techniques:
- Viewport culling and independent budgets for trails, orbs, labels, particles, and blur passes.
- Batch/instance geometry where the renderer supports it.
- Cache material/filter resources; avoid rebuilding the entire scene on every tick.
- Reduce particles, blur, and fine detail before reducing object visibility.
- Never merge liquidity objects or discard model records for performance.
- Benchmark p50/p95 frame time, CPU/GPU time, memory, and dropped frames on named target hardware.

## 9. References and acceptance

Use the centered studio as the visual orientation reference. The master SVG is a sprite/material atlas; it is not a substitute for camera integration.

- [ ] No candle graphics or candle terminology in the live UI.
- [ ] Live price marker remains at center.
- [ ] Historical trails map to past/left; future projections map to future/right.
- [ ] Orb identity remains separate from the live-price marker.
- [ ] Tier hue, orb material, lifecycle, and forecast confidence remain separate dimensions.
- [ ] No merging of separate liquidity objects.
- [ ] Trail effects do not alter calculations or lifecycle.
- [ ] Reduced-motion mode and stale-feed presentation are supported.
- [ ] Performance claims are backed by repeatable benchmark results.
