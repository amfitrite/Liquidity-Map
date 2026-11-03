"""Tests for Centered Game World Camera coordinate math."""
import unittest
from liquidity_map.engine.world import GameWorldCamera


class TestGameWorldCamera(unittest.TestCase):
    def setUp(self):
        self.camera = GameWorldCamera(
            viewport_width=1400.0,
            viewport_height=800.0,
            pixels_per_second=10.0,
            pixels_per_price=50.0,
        )

    def test_live_anchor_is_center(self):
        t_live = 1700000000.0
        p_live = 2750.0
        sx, sy = self.camera.world_to_screen(t_live, p_live, t_live, p_live)
        self.assertEqual(sx, 700.0)
        self.assertEqual(sy, 400.0)

    def test_past_is_left_future_is_right(self):
        t_live = 1700000000.0
        p_live = 2750.0
        # Past (5 seconds earlier)
        sx_past, _ = self.camera.world_to_screen(t_live - 5.0, p_live, t_live, p_live)
        self.assertLess(sx_past, 700.0)

        # Future (5 seconds later)
        sx_future, _ = self.camera.world_to_screen(t_live + 5.0, p_live, t_live, p_live)
        self.assertGreater(sx_future, 700.0)

    def test_higher_price_is_above(self):
        t_live = 1700000000.0
        p_live = 2750.0
        # Higher price (2755) should have smaller Y coordinate in SVG/Canvas (higher on screen)
        _, sy_high = self.camera.world_to_screen(t_live, p_live + 5.0, t_live, p_live)
        self.assertLess(sy_high, 400.0)

        # Lower price (2745) should have larger Y coordinate (lower on screen)
        _, sy_low = self.camera.world_to_screen(t_live, p_live - 5.0, t_live, p_live)
        self.assertGreater(sy_low, 400.0)


if __name__ == "__main__":
    unittest.main()
