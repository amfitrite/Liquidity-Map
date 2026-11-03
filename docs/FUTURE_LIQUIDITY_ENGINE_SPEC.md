# Future Liquidity Engine — Concept & Technical Specification

**Version:** 2.0  
**Status:** Corrected architecture specification; implementation and predictive performance are not yet verified  
**Scope:** Forward-looking price scenarios and potential liquidity-structure formation for XAUUSD  
**Design priority:** Falsifiable forecasts, explicit event definitions, honest uncertainty, and strict separation from Historical Liquidity

## 0. Executive definition

Future Liquidity is a collection of **forward-looking, testable scenarios**. It is not a live order book, a map of known stop orders, or a deterministic prediction of the next price path.

The system must distinguish three different questions:

1. **Where might price travel?** — estimated with conditional price-path, volatility, and statistical-distribution models.
2. **Where might a new liquidity-relevant structure form if a scenario develops?** — estimated with conditional structural-formation scenarios. Until subsequent observed Dukascopy price updates meet the required structural criteria, this is only a scenario, not an existing liquidity pool.
3. **What external market context may affect price?** — for example, options-derived gamma exposure, when authentic options data and mapping are available.

These outputs must not be collapsed into one generic “liquidity” object. A price-density area, expected-range boundary, potential EQH/EQL formation scenario, and options-derived gamma level have different meanings and must retain different types.

**Core rule:** a model may estimate a future price event; it cannot prove that resting stop orders or institutional orders exist at the projected price.

## 1. Domain separation

### 1.1 Historical Liquidity

Historical Liquidity contains candidates detected from price structures that have already formed in observed market data. It owns its own detection, IDs, tier rules, lifecycle, storage, and renderer.

### 1.2 Future Liquidity

Future Liquidity contains immutable forecast records and separately evaluated outcomes. It owns its own IDs, model versions, probabilities, validation state, tier policy, lifecycle, and renderer.

- Do not change Historical Liquidity detection or lifecycle to implement Future Liquidity.
- Never merge a future forecast object into a historical liquidity object.
- When a projected structural scenario actually forms, create a new Historical Liquidity candidate through the Historical engine. Link it to the source forecast with `origin_forecast_id`; do not transform or overwrite the forecast.
- A future forecast that is touched, wrong, expired, invalidated, or superseded must remain in the forecast archive.
- Visual effects must never change price coordinates, event outcomes, probabilities, scores, tiers, or model inputs.

### 1.3 Evidence labels

Every displayed output must make its epistemic status clear:

| Label | Meaning |
|---|---|
| OBSERVED | Directly present in the selected source data |
| MODEL_ESTIMATE | Computed probability or distribution from a model |
| SCENARIO | Conditional possibility; not yet an observed structure |
| EXTERNAL_CONTEXT | Data from another market/instrument, with source and mapping shown |
| EXPERIMENTAL | Not yet adequately validated |
| STALE | Input data or external source is no longer fresh enough for the configured policy |

Never style MODEL_ESTIMATE or SCENARIO as if it were OBSERVED.

## 2. Model families and what each one can claim

Implement each family as an independent adapter that emits typed evidence. A separate validation and aggregation layer decides whether the evidence is usable.

### 2.1 Conditional price-path simulation — Monte Carlo / block bootstrap

Purpose: estimate the distribution of possible future price paths conditional on current information.

Recommended starting approach:
- Sample historical return blocks rather than independent single-bar returns.
- Condition eligible blocks on a documented market-regime classification and, where justified by out-of-sample evidence, session or volatility state.
- Use volatility normalization/scaling only when the transformation is defined and tested without future information.
- Preserve relevant short-run dependence and volatility clustering; do not assume an independent Gaussian random walk.
- Reconstruct paths from the declared price basis.
- Run explicit event evaluators on simulated paths to estimate touch, breach, sweep-reclaim, reaction, and continuation events separately.
- Store model parameters, data cutoff, random seed or reproducibility metadata, block-selection method, and model version.

Monte Carlo is a **sampling and scenario-generation technique**, not an independent source of market information. One thousand simulations generated from the same underlying Dukascopy price history do not represent one thousand independent market observations.

Outputs may include:
- Raw and calibrated probability of touch by horizon.
- Raw and calibrated probability of breach or sweep-reclaim by horizon.
- Conditional quantile bands for future price and path extrema.
- First-touch-time distribution, where the event can be resolved reliably.
- Price occupancy/density by price interval and time horizon.
- Monte Carlo sampling uncertainty, separately from model/data uncertainty.

Do not describe a simulated path as the route price will take. Render an ensemble, quantile fan, or density distribution—not a single authoritative path.

