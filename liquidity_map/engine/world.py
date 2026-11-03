"""Centered Live-Price Game World Camera and Coordinate Engine."""
from typing import Dict, Tuple, Any, List, Optional


class GameWorldCamera:
    """Manages the centered live-price camera transform and playfield coordinate spaces.
    
    Unified Coordinate Philosophy:
    - Center anchor is at (cx, cy) = (viewport_width / 2 + pan_offset_x, viewport_height / 2 + pan_offset_y).
    - Time axis: Past is Left (-), Future is Right (+). dx = (t - t_live) * pixels_per_second.
    - Price axis: Higher is Up (- Y in SVG/Canvas), Lower is Down (+ Y). dy = - (p - p_live) * pixels_per_price.
    """

    def __init__(
        self,
        viewport_width: float = 1400.0,
        viewport_height: float = 800.0,
        pixels_per_second: float = 8.0,
        pixels_per_price: float = 35.0,
    ):
        self.width = float(viewport_width)
        self.height = float(viewport_height)
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0

        self.pixels_per_second = float(pixels_per_second)
        self.pixels_per_price = float(pixels_per_price)

        self.mode = "FOLLOW"  # "FOLLOW" or "FREE_PAN"
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0

        self.min_zoom_x = 0.8
        self.max_zoom_x = 60.0
        self.min_zoom_y = 4.0
        self.max_zoom_y = 300.0

    def set_viewport(self, width: float, height: float):
        self.width = float(width)
        self.height = float(height)
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0

    def pan(self, dx: float, dy: float):
        """Applies translation offset and switches mode to FREE_PAN."""
        self.pan_offset_x += dx
        self.pan_offset_y += dy
        self.mode = "FREE_PAN"

    def reset_view(self):
        """Resets camera translation to center on live price anchor."""
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.mode = "FOLLOW"

    def set_zoom(self, zoom_x: Optional[float] = None, zoom_y: Optional[float] = None):
        """Sets zoom scale along time and price axes within safe bounds."""
        if zoom_x is not None:
            self.pixels_per_second = max(self.min_zoom_x, min(self.max_zoom_x, float(zoom_x)))
        if zoom_y is not None:
            self.pixels_per_price = max(self.min_zoom_y, min(self.max_zoom_y, float(zoom_y)))

    def world_to_screen(
        self, world_time: float, world_price: float, t_live: float, p_live: float
    ) -> Tuple[float, float]:
        """Calculates screen coordinate from immutable world coordinate relative to live player."""
        base_cx = self.cx + (self.pan_offset_x if self.mode == "FREE_PAN" else 0.0)
        base_cy = self.cy + (self.pan_offset_y if self.mode == "FREE_PAN" else 0.0)

        screen_x = base_cx + (world_time - t_live) * self.pixels_per_second
        screen_y = base_cy - (world_price - p_live) * self.pixels_per_price

        return screen_x, screen_y

    def screen_to_world(
        self, screen_x: float, screen_y: float, t_live: float, p_live: float
    ) -> Tuple[float, float]:
        """Inverts screen coordinate back to exact world time and price."""
        base_cx = self.cx + (self.pan_offset_x if self.mode == "FREE_PAN" else 0.0)
        base_cy = self.cy + (self.pan_offset_y if self.mode == "FREE_PAN" else 0.0)

        world_time = t_live + (screen_x - base_cx) / self.pixels_per_second
        world_price = p_live - (screen_y - base_cy) / self.pixels_per_price

        return world_time, world_price

    def is_visible(self, screen_x: float, screen_y: float, margin: float = 80.0) -> bool:
        return (
            -margin <= screen_x <= self.width + margin
            and -margin <= screen_y <= self.height + margin
        )
