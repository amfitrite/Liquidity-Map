# Liquidity Map — Master Liquidity Registry

Status: Detection and data-model specification (not proof of implementation)
Instrument focus: XAUUSD
Scope: Canonical inventory of historical liquidity candidates and separately typed market-context overlays

## 1. Purpose and epistemic rules

This registry defines what the project may detect and how each result must be classified. A price-structure candidate is not direct evidence of resting stop orders, institutional orders, or order-book depth. Use terms such as *liquidity candidate*, *likely BSL/SSL location*, or *structural reference* rather than claiming that actual orders are visible.

Every detector must have a versioned definition, input timeframe, price basis, tolerance, confirmation rule, invalidation rule, and test coverage. Do not register a detector as implemented merely because it appears in this specification.

Keep three epistemic classes distinct:

- **DETECTED_CANDIDATE** — the required observed price structure exists and passes the detector's rules.
- **PROVISIONAL_CANDIDATE** — a partial or developing structure exists but confirmation requirements are not yet met.
- **CONTEXT_ONLY** — a reference or analytical overlay that is not itself a liquidity pool.

A level can be a detected structural candidate without proving that stops are actually resting there.

## 2. Canonical registry families

### A. Period and session extremes

| Registry type | Definition / detector concept | Typical side |
|---|---|---|
| PREVIOUS_MONTH_HIGH / LOW | Completed previous calendar month's extreme | BSL / SSL |
| PREVIOUS_WEEK_HIGH / LOW | Completed previous trading week's extreme | BSL / SSL |
| PREVIOUS_DAY_HIGH / LOW | Completed previous trading day's extreme | BSL / SSL |
| PREVIOUS_SESSION_HIGH / LOW | Completed Asia, London, or New York session extreme, stored per session | BSL / SSL |
| CURRENT_SESSION_HIGH / LOW | Developing current-session extreme; provisional until session closes | BSL / SSL |
| SESSION_OPENING_RANGE_HIGH / LOW | High/low of a configured opening-range window | BSL / SSL |
| INITIAL_BALANCE_HIGH / LOW | High/low of a configured initial-balance period; commonly the first hour, but duration must be configurable | BSL / SSL |
| DAILY_OPEN / WEEKLY_OPEN / MONTHLY_OPEN | Period opening price; reference level, not automatically a stop pool | CONTEXT_ONLY by default |

Previous period/session levels are distinct records from current period/session levels. Session definitions must be timezone-aware, configurable, and stored in UTC; Asia/Jakarta may be used for display.

### B. Swing and equal-level structure

| Registry type | Definition / detector concept | Typical side |
|---|---|---|
| SWING_HIGH / SWING_LOW | Confirmed pivot using configurable left/right bars or another causal pivot rule | BSL / SSL |
| INTERNAL_SWING_HIGH / LOW | Smaller confirmed pivot inside a defined dealing range or larger swing structure | BSL / SSL |
| EQUAL_HIGHS / EQUAL_LOWS | Two or more qualifying highs/lows within a volatility-normalized price tolerance | BSL / SSL |
| MULTIPLE_TOPS / MULTIPLE_BOTTOMS | Repeated tests of a common region; distinguish from strict EQH/EQL using separate tolerance/touch rules | BSL / SSL |
| UNMITIGATED_SWING_HIGH / LOW | A swing candidate that has not met the configured sweep/mitigation rule | BSL / SSL |
| EXTERNAL_RANGE_HIGH / LOW | Confirmed outer boundary of a declared dealing range | BSL / SSL |
| INTERNAL_RANGE_HIGH / LOW | Confirmed inner boundary within a larger dealing range | BSL / SSL |
| RANGE_MIDPOINT | 50% midpoint of a declared range; reference/confluence only | CONTEXT_ONLY |

A pivot is not confirmed until its confirmation rule is satisfied. If a right-bar pivot rule is used, the detector's confirmation delay must be explicit and must not backdate the time at which the level became knowable.

### C. Geometric structure

| Registry type | Definition / detector concept | Typical side |
|---|---|---|
| TRENDLINE_HIGH / LOW | A diagonal line fitted to at least the configured number of confirmed swing highs/lows, with documented fit tolerance | BSL / SSL candidate |
| CHANNEL_UPPER / LOWER | Upper/lower boundary of a validated price channel built from confirmed pivots | BSL / SSL candidate |
| COMPRESSION_BOUNDARY_HIGH / LOW | Converging boundaries from a measurable contracting range/triangle/wedge structure | BSL / SSL candidate |
| DIAGONAL_EQUAL_HIGHS / LOWS | Repeated highs/lows aligned along a diagonal tolerance band; separate from horizontal EQH/EQL | BSL / SSL candidate |

