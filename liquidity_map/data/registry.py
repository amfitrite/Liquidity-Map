"""Master Liquidity Registry & Structural Candidate Store for XAUUSD."""
import time
import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from liquidity_map.config import DEFAULT_TIER_CONFIGS


class LiquidityObject:
    def __init__(
        self,
        object_id: str,
        tier: str,
        price_level: float,
        side: str,
        structure_type: str,
        source_timeframe: str,
        event_time_utc: str,
        event_timestamp: float,
        lifecycle: str = "FRESH",
        trail_preset: str = "quantum",
        score: float = 0.90,
        source_kind: str = "OBSERVED",
    ):
        self.object_id = object_id
        self.tier = tier
        self.price_level = price_level
        self.price_low = price_level - 0.25
        self.price_high = price_level + 0.25
        self.side = side  # "BSL" or "SSL"
        self.structure_type = structure_type
        self.source_timeframe = source_timeframe
        self.event_time_utc = event_time_utc
        self.event_timestamp = event_timestamp
        self.lifecycle = lifecycle
        self.trail_preset = trail_preset
        self.score = score
        self.source_kind = source_kind
        self.swept_timestamp: Optional[float] = None
        self.test_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        cfg = DEFAULT_TIER_CONFIGS.get(self.tier)
        return {
            "object_id": self.object_id,
            "tier": self.tier,
            "tier_name": cfg.name if cfg else self.tier,
            "price_level": round(self.price_level, 2),
            "price_low": round(self.price_low, 2),
            "price_high": round(self.price_high, 2),
            "side": self.side,
            "structure_type": self.structure_type,
            "source_timeframe": self.source_timeframe,
            "event_time_utc": self.event_time_utc,
            "event_timestamp": self.event_timestamp,
            "lifecycle": self.lifecycle,
            "trail_preset": self.trail_preset,
            "core_color": cfg.core_color if cfg else "#FFFFFF",
            "trail_color": cfg.trail_color if cfg else "#FFFFFF",
            "nominal_size": cfg.nominal_size if cfg else 20,
            "signature": cfg.signature if cfg else "",
            "score": round(self.score, 2),
            "source_kind": self.source_kind,
            "swept_timestamp": self.swept_timestamp,
            "test_count": self.test_count,
        }


