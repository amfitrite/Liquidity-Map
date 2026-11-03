"""FastAPI Web Server & Chrome Frameless Window Launcher for Liquidity Map."""
import os
import sys
import time
import subprocess
import threading
import logging
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from liquidity_map.service import LiquidityMapService

logger = logging.getLogger("LiquidityMap.GUI")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "liquidity_map" / "gui" / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"


def create_app(service: LiquidityMapService) -> FastAPI:
    app = FastAPI(title="Liquidity Map Engine", version="1.0.0")

    # Mount static assets
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    @app.get("/", response_class=HTMLResponse)
    async def index_page():
        template_file = TEMPLATES_DIR / "index.html"
        if not template_file.exists():
            return HTMLResponse("<h1>Index template not found</h1>", status_code=404)
        with open(template_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    @app.get("/api/state")
    async def get_state(w: float = Query(1400.0), h: float = Query(800.0)):
        return service.get_world_snapshot(viewport_w=w, viewport_h=h)

    @app.get("/api/quote")
    async def get_quote():
        return service.feed.get_latest_quote()

    @app.post("/api/camera/mode")
    async def set_camera_mode(mode: str = Query("FOLLOW")):
        service.camera.mode = mode.upper()
        return {"status": "ok", "mode": service.camera.mode}

    @app.post("/api/camera/zoom")
    async def set_camera_zoom(time_scale: float = Query(8.0), price_scale: float = Query(40.0)):
        service.camera.pixels_per_second = max(1.0, min(50.0, time_scale))
        service.camera.pixels_per_price = max(5.0, min(200.0, price_scale))
        return {
            "status": "ok",
            "pixels_per_second": service.camera.pixels_per_second,
            "pixels_per_price": service.camera.pixels_per_price,
        }

    return app


def find_chrome_executable() -> Optional[str]:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def launch_gui(service: LiquidityMapService, host: str = "127.0.0.1", port: int = 8055, auto_open: bool = True):
    """Starts service, runs HTTP server, and opens Google Chrome Frameless window."""
    service.start()
    app = create_app(service)

    server_config = uvicorn.Config(app=app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(server_config)

    server_thread = threading.Thread(target=server.run, daemon=True, name="UvicornServerThread")
    server_thread.start()

    url = f"http://{host}:{port}"
    logger.info("Liquidity Map server running at %s", url)
    print(f"\n[+] Liquidity Map Server running at: {url}")

    time.sleep(1.2)  # Give uvicorn a moment to bind

    chrome_proc = None
    if auto_open:
        chrome_exe = find_chrome_executable()
        if chrome_exe:
            user_data_dir = os.path.join(os.environ.get("TEMP", "C:/Temp"), "liquidity_map_chrome_profile")
            cmd = [
                chrome_exe,
                f"--app={url}",
                "--window-size=1540,940",
                f"--user-data-dir={user_data_dir}",
                "--disable-features=Translate",
                "--no-first-run",
            ]
            try:
                chrome_proc = subprocess.Popen(cmd)
                print(f"[+] Launched Chrome Frameless GUI: {chrome_exe}")
            except Exception as e:
                print(f"[!] Failed to launch browser process: {e}")
        else:
            print(f"[i] Please open browser manually at: {url}")

    try:
        # Keep server alive until interrupt or browser exit
        while server_thread.is_alive():
            if chrome_proc and chrome_proc.poll() is not None:
                # Browser was closed by user
                print("\n[i] Frameless browser window closed.")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[!] Shutting down Liquidity Map...")
    finally:
        server.should_exit = True
        service.stop()
        if chrome_proc and chrome_proc.poll() is None:
            chrome_proc.terminate()
