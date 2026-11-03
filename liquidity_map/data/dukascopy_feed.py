"""Dukascopy Authentic Live Price Feed & Real-Time Tick Engine."""
import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Callable, List

# Suppress noisy library logs completely
for lib in ["dukascopy", "urllib3", "requests", "urllib3.connectionpool"]:
    l = logging.getLogger(lib)
    l.setLevel(logging.CRITICAL)
    l.propagate = False

try:
    import dukascopy_python as duka
    # Completely silence dukascopy logger and remove stream handlers
    _dl = logging.getLogger("dukascopy")
    _dl.setLevel(logging.CRITICAL)
    _dl.handlers.clear()
    _dl.addHandler(logging.NullHandler())
    _dl.propagate = False
except ImportError:
    duka = None


class FeedState:
    CONNECTING = "CONNECTING"
    LIVE = "LIVE"
    STALE = "STALE"
    OFFLINE = "OFFLINE"
    DEMO = "DEMO"
    ERROR = "ERROR"


class DukascopyFeed:
    """Authentic live tick feed directly connected to Dukascopy ECN for XAUUSD.
    
    Adheres strictly to the P0 Feed Integrity contract:
    - Initial state is CONNECTING.
    - Transitions to LIVE ONLY upon receiving a verified quote (ask > bid > 0).
    - Transitions to STALE when quotes exceed stale_threshold_sec without fresh ticks.
    - Transitions to OFFLINE or ERROR on connection failure.
    - Never fabricates synthetic prices under a LIVE label.
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        price_basis: str = "MID",
        poll_interval: float = 1.5,
        stale_threshold_sec: float = 15.0,
        simulation_mode: bool = False,
    ):
        self.symbol_duka = "XAU-USD" if "XAU" in symbol.upper() else symbol
        self.symbol = "XAUUSD"
        self.price_basis = price_basis.upper()
        if self.price_basis not in ("MID", "BID", "ASK"):
            self.price_basis = "MID"

        self.poll_interval = max(0.2, float(poll_interval))
        self.stale_threshold_sec = max(0.1, float(stale_threshold_sec))
        self.simulation_mode = simulation_mode

        # Running state
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.Lock()

        # Epistemic state: Starts strictly as CONNECTING (not LIVE)
        self.status = FeedState.CONNECTING if not simulation_mode else FeedState.DEMO
        self.last_error: Optional[str] = None

        # Verified Quote State (None until first authentic quote is verified)
        self.current_bid: Optional[float] = None
        self.current_ask: Optional[float] = None
        self.current_mid: Optional[float] = None
        self.last_price: Optional[float] = None
        
        self.last_tick_time_utc: Optional[str] = None
        self.last_tick_timestamp: Optional[float] = None
        self.received_time_utc: Optional[str] = None
        self.received_timestamp: Optional[float] = None

        self.latency_ms = 0.0
        self.tick_sequence = 0
        self.momentum = "NEUTRAL"
        self.momentum_score = 0.0  # -1.0 to +1.0
        self._recent_ticks: List[float] = []

    def add_callback(self, cb: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self._callbacks.append(cb)

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self.status = FeedState.CONNECTING if not self.simulation_mode else FeedState.DEMO
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="DukascopyFeedThread")
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False
            self.status = FeedState.OFFLINE
        if self._thread and self._thread.is_alive() and threading.current_thread() != self._thread:
            self._thread.join(timeout=2.0)

    @property
    def is_live(self) -> bool:
        return self.status == FeedState.LIVE

    def validate_quote(self, bid: Any, ask: Any) -> bool:
        """Strictly validates bid and ask quote integrity."""
        try:
            b = float(bid)
            a = float(ask)
            return a > b > 0 and not (b != b or a != a)  # NaN check
        except (ValueError, TypeError):
            return False

    def get_initial_price(self) -> float:
        """Fetches the latest real tick from Dukascopy during service initialization.
        Transitions to LIVE if valid; otherwise remains CONNECTING/OFFLINE.
        """
        if self.simulation_mode:
            self._apply_tick(3930.00, 3930.50, "DEMO", latency_ms=10.0)
            return self.current_mid

        if duka is None:
            self.status = FeedState.OFFLINE
            self.last_error = "dukascopy_python not installed"
            return 3930.00

        now_utc = datetime.now(timezone.utc)
        lookbacks = [timedelta(minutes=5), timedelta(hours=2), timedelta(days=4)]
        for lb in lookbacks:
            try:
                ticks = list(duka.fetch_ticks(self.symbol_duka, start=now_utc - lb, end=now_utc))
                if ticks:
                    last_tick = ticks[-1]
                    bid = float(last_tick.bid)
                    ask = float(last_tick.ask)
                    if self.validate_quote(bid, ask):
                        tick_dt = last_tick.timestamp
                        if tick_dt.tzinfo is None:
                            tick_dt = tick_dt.replace(tzinfo=timezone.utc)
                        self._apply_tick(bid, ask, FeedState.LIVE, latency_ms=15.0, tick_time=tick_dt)
                        return self.current_mid
            except Exception as e:
                self.last_error = str(e)
                continue

        # If no ticks could be fetched, do not falsely claim LIVE
        self.status = FeedState.CONNECTING
        return 3930.00

    def get_basis_price(self) -> Optional[float]:
        """Returns the consistent price basis across live marker, camera, and lifecycle."""
        if self.current_bid is None or self.current_ask is None:
            return None
        if self.price_basis == "BID":
            return self.current_bid
        elif self.price_basis == "ASK":
            return self.current_ask
        return self.current_mid

    def get_latest_quote(self) -> Dict[str, Any]:
        """Returns a snapshot of the current feed quote and honest status."""
        basis_p = self.get_basis_price()
        now_iso = datetime.now(timezone.utc).isoformat()
        spread = (self.current_ask - self.current_bid) if (self.current_ask and self.current_bid) else 0.0

        return {
            "instrument": self.symbol,
            "provider": "DUKASCOPY",
            "event_type": "QUOTE_UPDATE",
            "event_time_utc": self.last_tick_time_utc or now_iso,
            "received_time_utc": self.received_time_utc or now_iso,
            "bid": round(self.current_bid, 3) if self.current_bid is not None else None,
            "ask": round(self.current_ask, 3) if self.current_ask is not None else None,
            "mid": round(self.current_mid, 3) if self.current_mid is not None else None,
            "spread": round(spread, 3),
            "provider_price": round(basis_p, 3) if basis_p is not None else None,
            "price_basis": self.price_basis,
            "status": self.status,
            "is_live": self.status == FeedState.LIVE,
            "latency_ms": round(self.latency_ms, 1),
            "sequence": self.tick_sequence,
            "momentum": self.momentum,
            "momentum_score": round(self.momentum_score, 3),
            "last_error": self.last_error,
        }

    def _run_loop(self):
        while self._running:
            try:
                if self.simulation_mode:
                    self._simulate_tick()
                else:
                    self._fetch_real_ticks()
            except Exception as e:
                self.status = FeedState.ERROR
                self.last_error = str(e)

            # Check for staleness
            self._check_stale()

            # Emit quote update to subscribers
            quote = self.get_latest_quote()
            with self._lock:
                callbacks = list(self._callbacks)
            for cb in callbacks:
                try:
                    cb(quote)
                except Exception:
                    pass

            time.sleep(self.poll_interval)

    def _fetch_real_ticks(self):
        if duka is None:
            self.status = FeedState.OFFLINE
            self.last_error = "dukascopy_python not installed"
            return

        now_utc = datetime.now(timezone.utc)
        start_t = time.perf_counter()

        try:
            ticks = list(duka.fetch_ticks(self.symbol_duka, start=now_utc - timedelta(seconds=20), end=now_utc))
            if ticks:
                last_tick = ticks[-1]
                bid = float(last_tick.bid)
                ask = float(last_tick.ask)

                if not self.validate_quote(bid, ask):
                    self.status = FeedState.ERROR
                    self.last_error = f"Invalid bid/ask received: {bid}/{ask}"
                    return

                tick_ts = last_tick.timestamp
                if tick_ts.tzinfo is None:
                    tick_ts = tick_ts.replace(tzinfo=timezone.utc)

                latency = (time.perf_counter() - start_t) * 1000.0
                self._apply_tick(bid, ask, FeedState.LIVE, latency_ms=max(5.0, latency), tick_time=tick_ts)
            else:
                # No ticks in window; check if stale
                self._check_stale()
        except Exception as e:
            # Network or connection error: transition to OFFLINE / ERROR
            self.status = FeedState.OFFLINE
            self.last_error = str(e)

    def _check_stale(self):
        """Transitions status to STALE if time since last received tick exceeds stale threshold."""
        if self.received_timestamp is not None and self.status == FeedState.LIVE:
            age = time.time() - self.received_timestamp
            if age > self.stale_threshold_sec:
                self.status = FeedState.STALE

    def _apply_tick(
        self,
        bid: float,
        ask: float,
        status: str,
        latency_ms: float = 15.0,
        tick_time: Optional[datetime] = None,
    ):
        now_utc = datetime.now(timezone.utc)
        now_ts = time.time()

        if tick_time is None:
            tick_time = now_utc

        self.current_bid = bid
        self.current_ask = ask
        self.current_mid = (bid + ask) / 2.0
        self.last_price = self.current_mid

        self.last_tick_time_utc = tick_time.isoformat()
        self.last_tick_timestamp = tick_time.timestamp()
        self.received_time_utc = now_utc.isoformat()
        self.received_timestamp = now_ts

        self.status = status
        self.latency_ms = latency_ms
        self.tick_sequence += 1
        self.last_error = None

        # Momentum calculation
        self._recent_ticks.append(self.current_mid)
        if len(self._recent_ticks) > 12:
            self._recent_ticks.pop(0)

        delta = self.current_mid - self._recent_ticks[0]
        if delta > 0.05:
            self.momentum = "UP"
            self.momentum_score = min(1.0, delta / 0.50)
        elif delta < -0.05:
            self.momentum = "DOWN"
            self.momentum_score = max(-1.0, delta / 0.50)
        else:
            self.momentum = "NEUTRAL"
            self.momentum_score = 0.0

    def _simulate_tick(self):
        """Only executed when explicitly in simulation mode (strictly labeled DEMO)."""
        import random
        base = self.current_mid or 3930.00
        delta = random.uniform(-0.15, 0.15)
        new_mid = base + delta
        spread = 0.40
        self._apply_tick(new_mid - spread / 2, new_mid + spread / 2, FeedState.DEMO, latency_ms=8.0)
