# Liquidity Map — MTF Liquidity, Tier & Rendering Specification

Status: Design specification  
Scope: XAUUSD liquidity detection presentation and rendering

## 1. Core principles

- The default world view uses a centered Dukascopy live-price marker and game-like follow camera, not a conventional candlestick chart. No candles are rendered. See [Centered Live-Price Game World specification](CENTERED_PRICE_GAME_WORLD_SPEC.md) and [Dukascopy Live Price Feed specification](DUKASCOPY_LIVE_PRICE_FEED_SPEC.md).
- In FOLLOW mode, the latest accepted live time/price point stays at the center of the main playfield. Historical world content is left/past; future scenarios are right/future; higher prices are above and lower prices are below the live anchor.
- Camera transforms and visual offsets must never rewrite source timestamps, exact prices, object IDs, detection results, lifecycle, or tiers.
- Historical detection may use raw price updates or internal derived bars where appropriate, but any such bars are data/model inputs only and must not appear as visible candlesticks.

- Keep every liquidity object independent, with its own ID, price zone, source timeframe, type, side, tier, and lifecycle status.
- Never merge separate liquidity objects into one cluster or discard their identities for visual convenience.
- Rendering limits apply only to visible objects. Detection, storage, and lifecycle history remain independent of those limits.
- Orb size and visual treatment may reflect tier/structural strength.
- Trail effects are visual only; they must not affect liquidity calculations, scoring, or lifecycle.
- Retain mitigated/swept liquidity in history. It may be hidden from the active layer by default, but must not be deleted.
- A detected level is a price-structure-based liquidity candidate, not proof of resting institutional orders.

## 2. MTF liquidity inventory

| Timeframe | Candidate liquidity types |
|---|---|
| MN1 | Previous Month High/Low (PMH/PML), monthly swing high/low, monthly EQH/EQL |
| W1 | Previous Week High/Low (PWH/PWL), weekly swing high/low, weekly EQH/EQL |
| D1 | Previous Day High/Low (PDH/PDL), daily swing high/low, daily EQH/EQL |
| H4 | Major H4 swing high/low, H4 EQH/EQL, H4 range high/low |
| H1 | H1 swing high/low, H1 EQH/EQL, intraday range high/low |
| M15 | Asia/London/New York session high/low, M15 swing high/low, M15 EQH/EQL, opening-range high/low |
| M5 | M5 minor swing high/low, M5 EQH/EQL, micro-range high/low |
| M1 | M1 micro swing high/low, M1 EQH/EQL, internal liquidity |

Session boundaries must be configurable and timezone-aware. Store timestamps unambiguously (preferably UTC); allow Asia/Jakarta display.

### Liquidity side

- BSL (Buy-Side Liquidity): candidate levels above price, commonly above swing highs, EQH, PDH/PWH/PMH.
- SSL (Sell-Side Liquidity): candidate levels below price, commonly below swing lows, EQL, PDL/PWL/PML.

Side is a classification of the likely liquidity side, not a directional trade recommendation.

### Separate confluence layers

FVG, Order Block, VWAP, and Volume Profile are not automatically liquidity pools. Keep them as separate confluence/overlay objects. CFD tick volume must not be described as actual centralized traded volume.

## 3. Tier taxonomy

| Tier | Name | Default source timeframe | Meaning |
|---|---|---|---|
| SSS | Sovereign Liquidity | MN1 | Highest-priority macro structure candidate |
| SS | Supreme Liquidity | W1 | Major weekly external liquidity |
| S | Elite Liquidity | D1 | Significant daily external liquidity |
| A | Major Liquidity | H4 | Major higher-intraday structure |
| B | Strong Liquidity | H1 | Significant intraday structure |
| C | Standard Liquidity | M15 | Session/local structure |
| D | Minor Liquidity | M5, M1 | Short-term internal structure |

The timeframe mapping is a base tier, not an unconditional final score. Upgrade a candidate only through explicit, measurable confluence rules. Do not upgrade solely because it is close to current price. A higher-timeframe candidate must not remain active if its lifecycle is swept or invalidated.

### Suggested tier scoring inputs

1. Source timeframe/base tier.
2. MTF confluence: distinct timeframes identifying nearby, independently detected levels.
3. Structural significance: confirmed swing/pivot quality and surrounding structure.
4. EQH/EQL quality: touch count and dispersion within a volatility-normalized tolerance.
5. Freshness: whether the level has been approached or swept.
6. Zone quality: price dispersion/width among constituent observations.
7. Data quality: completeness and validity of source candles.

