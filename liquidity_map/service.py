"""Liquidity Map Orchestration Service."""
import time
import logging
from typing import Dict, Any, Optional
from liquidity_map.config import AppConfig
from liquidity_map.data.dukascopy_feed import DukascopyFeed
from liquidity_map.data.registry import MasterLiquidityRegistry
from liquidity_map.engine.future_engine import FutureLiquidityEngine
from liquidity_map.engine.world import GameWorldCamera

logger = logging.getLogger("LiquidityMap.Service")


class LiquidityMapService:
    """Master service linking live data, detection registry, future projection, and world camera."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()

        self.feed = DukascopyFeed(
            symbol=self.config.symbol,
            price_basis=self.config.price_basis,
            poll_interval=self.config.feed_poll_interval,
            simulation_mode=self.config.simulation_mode,
        )
        self.registry = MasterLiquidityRegistry(base_price=self.feed.current_mid)
        self.future_engine = FutureLiquidityEngine()
        self.camera = GameWorldCamera(
            pixels_per_second=self.config.default_pixels_per_second,
            pixels_per_price=self.config.default_pixels_per_price,
        )

        # Wire feed events to registry evaluator
        self.feed.add_callback(self._on_tick)

    def start(self):
        self.feed.start()

    def stop(self):
        self.feed.stop()

    def _on_tick(self, quote: Dict[str, Any]):
        basis_price = quote["provider_price"]
        now_ts = time.time()
        # Evaluate liquidity touches and sweeps
        self.registry.evaluate_live_price(basis_price, now_ts)

    def get_world_snapshot(self, viewport_w: float = 1400.0, viewport_h: float = 800.0) -> Dict[str, Any]:
        """Assembles a complete render frame for the centered game world."""
        self.camera.set_viewport(viewport_w, viewport_h)
        quote = self.feed.get_latest_quote()
        p_live = quote["provider_price"]
        t_live = time.time()

        # 1. Historical & Active Liquidity Objects with Screen Positions
        raw_objects = self.registry.get_all_objects(limit=self.config.max_visible_objects)
        rendered_objects = []

        for obj in raw_objects:
            # Map orb event coordinate to screen
            sx, sy = self.camera.world_to_screen(obj["event_timestamp"], obj["price_level"], t_live, p_live)
            # The trail horizontal line starts at sx and extends to the center anchor X (self.camera.cx)
            rendered_objects.append({
                **obj,
                "screen_x": round(sx, 1),
                "screen_y": round(sy, 1),
                "is_visible": self.camera.is_visible(sx, sy),
            })

        # 2. Future Liquidity Scenarios
        future_data = self.future_engine.generate_scenarios(p_live, t_live, volatility=0.35)

        # Map future fan corridor to screen space
        screen_fan = []
        for pt in future_data["fan_corridor"]:
            fx, fy_p50 = self.camera.world_to_screen(pt["future_ts"], pt["p50"], t_live, p_live)
            _, fy_p90 = self.camera.world_to_screen(pt["future_ts"], pt["p90"], t_live, p_live)
            _, fy_p10 = self.camera.world_to_screen(pt["future_ts"], pt["p10"], t_live, p_live)
            _, fy_p75 = self.camera.world_to_screen(pt["future_ts"], pt["p75"], t_live, p_live)
            _, fy_p25 = self.camera.world_to_screen(pt["future_ts"], pt["p25"], t_live, p_live)
            screen_fan.append({
                "screen_x": round(fx, 1),
                "y_p90": round(fy_p90, 1),
                "y_p75": round(fy_p75, 1),
                "y_p50": round(fy_p50, 1),
                "y_p25": round(fy_p25, 1),
                "y_p10": round(fy_p10, 1),
            })

        return {
            "symbol": self.config.symbol,
            "anchor": {
                "cx": self.camera.cx,
                "cy": self.camera.cy,
                "price": p_live,
                "quote": quote,
            },
            "camera": {
                "mode": self.camera.mode,
                "pixels_per_second": self.camera.pixels_per_second,
                "pixels_per_price": self.camera.pixels_per_price,
            },
            "liquidity_objects": rendered_objects,
            "future": {
                **future_data,
                "screen_fan": screen_fan,
            },
            "telemetry": {
                "visible_count": len(rendered_objects),
                "budget_cap": self.config.max_visible_objects,
                "camera_mode": self.camera.mode,
                "fps_target": 60,
                "timestamp": t_live,
            },
        }
