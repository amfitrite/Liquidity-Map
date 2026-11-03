# Future Liquidity Engine — Concept & Technical Specification

**Status:** Architecture/design specification; implementation not yet implied  
**Scope:** Probabilistic forward-looking liquidity zones for XAUUSD  
**Primary use:** Visualize where price may travel, where future stop clusters may form, and which projected zones have the strongest validated evidence.

## 1. Purpose and core distinction

Liquidity Map has two complementary but independent domains:

1. **Historical Liquidity** records price-structure candidates already observed in market data.
2. **Future Liquidity** represents forward-looking estimates produced by statistical and market-structure models.

Future Liquidity is not a live map of actual resting orders. A projected zone is a model estimate, not proof that stop orders, dealer inventory, or institutional orders exist at that price.

Keep the engines separate:
- Do not alter Historical Liquidity detection, records, tiers, lifecycle, rendering, or historical archive as part of this module.
- Future Liquidity has its own IDs, schema, scoring, tiers, lifecycle, validation records, and renderer layer.
- Future and Historical objects may be displayed together, but must never be merged into one object.
- Future projections must be visually distinguishable from observed historical liquidity.
- Cosmetic rendering must never alter model inputs, probabilities, scores, or outcomes.

## 2. Future Liquidity model families

Build the module as a collection of model adapters. Each adapter produces typed evidence; a separate aggregator evaluates that evidence.

### 2.1 Monte Carlo Price-Path Projection — primary foundation

Generate conditional future price paths from recent candle data and the current market regime. Prefer a hybrid model rather than a simple independent random walk.

Candidate methods:
- Block bootstrap to retain short-range dependence and volatility/move sequencing.
- Regime-conditioned sampling for trend, range, high-volatility, and transition states.
- Volatility-adaptive path scaling.
- OHLC-aware event evaluation so a candle touching both boundaries does not create impossible TP/SL or touch ordering.
- Execution/data-quality checks; do not add spread assumptions to price-touch probability unless the target event explicitly includes execution.

Outputs:
- Probability of touching a price zone before a defined horizon.
- Probability of crossing/sweeping a boundary by a defined tolerance.
- Conditional expected high/low and quantile bands.
- Price occupancy/density by price and horizon.
- Distribution of first-passage time to a zone, where supported.

Important:
- Probability of touch is not probability of reversal.
- Probability of sweep is not probability of continuation.
- Probability of a reaction after touch must be a separate event model and separately validated.
- A simulated price-density node is not automatically a liquidity pool. Label it as projected price attraction/density unless structural evidence supports a liquidity interpretation.

### 2.2 Structural Formation Projection

Estimate where new liquidity candidates may form if price develops future swing structures.

Candidate evidence:
- Projected equal-high / equal-low formation areas.
- Potential future swing extension zones.
- Range boundary extension and compression breakout areas.
- Session high/low development scenarios.
- Conditional stop-cluster candidates around repeated or obvious structure.

Do not claim that future EQH/EQL or future swing levels already exist. They are scenarios until price actually forms the structure. When the relevant candles form, the object may be handed off to Historical Liquidity as a newly observed candidate, while preserving a link to the original forecast for evaluation.

### 2.3 Volatility Projection

Estimate the plausible movement envelope for a specified horizon.

Candidate outputs:
- Expected range and quantile range.
- Volatility expansion/compression scenarios.
- Conditional session high/low envelope.
- Extreme-move probability bands.

Volatility bands are context overlays, not liquidity pools by themselves. Keep their object type distinct from projected stop clusters.

### 2.4 Statistical Price Attraction

Estimate conditional price density and historical tendency for price to revisit or spend time near particular regions.

Candidate methods:
- Conditional empirical price distribution.
- Regime-conditioned return distribution.
- Mean-reversion and momentum-conditioned models.
- Historical reaction/occupancy profiles.
- Optional volume-profile-derived context, with source and instrument limitations explicit.

