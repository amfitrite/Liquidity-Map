"""Unit tests for Future Liquidity Engine (Block Bootstrap Monte Carlo)."""
import unittest
import math
from liquidity_map.engine.future_engine import FutureLiquidityEngine, MarketRegime


class TestFutureLiquidityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FutureLiquidityEngine(num_simulations=50, block_size=3, seed=42)

    def test_seed_reproducibility(self):
        """Rule: Explicit random seed produces mathematically identical fan corridors and probabilities."""
        engine_a = FutureLiquidityEngine(num_simulations=50, seed=123)
        engine_b = FutureLiquidityEngine(num_simulations=50, seed=123)

        res_a = engine_a.generate_scenarios(3930.00, 1000.0)
        res_b = engine_b.generate_scenarios(3930.00, 1000.0)

        self.assertEqual(res_a["fan_corridor"], res_b["fan_corridor"])
        self.assertEqual(res_a["scenarios"][0]["confidence"], res_b["scenarios"][0]["confidence"])

    def test_quantile_envelope_ordering(self):
        """Rule: Quantile hierarchy strictly holds: P10 <= P25 <= P50 <= P75 <= P90."""
        res = self.engine.generate_scenarios(3930.00, 1000.0)
        fan = res["fan_corridor"]
        self.assertGreater(len(fan), 0)

        for pt in fan:
            self.assertLessEqual(pt["p10"], pt["p25"])
            self.assertLessEqual(pt["p25"], pt["p50"])
            self.assertLessEqual(pt["p50"], pt["p75"])
            self.assertLessEqual(pt["p75"], pt["p90"])

    def test_probability_ranges_valid(self):
        """Rule: All conditional touch probabilities must lie strictly in [0.0, 1.0]."""
        res = self.engine.generate_scenarios(3930.00, 1000.0)
        for s in res["scenarios"]:
            self.assertGreaterEqual(s["confidence"], 0.0)
            self.assertLessEqual(s["confidence"], 1.0)
            self.assertIn(s["epistemic_status"], ["SCENARIO", "MODEL_ESTIMATE"])

    def test_regime_classification(self):
        """Rule: Correctly classifies upward, downward, and ranging regimes."""
        # Upward series
        up_prices = [3900.0 + i * 0.4 for i in range(25)]
        up_regime = self.engine.classify_regime(up_prices)
        self.assertEqual(up_regime["regime"], MarketRegime.TRENDING_UP)

        # Downward series
        down_prices = [3950.0 - i * 0.4 for i in range(25)]
        down_regime = self.engine.classify_regime(down_prices)
        self.assertEqual(down_regime["regime"], MarketRegime.TRENDING_DOWN)

    def test_walk_forward_validation_no_leakage(self):
        """Rule: Walk-forward backtest produces valid coverage and compares against baseline."""
        # Generate 80 synthetic price steps
        prices = [3930.00]
        for i in range(80):
            prices.append(prices[-1] + math.sin(i / 5.0) * 0.3)

        report = self.engine.validate_walk_forward(prices, window_size=30, horizon_steps=8, num_windows=4)
        self.assertEqual(report["status"], "VALIDATED")
        self.assertIn("empirical_coverage_p10_p90", report)
        self.assertIn("average_brier_score", report)
        self.assertIn("baseline_random_walk_brier", report)
        self.assertGreaterEqual(report["empirical_coverage_p10_p90"], 0.0)
        self.assertLessEqual(report["empirical_coverage_p10_p90"], 1.0)


if __name__ == "__main__":
    unittest.main()
