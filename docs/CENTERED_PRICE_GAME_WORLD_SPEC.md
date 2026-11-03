# Centered Live-Price Game World — Camera & Coordinate Specification

**Version:** 1.0  
**Status:** Design specification; renderer implementation not yet verified  
**Applies to:** Entire Liquidity Map visual world, including Historical Liquidity, the Dukascopy live-price marker, Future Liquidity, and market overlays  
**Primary interaction model:** A game-like world camera that follows the live market point and keeps it at the center of the playfield

## 1. Product premise

Liquidity Map is **not a candlestick chart** and does not render candle bodies, wicks, OHLC bars, or a latest candle pinned to the right edge. The central player-like object is the continuously updated Dukascopy live price.

The default view behaves like a game camera following a player character:
- The current live market point is the player/anchor.
- The live point stays at the center of the main playfield.
- The historical market world moves behind it.
- Historical observations occupy the left/past side of the world.
- Future scenarios and forecast horizons occupy the right/future side.
- Price levels above the live price appear above the anchor; price levels below it appear below the anchor.

The current market point must not drift toward the right edge as new ticks arrive. New ticks update the market state and move the world relative to the fixed camera anchor.

The visual metaphor is a **market world with a centered live player**, not a standard chart with a right-aligned current-price marker.

## 2. Centered anchor

Define the live anchor from the latest valid market update:

- `t_live`: timestamp of the latest accepted live market observation.
- `p_live`: latest accepted price on the selected and consistent price basis.
- `A = (t_live, p_live)`: world-space live anchor.
- `C = (cx, cy)`: fixed screen-space anchor at the center of the main playfield.

The current live-price marker and live market point are rendered at `C` in default FOLLOW mode.

The anchor should use the selected data basis consistently (for example BID, ASK, or MID). Never move the camera using MID while drawing the live marker or evaluating touch events using BID/ASK without an explicit conversion policy.

The anchor is the center of the **main world viewport**, not necessarily the center of the full application window when fixed HUD panels or overlays occupy screen space.

## 3. World and screen coordinates

### 3.1 Immutable world coordinates

Market objects retain their actual domain coordinates:
- Time: UTC timestamp.
- Price: exact source price on the object's declared price basis.
- Zone bounds: original `price_low` and `price_high`.
- Forecast horizon: duration and issue timestamp.
- Object ID and source metadata.

Camera movement must never rewrite, round, offset, or otherwise mutate market data.

### 3.2 Camera transform

A simple orthographic mapping is recommended:

```text
screen_x = cx + (world_time - t_live) * pixels_per_second
screen_y = cy - (world_price - p_live) * pixels_per_price_unit
```

Interpretation:
- `world_time < t_live` appears left of center (history).
- `world_time > t_live` appears right of center (future).
- `world_price > p_live` appears above center.
- `world_price < p_live` appears below center.
- The current live point `(t_live, p_live)` maps to `(cx, cy)`.

The renderer may use another mathematically equivalent transform, but it must preserve these directional and anchoring rules.

### 3.3 Zoom and scale

- Time zoom controls pixels per second.
- Price zoom controls pixels per price unit.
- Horizontal and vertical zoom are independent.
- Do not auto-rescale the entire market world on every tick.
- A fixed price scale is the stable default. Optional volatility/ATR-normalized zoom may be offered as a user-selected presentation mode, but it must be smoothed, visible to the user, and must not modify any source price or probability.
- Grid labels and price readouts must continue to show real prices, not relative offsets.
- Relative vertical displacement may be used for rendering, but exact prices remain available on hover/selection.

## 4. World layout

### 4.1 Center — live market point

The center contains the live market anchor:
- A clear live-price marker/orb acts as the player.
- The live price marker and numeric price update directly from accepted Dukascopy tick/quote events. No candle is rendered.
- A live status/price readout can be attached to the marker or HUD.
- The center marker should remain visually legible above liquidity objects and effects.
- It must not be mistaken for a Historical or Future Liquidity tier orb.

### 4.2 Left — historical world

Past market content is rendered behind the live anchor:
- Historical price movement trace, only if enabled; never a candlestick series.
- Historical Liquidity objects at their recorded price/time coordinates.
- Existing trails that represent recorded historical movement.
- Swept, mitigated, expired, or archived objects according to visibility settings.
- Past session ranges and historical context overlays.