Do not equate frequent historical trading or CFD tick volume with current resting liquidity. If broker tick volume is used, label it as tick-volume-derived context, not centralized traded volume.

### 2.5 GEX / Gamma Exposure

GEX is an optional external-data adapter, not a required foundation of the engine.

For genuine options-derived GEX, require documented source data such as:
- Underlying/contract mapping and price basis.
- Option type, strike, expiry, open interest, implied volatility.
- Contract multiplier and units.
- A documented gamma calculation and sign convention.
- Data timestamp, source, coverage, and stale-data checks.

For XAUUSD, options-derived information may come from related gold futures/options or another explicitly named proxy instrument. Account for basis, expiry, session, and contract differences. Do not silently translate a COMEX or ETF options level into an exact XAUUSD CFD price.

If genuine options data is unavailable:
- Do not label outputs as actual GEX, dealer gamma, Call Wall, Put Wall, or Gamma Flip.
- Either disable the GEX adapter or expose a separately named experimental Gamma-like Proxy.
- The proxy must disclose its inputs and limitations and must not claim to reveal dealer positioning.
- Never allow a proxy to qualify as independent options evidence.

## 3. Projection object taxonomy

Every Future Liquidity object must declare what it represents. Suggested types:

| Type | Meaning | Is it an observed order pool? |
|---|---|---|
| PROJECTED_BSL_CLUSTER | Possible future buy-side stop cluster above price, inferred from structure/scenario | No |
| PROJECTED_SSL_CLUSTER | Possible future sell-side stop cluster below price, inferred from structure/scenario | No |
| PRICE_ATTRACTION_ZONE | Price-density or conditional attraction region | No |
| EXPECTED_RANGE_BOUNDARY | Volatility-derived range edge | No |
| MONTE_CARLO_TOUCH_ZONE | Zone with a calculated probability of being touched within a horizon | No |
| GEX_LEVEL | Options-derived gamma level with validated contract/source data | No; it is options exposure context |
| GAMMA_PROXY_LEVEL | Experimental proxy, clearly distinguished from actual GEX | No |

BSL and SSL describe the hypothesized side of a potential stop cluster. They are not buy/sell trade instructions.

A Future Liquidity map may also show non-liquidity context layers such as expected range, density, and GEX. Keep their semantic types separate; do not convert every overlay into a liquidity orb.

## 4. Future tier hierarchy

Use the same seven visible tier labels as Historical Liquidity for visual familiarity, but give Future Liquidity a completely separate scoring and validation meaning.

| Tier | Name | Future meaning |
|---|---|---|
| SSS | Sovereign Projection | Exceptional projection quality with strong out-of-sample evidence, reliable calibration, and robust independent support |
| SS | Supreme Projection | Very high validated quality and strong cross-model agreement |
| S | Elite Projection | High validated quality with consistent evidence |
| A | Major Projection | Strong projection quality, with some remaining uncertainty |
| B | Strong Projection | Useful evidence and acceptable validation, but not dominant |
| C | Standard Projection | Limited or moderate evidence; use as contextual information |
| D | Minor Projection | Weak, early-stage, or exploratory candidate |

Tier rules:
- Future tier measures **projection quality**, not source timeframe, distance from current price, or raw probability alone.
- Do not copy the Historical timeframe-to-tier mapping into Future Liquidity.
- Do not infer tier from orb size, GEX magnitude, Monte Carlo touch probability, or number of overlapping indicators alone.
- Probability Touch, Probability Sweep, confidence, horizon, and tier are separate fields.
- A high touch probability may simply reflect a nearby zone; it does not automatically make the projection SSS.
- Tier must be recalculated when model version, regime, source freshness, or validation evidence changes.
- Until out-of-sample validation exists, display tier as **PROVISIONAL** or use base label D/C with an explicit provisional marker. Do not present unvalidated tier as objective accuracy.

### 4.1 Candidate quality score

