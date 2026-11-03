"""Unit tests for Master Liquidity Registry, deduplication, and demo isolation."""
import unittest
import time
from liquidity_map.data.registry import MasterLiquidityRegistry, LiquidityObject


class TestMasterLiquidityRegistry(unittest.TestCase):
    def test_demo_isolation(self):
        """Rule: Demo fixtures are explicitly tagged and isolated from live registry."""
        demo_reg = MasterLiquidityRegistry(live_mode=False)
        demo_reg.load_demo_fixtures(base_price=3930.00)
        objects = demo_reg.get_all_objects()
        self.assertGreater(len(objects), 0)
        for obj in objects:
            self.assertTrue(obj["is_demo"])
            self.assertEqual(obj["epistemic_class"], "DEMO_FIXTURE")

        # Live registry must start completely clean without mock objects
        live_reg = MasterLiquidityRegistry(live_mode=True)
        self.assertEqual(len(live_reg.get_all_objects()), 0)

    def test_canonical_tiers_in_demo(self):
        """Rule: Demo mode includes full 7-tier Royal Social Hierarchy."""
        demo_reg = MasterLiquidityRegistry(live_mode=False)
        demo_reg.load_demo_fixtures(base_price=3930.00)
        objects = demo_reg.get_all_objects()
        tiers_found = {o["tier"] for o in objects}
        for expected in ["SSS", "SS", "S", "A", "B", "C", "D"]:
            self.assertIn(expected, tiers_found)

    def test_stable_identity_and_deduplication(self):
        """Rule: Objects with identical canonical ID preserve state and do not recreate."""
        reg = MasterLiquidityRegistry(live_mode=True)
        obj1 = LiquidityObject(
            object_id="liq_h1_bsl_abc123",
            tier="B",
            price_level=3935.00,
            side="BSL",
            structure_type="H1_SWING_HIGH",
            source_timeframe="H1",
            event_time_utc="2026-11-04T00:00:00Z",
            event_timestamp=1762128000.0,
            lifecycle="TESTED",  # Has been touched once
        )
        self.assertTrue(reg.register_object(obj1))
        self.assertEqual(len(reg.get_all_objects()), 1)

        # Re-registering same ID should NOT reset lifecycle state to FRESH
        obj2 = LiquidityObject(
            object_id="liq_h1_bsl_abc123",
            tier="B",
            price_level=3935.00,
            side="BSL",
            structure_type="H1_SWING_HIGH",
            source_timeframe="H1",
            event_time_utc="2026-11-04T00:00:00Z",
            event_timestamp=1762128000.0,
            lifecycle="FRESH",  # Newly queried candidate
        )
        self.assertFalse(reg.register_object(obj2))
        stored = reg._objects["liq_h1_bsl_abc123"]
        self.assertEqual(stored.lifecycle, "TESTED")  # Preserved!

    def test_spatial_relationships_linking(self):
        """Rule: Overlapping / confluent distinct levels link via relationships without deleting each other."""
        reg = MasterLiquidityRegistry(live_mode=True)
        obj1 = LiquidityObject(
            object_id="liq_pdh_bsl_1",
            tier="S",
            price_level=3935.00,
            side="BSL",
            structure_type="PREVIOUS_DAY_HIGH",
            source_timeframe="D1",
            event_time_utc="2026-11-03T00:00:00Z",
            event_timestamp=1762041600.0,
        )
        obj2 = LiquidityObject(
            object_id="liq_h4_bsl_2",
            tier="A",
            price_level=3935.20,  # 0.20 pts away -> Confluence!
            side="BSL",
            structure_type="H4_SWING_HIGH",
            source_timeframe="H4",
            event_time_utc="2026-11-03T16:00:00Z",
            event_timestamp=1762099200.0,
        )
        reg.register_object(obj1)
        reg.register_object(obj2)

        self.assertEqual(len(reg.get_all_objects()), 2)
        # Check relationship link
        self.assertTrue(any(r["target_id"] == "liq_h4_bsl_2" for r in obj1.relationships))
        self.assertTrue(any(r["target_id"] == "liq_pdh_bsl_1" for r in obj2.relationships))


if __name__ == "__main__":
    unittest.main()