### 2.2 Structural-formation scenarios

Purpose: estimate conditions under which a new price structure that may later become a liquidity candidate could form.

Potential scenario types:
- A future swing-high or swing-low formation region.
- A possible equal-high/equal-low formation scenario.
- A range-boundary or compression-breakout scenario.
- A potential session-extreme formation scenario.
- A conditional scenario in which repeated tests may make a future level visually obvious to market participants.

These are **formation scenarios**, not current EQH/EQL, swing levels, or known stop clusters. The structure only becomes an observed Historical Liquidity candidate after actual subsequent price observations meet the detection rules. Any internal resampling used by detection is not rendered as candles.

A scenario must state its condition. Example: “If price enters this region and forms two or more qualifying highs within the configured tolerance, a future EQH candidate may be created.” It must not state that an EQH or a stop cluster already exists.

Do not infer the location or quantity of actual resting stops from observed price structure alone. BSL/SSL may be used only as a hypothesis about the likely side of potential stop placement, not as an observed order-pool classification or trade instruction.

### 2.3 Volatility projection

Purpose: estimate the distribution of plausible movement ranges for a named horizon.

Possible outputs:
- Conditional expected-range quantiles.
- Volatility expansion/compression scenarios.
- Session high/low distribution.
- Tail-move probability bands.
- Regime-conditioned range estimates.

Volatility envelopes are **context overlays**, not liquidity pools. Do not convert an ATR band or expected-range boundary into a liquidity orb or stop cluster. Do not assume symmetric or normally distributed future returns without evidence.

### 2.4 Conditional price density and occupancy

Purpose: describe where simulated or historical conditional paths spend time or how their future prices are distributed.

Use precise names such as:
- PRICE_DENSITY
- PRICE_OCCUPANCY
- CONDITIONAL_PRICE_DISTRIBUTION
- FIRST_PASSAGE_DISTRIBUTION

A density peak means paths or observations concentrate there under the model. It does **not** prove that price is attracted to that level, that the market will target it, or that liquidity rests there.

“Price attraction” may be a UI grouping name only. The underlying model and tooltip must state the actual statistic being displayed.

Historical volume profile and broker-provided volume must retain source semantics. Unless the feed is proven to contain centralized traded volume, label XAUUSD CFD volume as tick-volume or feed-specific volume. Never treat it as current resting liquidity.

### 2.5 Options gamma exposure (GEX) — optional external context

GEX is not a required foundation of Future Liquidity. Enable a genuine options-derived adapter only when the underlying data, calculation, assumptions, and instrument mapping are documented.

Required input metadata:
- Source/provider and retrieval timestamp.
- Underlying and contract identity.
- Option type, strike, expiry, open interest, implied volatility, and option gamma.
- Contract multiplier, units, currency, and price basis.
- Calculation formula, sign convention, and aggregation method.
- Assumption used for long/short positioning or dealer positioning.
- Data coverage, missing contracts, stale-data threshold, and expiry handling.
- Mapping from the options underlying to the displayed XAUUSD feed, including futures/spot basis and timestamp alignment where applicable.

Important limitations:
- Open interest alone does not identify which side is held by dealers or customers. It cannot reveal actual dealer positioning by itself.
- A dealer-gamma estimate therefore depends on a stated positioning/sign assumption. Label it as an estimate under that assumption, not observed dealer inventory.
- COMEX gold futures/options, ETF options, and XAUUSD CFD are different instruments. Do not copy a strike or gamma level directly onto XAUUSD without a documented basis/mapping process and residual uncertainty.
- “Call Wall”, “Put Wall”, “Gamma Flip”, and “Zero Gamma” are not self-validating facts. Publish a label only when its exact computation and source convention are stated.
- Do not infer that a Call Wall is guaranteed resistance, a Put Wall guaranteed support, or a gamma sign a deterministic direction.

If authentic options data or mapping is unavailable:
- Disable the genuine GEX layer; or
- Show a separate **EXPERIMENTAL GAMMA-LIKE PROXY** whose inputs and limitations are explicit.

A proxy must never be represented as actual GEX, dealer gamma, dealer positioning, or independent options evidence. Price-only heuristics cannot qualify as an independent options signal.

## 3. Output taxonomy — keep meanings separate

Every output must have one primary semantic type. Do not turn every model output into a liquidity orb.