As time advances, past content moves left relative to the viewport because the camera follows the live timestamp. The underlying timestamps and prices remain unchanged.

Historical objects must not be visually reinterpreted as future projections merely because camera smoothing or replay is active.

### 4.3 Right — future/scenario world

The area to the right of the anchor is reserved for information about possible future time:
- Monte Carlo scenario fans and quantile distributions.
- Probability-of-touch or breach zones with explicit horizons.
- Conditional structural-formation scenarios.
- Volatility envelopes and other context overlays.
- Genuine options-derived gamma context or a separately marked experimental proxy.

Future content must carry its issue time, horizon, validation state, and semantic type. It is not observed price history and must never be rendered as a completed historical trail.

Future projections do not need to predict one exact arrival timestamp. When arrival time is uncertain, render the distribution or a horizon band rather than assigning a falsely precise point on the time axis.

### 4.4 Vertical price space

Vertical position is relative to the live price anchor:
- Above center: prices higher than current live price.
- Below center: prices lower than current live price.
- Center: current live price.

This makes price movement appear as the world shifting around a centered player. The y-axis may display real price values at grid intervals; a fixed right-hand vertical axis is not required.

## 5. Camera modes and interaction

### 5.1 FOLLOW mode — default

- Keep the live market point exactly at the center anchor.
- Recompute the world-to-screen transform from the latest accepted timestamp and price.
- Older time coordinates shift left as time advances.
- Price levels shift vertically relative to the current price.
- Preserve object IDs, timestamps, and price values.
- Do not pan the market anchor toward a conventional right-edge chart position.

### 5.2 INSPECT mode — user exploration

Users may temporarily pause live-follow to inspect historical or future regions:
- Pointer drag/pan changes only the camera transform, never object data.
- Zoom operates around the pointer or selected focus point.
- A visible indicator must state that the camera is in INSPECT mode and not centered on live price.
- Show a clear **Return to Live / Recenter** action.
- Re-entering FOLLOW mode re-anchors the live point at the center without altering market records.

If the product later decides that the live point must remain centered at all times, INSPECT mode may instead use a secondary inspection viewport; it must not silently change the default centered-camera premise.

### 5.3 Replay mode

- Replay selects a historical cursor `(t_replay, p_replay)` and treats it as the camera anchor.
- Render only data available at or before the replay timestamp in the historical world.
- Future scenario objects may be shown only if they were actually issued by that replay timestamp.
- Never reveal later Dukascopy ticks/quotes, later forecast revisions, or outcomes while replaying an earlier moment.
- A replay forecast is immutable and must display its original issue time and model version.

## 6. How market objects map into the centered world

| Object | Horizontal placement | Vertical placement |
|---|---|---|
| Historical tick/price sample | Its actual timestamp relative to live time | Its actual accepted price basis relative to live price |
| Live price marker | At the live-time anchor | The selected Dukascopy price basis at the center anchor |
| Historical Liquidity orb | Recorded detection/event time | Recorded price/zone relative to live price |
| Historical trail | Recorded samples only, leftward in time | Recorded prices relative to live price |
| Future probability zone | Forecast horizon/time distribution to the right | Projected price interval relative to live price |
| Structural formation scenario | Conditional future time window to the right | Scenario price range relative to live price |
| Volatility envelope | Forecast horizon to the right | Upper/lower quantile range relative to live price |
| GEX context level | Source timestamp / valid horizon; show staleness | Mapped level relative to live price, with instrument basis disclosed |
| Fixed HUD / controls | Screen-space, not market world-space | Screen-space, not market world-space |

An object may span an interval instead of a single timestamp or price. Preserve the source interval when drawing it.

A liquidity level that remains active over time may be represented as a price band/ribbon across its valid lifetime, ending at the current anchor or its recorded lifecycle event. This is a rendering rule only; it does not assert that resting orders continuously remain at that level.

## 7. Motion and camera smoothing

- The mathematical live anchor remains exact in data space.
- Default FOLLOW mode should keep the live marker visually fixed at the center; do not smooth the marker independently from the world.
- If camera smoothing is used for background/parallax or decorative layers, it must not create visible price-marker drift or alter event coordinates.
- Do not overshoot or add inertial lag that makes the current price appear somewhere other than the center anchor.
- Use interpolation only to render smooth visual motion between valid market updates.
- A dropped tick or data gap must trigger a data-quality indicator; do not invent a continuous price path.

