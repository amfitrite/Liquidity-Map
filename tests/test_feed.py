"""Unit tests for Dukascopy feed state machine, validation, and stale detection."""
import unittest
import time
from datetime import datetime, timezone
from liquidity_map.data.dukascopy_feed import DukascopyFeed, FeedState


class TestDukascopyFeedIntegrity(unittest.TestCase):
    def test_initial_state_not_live(self):
        """Rule: Initial state must be CONNECTING or OFFLINE, never prematurely LIVE."""
        feed = DukascopyFeed(symbol="XAUUSD", poll_interval=1.0)
        self.assertIn(feed.status, [FeedState.CONNECTING, FeedState.OFFLINE])
        self.assertFalse(feed.is_live)

    def test_valid_quote_transitions_to_live(self):
        """Rule: Status LIVE only granted upon receiving valid authentic quote (ask > bid > 0)."""
        feed = DukascopyFeed(symbol="XAUUSD", poll_interval=1.0)
        feed._apply_tick(bid=3932.10, ask=3932.60, status=FeedState.LIVE)
        
        self.assertEqual(feed.status, FeedState.LIVE)
        self.assertTrue(feed.is_live)
        quote = feed.get_latest_quote()
        self.assertEqual(quote["bid"], 3932.10)
        self.assertEqual(quote["ask"], 3932.60)
        self.assertEqual(quote["mid"], 3932.35)
        self.assertEqual(quote["spread"], 0.50)
        self.assertEqual(quote["provider_price"], 3932.35)

    def test_stale_detection(self):
        """Rule: If quote age exceeds stale threshold, status transitions to STALE."""
        feed = DukascopyFeed(symbol="XAUUSD", stale_threshold_sec=0.2)
        feed._apply_tick(bid=3932.10, ask=3932.60, status=FeedState.LIVE)
        self.assertEqual(feed.status, FeedState.LIVE)

        # Wait past stale threshold
        time.sleep(0.35)
        feed._check_stale()
        self.assertEqual(feed.status, FeedState.STALE)
        self.assertFalse(feed.is_live)

    def test_quote_validation_rules(self):
        """Rule: Reject non-positive bid, crossed spread (ask <= bid), and malformed types."""
        feed = DukascopyFeed()
        self.assertTrue(feed.validate_quote(3930.0, 3930.5))
        self.assertFalse(feed.validate_quote(3930.5, 3930.0))  # Crossed
        self.assertFalse(feed.validate_quote(3930.0, 3930.0))  # Zero spread
        self.assertFalse(feed.validate_quote(-10.0, 3930.0))   # Negative bid
        self.assertFalse(feed.validate_quote("invalid", 3930.0))
        self.assertFalse(feed.validate_quote(float("nan"), 3930.0))

    def test_demo_fallback_never_labelled_live(self):
        """Rule: Synthetic simulation fallback is strictly DEMO, never masquerading as LIVE."""
        feed = DukascopyFeed(simulation_mode=True)
        self.assertEqual(feed.status, FeedState.DEMO)
        feed._simulate_tick()
        self.assertEqual(feed.status, FeedState.DEMO)
        quote = feed.get_latest_quote()
        self.assertEqual(quote["status"], FeedState.DEMO)
        self.assertFalse(quote["is_live"])

    def test_offline_on_stop(self):
        """Rule: Explicit stop or disconnect sets status to OFFLINE."""
        feed = DukascopyFeed()
        feed._apply_tick(bid=3932.10, ask=3932.60, status=FeedState.LIVE)
        self.assertEqual(feed.status, FeedState.LIVE)
        feed.stop()
        self.assertEqual(feed.status, FeedState.OFFLINE)
        self.assertFalse(feed.is_live)

    def test_price_basis_consistency(self):
        """Rule: Selected price basis (MID, BID, ASK) is mathematically consistent."""
        feed_mid = DukascopyFeed(price_basis="MID")
        feed_mid._apply_tick(bid=3930.00, ask=3931.00, status=FeedState.LIVE)
        self.assertEqual(feed_mid.get_basis_price(), 3930.50)

        feed_bid = DukascopyFeed(price_basis="BID")
        feed_bid._apply_tick(bid=3930.00, ask=3931.00, status=FeedState.LIVE)
        self.assertEqual(feed_bid.get_basis_price(), 3930.00)

        feed_ask = DukascopyFeed(price_basis="ASK")
        feed_ask._apply_tick(bid=3930.00, ask=3931.00, status=FeedState.LIVE)
        self.assertEqual(feed_ask.get_basis_price(), 3931.00)

    def test_momentum_dynamics(self):
        """Rule: Directional price moves calculate consistent momentum without bias."""
        feed = DukascopyFeed()
        base = 3930.00
        # Upward price progression
        for step in [0.5, 1.2, 2.0, 3.0]:
            p = base + step
            feed._apply_tick(p - 0.2, p + 0.2, FeedState.LIVE)

        quote = feed.get_latest_quote()
        self.assertEqual(quote["momentum"], "UP")
        self.assertGreater(quote["momentum_score"], 0.2)


if __name__ == "__main__":
    unittest.main()
