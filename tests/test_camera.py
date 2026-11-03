"""Unit tests for Centered Game World Camera coordinate math and inversion."""
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
        p_live = 3930.0
        sx, sy = self.camera.world_to_screen(t_live, p_live, t_live, p_live)
        self.assertEqual(sx, 700.0)
        self.assertEqual(sy, 400.0)

    def test_inversion_screen_to_world(self):
        """Rule: Screen to world inversion must perfectly reproduce original coordinates."""
        t_live = 1700000000.0
        p_live = 3930.0
        target_t = t_live - 45.0
        target_p = p_live + 8.50

        sx, sy = self.camera.world_to_screen(target_t, target_p, t_live, p_live)
        rec_t, rec_p = self.camera.screen_to_world(sx, sy, t_live, p_live)

        self.assertAlmostEqual(rec_t, target_t, places=4)
        self.assertAlmostEqual(rec_p, target_p, places=4)

    def test_pan_and_reset(self):
        """Rule: Panning translates coordinates and reset_view restores center."""
        t_live = 1700000000.0
        p_live = 3930.0
        self.camera.pan(120.0, -80.0)
        self.assertEqual(self.camera.mode, "FREE_PAN")

        sx, sy = self.camera.world_to_screen(t_live, p_live, t_live, p_live)
        self.assertEqual(sx, 700.0 + 120.0)
        self.assertEqual(sy, 400.0 - 80.0)

        self.camera.reset_view()
        self.assertEqual(self.camera.mode, "FOLLOW")
        sx_reset, sy_reset = self.camera.world_to_screen(t_live, p_live, t_live, p_live)
        self.assertEqual(sx_reset, 700.0)
        self.assertEqual(sy_reset, 400.0)

    def test_zoom_clamping(self):
        """Rule: Zoom must be strictly clamped within min/max bounds."""
        self.camera.set_zoom(zoom_x=1000.0, zoom_y=0.1)
        self.assertEqual(self.camera.pixels_per_second, self.camera.max_zoom_x)
        self.assertEqual(self.camera.pixels_per_price, self.camera.min_zoom_y)

    def test_directional_geometry(self):
        """Rule: Past is Left (-), Future is Right (+); Higher price is Up (- Y in SVG/Canvas)."""
        t_live = 1700000000.0
        p_live = 3930.0

        sx_past, _ = self.camera.world_to_screen(t_live - 10.0, p_live, t_live, p_live)
        sx_future, _ = self.camera.world_to_screen(t_live + 10.0, p_live, t_live, p_live)
        self.assertLess(sx_past, 700.0)
        self.assertGreater(sx_future, 700.0)

        _, sy_high = self.camera.world_to_screen(t_live, p_live + 5.0, t_live, p_live)
        _, sy_low = self.camera.world_to_screen(t_live, p_live - 5.0, t_live, p_live)
        self.assertLess(sy_high, 400.0)
        self.assertGreater(sy_low, 400.0)


if __name__ == "__main__":
    unittest.main()