A transparent 0–100 quality score may be prototyped using these initial weights:

| Component | Initial weight | Evidence |
|---|---:|---|
| Out-of-sample model skill | 30% | Walk-forward performance against a simple baseline |
| Probability calibration | 25% | Brier Skill Score, reliability curves, calibration error |
| Independent model-family agreement | 20% | Agreement between genuinely different information sources |
| Structural validity | 15% | Strength and persistence of observed structure supporting the projection |
| Regime suitability and data quality | 10% | Model fit to current regime and source completeness/freshness |

These weights are starting design assumptions, not empirically optimal parameters. Version and store them. Tune only through training/validation data and retain a separate untouched test period.

### 4.2 Anti-double-counting rules

- Multiple Monte Carlo variants using the same candle history count as one model family, not independent votes.
- Several indicators derived from the same OHLC inputs are correlated evidence.
- GEX from options data can be a separate family only when the data is authentic, timestamped, and correctly mapped.
- Structural evidence and Monte Carlo evidence may share price data; measure their dependence rather than assuming independence.
- Agreement must be confidence-weighted and correlation-aware. Never simply sum every coincident signal.

### 4.3 Tier eligibility gates

Before assigning a high tier, require:
1. Sufficient comparable out-of-sample observations for the relevant symbol, timeframe, horizon, and regime.
2. Positive skill against a clearly defined baseline.
3. Acceptable probability calibration.
4. No critical data-quality or stale-source failure.
5. Robustness across walk-forward windows, not one favorable period.
6. Independent evidence where the tier definition requires multi-family support.

Determine minimum sample sizes and tier cutoffs from validation design. Do not invent arbitrary accuracy percentages or hard-code SSS thresholds before the test protocol and sample distribution are established. If a gate fails, cap the tier or mark it provisional.

## 5. Probability definitions — must be explicit

All probabilities must name the event, zone, horizon, data basis, and model version.

Recommended definitions:
- **P_TOUCH(zone, H):** fraction/estimated probability of price entering the zone at least once before horizon H.
- **P_SWEEP(boundary, tolerance, H):** probability of crossing the boundary by at least the stated tolerance before H.
- **P_REACTION(zone, definition, H):** probability of a separately defined reaction after touch. This is a separate model and must not be inferred from P_TOUCH.
- **P_CONTINUATION(zone, definition, H):** probability of continuing beyond the zone after touch, also separately defined.
- **Expected arrival time:** conditional distribution of first touch time, not a guaranteed ETA.

Use calibrated out-of-sample probabilities where possible. Raw Monte Carlo path frequency is only a model estimate until calibrated. Report uncertainty intervals or sample counts when available.

## 6. Timeframe and forecast horizon

Separate the chart timeframe from the forecast horizon. They are related but not interchangeable.

Suggested initial horizon presets for testing only:

| Context | Candidate forecast horizons |
|---|---|
| M1 | 5, 15, 30, 60 minutes |
| M5 | 15, 30, 60, 240 minutes |
| M15 | 1, 2, 4, 8 hours |
| H1 | 4, 8, 24, 48 hours |
| H4 | 12, 24, 72 hours |

These are configurable research horizons, not claims that each model is accurate at those durations. Validate each horizon independently. Avoid displaying a long-horizon projection as a precise M1 target.

## 7. Lifecycle and expiration

Future objects need their own lifecycle, distinct from Historical Liquidity:

- **PROJECTED:** created by a model and awaiting activation/monitoring.
- **ACTIVE:** model inputs remain valid and the forecast horizon has not expired.
- **APPROACHING:** price is within a configured distance of the projected zone.
- **TOUCHED:** price entered the zone; record time and path.
- **SWEPT:** the pre-defined boundary-crossing event occurred.
- **REALIZED:** the forecast event was evaluated and its outcome label finalized.
- **EXPIRED:** forecast horizon elapsed without the event.
- **INVALIDATED:** a pre-defined invalidation condition occurred before horizon completion.
- **SUPERSEDED:** replaced by a newer forecast version; retain the old forecast for scoring.

