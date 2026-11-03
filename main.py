"""Liquidity Map v1.0 - Main Launcher for XAUUSD Institutional Game World.
Launches the Google Chrome Frameless GUI with Dukascopy Live Feed & Kinetic Price Compass.
"""
import sys
import logging
from liquidity_map.service import LiquidityMapService
from liquidity_map.gui.app import launch_gui

# Set up clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    service = LiquidityMapService()
    launch_gui(service)


if __name__ == "__main__":
    main()
