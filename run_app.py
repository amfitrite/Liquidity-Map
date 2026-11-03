"""Main execution entry point for Liquidity Map."""
import sys
import logging
from liquidity_map.service import LiquidityMapService
from liquidity_map.gui.app import launch_gui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    service = LiquidityMapService()
    try:
        launch_gui(service)
    except KeyboardInterrupt:
        service.stop()
        sys.exit(0)
