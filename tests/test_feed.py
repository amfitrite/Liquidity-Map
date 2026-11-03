"""Tests for Dukascopy feed and momentum calculation."""
import unittest
from liquidity_map.data.dukascopy_feed import DukascopyFeed


class TestDukascopyFeed(unittest.TestCase):
    def setUp(self):
        self.feed = DukascopyFeed(symbol="XAUUSD", price_basis="MID", poll_interval=0.1)

    def test_quote_structure(self):
        quote = self.feed.get_latest_quote()
        self.assertEqual(quote["instrument"], "XAUUSD")
        self.assertEqual(quote["provider"], "DUKASCOPY")
        self.assertIn("bid", quote)
        self.assertIn("ask", quote)
        self.assertIn("mid", quote)
        self.assertIn("spread", quote)
        self.assertIn("momentum", quote)
        self.assertIn(quote["momentum"], ["UP", "DOWN", "NEUTRAL"])

    def test_momentum_dynamics(self):
        # Force a strong upward price series
        base = self.feed.current_mid
        for p in [base + 1.0, base + 2.5, base + 4.0, base + 5.5]:
            self.feed._apply_tick(p - 0.2, p + 0.2, "SIMULATED")

        quote = self.feed.get_latest_quote()
        self.assertEqual(quote["momentum"], "UP")
        self.assertGreater(quote["momentum_score"], 0.15)


if __name__ == "__main__":
    unittest.main()
