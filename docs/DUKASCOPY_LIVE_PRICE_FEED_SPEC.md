# Dukascopy Live Price Feed — Tick Adapter Specification

**Version:** 1.0  
**Status:** Design specification; a working live connection has not yet been verified  
**Purpose:** Define how live Dukascopy price updates drive the centered game-world price anchor  
**UI rule:** No candlesticks or candle chart are rendered. The live price marker is the central player-like object.

## 1. Product behavior

Liquidity Map displays a continuously updated live market price from the configured Dukascopy data adapter.

- The current live price is the central anchor of the game world.
- The displayed price value updates as new valid Dukascopy updates arrive.
- The live marker remains at the center of the main world viewport.
- The market world (liquidity objects, price levels, and scenario layers) moves relative to that fixed screen-space anchor.
- Do not render Japanese candlesticks, OHLC bars, candle bodies, candle wicks, or a conventional right-edge chart.
- Do not use a forming candle as the visual player. The live price marker itself is the player/anchor.
- Historical Liquidity and Future Liquidity remain the primary spatial objects around the live price.

This specification defines the feed contract and display behavior. It does not claim that the repository already has a working Dukascopy live connection.

## 2. Data semantics: quote update versus trade

A provider event called a “tick” is not automatically an executed transaction. Depending on the actual Dukascopy product/feed and adapter, updates may represent bid/ask quote changes or another price event.

The adapter must inspect and document the actual received payload. Do not assume field names or semantics until verified.

- If the feed supplies BID and ASK quotes, preserve both values and their event timestamps.
- If the feed supplies only one price field, preserve its documented meaning (for example, BID, ASK, LAST, or provider-defined price).
- Do not label quote changes as trade prints, traded volume, aggressive buy/sell volume, or footprint delta.
- Do not infer actual order-book depth or resting orders from price updates alone.
- If a volume field exists, document whether it is tick count, quote-update count, feed volume, or exchange-traded volume. Unknown semantics must remain unknown.

## 3. Normalized incoming event contract

Normalize source-specific messages into an internal event shape. This is an illustrative adapter contract, not an assertion about Dukascopy's raw JSON/protocol:

~~~python
{
    "instrument": "XAUUSD",
    "provider": "DUKASCOPY",
    "event_type": "QUOTE_UPDATE",
    "event_time_utc": "provider_event_timestamp",
    "received_time_utc": "local_receive_timestamp",

    "bid": None,
    "ask": None,
    "provider_price": None,
    "provider_price_semantics": None,

    "source_sequence": None,
    "source_payload_id": None,
    "connection_session_id": "session-id"
}
~~~

Rules:
- Preserve the raw source payload or a safely reproducible reference to it for diagnostics.
- Keep provider event time separate from local receive time.
- Preserve source sequence/ID only when supplied; never fabricate one.
- Record connection/session metadata so reconnect gaps and feed resets can be diagnosed.
- Normalize symbol mapping explicitly; do not silently treat every gold-related symbol as XAUUSD CFD.

## 4. Selected display price basis

The central live price must use one explicit, user-visible basis:

- BID
- ASK
- MID (computed only when both BID and ASK are valid)
- PROVIDER_PRICE (only when its semantics are documented)

The selected basis is used consistently for:
- Central price number and live marker.
- Camera vertical anchor.
- Live-price-relative object placement.
- Price-touch event evaluation when using that feed basis.

Never anchor the camera on MID while evaluating events on BID or ASK without an explicit conversion policy.

If the selected basis is missing or invalid, do not silently fall back to another basis. Mark the feed/basis as unavailable or DATA_INVALID. Retain the last valid displayed price only with a clearly visible stale state.

## 5. Update and rendering pipeline

Recommended flow:

1. Receive the provider update.
2. Validate instrument, field semantics, price precision, event timestamp, and quote consistency.
3. Reject or quarantine malformed events.
4. Handle duplicate and out-of-order updates according to a documented policy.
5. Select the configured price basis.
6. Update the authoritative live price state and its event/receive timestamps.
7. Re-anchor the world transform so the current live point remains at the exact center.
8. Render the numeric price and marker update.
9. Update screen positions for historical liquidity and future/context objects without changing their stored world coordinates.
10. Publish feed health and freshness state to the HUD.

The rendering loop may interpolate between two received prices for visual smoothness. Interpolation is display-only:
- It must not create synthetic source ticks.
- It must not be written to the historical data store as an observed price.
- It must not be used for probabilities, structure detection, touch/sweep evaluation, or backtesting.
- The authoritative price changes only on accepted source events.

