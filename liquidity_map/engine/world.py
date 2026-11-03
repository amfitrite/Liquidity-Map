"""Centered Live-Price Game World Camera and Coordinate Engine."""
from typing import Dict, Tuple, Any, List


class GameWorldCamera:
    """Manages the centered live-price camera transform and playfield coordinate spaces."""

    def __init__(
        self,
        viewport_width: float = 1400.0,
        viewport_height: float = 800.0,
        pixels_per_second: float = 8.0,
        pixels_per_price: float = 40.0,
    ):
        self.width = viewport_width
        self.height = viewport_height
        self.cx = viewport_width / 2.0
        self.cy = viewport_height / 2.0

        self.pixels_per_second = pixels_per_second
        self.pixels_per_price = pixels_per_price

        self.mode = "FOLLOW"  # "FOLLOW" or "INSPECT"
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0

    def set_viewport(self, width: float, height: float):
        self.width = width
        self.height = height
        self.cx = width / 2.0
        self.cy = height / 2.0

    def world_to_screen(
        self, world_time: float, world_price: float, t_live: float, p_live: float
    ) -> Tuple[float, float]:
        """Calculates screen coordinate from immutable world coordinate relative to live player."""
        base_cx = self.cx + (self.pan_offset_x if self.mode == "INSPECT" else 0.0)
        base_cy = self.cy + (self.pan_offset_y if self.mode == "INSPECT" else 0.0)

        # Time: Past is Left (-), Future is Right (+)
        screen_x = base_cx + (world_time - t_live) * self.pixels_per_second
        # Price: Higher is Up (- Y in SVG/Canvas), Lower is Down (+ Y)
        screen_y = base_cy - (world_price - p_live) * self.pixels_per_price

        return screen_x, screen_y

    def is_visible(self, screen_x: float, screen_y: float, margin: float = 60.0) -> bool:
        return (
            -margin <= screen_x <= self.width + margin
            and -margin <= screen_y <= self.height + margin
        )