| Type | Meaning | Display class |
|---|---|---|
| PROJECTED_BSL_FORMATION_SCENARIO | Conditional scenario for a future structure above price that may later qualify as buy-side liquidity | Scenario marker |
| PROJECTED_SSL_FORMATION_SCENARIO | Conditional scenario for a future structure below price that may later qualify as sell-side liquidity | Scenario marker |
| MONTE_CARLO_TOUCH_ZONE | Price interval evaluated for touch probability over a defined horizon | Probability zone |
| PRICE_DENSITY_ZONE | Conditional distribution/occupancy concentration | Density overlay |
| EXPECTED_RANGE_ENVELOPE | Volatility-derived range distribution | Context overlay |
| GEX_CONTEXT_LEVEL | Options-derived gamma exposure level under declared assumptions | External-context marker |
| GAMMA_PROXY_CONTEXT_LEVEL | Experimental price-derived proxy; never genuine GEX | Experimental context marker |

A projected structural scenario may receive a Future Liquidity orb treatment only if it is clearly marked FUTURE/SCENARIO and has its own forecast identity. Density, volatility, and GEX overlays should normally use distinct renderer primitives rather than masquerading as liquidity pools.

## 4. Price data contract and data-quality gates

No model may calculate or display a probability until its source data contract is explicit.

Each input series must identify:
- Symbol and exact instrument/feed identity.
- Broker/provider and dataset version.
- Tick/quote event semantics and any internal time-resampling method.
- Timestamp convention and timezone; store UTC internally.
- Price basis: BID, ASK, MID, LAST, or another explicitly named basis.
- Tick size, price precision, and any contract/unit conversion.
- Whether volume is tick volume, feed volume, or documented traded volume.
- Tick/quote completeness, missing intervals, duplicate timestamps, out-of-order events, and malformed updates.
- Spread availability and whether the requested event concerns price-touch or executable trading.

Rules:
1. Train, simulate, and evaluate using a consistent price basis. Do not silently mix bid, ask, midpoint, spot, futures, and CFD prices.
2. A price-touch probability is not an execution probability. Include spread, slippage, latency, and fill assumptions only for a separately named execution event.
3. Reject or flag incomplete/stale input windows. Never quietly backfill future data or use source ticks/quotes or derived features that were not available at forecast issuance time.
4. Normalize instrument mapping and session boundaries explicitly. Store timestamps in UTC; convert to Asia/Jakarta only for display.
5. If feed metadata or price basis is unknown, mark the forecast DATA_UNVERIFIED and prevent validated tier assignment.

The implementation phase must inspect the actual repository data pipeline before choosing field names or assuming Dukascopy column semantics.

## 5. Event definitions and probability contract

Every probability must identify:
- Exact event definition and version.
- Price basis and instrument/feed.
- Target zone or boundary.
- Forecast issuance timestamp.
- Forecast horizon.
- Model and calibration versions.
- Data cutoff timestamp.
- Raw estimate, calibrated estimate, and uncertainty metadata.

### 5.1 Price touch

For a zone `[L, U]`, TOUCH occurs when a valid observed/simulated price path enters the interval at least once within horizon `H`.

`P_TOUCH(zone, H)` is the probability of that event.

A valid Dukascopy price observation inside the zone can establish a touch on the declared quote/price basis. If only internally aggregated OHLC data is available, a range overlap can establish that the range intersected the zone, but it may not resolve event order. If a price gap jumps from one side of the entire zone to the other without a recorded price inside it, classify it as GAP_CROSS, not a confirmed touch, unless finer source data proves otherwise.

### 5.2 Boundary breach

`P_BREACH(boundary, tolerance, H)` estimates the probability that price trades beyond a specified boundary by at least the configured tolerance during `H`.

Breach is a price event only. It does not imply a liquidity sweep, reversal, or continuation.

### 5.3 Sweep and reclaim

Use a separately defined event such as `SWEEP_RECLAIM`:

- Define the reference boundary.
- Define the breach tolerance.
- Define which side of the boundary is the sweep side.
- Define the reclaim condition and reclaim deadline.
- Define the price basis and whether a close, quote, or individual trade resolves the reclaim.
- Store breach and reclaim timestamps separately where observable.

A move through a boundary without the required reclaim is a breach, not a completed sweep-reclaim event. Do not use “sweep” as a synonym for every penetration.

### 5.4 Reaction and continuation

Reaction and continuation must be separate, pre-registered events.

For reaction, define direction, minimum movement threshold (for example, a volatility-normalized distance), measurement start, and maximum time after first touch. For continuation, define the required move beyond the zone, time window, and any persistence/close condition.

Report conditional and joint probabilities separately where relevant:

- `P_REACTION_GIVEN_TOUCH`: reaction probability among paths that touched the zone.
- `P_TOUCH_AND_REACTION`: probability that a path both touches and subsequently meets the reaction definition.
- `P_CONTINUATION_GIVEN_TOUCH`: continuation probability among paths that touched the zone.