Keep base tier, final tier, and numeric strength score separate. Document score weights and thresholds. If no validated scoring model exists, show base tier and mark final tier provisional rather than presenting an arbitrary score as objective truth.

## 4. Lifecycle status

Keep lifecycle status separate from tier:

- FRESH: not yet touched under the defined touch rule.
- TESTED: price entered/tested the zone but sweep condition is not met.
- PARTIALLY_SWEPT: some constituent levels in a multi-observation zone have been swept, while others remain.
- SWEPT: the defined sweep condition has been met.
- INVALIDATED: the candidate no longer satisfies structural/detection rules.

Define touch and sweep conditions explicitly, using candle OHLC and configurable tolerance. Avoid ambiguous visual judgments. Preserve historical states/events with timestamps.

## 5. Rendering budget

Initial default rendering budget:

| Source timeframe | Maximum visible active objects |
|---|---:|
| MN1 | 4 |
| W1 | 6 |
| D1 | 8 |
| H4 | 12 |
| H1 | 14 |
| M15 | 18 |
| M5 | 18 |
| M1 | 20 |
| **Total** | **100** |

Hard cap: **120 simultaneously rendered liquidity objects**.

These are render budgets, not detection/storage limits. If fewer candidates exist, render fewer. If a timeframe exceeds its budget, prioritize valid visible candidates by tier, structural quality, freshness, and viewport relevance. Do not delete, merge, or mutate underlying records to satisfy the budget.

### Additional visual-effect budgets

| Visual element | Initial maximum |
|---|---:|
| Full-detail orb treatment | 40 |
| Text labels | 30 |
| Simultaneous active trails | 15 |
| Simultaneous particle effects | 5–8 |

Apply visual complexity progressively: SSS/SS/S/A may receive premium orb treatment; B/C medium or simplified treatment; D lightweight treatment. Trails and particles are optional and prioritized by tier and viewport relevance. A trail is a visual trace only; it must not imply measured liquidity flow or alter price levels.

## 6. Viewport and zoom-based LOD

- Zoomed out: prioritize MN1, W1, D1, H4; suppress lower-timeframe rendering when visually irrelevant.
- Medium zoom: prioritize D1, H4, H1, M15.
- Zoomed in: prioritize H1, M15, M5, M1.

LOD may simplify or hide objects, but must preserve records and stable IDs. Reuse render resources/object pools where supported.

Do not visually cluster or merge separate liquidity orbs. If levels overlap, render separate orbs with collision-aware offsets or distinct lanes while preserving exact price coordinates and identity.

## 7. Suggested object schema

~~~python
{
    "id": "stable_unique_id",
    "symbol": "XAUUSD",
    "timeframe": "H4",
    "liquidity_type": "EQUAL_HIGH",
    "side": "BSL",
    "price_low": 4020.0,
    "price_high": 4021.0,
    "base_tier": "A",
    "final_tier": "A",
    "strength_score": None,
    "score_version": None,
    "source": "H4_SWING",
    "mtf_confluence": ["D1", "H4"],
    "touch_count": 0,
    "status": "FRESH",
    "detected_at": "UTC timestamp",
    "last_updated": "UTC timestamp"
}
~~~

Illustrative values only. Do not populate numeric strength score until a documented scoring method is implemented and tested.

## 8. Performance implementation requirements

1. Separate detection/data lifecycle from rendering.
2. Apply viewport culling before creating/updating expensive visual effects.
3. Reuse orb, trail, and particle resources through object pooling where supported.
4. Batch compatible drawing operations or use instancing where supported by the renderer.
5. Avoid full scene reconstruction on every incoming candle or zoom event.
6. Update only changed objects where possible.
7. Keep labels and particle effects under independent budgets.
8. Add diagnostics for FPS, visible object count, active trail count, particle count, and frame/render time.
9. Benchmark with 100 visible objects and then the 120-object hard cap on the target machine. Do not promise a particular FPS without measurement.
10. Performance degradation must never change detection results or silently drop stored liquidity.

## 9. Acceptance criteria

- MTF inventory covers MN1, W1, D1, H4, H1, M15, M5, and M1.
- BSL and SSL are independently classified.
- Base tier and final tier are separate fields.
- Tier and lifecycle status are independent.
- Render defaults are 100 objects total with a hard cap of 120.
- Detection and historical storage are not capped by render limits.
- Distinct liquidity objects remain distinct; no clustering merge.
- Zoom/LOD only affects presentation.
- Trail effects do not affect calculations.
- Swept/mitigated history remains available.
- FPS and render diagnostics are available for benchmarking.