Geometric detectors must define pivot count, fit method, maximum residual, minimum separation, line/channel expiry, and whether the boundary is still valid. A visually drawn line alone is not sufficient. A trendline/channel is a *candidate boundary*, not proof that stops are placed on it.

### D. Internal structure and inducement hypotheses

| Registry type | Definition / detector concept | Typical side |
|---|---|---|
| INDUCEMENT_CANDIDATE_HIGH / LOW | Internal swing that may act as a nearer liquidity objective before an external level; requires an explicit structural pattern rule | BSL / SSL hypothesis |
| INTERNAL_BSL / INTERNAL_SSL | Qualifying internal swing/equal-level structures inside a declared range | BSL / SSL |
| LIQUIDITY_VOID_BOUNDARY_HIGH / LOW | Boundary of a fast-travel / low-observation-density region, only if computed from a defined price/time statistic | CONTEXT_ONLY by default |

“Inducement” is interpretive and must not be inferred merely because a swing was later swept. The detector must state the pattern criteria and record the evidence available at detection time. Do not use future price action to retroactively label an earlier swing as inducement.

### E. Psychological price references

| Registry type | Definition / detector concept | Default classification |
|---|---|---|
| ROUND_NUMBER_LEVEL | Configurable major round-number price levels | CONTEXT_ONLY |
| HALF_NUMBER_LEVEL | Configurable half-step psychological price levels | CONTEXT_ONLY |

For XAUUSD, step sizes must be configurable per feed/quote precision and tested across price regimes. A round number is not automatically a liquidity pool. It may become a separate candidate only when an observed qualifying structure (such as repeated highs/lows) forms around it; preserve the psychological reference and the structural candidate as related but distinct records.

### F. Gap and opening references

| Registry type | Definition / detector concept | Default classification |
|---|---|---|
| SESSION_GAP_BOUNDARY | Boundary of a measurable gap between defined session close/open prices | CONTEXT_ONLY |
| WEEKLY_GAP_BOUNDARY | Boundary of a measurable weekend/week-open gap | CONTEXT_ONLY |
| OPENING_GAP_ZONE | Gap zone with explicit source timestamps and price basis | CONTEXT_ONLY |

A gap is not automatically liquidity. Keep gap boundaries as context objects unless a separate, observed swing/equal-level detector qualifies a liquidity candidate there.

## 3. Separate confluence and context objects — never auto-promote

The following are useful analytical layers but must not be automatically registered as historical liquidity pools:

| Object family | Examples | Correct semantics |
|---|---|---|
| Imbalance | FVG, displacement gap | Price-imbalance/confluence zone |
| Supply/demand structure | Order Block, breaker block | Price-reaction hypothesis |
| Volume profile | POC, VAH, VAL, HVN, LVN | Profile statistics; not resting order depth |
| Price reference | VWAP, anchored VWAP, daily/weekly open | Reference/confluence |
| Volatility | ATR bands, expected range, volatility envelope | Volatility context |
| Options context | GEX, gamma flip, call/put wall | External options-derived estimate with instrument mapping and assumptions |
| Probabilistic forecast | Monte Carlo touch zone, price density, quantile fan | Forecast distribution, not observed liquidity |
| Flow proxy | Tick volume, delta/CVD proxy | Feed-specific activity proxy, not centralized XAUUSD traded volume |

If a context layer overlaps a liquidity candidate, link them through a confluence relation. Do not convert the context object into a liquidity candidate or merge their identities.

## 4. BSL / SSL classification

- **BSL**: a candidate structure whose likely stop-side location is above its relevant reference price, commonly above highs.
- **SSL**: a candidate structure whose likely stop-side location is below its relevant reference price, commonly below lows.
- **CONTEXT_ONLY**: no BSL/SSL claim is made.

Side is not a trade direction or an assertion that orders have been observed. For diagonal structures, side must be computed relative to the relevant time/price point, not hard-coded for the entire line.

## 5. Canonical identity, duplicates, and relationships

Do not collapse distinct detector outputs into one object. Use stable IDs and explicit relationships:

- **same_structure_as**: two detector records refer to the same underlying observed structure, but remain separately inspectable.
- **overlaps_with**: price zones overlap without asserting identical structure.
- **confluence_with**: independent context or timeframe evidence overlaps this candidate.
- **derived_from**: a composite structure was derived from one or more source records.
- **supersedes**: a newer version replaces a detector interpretation; preserve the old record and its audit trail.

