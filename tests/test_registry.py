"""Tests for Master Liquidity Registry and Royal Tier hierarchy."""
import unittest
import time
from liquidity_map.data.registry import MasterLiquidityRegistry


class TestMasterLiquidityRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = MasterLiquidityRegistry(base_price=2750.00)

    def test_canonical_tiers_presence(self):
        objects = self.registry.get_all_objects()
        tiers_found = {o["tier"] for o in objects}
        for expected in ["SSS", "SS", "S", "A", "B", "C", "D"]:
            self.assertIn(expected, tiers_found)

    def test_price_touch_and_sweep(self):
        # Find a BSL object above 2750
        bsl_obj = next(o for o in self.registry._objects.values() if o.side == "BSL" and o.price_level > 2750.0)
        target_price = bsl_obj.price_level

        # Test approach
        self.registry.evaluate_live_price(target_price - 0.30, time.time())
        self.assertEqual(bsl_obj.lifecycle, "TESTED")

        # Test sweep
        self.registry.evaluate_live_price(target_price + 0.10, time.time())
        self.assertEqual(bsl_obj.lifecycle, "SWEPT")
        self.assertIsNotNone(bsl_obj.swept_timestamp)


if __name__ == "__main__":
    unittest.main()
