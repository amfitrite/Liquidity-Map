# Orb & Trail Production Integration Specification

**Version:** 1.0  
**Status:** Design contract for renderer integration and QA  
**Scope:** Seven liquidity orb tiers, straight trail VFX, lifecycle states, centered live-price world, performance, and asset handoff  
**Important:** SVG/HTML artwork is a visual reference. It is not evidence that the Python renderer, Dukascopy feed, GPU batching, or target FPS is already implemented.

## 1. Non-negotiable world model

Liquidity Map is a live-price game world, not a candlestick chart.

- No candles, OHLC bars, candle bodies, or wicks are rendered.
- The latest accepted Dukascopy price is the central live marker and numeric readout.
- The live marker stays at the center of the main world viewport.
- Historical liquidity is placed to the left/past side; future scenarios are placed to the right/future side.
- Higher prices are above the live anchor; lower prices are below it.
- All market objects retain exact source price, timestamp, ID, and lifecycle. Camera transforms never mutate these values.
- A local animation in a design studio must be labeled SIMULATED. It must not be mistaken for a live Dukascopy connection.

The authoritative camera and feed contracts are:
- [Centered Live-Price Game World](CENTERED_PRICE_GAME_WORLD_SPEC.md)
- [Dukascopy Live Price Feed](DUKASCOPY_LIVE_PRICE_FEED_SPEC.md)

## 2. Orb tier identity

The seven tier identities are:

| Tier | Rank identity | Visual identity |
|---|---|---|
| SSS | Sovereign | Royal gold, crown/regalia, brightest premium silhouette |
| SS | Dynast | Ruby/crimson royal crest |
| S | Duke | Violet/sapphire nobility |
| A | Knight | Azure armor / heraldic geometry |
| B | Merchant | Jade guild seal |
| C | Crafter | Forged iron / worked metal |
| D | Peasant | Earth, clay, stone, humble simple core |

The tier artwork must remain recognizable by silhouette and construction, not hue alone. Color must never be the only distinction because color may be altered by state, accessibility settings, display calibration, or low-detail rendering.

### Tier is not lifecycle

Tier expresses structural rank/importance. Lifecycle expresses what happened to that liquidity object. Keep these as independent data dimensions.

Required lifecycle states:
- FRESH — newly detected, not yet tested.
- TESTED — price has approached or interacted with the level, but the level remains active under the detector's rules.
- PARTIALLY_SWEPT — part of the defined liquidity region has been consumed, but residual liquidity remains under the model's explicit criteria.
- SWEPT — the defined sweep/mitigation condition has been confirmed.
- INVALIDATED — the original structural premise no longer qualifies under its invalidation rule.
- EXPIRED — optional operational state for time-bounded objects whose validity window ended without a sweep.

Do not use visual appearance alone to decide state. State transitions must come from the detection/lifecycle engine and carry event timestamps and reason codes. Do not silently transition TESTED to SWEPT on a mere approach.

### State overlays

- FRESH: normal tier material and restrained active glow.
- TESTED: subtle pulse/ring or small test marker; preserve tier silhouette.
- PARTIALLY_SWEPT: partial arc, segmented rim, or clipped energy edge; do not shrink or recolor into a different tier.
- SWEPT: frozen/dimmed afterimage with a clear swept mark; no active pulsing.
- INVALIDATED/EXPIRED: muted archival presentation; hidden by default if user chooses, but retained in data.
- State overlays must be visually subordinate to tier identity.

## 3. Orb sizing, overlap, and identity

- Base size is driven by the validated tier/strength mapping, with a documented minimum and maximum.
- Tier size mapping must be monotonic if size communicates rank; SSS must not render smaller than D at the same zoom and state.
- Size must not imply an unvalidated numeric probability or exact amount of liquidity.
- Each orb has a stable unique object ID and independent source coordinates.
- Never merge, average, or delete nearby liquidity objects because their sprites overlap.
- Collision avoidance may use small screen-space offsets, lanes, leader lines, or stacked presentation. It must preserve exact world coordinates and allow selection to reveal the true price.
- Screen-space displacement is a rendering accommodation only; it must never affect touch, sweep, distance, or scoring calculations.

## 4. LOD without tier loss

LOD is a rendering optimization, not a data-clustering operation.

- LOD 0: full sprite layers, selected animation, high-quality glow, detailed state overlay.
- LOD 1: preserve each tier's primary silhouette, core material, and state indicator; reduce particles and secondary ornaments.
- LOD 2: preserve a distinct tier-specific silhouette/core and state cue; remove expensive micro-details.
- Off-screen objects may be culled from rendering but remain in the model/store.
- Do not replace multiple orbs with one cluster orb. If density is high, use overlap-aware layout or user-controlled visibility filters while retaining independent objects.
- Tooltips/inspection must expose ID, tier, lifecycle, exact price/zone, source timeframe, detection time, and confidence/score with its calibration status.

## 5. Trail semantics and orientation

A trail is a visual representation of an object's spatial/history context. It is not a separate liquidity pool and it must not change detection or probability.

### Historical liquidity trail

- The associated liquidity orb is positioned at its true price level and its mapped event/anchor time.
- In the centered live world, the current live anchor is at screen center. Historical trace extends from the historical object's recorded time toward the live anchor, so it appears on the past/left side.
- The orb is attached to its actual object coordinate. Do not force every historical liquidity orb to become the central live-price orb.
- If the trail is designed as an attached tail, its head is the liquidity orb and its tail direction is determined by the object's temporal history; it must not assume that the orb is always the latest market price.
- Camera transformation determines screen orientation. Do not hard-code the live head at the right edge.

### Future projection trail

