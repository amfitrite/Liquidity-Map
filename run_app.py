"""Main execution entry point for Liquidity Map."""
import os
import sys
import logging

logging.disable(logging.CRITICAL)

from liquidity_map.service import LiquidityMapService
from liquidity_map.gui.app import launch_gui

if __name__ == "__main__":
    service = LiquidityMapService()
    try:
        launch_gui(service)
    except KeyboardInterrupt:
        service.stop()
        sys.exit(0)
