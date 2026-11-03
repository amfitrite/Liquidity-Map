"""Liquidity Lifecycle Engine adhering to docs/LIQUIDITY_MASTER_REGISTRY.md.

Implements sequential-price crossing verification:
- Requires both previous_valid_price and current_valid_price.
- Strictly separates APPROACHING, TOUCHED, BREACHED, SWEPT, RECLAIMED, INVALIDATED.
- Records GAP_CROSS when price jumps across levels without intermediate observations.
- Price already past level at initialization is never falsely marked as swept.
- Idempotent and maintains an immutable transition audit trail.
- Preserves liquidity tier without modification.
"""
import time
from typing import Dict, List, Optional, Any
from liquidity_map.data.registry import LiquidityObject


class LifecycleState:
    FRESH = "FRESH"
    APPROACHING = "APPROACHING"
    TOUCHED = "TOUCHED"
    BREACHED = "BREACHED"
    SWEPT = "SWEPT"
    RECLAIMED = "RECLAIMED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class LiquidityLifecycleEngine:
    """Evaluates sequential market price observations against registered liquidity candidates."""

    def __init__(
        self,
        touch_threshold: float = 0.20,
        sweep_threshold: float = 0.45,
        approach_threshold: float = 1.00,
        gap_threshold: float = 1.80,
    ):
        self.touch_threshold = touch_threshold
        self.sweep_threshold = sweep_threshold
        self.approach_threshold = approach_threshold
        self.gap_threshold = gap_threshold

        self.previous_valid_price: Optional[float] = None
        self.last_evaluation_ts: Optional[float] = None
        self.transition_log: List[Dict[str, Any]] = []

    def evaluate(
        self,
        objects: Dict[str, LiquidityObject],
        current_price: float,
        timestamp: float,
        source_quote: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Evaluates price updates against all active candidates using verified sequential crossing."""
        events: List[Dict[str, Any]] = []

        if current_price is None or current_price <= 0:
            return events

        # If this is the very first price observation, record baseline without triggering crossings
        if self.previous_valid_price is None:
            self.previous_valid_price = current_price
            self.last_evaluation_ts = timestamp
            # Tag objects where current price is already past the level at inception
            for obj in objects.values():
                if obj.side == "BSL" and current_price >= obj.price_level:
                    if obj.lifecycle == LifecycleState.FRESH:
                        obj.evidence["initial_relation"] = "PRICE_ALREADY_ABOVE"
                elif obj.side == "SSL" and current_price <= obj.price_level:
                    if obj.lifecycle == LifecycleState.FRESH:
                        obj.evidence["initial_relation"] = "PRICE_ALREADY_BELOW"
            return events

        prev_p = self.previous_valid_price
        curr_p = current_price

        # Idempotence: zero price delta produces zero duplicate state transitions
        if prev_p == curr_p:
            return events

        is_gap = abs(curr_p - prev_p) >= self.gap_threshold

        for obj in objects.values():
            if obj.lifecycle in (LifecycleState.SWEPT, LifecycleState.INVALIDATED, LifecycleState.EXPIRED):
                # Check for possible RECLAIM if previously swept or breached
                if obj.lifecycle == LifecycleState.SWEPT:
                    if obj.side == "BSL" and prev_p >= obj.price_level and curr_p < (obj.price_level - self.touch_threshold):
                        event = self._record_transition(
                            obj, LifecycleState.RECLAIMED, timestamp, prev_p, curr_p, is_gap, "Reclaimed below BSL level", source_quote
                        )
                        events.append(event)
                    elif obj.side == "SSL" and prev_p <= obj.price_level and curr_p > (obj.price_level + self.touch_threshold):
                        event = self._record_transition(
                            obj, LifecycleState.RECLAIMED, timestamp, prev_p, curr_p, is_gap, "Reclaimed above SSL level", source_quote
                        )
                        events.append(event)
                continue

            lvl = obj.price_level

            # --- BSL EVALUATION (Level is above historical market) ---
            if obj.side == "BSL":
                # Check if price was already above level at startup
                if obj.evidence.get("initial_relation") == "PRICE_ALREADY_ABOVE" and obj.lifecycle == LifecycleState.FRESH:
                    # Do not synthesize sweep without observed sequential crossing from below
                    continue

                # 1. Crossing from below to above or continuation of breach to sweep
                is_crossing = (prev_p < lvl <= curr_p) or (prev_p < lvl and curr_p > lvl)
                is_breach_advancing = (obj.lifecycle == LifecycleState.BREACHED and curr_p > lvl)

                if is_crossing or is_breach_advancing:
                    penetration = curr_p - lvl
                    if penetration > self.sweep_threshold:
                        target_state = LifecycleState.SWEPT
                        reason = f"BSL swept with penetration +{penetration:.2f} pts"
                        obj.swept_timestamp = timestamp
                    else:
                        target_state = LifecycleState.BREACHED
                        reason = f"BSL breached with marginal penetration +{penetration:.2f} pts"
                        obj.breached_timestamp = timestamp

                    if obj.lifecycle != target_state:
                        event = self._record_transition(obj, target_state, timestamp, prev_p, curr_p, is_gap, reason, source_quote)
                        events.append(event)

                # 2. Touch within tolerance without full penetration
                elif abs(curr_p - lvl) <= self.touch_threshold:
                    if obj.lifecycle != LifecycleState.TOUCHED and obj.lifecycle != LifecycleState.BREACHED:
                        obj.test_count += 1
                        event = self._record_transition(
                            obj, LifecycleState.TOUCHED, timestamp, prev_p, curr_p, is_gap, "Proximity touch observed", source_quote
                        )
                        events.append(event)

                # 3. Approaching within proximity window
                elif curr_p < lvl and (lvl - curr_p) <= self.approach_threshold:
                    if obj.lifecycle == LifecycleState.FRESH:
                        event = self._record_transition(
                            obj, LifecycleState.APPROACHING, timestamp, prev_p, curr_p, is_gap, "Approaching BSL level", source_quote
                        )
                        events.append(event)

            # --- SSL EVALUATION (Level is below historical market) ---
            elif obj.side == "SSL":
                # Check if price was already below level at startup
                if obj.evidence.get("initial_relation") == "PRICE_ALREADY_BELOW" and obj.lifecycle == LifecycleState.FRESH:
                    continue

                # 1. Crossing from above to below or continuation of breach to sweep
                is_crossing = (prev_p > lvl >= curr_p) or (prev_p > lvl and curr_p < lvl)
                is_breach_advancing = (obj.lifecycle == LifecycleState.BREACHED and curr_p < lvl)

                if is_crossing or is_breach_advancing:
                    penetration = lvl - curr_p
                    if penetration > self.sweep_threshold:
                        target_state = LifecycleState.SWEPT
                        reason = f"SSL swept with penetration -{penetration:.2f} pts"
                        obj.swept_timestamp = timestamp
                    else:
                        target_state = LifecycleState.BREACHED
                        reason = f"SSL breached with marginal penetration -{penetration:.2f} pts"
                        obj.breached_timestamp = timestamp

                    if obj.lifecycle != target_state:
                        event = self._record_transition(obj, target_state, timestamp, prev_p, curr_p, is_gap, reason, source_quote)
                        events.append(event)

                # 2. Touch within tolerance
                elif abs(curr_p - lvl) <= self.touch_threshold:
                    if obj.lifecycle != LifecycleState.TOUCHED and obj.lifecycle != LifecycleState.BREACHED:
                        obj.test_count += 1
                        event = self._record_transition(
                            obj, LifecycleState.TOUCHED, timestamp, prev_p, curr_p, is_gap, "Proximity touch observed", source_quote
                        )
                        events.append(event)

                # 3. Approaching
                elif curr_p > lvl and (curr_p - lvl) <= self.approach_threshold:
                    if obj.lifecycle == LifecycleState.FRESH:
                        event = self._record_transition(
                            obj, LifecycleState.APPROACHING, timestamp, prev_p, curr_p, is_gap, "Approaching SSL level", source_quote
                        )
                        events.append(event)

        # Update previous valid price
        self.previous_valid_price = curr_p
        self.last_evaluation_ts = timestamp
        return events

    def _record_transition(
        self,
        obj: LiquidityObject,
        new_state: str,
        timestamp: float,
        prev_p: float,
        curr_p: float,
        is_gap: bool,
        reason: str,
        source_quote: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mutates lifecycle state, ensuring idempotence and recording transition metadata."""
        old_state = obj.lifecycle
        obj.lifecycle = new_state

        event = {
            "object_id": obj.object_id,
            "tier": obj.tier,
            "side": obj.side,
            "price_level": obj.price_level,
            "previous_state": old_state,
            "new_state": new_state,
            "timestamp": timestamp,
            "previous_price": prev_p,
            "current_price": curr_p,
            "is_gap_cross": is_gap,
            "reason": reason,
            "source_quote": source_quote or {},
        }
        self.transition_log.append(event)
        return event