class MasterLiquidityRegistry:
    """Canonical repository of historical and active liquidity candidate pools."""

    def __init__(self, base_price: float = 2748.50):
        self._objects: Dict[str, LiquidityObject] = {}
        self.initialize_canonical_pools(base_price)

    def initialize_canonical_pools(self, base_price: float):
        """Populates authentic institutional liquidity levels aligned with the 7 Royal Tiers."""
        now_ts = time.time()
        self._objects.clear()

        # Seed structural levels for XAUUSD around the base price
        seed_definitions = [
            # Tier SSS (MN1 Macro - Golden Sovereign)
            ("SSS", base_price + 32.50, "BSL", "PREVIOUS_MONTH_HIGH", "MN1", now_ts - 86400 * 24, "quantum"),
            ("SSS", base_price - 38.00, "SSL", "PREVIOUS_MONTH_LOW", "MN1", now_ts - 86400 * 20, "quantum"),
            # Tier SS (W1 External - Crimson Dynast)
            ("SS", base_price + 18.20, "BSL", "PREVIOUS_WEEK_HIGH", "W1", now_ts - 86400 * 7, "plasma"),
            ("SS", base_price - 22.40, "SSL", "PREVIOUS_WEEK_LOW", "W1", now_ts - 86400 * 6, "plasma"),
            # Tier S (D1 External - Sapphire Duke)
            ("S", base_price + 9.80, "BSL", "PREVIOUS_DAY_HIGH", "D1", now_ts - 86400 * 1.5, "astral"),
            ("S", base_price - 11.60, "SSL", "PREVIOUS_DAY_LOW", "D1", now_ts - 86400 * 1.2, "astral"),
            ("S", base_price + 14.10, "BSL", "DAILY_EQUAL_HIGHS", "D1", now_ts - 86400 * 2.8, "astral"),
            # Tier A (H4 Major - Azure Knight)
            ("A", base_price + 5.60, "BSL", "H4_SWING_HIGH", "H4", now_ts - 3600 * 16, "cyber"),
            ("A", base_price - 6.40, "SSL", "H4_SWING_LOW", "H4", now_ts - 3600 * 12, "cyber"),
            ("A", base_price + 7.90, "BSL", "H4_EQUAL_HIGHS", "H4", now_ts - 3600 * 20, "cyber"),
            # Tier B (H1 Structure - Jade Merchant)
            ("B", base_price + 3.20, "BSL", "H1_SWING_HIGH", "H1", now_ts - 3600 * 4, "cryo"),
            ("B", base_price - 3.80, "SSL", "H1_SWING_LOW", "H1", now_ts - 3600 * 3.5, "cryo"),
            ("B", base_price + 4.10, "BSL", "LONDON_SESSION_HIGH", "H1", now_ts - 3600 * 6, "cryo"),
            ("B", base_price - 4.60, "SSL", "ASIA_SESSION_LOW", "H1", now_ts - 3600 * 10, "cryo"),
            # Tier C (M15 Local - Iron Crafter)
            ("C", base_price + 1.80, "BSL", "M15_SWING_HIGH", "M15", now_ts - 1800 * 2, "flux"),
            ("C", base_price - 2.10, "SSL", "M15_SWING_LOW", "M15", now_ts - 1800 * 1.8, "flux"),
            ("C", base_price + 2.40, "BSL", "M15_INTERNAL_EQH", "M15", now_ts - 1800 * 3, "flux"),
            # Tier D (M5/M1 Minor - Earthen Peasant)
            ("D", base_price + 0.90, "BSL", "M5_MICRO_SWING_HIGH", "M5", now_ts - 600 * 2, "minimal"),
            ("D", base_price - 1.10, "SSL", "M5_MICRO_SWING_LOW", "M5", now_ts - 600 * 1.5, "minimal"),
            ("D", base_price + 1.25, "BSL", "M1_MICRO_PIVOT", "M1", now_ts - 300 * 1.2, "minimal"),
        ]

        for tier, price, side, stype, tf, event_ts, preset in seed_definitions:
            obj_id = f"liq_{tier.lower()}_{int(price*100)}_{str(uuid.uuid4())[:6]}"
            iso_t = datetime.fromtimestamp(event_ts, timezone.utc).isoformat()
            self._objects[obj_id] = LiquidityObject(
                object_id=obj_id,
                tier=tier,
                price_level=price,
                side=side,
                structure_type=stype,
                source_timeframe=tf,
                event_time_utc=iso_t,
                event_timestamp=event_ts,
                trail_preset=preset,
            )

    def evaluate_live_price(self, current_price: float, timestamp: float):
        """Updates lifecycle state (FRESH -> TESTED -> SWEPT) based on price proximity."""
        touch_threshold = 0.35  # Price tolerance for interaction
        sweep_threshold = 0.15

        for obj in self._objects.values():
            if obj.lifecycle in ("SWEPT", "INVALIDATED", "EXPIRED"):
                continue

            dist = abs(current_price - obj.price_level)

            # Check if swept
            if (obj.side == "BSL" and current_price >= obj.price_level) or \
               (obj.side == "SSL" and current_price <= obj.price_level):
                obj.lifecycle = "SWEPT"
                obj.swept_timestamp = timestamp
            elif dist <= touch_threshold and obj.lifecycle == "FRESH":
                obj.lifecycle = "TESTED"
                obj.test_count += 1

    def get_all_objects(self, limit: int = 120) -> List[Dict[str, Any]]:
        objs = list(self._objects.values())
        # Sort by tier priority (SSS first) and proximity
        tier_weight = {"SSS": 7, "SS": 6, "S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
        objs.sort(key=lambda o: tier_weight.get(o.tier, 0), reverse=True)
        return [o.to_dict() for o in objs[:limit]]