Do not delete expired, invalidated, or superseded forecasts. They are essential for unbiased evaluation. A touched or swept forecast is not automatically a successful prediction if its event definition differs from the forecast target.

## 8. Visual language and renderer contract

Future and Historical layers must be immediately distinguishable.

Suggested visual language:
- Historical Liquidity: existing solid orb treatment and existing tier identity.
- Future Liquidity: translucent/holographic orb or zone treatment, dashed/segmented boundary, subtle projected-path texture.
- Keep the same tier label hierarchy (SSS–D) but add a visible **FUTURE** marker or different silhouette so users cannot mistake a projection for an observed pool.
- Render projected paths as scenario paths or probability fans, never as a single certain route.
- Use separate line/texture conventions for Monte Carlo density, volatility envelope, GEX context, and structural candidate zones.
- Display horizon, probability event, confidence/validation status, and source family on selection/hover.
- Provide toggles per model family and a master Future Liquidity toggle.
- No decorative trail may imply actual order flow or certainty.

Do not reuse historical trail semantics for a predicted path. The existing orb/trail system describes recorded historical movement; future paths require a separate renderer component and legend.

## 9. Suggested data contract

Illustrative schema only; adapt names to the repository's actual data model.

~~~python
{
    "id": "stable_forecast_id",
    "symbol": "XAUUSD",
    "object_type": "PROJECTED_BSL_CLUSTER",
    "side": "BSL",
    "price_low": 4050.0,
    "price_high": 4055.0,
    "chart_timeframe": "M15",
    "forecast_horizon_seconds": 14400,
    "model_families": ["MONTE_CARLO", "STRUCTURAL", "VOLATILITY"],
    "probability_touch": 0.78,
    "probability_sweep": 0.54,
    "probability_reaction": None,
    "quality_score": None,
    "tier": "PROVISIONAL",
    "confidence_label": "UNVALIDATED",
    "current_regime": "UNKNOWN",
    "model_version": "model-version",
    "calibration_version": None,
    "created_at_utc": "timestamp",
    "expires_at_utc": "timestamp",
    "status": "PROJECTED",
    "evaluation": None
}
~~~

All numeric values above are illustrative only. They are not XAUUSD predictions. Store exact event definitions and validation metadata alongside any probability.

Recommended additional metadata:
- Source dataset and last available candle timestamp.
- Broker/feed and instrument mapping.
- Model parameters and random seed or reproducibility metadata.
- Forecast generation timestamp and timezone.
- Training/validation/test window IDs.
- Calibration bucket or calibration model version.
- Outcome label and evaluation timestamp.
- Invalidation and expiry reason.

## 10. Validation and anti-hallucination requirements

A future projection must be testable and falsifiable.

Required evaluation:
- Chronological walk-forward testing; never random-shuffle time series across train/test.
- Purge/embargo overlapping forecast windows where necessary to prevent leakage.
- Compare against transparent baselines (for example ATR bands, empirical unconditional frequency, and simple regime-conditioned models).
- Brier Score and Brier Skill Score for binary events.
- Reliability diagram / calibration curve and calibration error.
- Precision/recall or event hit rate with clearly defined event labels.
- Zone-width-aware evaluation so very wide zones do not win trivially.
- Time-to-touch and horizon-specific evaluation.
- Results split by M1/M5/M15/H1/H4, forecast horizon, and market regime.
- Confidence intervals and sample counts; show when evidence is insufficient.
- Track false positives, missed events, expired forecasts, and invalidated forecasts.
- Keep an immutable forecast log so forecasts cannot be rewritten after the outcome is known.

Do not claim accuracy from in-sample simulation. Do not optimize thresholds on the final test set. Do not display model output as fact. If calibration or validation is insufficient, visibly label the projection **EXPERIMENTAL / UNVALIDATED**.