The camera must remain deterministic for a given set of input data, zoom, and replay state.

## 8. Parallax, background, and game-like presentation

- Background stars, grid, depth layers, and decorative scenery may use restrained parallax.
- Market objects, optional price trace, liquidity zones, and price labels must use the true market-world transform, not decorative parallax.
- Background motion must never imply measured order flow, actual order-book depth, or a forecast.
- HUD, menus, legends, status panels, and buttons remain fixed in screen-space.
- Preserve readability of liquidity objects; visual effects cannot obscure the live anchor or numeric price information.
- Any game-like ornament is cosmetic and must never alter calculations, object lifecycle, tiers, or probabilities.

## 9. Performance and viewport management

- Apply world-space viewport culling after applying the camera transform or using an equivalent inverse-viewport query.
- Keep model updates independent from frame rendering.
- Avoid rebuilding the entire scene for every tick.
- Reuse renderer objects and update only changed data.
- Apply LOD to visual effects, not to market data or forecast records.
- Keep object IDs and true coordinates even when off-screen.
- Do not merge nearby liquidity objects to reduce draw calls.
- Use independent budgets for orbs, labels, trails, particles, and future probability fans.
- Benchmark the camera-follow transform and scene update under the actual target renderer; do not promise FPS without measurement.

## 10. Acceptance tests

- [ ] In FOLLOW mode, the latest accepted live market point maps to the center of the main playfield.
- [ ] The live point does not drift toward the right edge as new ticks arrive.
- [ ] Earlier timestamps render left of the live anchor; later forecast horizons render right.
- [ ] Higher prices render above the live price; lower prices render below it.
- [ ] Historical and future data retain their original timestamps, prices, IDs, and source metadata after camera movement.
- [ ] A price change shifts the world vertically around the fixed live anchor without altering historical prices.
- [ ] Time progression shifts historical objects left while keeping the live anchor centered.
- [ ] Future scenarios remain visually distinct from observed historical movement and trails.
- [ ] Zoom changes only the camera scale and never modify price coordinates or forecast probabilities.
- [ ] INSPECT mode is clearly indicated and has an explicit Return to Live action.
- [ ] Replay cannot access future ticks/quotes, forecast revisions, or outcomes unavailable at the replay timestamp.
- [ ] HUD controls remain screen-anchored while market objects move in world space.
- [ ] Background parallax cannot be mistaken for market movement or order flow.
- [ ] Camera/rendering changes do not alter detection, probabilities, tiers, lifecycle, or storage.

## 11. Integration boundaries

- This specification defines the camera, coordinate mapping, and world presentation only.
- Historical Liquidity retains its existing detection and tier semantics.
- Future Liquidity retains its distinct forecast/scenario semantics and validation requirements.
- The Future Liquidity specification must use this centered world layout when defining its renderer.
- The MTF tier/render specification must preserve independent liquidity objects and existing performance limits under this camera.
- No trading-platform convention (candlesticks or a right-edge latest-price marker) may override the centered live-anchor default.
- No buy/sell automation or trading execution is introduced by this visual specification.


## 12. No-candlestick, Dukascopy-driven live price

The default renderer has **no candle visualization**. The central market object is the current price marker driven by the accepted Dukascopy feed.

- The actual Dukascopy event/payload semantics must be inspected by the feed adapter; do not assume a quote update is an executed trade.
- Choose and display one consistent price basis (BID, ASK, MID, or a documented provider price).
- Every accepted update changes the numeric live-price value and causes the world transform to recenter around that price.
- The live marker remains fixed at the center of the main playfield; historical and projected objects shift relative to it.
- If feed updates stop, show STALE/OFFLINE state and the last update time. Never make a frozen value look live.
- Rendering interpolation may smooth visual movement but cannot create synthetic market ticks or feed model calculations.

Internal OHLC/time aggregation may be used by a detection/model adapter if justified, but those derived bars must never be rendered as candles. Raw source observations and derived aggregates must remain distinguishable.

The feed payload, selected price basis, freshness rules, and reconnect behavior are specified in [DUKASCOPY_LIVE_PRICE_FEED_SPEC.md](DUKASCOPY_LIVE_PRICE_FEED_SPEC.md).