Do not infer any reaction or continuation probability from P_TOUCH or P_BREACH.

### 5.5 Intrabar ambiguity

Internally aggregated OHLC bars do not encode the complete intrabar path. If the order of two relevant barriers/events cannot be established:
- Resolve using lower-timeframe or tick data when available and aligned to the same price basis.
- Otherwise label the outcome AMBIGUOUS, or apply a pre-registered conservative evaluation rule.
- Never invent an intrabar sequence or choose the path that improves model performance.
- Report how many outcomes were ambiguous and how they were handled.

For a simple touch event, an observed source price inside the zone establishes a touch on that price basis. If only internal OHLC aggregation is available, a valid range intersection can show that the range reached the zone. For ordering-dependent events, OHLC alone may be insufficient.

### 5.6 Raw and calibrated probabilities

A Monte Carlo path fraction is a **raw model estimate**, not automatically a calibrated real-world probability.

Store separately:
- `probability_raw`
- `probability_calibrated` (nullable until a valid calibration model exists)
- `calibration_method` and `calibration_version`
- `uncertainty_interval`
- `simulation_path_count`
- `effective_evaluation_sample_size` where available

Do not confuse Monte Carlo sampling error with model uncertainty. More simulated paths can reduce numerical sampling noise; they cannot compensate for poor data, misspecified dynamics, regime shifts, or too few independent historical forecast outcomes.

## 6. Monte Carlo method requirements

### 6.1 Avoid the naive random walk

Do not use independent, identically distributed single-bar returns as the default assumption for XAUUSD M1/M5. Such a model can erase volatility clustering, short-run dependence, session effects, and regime transitions.

A block-bootstrap/hybrid model is the preferred research baseline:
1. Build a clean chronological return series from the declared price basis.
2. Define candidate regime features using only information available at forecast time.
3. Select historical blocks using a documented method and eligibility rules.
4. Resample blocks without leaking future observations across the forecast cutoff.
5. Apply any volatility normalization/scaling based only on past data and validated transformations.
6. Construct paths and evaluate the pre-defined events.
7. Compare the model with simpler baselines before adding complexity.

Block length, regime definitions, scaling, simulation count, and session conditioning are hyperparameters. Select them in training/validation windows, not by repeatedly inspecting the final test period.

### 6.2 Model uncertainty and stability

Evaluate sensitivity to:
- Block length and sampling method.
- Regime classifier and regime transitions.
- Volatility normalization.
- Forecast horizon.
- Source feed and price basis.
- Sample window and unusual event periods.

Use ensembles or bootstrap confidence intervals where appropriate, but document the resampling unit. Overlapping or dependent paths are not independent historical observations.

### 6.3 Price distribution is not a route

A quantile fan represents a distribution of outcomes. Do not connect median or modal values into a single “predicted route” without clearly labeling it as a summary statistic. The mean/median path may not itself be a likely realized path.

## 7. Forecast horizon

Separate chart timeframe from forecast horizon. A M1 chart can display a 15-minute forecast; an H1 chart can display a 24-hour forecast. They are not interchangeable.

Candidate horizon grids may be tested for M1, M5, M15, H1, and H4, but no default horizon should be treated as accurate by assumption. Validate each combination of:
- Symbol/feed and price basis.
- Chart timeframe/input resolution.
- Forecast horizon.
- Event definition.
- Relevant regime.

Do not display a long-horizon distribution as a precise short-term target. Every projected zone must show its horizon and creation time.

## 8. Two-layer reliability and tier system

### 8.1 Layer A — Model Reliability

Model Reliability measures the historical performance of a model family for a specific scope, not the quality of one particular zone.

Scope it by at least:
- Symbol and feed.
- Price basis.
- Input timeframe.
- Forecast horizon.
- Event definition.
- Regime, when sample size permits.
- Model and calibration version.

Track:
- Out-of-sample skill versus relevant baselines.
- Probability calibration.
- Stability across walk-forward windows.
- Discrimination and event ranking, separately from calibration.
- Data freshness and completeness.
- Sample count, effective sample size, and uncertainty intervals.
- Performance drift and failure conditions.

Suggested validation states:
- UNVALIDATED — no completed out-of-sample evidence.
- INSUFFICIENT — evidence exists but does not meet the pre-registered sample/quality gates.
- VALIDATED — required test gates have been met.
- DEGRADED — previously validated performance has materially deteriorated.
- STALE — required current input or external data is too old.

A model validated for M15 touch prediction is not automatically validated for M1 sweep-reclaim prediction.

### 8.2 Layer B — Individual Projection Quality

Projection Quality measures the evidence and uncertainty of one forecast object, conditional on the reliability state of its generating model.

