"""Liquidity Map v1.0 - Main Launcher for XAUUSD Institutional Game World.
Launches the Google Chrome Frameless GUI with Dukascopy Live Feed & Kinetic Price Compass.
"""
import os
import sys
import logging

# Silence all log output completely (tidak ada log di console/terminal)
logging.disable(logging.CRITICAL)

from liquidity_map.service import LiquidityMapService
from liquidity_map.gui.app import launch_gui


def main():
    service = LiquidityMapService()
    launch_gui(service)


if __name__ == "__main__":
    main()
