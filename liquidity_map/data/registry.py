"""Master Liquidity Registry & Structural Candidate Store for XAUUSD.

Strict Separation of Concerns:
- LIVE LIQUIDITY is produced exclusively by algorithmic detectors from authentic historical market data.
- DEMO FIXTURES are isolated in load_demo_fixtures() and tagged DEMO_FIXTURE (never shown as live data).
- Preserves deterministic canonical identities, metadata, and relationship graphs.
"""
import time
import math
import uuid
import hashlib
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
        price_low: Optional[float] = None,
        price_high: Optional[float] = None,
        lifecycle: str = "FRESH",
        trail_preset: str = "quantum",
        score: float = 0.90,
        source_kind: str = "OBSERVED",
        epistemic_class: str = "DETECTED_CANDIDATE",
        is_demo: bool = False,
        anchor_event_ids: Optional[List[str]] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ):
        self.object_id = object_id
        self.tier = tier
        self.price_level = round(float(price_level), 3)
        self.price_low = round(float(price_low if price_low is not None else price_level - 0.25), 3)
        self.price_high = round(float(price_high if price_high is not None else price_level + 0.25), 3)
        self.side = side.upper()  # "BSL" or "SSL"
        self.structure_type = structure_type
        self.source_timeframe = source_timeframe.upper()
        self.event_time_utc = event_time_utc
        self.event_timestamp = float(event_timestamp)
        self.lifecycle = lifecycle
        self.trail_preset = trail_preset
        self.score = score
        self.source_kind = source_kind
        self.epistemic_class = epistemic_class
        self.is_demo = is_demo
        self.anchor_event_ids = anchor_event_ids or []
        self.evidence = evidence or {}

        # Lifecycle tracking
        self.swept_timestamp: Optional[float] = None
        self.reclaimed_timestamp: Optional[float] = None
        self.breached_timestamp: Optional[float] = None
        self.test_count: int = 0
        self.relationships: List[Dict[str, str]] = []

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
            "epistemic_class": self.epistemic_class,
            "is_demo": self.is_demo,
            "anchor_event_ids": self.anchor_event_ids,
            "evidence": self.evidence,
            "swept_timestamp": self.swept_timestamp,
            "reclaimed_timestamp": self.reclaimed_timestamp,
            "breached_timestamp": self.breached_timestamp,
            "test_count": self.test_count,
            "relationships": self.relationships,
        }


class MasterLiquidityRegistry:
    """Canonical repository of historical and active liquidity candidate pools."""

    def __init__(self, live_mode: bool = True):
        self.live_mode = live_mode
        self._objects: Dict[str, LiquidityObject] = {}

    def register_object(self, obj: LiquidityObject) -> bool:
        """Registers a liquidity candidate with deterministic deduplication and relationship linking."""
        if not self.live_mode and not obj.is_demo:
            return False

        if obj.object_id in self._objects:
            # Preserve existing lifecycle state; update metadata if necessary
            existing = self._objects[obj.object_id]
            existing.evidence.update(obj.evidence)
            return False

        # Link spatial relationships with existing objects (overlaps_with / confluence)
        for existing in self._objects.values():
            if abs(existing.price_level - obj.price_level) <= 0.40:
                rel_type = "same_structure_as" if existing.structure_type == obj.structure_type else "confluence_with"
                obj.relationships.append({"type": rel_type, "target_id": existing.object_id})
                existing.relationships.append({"type": rel_type, "target_id": obj.object_id})

        self._objects[obj.object_id] = obj
        return True

    def populate_from_detector(self, candidates: List[Dict[str, Any]]):
        """Populates the registry with candidates emitted from authentic structural detectors."""
        for c in candidates:
            # Parse timestamp
            dt_str = c.get("detected_at_utc", datetime.now(timezone.utc).isoformat())
            try:
                ev_ts = datetime.fromisoformat(dt_str).timestamp()
            except Exception:
                ev_ts = time.time()

            obj = LiquidityObject(
                object_id=c["id"],
                tier=c.get("tier", "D"),
                price_level=c["price_level"],
                side=c["side"],
                structure_type=c["detector_type"],
                source_timeframe=c["source_timeframe"],
                event_time_utc=dt_str,
                event_timestamp=ev_ts,
                price_low=c.get("price_low"),
                price_high=c.get("price_high"),
                lifecycle=c.get("lifecycle", "FRESH"),
                trail_preset=c.get("trail_preset", "minimal"),
                score=c.get("score", 0.90),
                source_kind="OBSERVED",
                epistemic_class=c.get("epistemic_class", "DETECTED_CANDIDATE"),
                is_demo=False,
                anchor_event_ids=c.get("anchor_event_ids", []),
                evidence=c.get("evidence", {}),
            )
            self.register_object(obj)

    def load_demo_fixtures(self, base_price: float = 3930.00):
        """Loads static mock fixtures strictly for offline UI demonstration (never used in live mode)."""
        self._objects.clear()
        now_ts = time.time()

        fixtures = [
            ("SSS", base_price + 32.50, "BSL", "PREVIOUS_MONTH_HIGH", "MN1", now_ts - 86400 * 24, "quantum"),
            ("SSS", base_price - 38.00, "SSL", "PREVIOUS_MONTH_LOW", "MN1", now_ts - 86400 * 20, "quantum"),
            ("SS", base_price + 18.20, "BSL", "PREVIOUS_WEEK_HIGH", "W1", now_ts - 86400 * 7, "plasma"),
            ("SS", base_price - 22.40, "SSL", "PREVIOUS_WEEK_LOW", "W1", now_ts - 86400 * 6, "plasma"),
            ("S", base_price + 9.80, "BSL", "PREVIOUS_DAY_HIGH", "D1", now_ts - 86400 * 1.5, "astral"),
            ("S", base_price - 11.60, "SSL", "PREVIOUS_DAY_LOW", "D1", now_ts - 86400 * 1.2, "astral"),
            ("A", base_price + 5.60, "BSL", "H4_SWING_HIGH", "H4", now_ts - 3600 * 16, "cyber"),
            ("A", base_price - 6.40, "SSL", "H4_SWING_LOW", "H4", now_ts - 3600 * 12, "cyber"),
            ("B", base_price + 3.20, "BSL", "H1_SWING_HIGH", "H1", now_ts - 3600 * 4, "cryo"),
            ("B", base_price - 3.80, "SSL", "H1_SWING_LOW", "H1", now_ts - 3600 * 3.5, "cryo"),
            ("C", base_price + 1.80, "BSL", "M15_SWING_HIGH", "M15", now_ts - 1800 * 2, "flux"),
            ("C", base_price - 2.10, "SSL", "M15_SWING_LOW", "M15", now_ts - 1800 * 1.8, "flux"),
            ("D", base_price + 0.90, "BSL", "M5_MICRO_SWING_HIGH", "M5", now_ts - 600 * 2, "minimal"),
            ("D", base_price - 1.10, "SSL", "M5_MICRO_SWING_LOW", "M5", now_ts - 600 * 1.5, "minimal"),
        ]

        for tier, price, side, stype, tf, event_ts, preset in fixtures:
            obj_id = f"demo_{tier.lower()}_{int(price*100)}_{str(uuid.uuid4())[:6]}"
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
                epistemic_class="DEMO_FIXTURE",
                is_demo=True,
            )

    def get_all_objects(self, limit: int = 120) -> List[Dict[str, Any]]:
        objs = list(self._objects.values())
        tier_weight = {"SSS": 7, "SS": 6, "S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
        objs.sort(key=lambda o: tier_weight.get(o.tier, 0), reverse=True)
        return [o.to_dict() for o in objs[:limit]]