Candidate components:
- Structural evidence actually observed at issuance time.
- Zone width and distance, normalized to relevant volatility/tick scale.
- Forecast horizon and uncertainty.
- Regime suitability.
- Data freshness/completeness.
- Incremental out-of-sample value from genuinely distinct evidence families.
- Agreement/dependence among inputs.

Do not reward the number of indicators or models by itself. Several features built from the same underlying price stream or internal OHLC aggregations are correlated evidence. Multiple Monte Carlo runs using the same price history are one model family, not independent votes.

### 8.3 Tier policy

Use the familiar seven visible labels, but do not reuse Historical Liquidity's timeframe-to-tier mapping.

| Tier | Name | Meaning |
|---|---|---|
| SSS | Sovereign Projection | Exceptional individual projection quality, supported by robust out-of-sample reliability and strong, incremental evidence |
| SS | Supreme Projection | Very high validated projection quality |
| S | Elite Projection | High validated projection quality with consistent evidence |
| A | Major Projection | Strong validated projection quality |
| B | Strong Projection | Useful validated evidence with material limitations |
| C | Standard Projection | Validated but moderate/limited projection quality |
| D | Minor Projection | Validated lowest-quality/weak candidate; contextual only |

**PROVISIONAL is not a tier.** An unvalidated forecast must have `tier = null` and a visible validation label such as PROVISIONAL/UNVALIDATED. Do not assign D merely because a model has not yet been tested. D is reserved for a forecast that has passed the validation eligibility gates but has the weakest relative projection quality.

### 8.4 No arbitrary weights or tier cutoffs

Do not hard-code the earlier illustrative 30/25/20/15/10 weighting as if it were scientifically established. Do not invent universal accuracy percentages or sample-size thresholds.

The scoring policy must be developed as follows:
1. Define the target outcomes and validation scope.
2. Pre-register candidate features, score normalization, and tier eligibility gates.
3. Fit/tune only on training data.
4. Select candidate cutoffs using validation data and stability analysis.
5. Lock the policy before the untouched final test.
6. Publish the resulting tier distributions, uncertainty, and limitations.
7. Recalibrate only under a versioned process; never rewrite historical tier decisions silently.

A high tier requires adequate evidence, positive skill versus an appropriate baseline, acceptable calibration, stable walk-forward results, and no critical data-quality/staleness failure. Higher tiers may require incremental support from distinct information families, but that requirement must be explicit and dependency-aware.

If gates fail, tier remains unassigned/PROVISIONAL or the model is DEGRADED/STALE. Never manufacture a tier from raw probability alone.

## 9. Forecast lifecycle and outcome ledger

Do not overload one status field with both forecast lifecycle and observed market events.

### 9.1 Forecast monitoring status

Use a small lifecycle state machine:
- CREATED — forecast snapshot has been written.
- ACTIVE — its horizon remains open and input policy still permits monitoring.
- SUPERSEDED — a newer forecast version replaces it for display; retain it for evaluation.
- EXPIRED — the forecast horizon ended.
- INVALIDATED — a pre-defined model/input/structural invalidation condition occurred.
- EVALUATED — the forecast's required outcome window has been resolved and evaluation recorded.

APPROACHING is a derived display state based on current price and configured distance; it should not rewrite the forecast's lifecycle history.

TOUCHED, BREACHED, SWEPT_RECLAIMED, REACTED, and CONTINUED are **event observations**, not mutually exclusive lifecycle states. A single forecast can experience several events.

### 9.2 Independent outcome records

For each event definition, store:
- Event name and definition version.
- Outcome: YES, NO_BY_HORIZON, AMBIGUOUS, DATA_GAP, or CENSORED.
- First event timestamp and relevant price, if observed.
- Measurement window and price basis.
- Resolution source (Dukascopy quote/tick, finer source interval, internal OHLC proxy, etc.).
- Evaluation timestamp and evaluator version.

An invalidated or superseded forecast must not silently disappear from evaluation. Define in advance whether its event outcome is still measurable, censored, or invalidated for a documented reason. Report all categories and never exclude difficult forecasts after seeing their outcomes.

### 9.3 Immutable forecast versioning

- Every issuance is immutable and receives a unique forecast ID/revision.
- A changed model output creates a new forecast record, linked with `supersedes_forecast_id`; it does not overwrite the previous forecast.
- Store input cutoff, source hashes/version, parameters, model version, calibration version, and generation timestamp.
- Keep a complete audit trail of forecasts, failures, invalidations, expiry, and outcomes.
- Use UTC timestamps internally.

## 10. Validation and backtesting protocol

Future Liquidity is not ready for a predictive-quality claim until this protocol is implemented.

