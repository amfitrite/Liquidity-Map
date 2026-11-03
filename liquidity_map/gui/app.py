"""Google Chrome Frameless GUI Application for Liquidity Map (pywebview)."""
import ctypes
import json
import logging
from pathlib import Path
import sys
import time
from typing import Optional
import webview

from liquidity_map.service import LiquidityMapService
from liquidity_map.config import AppConfig

logger = logging.getLogger("LiquidityMap.GUI")

if sys.platform == "win32":
    try:
        myappid = "LiquidityMap.Institutional.World.v1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        logger.debug(f"Could not set AppUserModelID: {e}")


class ChromeWindowAPI:
    """JS API bridge exposed to the pywebview frontend."""

    def __init__(self, service: LiquidityMapService):
        self._service = service
        self._window: Optional[webview.Window] = None

    def set_window(self, window: webview.Window):
        self._window = window

    # --- Frameless Window Controls ---
    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def toggle_maximize(self):
        if self._window:
            try:
                self._window.maximize()
            except Exception:
                pass

    def close_window(self):
        if self._window:
            self._window.destroy()

    # --- Game World State & Controls ---
    def get_world_state(self, viewport_w: float = 1400.0, viewport_h: float = 800.0) -> str:
        """Returns the complete world snapshot for canvas rendering."""
        try:
            w = float(viewport_w) if viewport_w else 1400.0
            h = float(viewport_h) if viewport_h else 800.0
            state = self._service.get_world_snapshot(w, h)
            return json.dumps(state)
        except Exception as e:
            logger.error(f"get_world_state failed: {e}")
            return json.dumps({"error": str(e)})

    def get_quote(self) -> str:
        """Fetches the latest real-time tick and momentum quote."""
        try:
            quote = self._service.feed.get_latest_quote()
            return json.dumps(quote)
        except Exception as e:
            logger.error(f"get_quote failed: {e}")
            return json.dumps({"error": str(e)})

    def set_camera_mode(self, mode: str) -> str:
        """Updates camera mode (FOLLOW or FREE_PAN)."""
        try:
            self._service.camera.mode = mode.upper()
            return json.dumps({"status": "ok", "mode": self._service.camera.mode})
        except Exception as e:
            logger.error(f"set_camera_mode failed: {e}")
            return json.dumps({"error": str(e)})

    def set_camera_zoom(self, time_scale: float, price_scale: float) -> str:
        """Updates camera zoom levels for time and price dimensions."""
        try:
            self._service.camera.pixels_per_second = max(1.0, min(60.0, float(time_scale)))
            self._service.camera.pixels_per_price = max(5.0, min(250.0, float(price_scale)))
            return json.dumps({
                "status": "ok",
                "pixels_per_second": self._service.camera.pixels_per_second,
                "pixels_per_price": self._service.camera.pixels_per_price,
            })
        except Exception as e:
            logger.error(f"set_camera_zoom failed: {e}")
            return json.dumps({"error": str(e)})

    def toggle_live_feed(self, enabled: bool) -> str:
        """Toggles real-time streaming feed."""
        try:
            if enabled:
                self._service.start()
            else:
                self._service.stop()
            return json.dumps({"status": "ok", "live_active": enabled})
        except Exception as e:
            logger.error(f"toggle_live_feed failed: {e}")
            return json.dumps({"error": str(e)})


def _apply_taskbar_icon():
    """Applies custom icon to Win32 window handle for crisp taskbar thumbnail."""
    if sys.platform != "win32":
        return
    try:
        time.sleep(0.5)
        hwnd = ctypes.windll.user32.FindWindowW(None, "Liquidity Map | Centered Live-Price Game World")
        if hwnd:
            ico_path = str(Path(__file__).parent.parent.parent / "assets" / "icon.ico")
            if Path(ico_path).exists():
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                hicon_big = ctypes.windll.user32.LoadImageW(None, ico_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
                hicon_small = ctypes.windll.user32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                WM_SETICON = 0x0080
                if hicon_big:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)
                if hicon_small:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_small)
    except Exception as e:
        logger.debug(f"Taskbar icon notice: {e}")


def launch_gui(service: Optional[LiquidityMapService] = None):
    """Launches Google Chrome Frameless GUI without console logs."""
    app_service = service or LiquidityMapService()
    app_service.start()

    api = ChromeWindowAPI(app_service)

    html_file = Path(__file__).parent / "templates" / "chrome_ui.html"
    if not html_file.exists():
        raise FileNotFoundError(f"HTML UI template not found at {html_file}")

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    def _on_tick_dispatch(quote):
        if api._window:
            try:
                payload = json.dumps(quote)
                api._window.evaluate_js(f"if (window.onLiveTickUpdate) window.onLiveTickUpdate({payload});")
            except Exception:
                pass

    app_service.feed.add_callback(_on_tick_dispatch)

    window = webview.create_window(
        title="Liquidity Map | Centered Live-Price Game World",
        html=html_content,
        js_api=api,
        width=1340,
        height=860,
        frameless=True,       # Frameless Chrome styling!
        easy_drag=True,
        min_size=(1050, 700),
        background_color="#1f1f23"
    )
    api.set_window(window)

    try:
        webview.start(_apply_taskbar_icon, debug=False)
    finally:
        app_service.stop()
