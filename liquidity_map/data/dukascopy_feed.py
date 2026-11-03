"""Dukascopy Live Price Feed & Real-Time Tick Engine."""
import time
import math
import random
import logging
import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable, List
import requests

logger = logging.getLogger("LiquidityMap.Feed")


class DukascopyFeed:
    """Live tick feed adapter for Dukascopy XAUUSD quotes with simulation fallback."""

    def __init__(self, symbol: str = "XAUUSD", price_basis: str = "MID", poll_interval: float = 0.5):
        self.symbol = symbol.upper()
        self.price_basis = price_basis.upper()
        self.poll_interval = poll_interval

        # Running state
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Current Price State
        self.current_bid = 2748.20
        self.current_ask = 2748.55
        self.current_mid = (self.current_bid + self.current_ask) / 2.0
        self.last_price = self.current_mid
        self.last_update_utc = datetime.now(timezone.utc).isoformat()
        self.status = "INITIALIZING"
        self.latency_ms = 12.0
        self.tick_sequence = 0
        self.momentum = "NEUTRAL"
        self.momentum_score = 0.0  # -1.0 to +1.0
        self._recent_ticks: List[float] = [self.current_mid]

    def add_callback(self, cb: Callable[[Dict[str, Any]], None]):
        self._callbacks.append(cb)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="DukascopyFeedThread")
        self._thread.start()
        logger.info("DukascopyFeed started for %s (Basis: %s)", self.symbol, self.price_basis)

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("DukascopyFeed stopped.")

    def get_latest_quote(self) -> Dict[str, Any]:
        return {
            "instrument": self.symbol,
            "provider": "DUKASCOPY",
            "event_type": "QUOTE_UPDATE",
            "event_time_utc": self.last_update_utc,
            "received_time_utc": datetime.now(timezone.utc).isoformat(),
            "bid": round(self.current_bid, 2),
            "ask": round(self.current_ask, 2),
            "mid": round(self.current_mid, 2),
            "spread": round(self.current_ask - self.current_bid, 2),
            "provider_price": round(self._get_basis_price(), 2),
            "price_basis": self.price_basis,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 1),
            "sequence": self.tick_sequence,
            "momentum": self.momentum,
            "momentum_score": round(self.momentum_score, 3),
        }

    def _get_basis_price(self) -> float:
        if self.price_basis == "BID":
            return self.current_bid
        elif self.price_basis == "ASK":
            return self.current_ask
        return self.current_mid

    def _run_loop(self):
        while self._running:
            success = self._fetch_live_dukascopy()
            if not success:
                self._simulate_tick()

            # Emit quote update
            quote = self.get_latest_quote()
            for cb in self._callbacks:
                try:
                    cb(quote)
                except Exception as err:
                    logger.debug("Error in feed callback: %s", err)

            time.sleep(self.poll_interval)

    def _fetch_live_dukascopy(self) -> bool:
        """Attempt to fetch live quote from public Dukascopy widget endpoint."""
        try:
            start_t = time.perf_counter()
            url = f"https://freeserv.dukascopy.com/2.0/index.php?path=chart/json&instrument={self.symbol}&offer_side=B&interval=1SEC&points=1"
            res = requests.get(url, timeout=1.8, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            if res.status_code == 200 and len(res.content) > 10:
                data = res.json()
                if isinstance(data, list) and len(data) > 0 and len(data[-1]) >= 2:
                    last_point = data[-1]
                    price = float(last_point[1])
                    if 1500.0 <= price <= 4000.0:
                        spread = 0.35 + random.uniform(0.05, 0.15)
                        self._apply_tick(price - (spread / 2.0), price + (spread / 2.0), "LIVE")
                        self.latency_ms = (time.perf_counter() - start_t) * 1000.0
                        return True
        except Exception:
            pass
        return False

    def _simulate_tick(self):
        """Micro-step simulation engine when live market is closed or offline."""
        # Mean reverting random walk with micro jumps
        mean_price = 2748.50
        drift = (mean_price - self.current_mid) * 0.005
        vol = 0.25
        shock = random.gauss(0, vol)
        jump = 0.0
        if random.random() < 0.05:
            jump = random.choice([-0.8, 0.8])

        new_mid = self.current_mid + drift + shock + jump
        spread = 0.30 + random.uniform(0.02, 0.12)

        self._apply_tick(new_mid - (spread / 2.0), new_mid + (spread / 2.0), "SIMULATED")
        self.latency_ms = random.uniform(8.0, 15.0)

    def _apply_tick(self, bid: float, ask: float, status: str):
        prev_price = self.current_mid
        self.current_bid = bid
        self.current_ask = ask
        self.current_mid = (bid + ask) / 2.0
        self.last_update_utc = datetime.now(timezone.utc).isoformat()
        self.status = status
        self.tick_sequence += 1

        # Track rolling momentum
        self._recent_ticks.append(self.current_mid)
        if len(self._recent_ticks) > 10:
            self._recent_ticks.pop(0)

        delta = self.current_mid - self._recent_ticks[0]
        # Normalize momentum score between -1.0 and +1.0
        self.momentum_score = math.tanh(delta / 0.8)

        if self.momentum_score > 0.15:
            self.momentum = "UP"
        elif self.momentum_score < -0.15:
            self.momentum = "DOWN"
        else:
            self.momentum = "NEUTRAL"