### 10.1 Chronological evaluation

- Use chronological walk-forward splits.
- Perform feature selection, hyperparameter tuning, calibration, and tier-policy tuning only inside the training/validation process.
- Keep a final untouched test period.
- Purge/embargo where labels or forecast horizons overlap training/test boundaries.
- Never use random shuffling of time-series observations across train/test.
- Ensure every forecast uses only information available at its issuance timestamp.

### 10.2 Baselines

Compare each model against appropriate simple baselines evaluated on the same event, price basis, zone width, distance, timeframe, and horizon.

Candidate baselines:
- Unconditional empirical event frequency.
- Distance- and horizon-conditioned empirical frequency.
- Simple volatility/ATR range model.
- Simple regime-conditioned return/event model.

A complex model must demonstrate incremental out-of-sample value, not merely beat an irrelevant baseline.

### 10.3 Metrics

For binary event probabilities:
- Brier Score and Brier Skill Score versus a stated baseline.
- Log loss where appropriate.
- Reliability diagrams and calibration curves.
- Calibration intercept/slope or another documented calibration diagnostic.
- Discrimination/ranking metrics, reported separately from calibration.
- Precision/recall only with the event definition, prevalence, and threshold stated.

For zones and paths:
- Width-normalized evaluation so a very wide zone cannot win trivially.
- First-touch time and horizon-specific performance.
- Quantile coverage and interval sharpness for range/path distributions.
- Error and uncertainty by regime and session.
- Sampling uncertainty versus model uncertainty.

Do not treat Brier Score alone as a pure calibration measure or use hit rate alone to claim predictive quality.

### 10.4 Overlapping forecasts and dependence

M1/M5 forecasts issued repeatedly may have heavily overlapping outcome windows. They must all be retained, but they are not independent samples.

- Report raw forecast count and effective/independent sample estimates separately.
- Use time-blocked or clustered uncertainty estimates appropriate to the issuance cadence and overlapping labels.
- Report results by forecast cohort, horizon, regime, and session.
- Avoid inflating confidence by counting hundreds of nearly identical adjacent forecasts as hundreds of independent successes.

### 10.5 Selection and multiple-testing bias

- Log every forecast generated under the evaluation protocol, not only attractive/high-tier ones.
- Predefine model variants, event definitions, and tier-policy experiments.
- Record how many variants and hypotheses were tested.
- Do not select the best-looking result after testing many configurations and then report it as an unbiased final result.
- Preserve the final test set from repeated tuning.
- Report sample sizes, confidence intervals, missing/ambiguous outcomes, failed forecasts, and model degradation.

### 10.6 Calibration and drift

Calibration must be fitted on past out-of-sample predictions and outcomes, then applied prospectively. Do not calibrate on the same final observations used to claim performance.

Monitor:
- Reliability drift.
- Regime distribution changes.
- Feed/source changes.
- Calibration sample freshness.
- Model performance degradation.

When calibration is stale or data regime has materially changed, mark forecasts DEGRADED or STALE and block high-tier display until the policy permits revalidation.

## 11. Suggested forecast data contract

Illustrative schema only; adapt it to the repository's real data model after inspecting the actual source pipeline.

~~~python
{
    "forecast_id": "immutable_unique_id",
    "revision": 1,
    "supersedes_forecast_id": None,

    "symbol": "XAUUSD",
    "instrument_feed": "explicit_provider_and_contract",
    "price_basis": "MID",
    "input_timeframe": "M5",
    "forecast_horizon_seconds": 3600,
    "issued_at_utc": "timestamp",
    "data_cutoff_utc": "timestamp",
    "expires_at_utc": "timestamp",

    "object_type": "MONTE_CARLO_TOUCH_ZONE",
    "evidence_label": "MODEL_ESTIMATE",
    "side_hypothesis": None,
    "price_low": 4050.0,
    "price_high": 4055.0,

    "event_definitions": {
        "touch": "definition_id_and_version",
        "breach": "definition_id_and_version",
        "sweep_reclaim": None,
        "reaction": None,
        "continuation": None
    },

    "probabilities": {
        "touch_raw": 0.78,
        "touch_calibrated": None,
        "breach_raw": None,
        "breach_calibrated": None,
        "sweep_reclaim_raw": None,
        "sweep_reclaim_calibrated": None,
        "reaction_given_touch": None,
        "continuation_given_touch": None
    },

    "uncertainty": {
        "interval": None,
        "interval_method": None,
        "simulation_path_count": None,
        "model_uncertainty_status": "NOT_QUANTIFIED"
    },

    "model": {
        "family": "MONTE_CARLO_BLOCK_BOOTSTRAP",
        "model_version": "version",
        "parameters_hash": "hash_or_reference",
        "random_seed": None,
        "regime_at_issue": "UNKNOWN"
    },

    "validation": {
        "state": "UNVALIDATED",
        "scope_id": None,
        "calibration_version": None,
        "sample_count": None,
        "effective_sample_size": None
    },

    "projection_quality": {
        "score": None,
        "score_version": None,
        "tier": None,
        "tier_policy_version": None
    },

    "status": "CREATED",
    "outcomes": [],
    "invalidation_reason": None,
    "evaluation_version": None
}
~~~

