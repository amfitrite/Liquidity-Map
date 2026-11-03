"""Unit tests for Historical Liquidity Detector suite."""
import unittest
from datetime import datetime, timezone
from liquidity_map.data.detector import HistoricalLiquidityDetector


class TestHistoricalLiquidityDetector(unittest.TestCase):
    def setUp(self):
        self.detector = HistoricalLiquidityDetector(symbol="XAUUSD")

    def test_stable_identity_reproducibility(self):
        """Rule: Canonical ID tuple is strictly deterministic and idempotent."""
        id1 = self.detector._generate_stable_id("PREVIOUS_DAY_HIGH", "D1", "BSL", 1762128000, 3945.50)
        id2 = self.detector._generate_stable_id("PREVIOUS_DAY_HIGH", "D1", "BSL", 1762128000, 3945.50)
        self.assertEqual(id1, id2)

        # Different price or timestamp must yield different ID
        id3 = self.detector._generate_stable_id("PREVIOUS_DAY_HIGH", "D1", "BSL", 1762128000, 3946.00)
        self.assertNotEqual(id1, id3)

    def test_equal_levels_detection(self):
        """Rule: Swings within tolerance are classified as EQUAL_HIGHS / EQUAL_LOWS."""
        mock_candidates = [
            {
                "id": "cand_1",
                "detector_type": "H1_SWING_HIGH",
                "side": "BSL",
                "price_level": 3935.20,
                "detected_at_utc": "2026-11-04T00:00:00Z",
                "source_timeframe": "H1",
            },
            {
                "id": "cand_2",
                "detector_type": "H1_SWING_HIGH",
                "side": "BSL",
                "price_level": 3935.50,  # 0.30 difference <= tolerance 0.60
                "detected_at_utc": "2026-11-04T04:00:00Z",
                "source_timeframe": "H1",
            },
        ]

        eq_candidates = self.detector.detect_equal_levels(mock_candidates, tolerance=0.60)
        self.assertEqual(len(eq_candidates), 1)
        eq = eq_candidates[0]
        self.assertEqual(eq["detector_type"], "EQUAL_HIGHS")
        self.assertEqual(eq["side"], "BSL")
        self.assertEqual(eq["tier"], "A")
        self.assertEqual(eq["price_level"], 3935.35)
        self.assertEqual(eq["epistemic_class"], "DETECTED_CANDIDATE")

    def test_live_detection_real_or_graceful(self):
        """Rule: Runs full detection without raising unhandled errors."""
        candidates = self.detector.detect_all(current_live_price=3930.00)
        self.assertIsInstance(candidates, list)
        for c in candidates:
            self.assertIn("id", c)
            self.assertIn("detector_type", c)
            self.assertIn("price_level", c)
            self.assertIn(c["side"], ["BSL", "SSL"])
            self.assertIn(c["tier"], ["SSS", "SS", "S", "A", "B", "C", "D"])
            self.assertEqual(c["epistemic_class"], "DETECTED_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