Deduplication is metadata/linking, not deletion or visual clustering. A single swing high may legitimately be referenced by a timeframe-specific swing detector, an EQH detector, and a session-extreme detector. Preserve the detector-specific records and explain their relationship.

A recommended canonical identity tuple is:
`symbol + detector_type + source_timeframe + source_period/session_id + anchor_event_ids + detector_version`

Never use screen coordinates or rounded display prices as identity keys.

## 6. Detection contract

Every detector implementation must publish:

1. `detector_type` and semantic family.
2. `detector_version`.
3. `symbol`, `source_timeframe`, and source feed.
4. `price_basis` (bid, ask, mid, or documented derived price).
5. `anchor_event_ids` and source timestamps.
6. Confirmation rule and the exact time the candidate became knowable.
7. Tolerance/thresholds, preferably volatility-normalized where appropriate.
8. Candidate zone `price_low` and `price_high`.
9. Side: BSL, SSL, or CONTEXT_ONLY.
10. Epistemic class: DETECTED_CANDIDATE, PROVISIONAL_CANDIDATE, or CONTEXT_ONLY.
11. Invalidation, touch, breach, sweep, and expiry rules as applicable.
12. Evidence and reason codes sufficient to reproduce the decision.

Use causal inputs only. No future bars, future ticks, or hindsight labels may influence the original detection timestamp or score.

## 7. Lifecycle and event semantics

Lifecycle remains independent of detector type and visual tier. Reuse the project's explicit lifecycle contract (FRESH, TESTED, PARTIALLY_SWEPT, SWEPT, INVALIDATED, and optional EXPIRED).

Do not treat approach as touch, breach as sweep, or breach as reversal. A sweep-reclaim requires a separately defined penetration and reclaim sequence. Handle gaps and intrabar event ordering ambiguity explicitly. Retain historical records and lifecycle events rather than deleting swept candidates.

## 8. Suggested data model

```python
{
    "id": "stable_unique_id",
    "symbol": "XAUUSD",
    "detector_type": "TRENDLINE_HIGH",
    "semantic_family": "GEOMETRIC",
    "source_timeframe": "M15",
    "source_feed": "DUKASCOPY",
    "price_basis": "documented_quote_basis",
    "price_low": 4020.0,
    "price_high": 4021.0,
    "side": "BSL",
    "epistemic_class": "DETECTED_CANDIDATE",
    "base_tier": "C",
    "final_tier": None,
    "detector_version": "1.0.0",
    "anchor_event_ids": ["pivot_id_1", "pivot_id_2"],
    "detected_at": "UTC timestamp",
    "status": "FRESH",
    "relationships": [],
    "evidence": {},
    "reason_codes": []
}
```

Illustrative schema only. Do not assign a final tier or numeric confidence until a documented, tested scoring policy exists. Context-only records should use their own object schema and renderer rather than masquerading as liquidity orbs.

## 9. Recommended implementation priority

This is a proposed order, not a claim that the detectors already exist.

### Phase 1 — add high-value structural coverage
1. Previous session high/low per session.
2. Initial Balance high/low and configurable opening range.
3. Internal swing high/low and explicit external/internal range boundaries.
4. Unmitigated swing tracking (derived lifecycle attribute, not a duplicate independent price level).
5. Multiple tops/bottoms with separate rules from strict EQH/EQL.

### Phase 2 — geometric and conditional structures
1. Trendline boundaries.
2. Channel boundaries.
3. Compression boundaries.
4. Diagonal equal highs/lows.
5. Inducement candidate detector, only after its causal pattern definition is testable.

### Phase 3 — contextual references
1. Round and half-number references.
2. Daily/weekly/monthly and session opening prices.
3. Gap boundaries and liquidity-void context.

Context references should not receive liquidity tiers by default. Promote nothing automatically.

## 10. Acceptance checklist

- [ ] Every detector has a versioned, causal definition.
- [ ] Historical candidates are distinct from context/overlay objects.
- [ ] BSL/SSL is a side hypothesis, not a trade recommendation or observed order claim.
- [ ] Period/session boundaries are configurable and timezone-aware.
- [ ] Trendline/channel/compression candidates require measurable pivot and fit rules.
- [ ] Inducement is not assigned retrospectively using future outcomes.
- [ ] Round numbers and gaps remain context-only by default.
- [ ] FVG, OB, VWAP, profile levels, ATR, GEX, and Monte Carlo outputs are not auto-promoted to liquidity.
- [ ] Overlapping detector outputs keep unique IDs and explicit relationships.
- [ ] No hindsight leakage in detection time, tier, or score.
- [ ] Lifecycle events and swept history are preserved.
- [ ] This specification is not represented as proof of detector implementation.