All numbers and prices above are illustrative only; they are not XAUUSD predictions. Store the full event-definition version and source metadata. Do not use a nullable placeholder as a fabricated probability or score.

## 12. Renderer and visual semantics

**Primary camera model:** use the centered live-price game world defined in [CENTERED_PRICE_GAME_WORLD_SPEC.md](CENTERED_PRICE_GAME_WORLD_SPEC.md). The latest Dukascopy live-price point is anchored at the center of the main playfield; historical data occupies the left/past side and future scenarios the right/future side. Price offsets are drawn vertically relative to the live price. No candles are rendered and no conventional right-edge latest-price layout is used. Camera transforms must never modify forecast prices, timestamps, probabilities, or IDs.

Future and Historical layers must be unmistakably different at normal chart zoom.

Historical:
- Preserve the existing Historical Liquidity orb, tier identity, trail semantics, and lifecycle presentation.

Future:
- Use a different silhouette/material: translucent, holographic, dashed/segmented boundary, or another clearly projected treatment.
- Show a persistent FUTURE / SCENARIO / EXPERIMENTAL marker as applicable.
- A projected path is an ensemble/fan/density, not a guaranteed trail.
- Distinguish structural formation scenarios from probability zones, density, volatility envelope, and GEX context.
- Show horizon, issue time, event definition, raw/calibrated probability, validation state, and source/model family on selection or hover.
- Display stale/invalidated/expired forecasts distinctly.
- Keep model-family toggles and a master Future layer toggle.
- Preserve every forecast ID. Visual LOD may hide or simplify objects but may not merge or delete their records.

Do not reuse the Historical movement trail as a future predicted path. Historical trails represent recorded movement; forecast distributions require a separate renderer and legend.

Tier SSS/SS/S/A/B/C/D may share the familiar hierarchy, but Future styling must not let color/size imply observed order-book intensity. Tier communicates validated projection quality only—not order size, expected profit, or certainty.

## 13. Compute, cache, and performance boundaries

- Run simulation and validation workloads outside the UI render loop.
- Separate forecast generation cadence from display refresh cadence.
- Cache results using a key that includes data cutoff, model version, parameters, regime, horizon, and event-definition version.
- Invalidate cache only when a relevant input changes.
- Keep a timestamp and stale indicator on the last valid forecast if refresh fails; never display it as current.
- Use configurable simulation budgets and benchmark actual latency before setting defaults.
- Do not silently reduce simulation/evaluation quality for frame rate.
- Rendering caps only affect visible presentation; never delete forecast history.
- Log data failures, model failures, fallback behavior, computation time, and cache hits.

## 14. Implementation phases

### Phase 0 — repository and data audit

- Inspect the real repository tree, runtime, dependencies, Dukascopy event payload, price basis, and any internal aggregation schema.
- Confirm instrument/feed identity, timezone, price basis, precision, completeness, and volume semantics.
- Define event specifications, forecast IDs, immutable logs, and outcome records.
- Build a chronological evaluator and simple baselines before a sophisticated model.
- Do not assume the repository already has a working Historical engine or Dukascopy live-feed adapter until verified in source.

### Phase 1 — event and evaluation foundation

- Implement touch, breach, sweep-reclaim, reaction, and continuation event evaluators.
- Add intrabar ambiguity and data-gap handling.
- Create forecast snapshot storage and immutable outcome ledger.
- Add walk-forward splits, leakage checks, baseline comparison, metrics, and reports.
- Test the evaluator with synthetic tick/quote streams, gaps, duplicates, out-of-order events, and internal-bar edge cases.

### Phase 2 — first price-path baseline

- Implement a regime-aware block-bootstrap model.
- Produce raw touch/breach probabilities, quantile ranges, and density/occupancy outputs.
- Add reproducibility, Monte Carlo convergence checks, and uncertainty reporting.
- Do not enable validated tiers until real walk-forward evidence exists.

### Phase 3 — structural and volatility scenarios

- Add conditional structural-formation scenarios and volatility context overlays.
- Keep context overlays semantically separate from liquidity candidates.
- Test whether each addition improves outcomes beyond the existing baseline.

