"""Liquidity Map Orchestration Service adhering to P0 Integrity & Architecture Specifications."""
import time
import logging
from typing import Dict, Any, Optional
from liquidity_map.config import AppConfig
from liquidity_map.data.dukascopy_feed import DukascopyFeed
from liquidity_map.data.detector import HistoricalLiquidityDetector
from liquidity_map.data.registry import MasterLiquidityRegistry
from liquidity_map.engine.lifecycle import LiquidityLifecycleEngine
from liquidity_map.engine.future_engine import FutureLiquidityEngine
from liquidity_map.engine.world import GameWorldCamera

logger = logging.getLogger("LiquidityMap.Service")


class LiquidityMapService:
    """Master service linking live data, detection registry, lifecycle engine, future projection, and world camera."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()

        self.feed = DukascopyFeed(
            symbol=self.config.symbol,
            price_basis=self.config.price_basis,
            poll_interval=self.config.feed_poll_interval,
            simulation_mode=self.config.simulation_mode,
        )

        self.detector = HistoricalLiquidityDetector(symbol=self.config.symbol)
        self.registry = MasterLiquidityRegistry(live_mode=not self.config.simulation_mode)
        self.lifecycle = LiquidityLifecycleEngine()
        self.future_engine = FutureLiquidityEngine()

        self.camera = GameWorldCamera(
            pixels_per_second=self.config.default_pixels_per_second,
            pixels_per_price=self.config.default_pixels_per_price,
        )

        # Wire feed events to lifecycle evaluator
        self.feed.add_callback(self._on_tick)

        # Initialize candidates
        self._initialize_liquidity_candidates()

    def _initialize_liquidity_candidates(self):
        """Initializes liquidity registry strictly separating live detected candidates from demo fixtures."""
        if self.config.simulation_mode:
            # Demo mode: load explicitly tagged mock fixtures
            base_p = self.feed.get_basis_price() or 3930.00
            self.registry.load_demo_fixtures(base_price=base_p)
        else:
            # Live mode: run authentic structural detector on historical market data
            base_p = self.feed.get_initial_price()
            candidates = self.detector.detect_all(current_live_price=base_p)
            if candidates:
                self.registry.populate_from_detector(candidates)
            else:
                # Fallback to demo fixtures ONLY if offline/network unavailable, explicitly labeled
                self.registry.load_demo_fixtures(base_price=base_p)

    def start(self):
        self.feed.start()

    def stop(self):
        self.feed.stop()

    def _on_tick(self, quote: Dict[str, Any]):
        basis_price = quote.get("provider_price")
        if basis_price is None:
            return
        now_ts = time.time()
        # Evaluate liquidity state transitions causally
        self.lifecycle.evaluate(self.registry._objects, basis_price, now_ts, source_quote=quote)

    def get_world_snapshot(self, viewport_w: float = 1400.0, viewport_h: float = 800.0) -> Dict[str, Any]:
        """Assembles a complete render frame for the centered game world."""
        self.camera.set_viewport(viewport_w, viewport_h)
        quote = self.feed.get_latest_quote()
        p_live = quote.get("provider_price") or self.feed.current_mid or 3930.00
        t_live = time.time()

        # 1. Historical & Active Liquidity Objects with Screen Positions
        raw_objects = self.registry.get_all_objects(limit=self.config.max_visible_objects)
        rendered_objects = []

        for obj in raw_objects:
            sx, sy = self.camera.world_to_screen(obj["event_timestamp"], obj["price_level"], t_live, p_live)
            rendered_objects.append({
                **obj,
                "screen_x": round(sx, 1),
                "screen_y": round(sy, 1),
                "is_visible": self.camera.is_visible(sx, sy),
            })

        # 2. Future Liquidity Scenarios (Block Bootstrap Monte Carlo)
        price_history = self.feed._recent_ticks if hasattr(self.feed, "_recent_ticks") and self.feed._recent_ticks else None
        future_data = self.future_engine.generate_scenarios(p_live, t_live, price_history=price_history)

        # Map future fan corridor to screen space
        screen_fan = []
        for pt in future_data.get("fan_corridor", []):
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
                "feed_status": quote.get("status", "CONNECTING"),
                "regime": future_data.get("regime", "RANGING"),
                "model_version": self.future_engine.model_version,
            },
        }