- Future scenarios are a different semantic object, not a continuation of observed history.
- Render them to the right of the live anchor using a distinct material/line grammar (e.g. dashed/segmented, translucent, forecast fan or horizon ribbon).
- Display forecast issue time, horizon, scenario/quantile, model version, and validation state.
- Do not attach a historical orb sprite to an unconfirmed future event as though it were observed.
- Never present a future projection as a confirmed liquidity pool or actual resting orders.

### Trail visual channels

- Tier determines the heatmap hue (SSS hottest/brightest through D coolest/darkest) but the orb's own tier material remains independent.
- Preset determines material silhouette (Quantum Beam, Plasma Conduit, Astral Constellation, Cyber Rail, Cryo-Prismatic, Heavy Flux, Minimal Horizon).
- Lifecycle determines animation/state treatment.
- Quality/LOD determines rendering cost.
- Do not overload one color channel to communicate tier, direction, state, and probability simultaneously. Use shape, line pattern, label, or small state glyph for additional semantics.

## 6. Trail lifecycle

- ACTIVE: trail follows the camera transform and current valid object lifetime.
- TESTED: optional short pulse at the recorded interaction location; do not imply a sweep unless confirmed.
- PARTIALLY_SWEPT: preserve only the historically valid residual segment if the data model supports it; otherwise show a state overlay without fabricating a residual geometry.
- SWEPT: freeze at the confirmed sweep event timestamp; fade/desaturate as an archival visual. Do not refer to a "sweep candle" because the UI has no candles.
- INVALIDATED/EXPIRED: stop active animation and transition to a muted archival style.
- FUTURE_PROJECTION: render as a separate forecast primitive with uncertainty/horizon encoding; it is not an ACTIVE historical trail.
- Trail animation must never write new price samples, create liquidity, alter tier, change probability, or mutate lifecycle.

## 7. Material and animation rules

- Use a restrained layered stack: envelope, containment rails, telemetry ticks, optional particles/nodes, sharp core.
- The brightest white-hot core is reserved for a narrow highlight, not the entire broad trail.
- Tier palette controls the trail's dominant heat hue; avoid making every tier equally bright.
- Particle motion is cosmetic and deterministic from object ID + animation time seed where practical, so it does not flicker randomly on every render.
- Animation must be pausable. Respect reduced-motion/accessibility settings.
- Avoid excessive Gaussian blur stacking. Prefer precomputed sprite textures, cached filters, instanced geometry, or shader passes in the production renderer.
- SVG filters are suitable as artwork references but must be benchmarked before being used at scale in the main application.

## 8. Performance contract

The previously stated 60–120 FPS is a target, not a measured guarantee.

- Measure on the actual supported hardware, viewport size, renderer backend, and object/effect budget.
- Separate budgets for orb instances, trail instances, labels, particles, and expensive blur passes.
- Use viewport culling, object reuse, batched/instanced rendering, cached materials, and LOD.
- Update market/model state independently from the frame loop; render only changed state.
- Never trade data correctness for visual frame rate. Reduce visual detail first.
- Do not merge liquidity records to improve performance.
- Record p50/p95 frame time, CPU time, GPU time where available, memory, dropped frames, and object counts.
- Acceptance target should be configurable; do not hard-code a universal FPS claim into UI copy.

## 9. Data contract for renderer

Each rendered liquidity object should receive immutable model data similar to:

```python
{
    "object_id": "stable-id",
    "tier": "SSS|SS|S|A|B|C|D",
    "lifecycle": "FRESH|TESTED|PARTIALLY_SWEPT|SWEPT|INVALIDATED|EXPIRED",
    "price_low": 0.0,
    "price_high": 0.0,
    "anchor_price": 0.0,
    "event_time_utc": "ISO-8601",
    "source_timeframe": "M1|M5|M15|H1|H4|D1|W1|MN1",
    "side": "BSL|SSL|OTHER",
    "score": None,
    "score_calibration": "UNVALIDATED|CALIBRATED|NOT_APPLICABLE",
    "trail_preset": "preset-id",
    "source_kind": "OBSERVED|FORECAST"
}
```

This is an illustrative rendering contract. The actual schema must be reconciled with the repository's existing models before implementation; do not create duplicate sources of truth.

## 10. Required QA matrix

- [ ] All seven tier sprites are distinguishable in monochrome and at small LOD sizes.
- [ ] SSS remains visually premium/royal; D remains visually humble, not simply a smaller SSS.
- [ ] Tier identity survives every lifecycle overlay.
- [ ] All lifecycle states can be distinguished without relying on hue alone.
- [ ] Two or more nearby liquidity objects remain separate, selectable, and independently addressable.
- [ ] Screen-space collision offsets do not alter stored prices or hit-test coordinates.
- [ ] Historical trails appear in the past/left world under centered camera mode.
- [ ] Future projections appear to the right and cannot be confused with observed trails.
- [ ] No candlestick or OHLC UI appears in the live world or its studio demos.
- [ ] A demo simulation is visibly labeled SIMULATED and cannot be mistaken for a live feed.
- [ ] Stale/offline Dukascopy state is visible and does not keep animating as live.
- [ ] Swept trails freeze at the confirmed event time, not an invented candle time.
- [ ] Reduced-motion mode disables decorative particle/orbit animation.
- [ ] Performance is benchmarked under named hardware/backend and reported with frame-time percentiles.
- [ ] Rendering changes do not alter detection, score, probability, tier, lifecycle, or raw data.

## 11. Implementation boundary

This document is a renderer/asset integration contract. It does not claim that these behaviors are implemented. Before coding, inspect the current Python model, renderer, data schema, and Dukascopy adapter; map existing fields to this contract and report missing fields rather than inventing them.
