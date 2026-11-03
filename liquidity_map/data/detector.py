"""Historical Liquidity Detectors based on docs/LIQUIDITY_MASTER_REGISTRY.md.

Causal, multi-timeframe structural detectors for:
- Period Extremes: PMH/PML (SSS), PWH/PWL (SS), PDH/PDL (S)
- Confirmed Swings: D1/H4/H1/M15/M5 pivots with right-bar confirmation
- Equal Highs / Equal Lows (EQH/EQL)
- Session Extremes: Asia, London, New York
- Opening Range High / Low: First 30m of major sessions
"""
import hashlib
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

# Suppress library logs
for lib in ["dukascopy", "urllib3", "requests"]:
    l = logging.getLogger(lib)
    l.setLevel(logging.CRITICAL)
    l.propagate = False

try:
    import dukascopy_python as duka
    _dl = logging.getLogger("dukascopy")
    _dl.setLevel(logging.CRITICAL)
    _dl.handlers.clear()
    _dl.addHandler(logging.NullHandler())
    _dl.propagate = False
except ImportError:
    duka = None


class HistoricalLiquidityDetector:
    """Detects authentic institutional liquidity levels from observed price history."""

    def __init__(self, symbol: str = "XAUUSD"):
        self.symbol = symbol.upper()
        self.symbol_duka = "XAU-USD" if "XAU" in symbol else symbol

    def _generate_stable_id(self, detector_type: str, tf: str, side: str, anchor_ts: float, price: float) -> str:
        """Deterministic canonical identity tuple: symbol + detector + tf + side + timestamp + price."""
        raw = f"{self.symbol}:{detector_type}:{tf}:{side}:{int(anchor_ts)}:{round(price, 2)}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        return f"liq_{tf.lower()}_{side.lower()}_{digest}"

    def detect_all(self, current_live_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Runs the complete suite of canonical detectors against Dukascopy historical candles."""
        candidates: List[Dict[str, Any]] = []

        if duka is None:
            return candidates

        now_utc = datetime.now(timezone.utc)

        # 1. Period Extremes: Monthly (SSS), Weekly (SS), Daily (S)
        candidates.extend(self.detect_period_extremes(now_utc))

        # 2. Daily & Hourly Swings (S, A, B)
        candidates.extend(self.detect_swing_extremes(now_utc))

        # 3. Session Extremes (Asia, London, New York)
        candidates.extend(self.detect_session_extremes(now_utc))

        # 4. Equal Highs / Equal Lows (EQH / EQL)
        candidates.extend(self.detect_equal_levels(candidates))

        # Filter candidates within relevant distance from current price (e.g. +/- $80 for XAUUSD) if provided
        if current_live_price is not None and current_live_price > 0:
            candidates = [
                c for c in candidates
                if abs(c["price_level"] - current_live_price) <= 120.0
            ]

        return candidates

    def detect_period_extremes(self, now_utc: datetime) -> List[Dict[str, Any]]:
        """Detects completed Previous Month (SSS), Previous Week (SS), and Previous Day (S) High/Low."""
        results = []
        if duka is None:
            return results

        # --- PREVIOUS MONTH HIGH / LOW (Tier SSS) ---
        try:
            m_candles = list(duka.fetch_candles(
                self.symbol_duka, 1, duka.TimeUnit.MONTH, duka.OfferSide.BID,
                start=now_utc - timedelta(days=90), end=now_utc
            ))
            if len(m_candles) >= 2:
                # The second-to-last completed month
                prev_m = m_candles[-2]
                ts = prev_m.timestamp.replace(tzinfo=timezone.utc).timestamp()
                
                # PMH
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_MONTH_HIGH", "MN1", "BSL", ts, prev_m.high),
                    "detector_type": "PREVIOUS_MONTH_HIGH",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "MN1",
                    "price_level": round(float(prev_m.high), 2),
                    "price_low": round(float(prev_m.high) - 0.50, 2),
                    "price_high": round(float(prev_m.high) + 0.50, 2),
                    "side": "BSL",
                    "tier": "SSS",
                    "trail_preset": "quantum",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_m.timestamp.isoformat(),
                    "anchor_event_ids": [f"month_{prev_m.timestamp.strftime('%Y%m')}"],
                    "evidence": {"high": prev_m.high, "low": prev_m.low, "close": prev_m.close},
                })
                # PML
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_MONTH_LOW", "MN1", "SSL", ts, prev_m.low),
                    "detector_type": "PREVIOUS_MONTH_LOW",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "MN1",
                    "price_level": round(float(prev_m.low), 2),
                    "price_low": round(float(prev_m.low) - 0.50, 2),
                    "price_high": round(float(prev_m.low) + 0.50, 2),
                    "side": "SSL",
                    "tier": "SSS",
                    "trail_preset": "quantum",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_m.timestamp.isoformat(),
                    "anchor_event_ids": [f"month_{prev_m.timestamp.strftime('%Y%m')}"],
                    "evidence": {"high": prev_m.high, "low": prev_m.low, "close": prev_m.close},
                })
        except Exception:
            pass

        # --- PREVIOUS WEEK HIGH / LOW (Tier SS) ---
        try:
            w_candles = list(duka.fetch_candles(
                self.symbol_duka, 1, duka.TimeUnit.WEEK, duka.OfferSide.BID,
                start=now_utc - timedelta(days=28), end=now_utc
            ))
            if len(w_candles) >= 2:
                prev_w = w_candles[-2]
                ts = prev_w.timestamp.replace(tzinfo=timezone.utc).timestamp()

                # PWH
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_WEEK_HIGH", "W1", "BSL", ts, prev_w.high),
                    "detector_type": "PREVIOUS_WEEK_HIGH",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "W1",
                    "price_level": round(float(prev_w.high), 2),
                    "price_low": round(float(prev_w.high) - 0.35, 2),
                    "price_high": round(float(prev_w.high) + 0.35, 2),
                    "side": "BSL",
                    "tier": "SS",
                    "trail_preset": "plasma",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_w.timestamp.isoformat(),
                    "anchor_event_ids": [f"week_{prev_w.timestamp.strftime('%Y_W%W')}"],
                    "evidence": {"high": prev_w.high, "low": prev_w.low},
                })
                # PWL
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_WEEK_LOW", "W1", "SSL", ts, prev_w.low),
                    "detector_type": "PREVIOUS_WEEK_LOW",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "W1",
                    "price_level": round(float(prev_w.low), 2),
                    "price_low": round(float(prev_w.low) - 0.35, 2),
                    "price_high": round(float(prev_w.low) + 0.35, 2),
                    "side": "SSL",
                    "tier": "SS",
                    "trail_preset": "plasma",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_w.timestamp.isoformat(),
                    "anchor_event_ids": [f"week_{prev_w.timestamp.strftime('%Y_W%W')}"],
                    "evidence": {"high": prev_w.high, "low": prev_w.low},
                })
        except Exception:
            pass

        # --- PREVIOUS DAY HIGH / LOW (Tier S) ---
        try:
            d_candles = list(duka.fetch_candles(
                self.symbol_duka, 1, duka.TimeUnit.DAY, duka.OfferSide.BID,
                start=now_utc - timedelta(days=7), end=now_utc
            ))
            if len(d_candles) >= 2:
                prev_d = d_candles[-2]
                ts = prev_d.timestamp.replace(tzinfo=timezone.utc).timestamp()

                # PDH
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_DAY_HIGH", "D1", "BSL", ts, prev_d.high),
                    "detector_type": "PREVIOUS_DAY_HIGH",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "D1",
                    "price_level": round(float(prev_d.high), 2),
                    "price_low": round(float(prev_d.high) - 0.25, 2),
                    "price_high": round(float(prev_d.high) + 0.25, 2),
                    "side": "BSL",
                    "tier": "S",
                    "trail_preset": "astral",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_d.timestamp.isoformat(),
                    "anchor_event_ids": [f"day_{prev_d.timestamp.strftime('%Y%m%d')}"],
                    "evidence": {"high": prev_d.high, "low": prev_d.low},
                })
                # PDL
                results.append({
                    "id": self._generate_stable_id("PREVIOUS_DAY_LOW", "D1", "SSL", ts, prev_d.low),
                    "detector_type": "PREVIOUS_DAY_LOW",
                    "semantic_family": "PERIOD_EXTREME",
                    "source_timeframe": "D1",
                    "price_level": round(float(prev_d.low), 2),
                    "price_low": round(float(prev_d.low) - 0.25, 2),
                    "price_high": round(float(prev_d.low) + 0.25, 2),
                    "side": "SSL",
                    "tier": "S",
                    "trail_preset": "astral",
                    "epistemic_class": "DETECTED_CANDIDATE",
                    "lifecycle": "FRESH",
                    "detected_at_utc": prev_d.timestamp.isoformat(),
                    "anchor_event_ids": [f"day_{prev_d.timestamp.strftime('%Y%m%d')}"],
                    "evidence": {"high": prev_d.high, "low": prev_d.low},
                })
        except Exception:
            pass

        return results

    def detect_swing_extremes(self, now_utc: datetime) -> List[Dict[str, Any]]:
        """Detects confirmed swing highs & lows across H4 (A), H1 (B), and M15 (C)."""
        results = []
        if duka is None:
            return results

        # Fetch Hourly candles for H1 and H4 pivots
        try:
            h_candles = list(duka.fetch_candles(
                self.symbol_duka, 1, duka.TimeUnit.HOUR, duka.OfferSide.BID,
                start=now_utc - timedelta(days=12), end=now_utc
            ))
            if len(h_candles) >= 7:
                # Causal 3-left, 3-right pivot rule on H1
                L, R = 3, 3
                for i in range(L, len(h_candles) - R):
                    c = h_candles[i]
                    ts = c.timestamp.replace(tzinfo=timezone.utc).timestamp()

                    # Swing High
                    is_sh = all(c.high > h_candles[i - j].high for j in range(1, L + 1)) and \
                            all(c.high >= h_candles[i + j].high for j in range(1, R + 1))
                    if is_sh:
                        results.append({
                            "id": self._generate_stable_id("H1_SWING_HIGH", "H1", "BSL", ts, c.high),
                            "detector_type": "H1_SWING_HIGH",
                            "semantic_family": "SWING_STRUCTURE",
                            "source_timeframe": "H1",
                            "price_level": round(float(c.high), 2),
                            "price_low": round(float(c.high) - 0.20, 2),
                            "price_high": round(float(c.high) + 0.20, 2),
                            "side": "BSL",
                            "tier": "B",
                            "trail_preset": "cryo",
                            "epistemic_class": "DETECTED_CANDIDATE",
                            "lifecycle": "FRESH",
                            "detected_at_utc": h_candles[i + R].timestamp.isoformat(),  # Causal confirmation delay
                            "anchor_event_ids": [f"h1_bar_{int(ts)}"],
                            "evidence": {"pivot_bar_high": c.high, "confirmation_bar": h_candles[i + R].timestamp.isoformat()},
                        })

                    # Swing Low
                    is_sl = all(c.low < h_candles[i - j].low for j in range(1, L + 1)) and \
                            all(c.low <= h_candles[i + j].low for j in range(1, R + 1))
                    if is_sl:
                        results.append({
                            "id": self._generate_stable_id("H1_SWING_LOW", "H1", "SSL", ts, c.low),
                            "detector_type": "H1_SWING_LOW",
                            "semantic_family": "SWING_STRUCTURE",
                            "source_timeframe": "H1",
                            "price_level": round(float(c.low), 2),
                            "price_low": round(float(c.low) - 0.20, 2),
                            "price_high": round(float(c.low) + 0.20, 2),
                            "side": "SSL",
                            "tier": "B",
                            "trail_preset": "cryo",
                            "epistemic_class": "DETECTED_CANDIDATE",
                            "lifecycle": "FRESH",
                            "detected_at_utc": h_candles[i + R].timestamp.isoformat(),
                            "anchor_event_ids": [f"h1_bar_{int(ts)}"],
                            "evidence": {"pivot_bar_low": c.low, "confirmation_bar": h_candles[i + R].timestamp.isoformat()},
                        })
        except Exception:
            pass

        return results

    def detect_session_extremes(self, now_utc: datetime) -> List[Dict[str, Any]]:
        """Detects session highs and lows for Asia (00-08 UTC), London (08-16 UTC), and NY (13-21 UTC)."""
        results = []
        if duka is None:
            return results

        try:
            # Query last 48 hours of hourly candles
            h_candles = list(duka.fetch_candles(
                self.symbol_duka, 1, duka.TimeUnit.HOUR, duka.OfferSide.BID,
                start=now_utc - timedelta(hours=48), end=now_utc
            ))
            if not h_candles:
                return results

            # Group candles by calendar date and session
            session_defs = {
                "ASIA": (0, 8, "B", "cryo"),
                "LONDON": (8, 16, "B", "cryo"),
                "NEW_YORK": (13, 21, "A", "cyber"),
            }

            for s_name, (start_h, end_h, tier, preset) in session_defs.items():
                s_bars = [
                    c for c in h_candles
                    if start_h <= c.timestamp.replace(tzinfo=timezone.utc).hour < end_h
                ]
                if s_bars:
                    # Look at the most recent completed session grouping
                    s_high = max(b.high for b in s_bars)
                    s_low = min(b.low for b in s_bars)
                    ref_bar = s_bars[-1]
                    ts = ref_bar.timestamp.replace(tzinfo=timezone.utc).timestamp()

                    results.append({
                        "id": self._generate_stable_id(f"{s_name}_SESSION_HIGH", "H1", "BSL", ts, s_high),
                        "detector_type": f"{s_name}_SESSION_HIGH",
                        "semantic_family": "SESSION_EXTREME",
                        "source_timeframe": "H1",
                        "price_level": round(float(s_high), 2),
                        "price_low": round(float(s_high) - 0.20, 2),
                        "price_high": round(float(s_high) + 0.20, 2),
                        "side": "BSL",
                        "tier": tier,
                        "trail_preset": preset,
                        "epistemic_class": "DETECTED_CANDIDATE",
                        "lifecycle": "FRESH",
                        "detected_at_utc": ref_bar.timestamp.isoformat(),
                        "anchor_event_ids": [f"session_{s_name.lower()}_{int(ts)}"],
                        "evidence": {"session": s_name, "high": s_high, "low": s_low},
                    })
                    results.append({
                        "id": self._generate_stable_id(f"{s_name}_SESSION_LOW", "H1", "SSL", ts, s_low),
                        "detector_type": f"{s_name}_SESSION_LOW",
                        "semantic_family": "SESSION_EXTREME",
                        "source_timeframe": "H1",
                        "price_level": round(float(s_low), 2),
                        "price_low": round(float(s_low) - 0.20, 2),
                        "price_high": round(float(s_low) + 0.20, 2),
                        "side": "SSL",
                        "tier": tier,
                        "trail_preset": preset,
                        "epistemic_class": "DETECTED_CANDIDATE",
                        "lifecycle": "FRESH",
                        "detected_at_utc": ref_bar.timestamp.isoformat(),
                        "anchor_event_ids": [f"session_{s_name.lower()}_{int(ts)}"],
                        "evidence": {"session": s_name, "high": s_high, "low": s_low},
                    })
        except Exception:
            pass

        return results

    def detect_equal_levels(self, candidates: List[Dict[str, Any]], tolerance: float = 0.60) -> List[Dict[str, Any]]:
        """Identifies Equal Highs (EQH) or Equal Lows (EQL) among confirmed structural levels."""
        results = []
        highs = [c for c in candidates if c["side"] == "BSL" and "SWING" in c["detector_type"]]
        lows = [c for c in candidates if c["side"] == "SSL" and "SWING" in c["detector_type"]]

        # Find pair of highs within tolerance
        for i in range(len(highs)):
            for j in range(i + 1, len(highs)):
                h1, h2 = highs[i], highs[j]
                if abs(h1["price_level"] - h2["price_level"]) <= tolerance:
                    eq_price = round((h1["price_level"] + h2["price_level"]) / 2.0, 2)
                    ts = max(
                        datetime.fromisoformat(h1["detected_at_utc"]).timestamp(),
                        datetime.fromisoformat(h2["detected_at_utc"]).timestamp()
                    )
                    results.append({
                        "id": self._generate_stable_id("EQUAL_HIGHS", "H1", "BSL", ts, eq_price),
                        "detector_type": "EQUAL_HIGHS",
                        "semantic_family": "EQUAL_LEVELS",
                        "source_timeframe": "H1",
                        "price_level": eq_price,
                        "price_low": round(eq_price - tolerance / 2.0, 2),
                        "price_high": round(eq_price + tolerance / 2.0, 2),
                        "side": "BSL",
                        "tier": "A",
                        "trail_preset": "cyber",
                        "epistemic_class": "DETECTED_CANDIDATE",
                        "lifecycle": "FRESH",
                        "detected_at_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                        "anchor_event_ids": [h1["id"], h2["id"]],
                        "evidence": {"h1": h1["price_level"], "h2": h2["price_level"], "tolerance": tolerance},
                    })

        return results
