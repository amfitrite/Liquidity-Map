"""Configuration module for Liquidity Map."""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class TierStyleConfig:
    name: str
    timeframe: str
    core_color: str
    trail_color: str
    nominal_size: int
    signature: str


DEFAULT_TIER_CONFIGS: Dict[str, TierStyleConfig] = {
    "SSS": TierStyleConfig(
        name="Golden Sovereign",
        timeframe="MN1",
        core_color="#D6A332",
        trail_color="#FFFFFF",
        nominal_size=36,
        signature="Imperial Crown, Triple Celestial Orbit, Diamond Inset",
    ),
    "SS": TierStyleConfig(
        name="Crimson Dynast",
        timeframe="W1",
        core_color="#C02645",
        trail_color="#FF303B",
        nominal_size=31,
        signature="Subordinate Coronet, Ceremonial Orbit, Marquise Ruby",
    ),
    "S": TierStyleConfig(
        name="Sapphire Duke",
        timeframe="D1",
        core_color="#7251C8",
        trail_color="#FF7900",
        nominal_size=26,
        signature="Heraldic Shield Cut, Dual Crescent Half-Orbits, Sapphire Inset",
    ),
    "A": TierStyleConfig(
        name="Azure Knight",
        timeframe="H4",
        core_color="#1D4ED8",
        trail_color="#FFD52A",
        nominal_size=21,
        signature="Armored Prism, Disciplined Circular Steel Halo",
    ),
    "B": TierStyleConfig(
        name="Jade Merchant",
        timeframe="H1",
        core_color="#16866B",
        trail_color="#73E6FF",
        nominal_size=17,
        signature="Polished Jade Bead, Guild Trade Seal, Simple Halo",
    ),
    "C": TierStyleConfig(
        name="Iron Crafter",
        timeframe="M15",
        core_color="#64748B",
        trail_color="#2787E5",
        nominal_size=13,
        signature="Forged Iron Slag, Worn Chisel Facets, No Orbit/Gem",
    ),
    "D": TierStyleConfig(
        name="Earthen Peasant",
        timeframe="M5",
        core_color="#9A7658",
        trail_color="#092B68",
        nominal_size=10,
        signature="Handmade Clay Nodule, Organic Asymmetry, Zero Ornament",
    ),
}


@dataclass
class AppConfig:
    # Server & GUI Host
    host: str = "127.0.0.1"
    port: int = 8055
    debug: bool = False

    # Instrument & Feed
    symbol: str = "XAUUSD"
    price_basis: str = "MID"  # MID, BID, or ASK
    feed_poll_interval: float = 1.5  # seconds
    simulation_mode: bool = False  # Strictly authentic Dukascopy live feed (no demo)

    # Rendering & World Camera Defaults
    max_visible_objects: int = 120
    default_pixels_per_second: float = 8.0
    default_pixels_per_price: float = 40.0
    dissipation_exponent: float = 1.8

    # Tiers Mapping
    tiers: Dict[str, TierStyleConfig] = field(default_factory=lambda: DEFAULT_TIER_CONFIGS)
