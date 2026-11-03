# Liquidity Map — Centered Live-Price Game World

[![XAUUSD](https://img.shields.io/badge/Asset-XAUUSD-gold.svg)](https://github.com/amfitrite/Liquidity-Map)
[![Feed](https://img.shields.io/badge/Feed-Dukascopy%20Live-10b981.svg)](docs/DUKASCOPY_LIVE_PRICE_FEED_SPEC.md)
[![World](https://img.shields.io/badge/World-Centered%20Live--Price-38bdf8.svg)](docs/CENTERED_PRICE_GAME_WORLD_SPEC.md)
[![GUI](https://img.shields.io/badge/GUI-Google%20Chrome%20Frameless-f59e0b.svg)](liquidity_map/gui/templates/index.html)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(7%2F7)-emerald.svg)](tests/)

An institutional-grade, multi-timeframe liquidity visualization terminal and game-world engine for **XAUUSD**. Built with a **Centered Live-Price Follow Camera**, eliminating traditional candlestick clutter in favor of pure institutional liquidity pools and straight horizontal horizon rays.

---

## 1. Quick Start

### Running the Application
Double-click `run_app.bat` or execute in terminal:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch application (starts backend and opens Google Chrome Frameless GUI)
python run_app.py
```

### Desktop Shortcut
To install a shortcut on your Windows desktop with the official custom icon:
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/create_desktop_shortcut.ps1"
```

---

## 2. Core Architectural Philosophy

### A. Centered Live-Price Game World (No Candlesticks)
* **The Live Player Anchor**: The continuously updated Dukascopy tick price is locked at the exact center of the screen `(cx, cy)`.
* **The Kinetic Price Compass**: The player character acts as a live directional compass indicating momentum bias:
  - **▲ UP (Green/Cyan)**: Pressure towards Buy-Side Liquidity (BSL).
  - **▼ DOWN (Red/Coral)**: Pressure towards Sell-Side Liquidity (SSL).
  - **◄► NEUTRAL (Gold)**: Balanced market consolidation.
* **Past vs. Future**:
  - **Left of Center**: Historical world moving left as time advances, populated by observed Liquidity Orbs and straight horizontal trails.
  - **Right of Center**: Future Liquidity Engine scenario horizons, quantile corridors, and conditional structural formation models.

---

## 3. The 7 Royal Social Hierarchy Tiers & Trail Heatmaps

| Tier | Rank Identity | Base Frame | Core Hue | Trail Heatmap Hue | 1x Size | Signature Silhouette |
|---|---|---|---|---|---:|---|
| **SSS** | **Golden Sovereign** | MN1 | `#D6A332` Gold | `#FFFFFF` White | **36 px** | Imperial Crown 5-titik, Triple Celestial Orbit, Heart Diamond |
| **SS** | **Crimson Dynast** | W1 | `#C02645` Ruby | `#FF303B` Red | **31 px** | Royal Coronet 3-titik, Ceremonial Orbit, Marquise Ruby |
| **S** | **Sapphire Duke** | D1 | `#7251C8` Violet | `#FF7900` Orange | **26 px** | Heraldic Shield Cut, Crescent Half-Orbits, Sapphire Inset |
| **A** | **Azure Knight** | H4 | `#1D4ED8` Azure | `#FFD52A` Yellow | **21 px** | Armored Octagonal Prism, Disciplined Steel Halo |
| **B** | **Jade Merchant** | H1 | `#16866B` Jade | `#73E6FF` Cyan | **17 px** | Polished Jade Cabochon, Guild Trade Seal, Thin Hoop |
| **C** | **Iron Crafter** | M15 | `#64748B` Iron | `#2787E5` Blue | **13 px** | Forged Slag Nugget, Worn Chisel Facets, **Zero Ornaments** |
| **D** | **Earthen Peasant** | M5 / M1 | `#9A7658` Clay | `#092B68` Deep Blue | **10 px** | Handmade Clay Nodule, Organic Thumb Dents, **Zero Halo** |

---

## 4. Straight-Line Liquidity Trail VFX Architecture

Liquidity levels represent static institutional price memory. Trails are strictly **straight horizontal rays** extending backwards into history with exponential dissipation:

$$\alpha(x) = \alpha_{\max} \cdot \left(\frac{x - x_{\text{start}}}{x_{\text{now}} - x_{\text{start}}}\right)^{1.8}$$

### 5-Layer Stack
1. **Layer 1: Volumetric Atmosphere Envelope** (Wide Gaussian bloom, 24-32px).
2. **Layer 2: Harmonic Containment Rails** (Parallel guide lines $\pm 6\text{px}$).
3. **Layer 3: Telemetry Ticks** (Institutional price calibration notches).
4. **Layer 4: Photonic Diamond Nodes** (Energy packet clusters along the line).
5. **Layer 5: Incandescent Laser Core** (Ultra-sharp 1.5 - 3.5px white-hot center ray).

---

## 5. Project Directory Structure

```text
Liquidity-Map/
├── assets/
│   ├── icon.ico / icon.png / icon.svg       # Official desktop & app icons
│   ├── thumbnail.png / thumbnail.svg         # Hero desktop shortcut card
│   └── sprites/
│       ├── orbs/                             # 7 standalone tier SVG sprites & matrix atlas
│       ├── trails/                           # Master straight-trail showcase & trail studio
│       └── orb_viewer.html                   # Interactive sprite inspection laboratory
├── docs/
│   ├── CENTERED_PRICE_GAME_WORLD_SPEC.md     # Follow camera & coordinate transforms
│   ├── DUKASCOPY_LIVE_PRICE_FEED_SPEC.md     # Real-time tick contract & price basis
│   ├── LIQUIDITY_MASTER_REGISTRY.md          # Canonical structural detector registry
│   ├── FUTURE_LIQUIDITY_ENGINE_SPEC.md       # Monte Carlo quantile corridors & scenarios
│   ├── AAA_STRAIGHT_TRAIL_SPEC.md            # Straight-line horizon VFX specifications
│   └── ORB_TRAIL_PRODUCTION_INTEGRATION_SPEC.md # Renderer contracts & performance QA
├── liquidity_map/
│   ├── config.py                             # Central application configurations
│   ├── service.py                            # Master orchestration service
│   ├── data/
│   │   ├── dukascopy_feed.py                 # Live tick feed & jump-diffusion simulator
│   │   └── registry.py                       # Master liquidity candidate store
│   ├── engine/
│   │   ├── world.py                          # Centered camera math & coordinate engine
│   │   └── future_engine.py                  # Quantile fans & structural scenario generator
│   └── gui/
│       ├── app.py                            # FastAPI server & Chrome frameless launcher
│       └── templates/index.html              # 60 FPS Canvas2D Game Viewport with Kronos Layout
├── scripts/
│   └── create_desktop_shortcut.ps1           # Windows Desktop shortcut generator
├── tests/                                    # Unit test suite (7/7 passing)
├── run_app.py / main.py                      # Application entry points
├── run_app.bat                               # Windows launcher batch script
└── requirements.txt                          # Python dependencies
```

---

## 6. Testing

Run the automated test suite:

```bash
python -m unittest discover tests
```
