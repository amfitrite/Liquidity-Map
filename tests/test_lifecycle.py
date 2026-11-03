"""Unit tests for Liquidity Lifecycle Engine."""
import unittest
import time
from liquidity_map.data.registry import LiquidityObject
from liquidity_map.engine.lifecycle import LiquidityLifecycleEngine, LifecycleState


class TestLiquidityLifecycleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LiquidityLifecycleEngine(
            touch_threshold=0.20,
            sweep_threshold=0.45,
            approach_threshold=1.00,
            gap_threshold=1.50,
        )

    def _create_mock_obj(self, obj_id: str, side: str, price: float, tier: str = "A") -> LiquidityObject:
        return LiquidityObject(
            object_id=obj_id,
            tier=tier,
            price_level=price,
            side=side,
            structure_type="SWING_TEST",
            source_timeframe="H1",
            event_time_utc="2026-11-04T00:00:00Z",
            event_timestamp=time.time() - 3600,
            lifecycle=LifecycleState.FRESH,
        )

    def test_price_already_above_at_inception_not_swept(self):
        """Rule 1: Price already past level at start is not automatically marked as swept."""
        obj = self._create_mock_obj("bsl_1", "BSL", 3930.00)
        objects = {obj.object_id: obj}

        # First price observation at 3935.00 (already $5 above level)
        events = self.engine.evaluate(objects, current_price=3935.00, timestamp=time.time())
        self.assertEqual(len(events), 0)
        self.assertEqual(obj.lifecycle, LifecycleState.FRESH)

        # Subsequent move to 3936.00 still does NOT count as crossing from below
        events2 = self.engine.evaluate(objects, current_price=3936.00, timestamp=time.time())
        self.assertEqual(len(events2), 0)
        self.assertEqual(obj.lifecycle, LifecycleState.FRESH)

    def test_sequential_crossing_bsl(self):
        """Rule 2: Sequential price observation from below to above proves crossing."""
        obj = self._create_mock_obj("bsl_2", "BSL", 3930.00, tier="A")
        objects = {obj.object_id: obj}

        # Step 1: Baseline at 3928.00 (below level)
        self.engine.evaluate(objects, current_price=3928.00, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.FRESH)

        # Step 2: Move to 3929.20 (within 1.00 approach)
        self.engine.evaluate(objects, current_price=3929.20, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.APPROACHING)

        # Step 3: Move to 3930.10 (penetration +0.10 <= sweep_threshold 0.45 -> BREACHED)
        self.engine.evaluate(objects, current_price=3930.10, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.BREACHED)

        # Step 4: Move to 3930.80 (penetration +0.80 > sweep_threshold 0.45 -> SWEPT)
        self.engine.evaluate(objects, current_price=3930.80, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.SWEPT)
        self.assertIsNotNone(obj.swept_timestamp)

        # Crucial Rule: Tier must NOT change
        self.assertEqual(obj.tier, "A")

    def test_touch_is_distinct_from_sweep(self):
        """Rule 3: Proximity touch within threshold is distinct from sweep."""
        obj = self._create_mock_obj("ssl_1", "SSL", 3925.00)
        objects = {obj.object_id: obj}

        # Step 1: Baseline at 3927.00 (above SSL)
        self.engine.evaluate(objects, current_price=3927.00, timestamp=time.time())

        # Step 2: Move to 3925.10 (|p - level| = 0.10 <= touch_threshold 0.20)
        events = self.engine.evaluate(objects, current_price=3925.10, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.TOUCHED)
        self.assertEqual(obj.test_count, 1)

    def test_gap_crossing_flagged(self):
        """Rule 4: When price jumps over level with large gap, record as GAP_CROSS."""
        obj = self._create_mock_obj("bsl_gap", "BSL", 3930.00)
        objects = {obj.object_id: obj}

        # Step 1: Price at 3928.50
        self.engine.evaluate(objects, current_price=3928.50, timestamp=time.time())

        # Step 2: Price jumps to 3931.50 (jump delta 3.00 > gap_threshold 1.50)
        events = self.engine.evaluate(objects, current_price=3931.50, timestamp=time.time())
        self.assertTrue(len(events) > 0)
        self.assertTrue(events[0]["is_gap_cross"])

    def test_sweep_and_reclaim_sequence(self):
        """Rule 5: Sweep followed by reversal across level triggers RECLAIMED."""
        obj = self._create_mock_obj("bsl_rec", "BSL", 3930.00)
        objects = {obj.object_id: obj}

        # Baseline -> Sweep
        self.engine.evaluate(objects, current_price=3929.00, timestamp=time.time())
        self.engine.evaluate(objects, current_price=3930.80, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.SWEPT)

        # Price drops back below level to 3929.50 -> RECLAIMED
        events = self.engine.evaluate(objects, current_price=3929.50, timestamp=time.time())
        self.assertEqual(obj.lifecycle, LifecycleState.RECLAIMED)

    def test_idempotence(self):
        """Rule 6: Identical subsequent prices produce no duplicate transitions."""
        obj = self._create_mock_obj("ssl_idem", "SSL", 3925.00)
        objects = {obj.object_id: obj}

        self.engine.evaluate(objects, current_price=3927.00, timestamp=time.time())
        events1 = self.engine.evaluate(objects, current_price=3925.10, timestamp=time.time())
        self.assertEqual(len(events1), 1)

        # Same price repeated
        events2 = self.engine.evaluate(objects, current_price=3925.10, timestamp=time.time())
        self.assertEqual(len(events2), 0)


if __name__ == "__main__":
    unittest.main()