### Phase 4 — calibration, reliability, quality, and tiers

- Add prospective probability calibration.
- Build Model Reliability and Individual Projection Quality as separate layers.
- Establish tier gates and cutoffs through a versioned training/validation policy.
- Keep unvalidated forecasts at tier N/A / PROVISIONAL.

### Phase 5 — optional external data and visual layer

- Add genuine options-derived gamma context only after source and instrument mapping validation.
- Keep Gamma-like Proxy visibly experimental and separate.
- Add a Future-only renderer, legend, controls, stale state, and probability fan.
- Preserve Historical Liquidity behavior and visual design.

### Phase 6 — robustness and release

- Run final untouched out-of-sample tests and regime stress tests.
- Inspect ambiguity, leakage, overlapping forecast dependence, and failure cases.
- Benchmark compute latency and UI rendering separately.
- Verify immutable logs, reproducibility, invalidation, expiry, and evaluation.
- Publish measured results and limitations; do not claim accuracy without evidence.

## 15. Explicit non-goals

This specification does not authorize:
- Replacing or changing Historical Liquidity detection or tiers.
- Claiming visibility into actual institutional stops or resting orders without direct source data.
- Treating CFD tick volume as centralized traded volume.
- Treating Monte Carlo path density as a price target or a liquidity pool.
- Treating a model's raw path frequency as calibrated real-world probability.
- Treating price breach as proof of sweep-reclaim or reversal.
- Treating open interest alone as proof of dealer positioning.
- Converting projected zones into buy-limit/sell-limit recommendations, trading signals, or automatic execution.
- Building an EA or automatic trading system.

## 16. Acceptance checklist

- [ ] Historical and Future engines have separate data, IDs, lifecycle, tiers, and renderers.
- [ ] Every Future output has one explicit semantic type and evidence label.
- [ ] Price-path probability, structural-formation scenario, volatility context, density, and GEX remain distinct.
- [ ] Every forecast records source/feed, price basis, data cutoff, issue time, horizon, and model version.
- [ ] Touch, breach, sweep-reclaim, reaction, and continuation have versioned event definitions.
- [ ] Intrabar ambiguity and gaps are handled without inventing a path.
- [ ] Raw and calibrated probabilities are stored separately.
- [ ] Monte Carlo path count is not confused with independent historical sample size.
- [ ] Model Reliability and Individual Projection Quality are separate.
- [ ] PROVISIONAL is a validation state, not tier D.
- [ ] Tier weights and cutoffs are empirically selected, versioned, and tested; no arbitrary thresholds are presented as facts.
- [ ] Model/evidence dependence is considered before confluence aggregation.
- [ ] GEX uses authentic documented options data and explicit positioning assumptions; otherwise it is disabled or labeled experimental proxy.
- [ ] Forecast versions are immutable and all outcomes, failures, expiry, and invalidation are retained.
- [ ] Walk-forward evaluation includes baselines, calibration, overlapping-window dependence, uncertainty, and untouched test data.
- [ ] Future visuals cannot be mistaken for observed liquidity, actual order-book depth, or historical trails.
- [ ] No auto-entry or trade execution is introduced.

## 17. Version 2.0 corrections

Version 2.0 corrects the earlier concept by:
- Separating forecast price distributions from conditional structural-formation scenarios and non-liquidity context overlays.
- Defining touch, breach, sweep-reclaim, reaction, continuation, gaps, and intrabar ambiguity as separate events.
- Separating raw Monte Carlo estimates from calibrated probabilities and simulation error from model uncertainty.
- Separating Model Reliability from the quality of an individual projection.
- Making PROVISIONAL a validation state rather than a tier; D is reserved for validated weak projections.
- Removing unsupported fixed score weights and arbitrary tier thresholds.
- Replacing overloaded lifecycle states with a forecast state machine plus an independent event-outcome ledger.
- Tightening GEX assumptions, dealer-positioning limitations, and futures/ETF-to-XAUUSD mapping requirements.
- Adding controls for overlapping forecasts, effective sample size, selection bias, immutability, and calibration drift.


## 18. UI rendering clarification — no candles

Future Liquidity is rendered inside the centered live-price game world, not on a candlestick chart. The player/anchor is the current Dukascopy price marker. No candle bodies, wicks, OHLC bars, or synthetic per-tick candles are displayed.

The forecast engine may still consume raw Dukascopy price updates or optional internal time aggregation. Such aggregation is a model input only and does not authorize a candlestick UI. See [Dukascopy Live Price Feed specification](DUKASCOPY_LIVE_PRICE_FEED_SPEC.md).