## 6. Feed health and stale-price handling

Expose explicit connection states:

- CONNECTING
- LIVE
- STALE
- RECONNECTING
- OFFLINE
- DATA_INVALID

Show the last provider event timestamp and last local receive timestamp. A stale threshold must be configured from observed feed cadence and operational requirements; do not hard-code an arbitrary universal timeout.

On disconnect, timeout, malformed data, or a feed gap:
- Do not keep animating the marker as if fresh live data were arriving.
- Freeze the last valid price only with a visible STALE/OFFLINE indication.
- Do not fill missing intervals with invented prices.
- Reconnect without rewriting historical ticks or forecast snapshots.
- Record the gap start/end and recovery state.
- Require a new valid event before returning to LIVE.

If event time and receive time diverge materially, expose feed latency or a data-quality warning rather than silently treating delayed data as current.

## 7. What the UI does not render

The primary world renderer does not render:
- Japanese candlesticks.
- Candle bodies or wicks.
- OHLC bars.
- A conventional chart whose newest bar is pinned to the right edge.
- A fake candle synthesized from each tick.
- A fake “trade” marker for every quote update unless that is a separately requested and accurately labeled visual feature.

The primary visible elements are:
- Central Dukascopy live-price marker and numeric price.
- Historical liquidity objects at their recorded prices/locations.
- Future projected liquidity/scenario objects, visibly differentiated from observed objects.
- Optional price-history trace/afterimage if separately enabled; this is a visual trace, not a candlestick series or trade-flow measurement.
- Price reference grid, session/time context, and fixed HUD controls.

## 8. Internal aggregation is allowed, visible candles are not

Some detection or statistical methods may benefit from fixed-time resampling or OHLC aggregation. This may be performed internally as a derived feature layer, but:

- The UI must not display those internal bars as candles.
- The source tick/quote events remain the primary raw observations.
- The aggregation interval and price basis must be versioned and documented.
- Aggregation must not invent an intrabar path or claim event order that the underlying data cannot resolve.
- Tick-based and derived-bar-based features must identify their source resolution.
- A model trained on internal bars must disclose this to the evaluation system; do not imply that it used tick-level path fidelity.

Prefer direct tick/quote-based event evaluation where valid source data is available and the event's meaning is compatible with quote prices.

## 9. Historical storage and replay

- Store accepted source observations with provider event time, local receive time, price basis, and source metadata.
- Preserve duplicates/out-of-order records in a diagnostics stream when useful, while applying a deterministic policy to the authoritative timeline.
- Do not overwrite raw events with resampled data.
- Replay must use only source events available by the replay cursor.
- The central live marker becomes a replay marker at the selected historical price; it remains centered while the world is inspected around that point.
- Replay must not leak later quotes, later forecast revisions, or future outcomes.

## 10. Acceptance checklist

- [ ] Dukascopy is explicitly identified as the configured live price source.
- [ ] The actual Dukascopy payload and event semantics are inspected before adapter fields are finalized.
- [ ] The displayed live price updates only from accepted source events.
- [ ] The central marker remains fixed at the center while the world moves around it.
- [ ] No candle body, wick, OHLC bar, or candlestick chart is rendered.
- [ ] BID/ASK/MID/provider-price semantics are explicit and consistently applied.
- [ ] Quote updates are not mislabeled as executed trades or traded volume.
- [ ] Event time and local receive time are recorded separately.
- [ ] Duplicate, out-of-order, delayed, stale, malformed, and disconnected states are handled.
- [ ] Visual interpolation never enters model calculations or historical source storage.
- [ ] Internal aggregation may be used by models but never appears as candle UI.
- [ ] Feed failure cannot leave a stale marker falsely presented as live.

## 11. Integration boundaries

- This document governs the live-price feed adapter and live marker.
- Camera positioning is specified in [CENTERED_PRICE_GAME_WORLD_SPEC.md](CENTERED_PRICE_GAME_WORLD_SPEC.md).
- Future forecast semantics remain in [FUTURE_LIQUIDITY_ENGINE_SPEC.md](FUTURE_LIQUIDITY_ENGINE_SPEC.md).
- Historical liquidity remains governed by [MTF_LIQUIDITY_TIER_RENDER_SPEC.md](MTF_LIQUIDITY_TIER_RENDER_SPEC.md).
- No candle chart, order execution, or automated trading is introduced.
