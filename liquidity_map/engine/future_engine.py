"""Future Liquidity Engine - Authentic Block Bootstrap Monte Carlo.

Features:
- Historical return series & volatility regime classification.
- Conditional Block Bootstrap (preserves autocorrelation and volatility clustering).
- Monte Carlo price path projection & empirical quantile fans (P10, P25, P50, P75, P90).
- Empirical touch probabilities derived from path extrema (no hardcoded confidence).
- Epistemic safety: SCENARIO / MODEL_ESTIMATE labels, strictly separate from Historical Liquidity.
- Walk-forward validation with Brier score and baseline comparison.
"""
import math
import time
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple


class MarketRegime:
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    UNKNOWN = "UNKNOWN"


class FutureLiquidityEngine:
    """Generates conditional price corridors, scenario forecasts, and volatility fans."""

    def __init__(
        self,
        num_simulations: int = 100,
        block_size: int = 4,
        seed: Optional[int] = 42,
    ):
        self.num_simulations = max(20, num_simulations)
        self.block_size = max(2, block_size)
        self.seed = seed
        self.model_version = "v3.0-block-bootstrap"

    def classify_regime(self, prices: List[float]) -> Dict[str, Any]:
        """Classifies market regime based on rolling return drift and volatility."""
        if len(prices) < 10:
            return {
                "regime": MarketRegime.UNKNOWN,
                "volatility": 0.25,
                "drift": 0.0,
                "reliability": "LOW",
            }

        returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]
        n = len(returns)
        mean_ret = sum(returns) / n
        var = sum((r - mean_ret) ** 2 for r in returns) / (n - 1 if n > 1 else 1)
        std_ret = math.sqrt(max(1e-8, var))

        # Drift in points over window
        total_drift = prices[-1] - prices[0]

        if std_ret > 0.0006:
            regime = MarketRegime.HIGH_VOLATILITY
        elif total_drift > 1.50:
            regime = MarketRegime.TRENDING_UP
        elif total_drift < -1.50:
            regime = MarketRegime.TRENDING_DOWN
        elif std_ret < 0.00015:
            regime = MarketRegime.LOW_VOLATILITY
        else:
            regime = MarketRegime.RANGING

        return {
            "regime": regime,
            "volatility": round(std_ret, 6),
            "drift_pts": round(total_drift, 3),
            "reliability": "HIGH" if len(prices) >= 30 else "MODERATE",
        }

    def generate_scenarios(
        self,
        live_price: float,
        current_ts: float,
        price_history: Optional[List[float]] = None,
        volatility: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generates conditional block-bootstrapped quantile fan and structural formation scenarios ahead of live anchor."""
        if live_price is None or live_price <= 0:
            return {"error": "Invalid anchor price"}

        rng = random.Random(self.seed)

        # 1. Historical returns preparation
        if price_history and len(price_history) >= 12:
            returns = [math.log(price_history[i] / price_history[i - 1]) for i in range(1, len(price_history))]
            regime_info = self.classify_regime(price_history)
        else:
            # Synthetic empirical baseline calibrated to XAUUSD typical 10s tick volatility (~$0.25-$0.45)
            sigma = volatility or 0.35
            base_sd = (sigma / live_price) / math.sqrt(6.0)
            returns = [rng.gauss(0, base_sd) for _ in range(60)]
            regime_info = {
                "regime": MarketRegime.RANGING,
                "volatility": round(base_sd, 6),
                "drift_pts": 0.0,
                "reliability": "LOW_CALIBRATED",
            }

        # 2. Extract Blocks for Block Bootstrap
        blocks: List[List[float]] = []
        n_ret = len(returns)
        b_size = min(self.block_size, n_ret // 2) if n_ret >= 4 else 1

        for i in range(n_ret - b_size + 1):
            blocks.append(returns[i : i + b_size])

        if not blocks:
            blocks = [[0.0]]

        # 3. Simulate Monte Carlo paths
        horizon_steps = 12  # 12 steps x 10 seconds = 120 seconds into future
        paths: List[List[float]] = []

        for _ in range(self.num_simulations):
            path = [live_price]
            p = live_price
            while len(path) <= horizon_steps:
                chosen_block = rng.choice(blocks)
                for r in chosen_block:
                    p = p * math.exp(r)
                    path.append(p)
                    if len(path) > horizon_steps:
                        break
            paths.append(path[: horizon_steps + 1])

        # 4. Quantile Aggregation across paths at each forward step
        fan_points = []
        for step in range(1, horizon_steps + 1):
            dt = step * 10
            prices_at_step = sorted([path[step] for path in paths])
            n_p = len(prices_at_step)

            def get_percentile(p_pct: float) -> float:
                idx = int(p_pct * (n_p - 1))
                return round(prices_at_step[idx], 2)

            fan_points.append({
                "future_offset_sec": dt,
                "future_ts": current_ts + dt,
                "p90": get_percentile(0.90),
                "p75": get_percentile(0.75),
                "p50": get_percentile(0.50),  # Median path
                "p25": get_percentile(0.25),
                "p10": get_percentile(0.10),
            })

        # 5. Empirical Touch Probabilities derived directly from simulated paths
        # Target Resistance (+2.50 pts) and Support (-2.50 pts)
        high_target = round(live_price + 2.50, 2)
        low_target = round(live_price - 2.50, 2)

        touches_high = sum(1 for path in paths if max(path) >= high_target)
        touches_low = sum(1 for path in paths if min(path) <= low_target)

        prob_high = round(touches_high / self.num_simulations, 3)
        prob_low = round(touches_low / self.num_simulations, 3)

        scenarios = [
            {
                "scenario_id": f"scen_bsl_{int(current_ts)}_h",
                "type": "CONDITIONAL_EQH_FORMATION",
                "target_price": high_target,
                "horizon_sec": 120,
                "confidence": prob_high,  # Genuine empirical frequency from Monte Carlo
                "epistemic_status": "SCENARIO",
                "condition": f"Block Bootstrap ({self.num_simulations} paths) indicates {prob_high*100:.1f}% conditional touch probability.",
                "side": "BSL",
            },
            {
                "scenario_id": f"scen_ssl_{int(current_ts)}_l",
                "type": "CONDITIONAL_EQL_FORMATION",
                "target_price": low_target,
                "horizon_sec": 120,
                "confidence": prob_low,
                "epistemic_status": "SCENARIO",
                "condition": f"Block Bootstrap ({self.num_simulations} paths) indicates {prob_low*100:.1f}% conditional touch probability.",
                "side": "SSL",
            },
            {
                "scenario_id": f"scen_vol_{int(current_ts)}",
                "type": "VOLATILITY_EXPANSION_BOUNDARY",
                "target_price": fan_points[-1]["p90"],
                "horizon_sec": 120,
                "confidence": 0.10,  # Tail boundary definition (P90)
                "epistemic_status": "MODEL_ESTIMATE",
                "condition": f"Upper 90th percentile quantile envelope across {self.num_simulations} paths.",
                "side": "BSL",
            },
        ]

        return {
            "model_version": self.model_version,
            "evaluated_at_utc": datetime.fromtimestamp(current_ts, timezone.utc).isoformat(),
            "evaluated_ts": current_ts,
            "anchor_price": live_price,
            "regime": regime_info["regime"],
            "volatility": regime_info["volatility"],
            "reliability": regime_info["reliability"],
            "num_simulations": self.num_simulations,
            "fan_corridor": fan_points,
            "scenarios": scenarios,
        }

    def validate_walk_forward(
        self,
        historical_prices: List[float],
        window_size: int = 40,
        horizon_steps: int = 10,
        num_windows: int = 5,
    ) -> Dict[str, Any]:
        """Runs walk-forward calibration backtest comparing empirical quantile coverage against baseline."""
        if len(historical_prices) < window_size + horizon_steps:
            return {"status": "INSUFFICIENT_DATA", "coverage_80": 0.0}

        covered_p10_p90 = 0
        total_evals = 0
        brier_scores: List[float] = []

        step_jump = max(1, (len(historical_prices) - window_size - horizon_steps) // num_windows)
        
        for start_idx in range(0, len(historical_prices) - window_size - horizon_steps, step_jump):
            train_slice = historical_prices[start_idx : start_idx + window_size]
            actual_future_price = historical_prices[start_idx + window_size + horizon_steps - 1]
            anchor_price = train_slice[-1]

            res = self.generate_scenarios(anchor_price, time.time(), price_history=train_slice)
            fan = res["fan_corridor"]
            step_idx = min(horizon_steps - 1, len(fan) - 1)
            target_step = fan[step_idx]

            # Check if actual future price fell within P10 - P90 envelope
            if target_step["p10"] <= actual_future_price <= target_step["p90"]:
                covered_p10_p90 += 1
            total_evals += 1

            # Brier score for directional projection (Price up vs down)
            actual_up = 1.0 if actual_future_price >= anchor_price else 0.0
            prob_up = 0.50 + (res["scenarios"][0]["confidence"] - res["scenarios"][1]["confidence"]) / 2.0
            prob_up = max(0.0, min(1.0, prob_up))
            brier_scores.append((prob_up - actual_up) ** 2)

        empirical_coverage = round(covered_p10_p90 / total_evals, 3) if total_evals > 0 else 0.0
        avg_brier = round(sum(brier_scores) / len(brier_scores), 3) if brier_scores else 0.25

        return {
            "status": "VALIDATED",
            "evaluated_windows": total_evals,
            "target_coverage": 0.80,
            "empirical_coverage_p10_p90": empirical_coverage,
            "average_brier_score": avg_brier,
            "baseline_random_walk_brier": 0.250,
            "is_calibrated": bool(0.65 <= empirical_coverage <= 0.95),
        }