## 11. Performance and reliability boundaries

- Future model computation must run independently of the UI render loop.
- Cache reusable simulations and invalidate only when required input data changes.
- Use configurable simulation counts and adaptive budgets; measure latency before choosing defaults.
- Never reduce validation rigor silently to meet a frame-rate target.
- Separate model update cadence from display refresh cadence.
- Keep last valid forecast with timestamp and stale indicator if a model update fails; do not silently show stale forecasts as current.
- Rendering limits must not delete forecast records or evaluation history.
- Log model failures, missing data, stale inputs, and fallback use.

## 12. Implementation phases

### Phase 0 — data and evaluation foundation
- Inspect actual repository architecture and candle data contract.
- Define timezone, price precision, symbol/feed metadata, and candle completeness.
- Build immutable forecast/outcome logging and chronological walk-forward evaluator.
- Implement baseline forecasts first.

### Phase 1 — Monte Carlo projection
- Implement regime-aware block bootstrap/hybrid path generator.
- Produce price-density, quantile range, P_TOUCH, and P_SWEEP outputs.
- Add event definitions, reproducibility, and calibration workflow.
- Do not add auto-entry, buy-limit, or sell-limit recommendations.

### Phase 2 — Structural and volatility projections
- Add conditional structural candidate zones and volatility envelopes.
- Keep true forecast objects separate from context overlays.
- Evaluate whether structural evidence improves the baseline out of sample.

### Phase 3 — Statistical attraction and optional external data
- Add conditional empirical density/reaction models.
- Add genuine options-derived GEX only after source and mapping validation.
- Expose Gamma-like Proxy only as an explicitly experimental separate type.

### Phase 4 — Confluence, tiering, and UI
- Implement correlation-aware aggregation and quality score versioning.
- Enable tier labels only after validation gates are met.
- Add Future-only visual layer, controls, legend, selection details, and stale indicators.
- Preserve Historical Liquidity visuals and behavior.

### Phase 5 — robustness and release
- Run out-of-sample tests and regime stress tests.
- Benchmark model latency and UI rendering separately.
- Verify forecast immutability, expiry, invalidation, and reproducibility.
- Ship only with documented limitations and evaluation results.

## 13. Explicit non-goals

This specification does not authorize:
- Changing or replacing Historical Liquidity detection or historical tier rules.
- Treating CFD tick volume as centralized order-book volume.
- Claiming access to institutional stop orders or dealer positioning without source data.
- Presenting Monte Carlo paths as deterministic future price paths.
- Converting projected zones directly into buy-limit/sell-limit orders or trading signals.
- Building an automated trading/EA system.
- Hiding failed forecasts or altering forecast history after outcomes are known.

## 14. Acceptance checklist

- [ ] Historical Liquidity engine remains unchanged and independent.
- [ ] Future Liquidity has separate data models, IDs, scoring, lifecycle, and renderer.
- [ ] Every projected object has a typed source and explicit forecast horizon.
- [ ] BSL/SSL projected clusters are distinguished from price-density and volatility overlays.
- [ ] Monte Carlo produces explicit, testable event probabilities.
- [ ] Touch, sweep, reaction, and continuation are separate events.
- [ ] GEX is genuine only when options data and contract mapping are documented.
- [ ] Any Gamma-like Proxy is visibly labeled experimental and is not presented as dealer positioning.
- [ ] Future tiers SSS, SS, S, A, B, C, D measure validated projection quality, not historical timeframe rank.
- [ ] Tier cutoffs are data-derived and gated; no arbitrary accuracy claims.
- [ ] Model-family dependence is considered before confluence scoring.
- [ ] Forecasts are immutable and every outcome, expiry, and invalidation is retained.
- [ ] Walk-forward, calibration, baseline comparison, and regime-split evaluation are available.
- [ ] Future visuals cannot be confused with observed historical liquidity.
- [ ] No auto-entry or trade execution is introduced by this specification.
