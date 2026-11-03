# Liquidity Map

A multi-timeframe liquidity visualization project.

## Visual design references

- [Orb & Trail Production Integration Specification](docs/ORB_TRAIL_PRODUCTION_INTEGRATION_SPEC.md)
- [Corrected AAA straight-trail specification](docs/AAA_STRAIGHT_TRAIL_SPEC.md)
- [Centered live-price trail studio](assets/sprites/trails/trail_studio.html)
- [Trail effects showcase atlas](assets/sprites/trails/trail_effects_showcase.svg)

- [Seven tier-specific orb designs and selectable styles](docs/ORB_DESIGN_SPEC.md)
- [Seven distinct orb tier designs (SVG)](assets/orb-tier-reference.svg)
- [Solar Crown style close-up](assets/orb-aaa-reference.svg)
- [Premium trail VFX reference — 10 distinct effects](assets/trail-effect-premium-reference.svg)
- [Trail VFX implementation and animation specification](docs/TRAIL_VFX_IMPLEMENTATION_SPEC.md)
- [Dukascopy live price feed — tick adapter and no-candlestick UI](docs/DUKASCOPY_LIVE_PRICE_FEED_SPEC.md)
- [Centered live-price game world — camera and coordinate specification](docs/CENTERED_PRICE_GAME_WORLD_SPEC.md)
- [Future Liquidity Engine v2.0 — corrected concept, event definitions, tier policy, and validation protocol](docs/FUTURE_LIQUIDITY_ENGINE_SPEC.md)
- [Master Liquidity Registry — expanded historical detectors, context separation, and implementation priorities](docs/LIQUIDITY_MASTER_REGISTRY.md)
- [MTF liquidity inventory, tiers, and rendering specification](docs/MTF_LIQUIDITY_TIER_RENDER_SPEC.md)
- [Legacy trail reference — retained for comparison](assets/trail-effect-reference.svg)

**Liquidity Map is a game-like live-price world, not a candlestick chart.** The central price marker follows accepted Dukascopy updates and stays centered; the world moves around it. No candle bodies, wicks, or OHLC bars are rendered. Internal data aggregation may be used by models but is not displayed.\n\n**Future Liquidity is a forecast/scenario layer, not a live order-book map.** Its specification separates price-path distributions, structural-formation scenarios, volatility/density overlays, and optional options-derived gamma context. It also separates Model Reliability from individual Projection Quality. Unvalidated forecasts remain PROVISIONAL (no tier); D is reserved for validated but weak projections.

**Terminology:** Liquidity tiers are SSS, SS, S, A, B, C, and D. "AAA" refers only to optional premium game-quality rendering, never to a liquidity tier or signal grade. The SSS orb is the Golden Sovereign in royal gold; the D orb is the Humble Earthen Seed, deliberately plain and unadorned. Solar Crown remains a selectable finishing style and cannot erase these tier identities.

Trail hue follows the tier heatmap: SSS white, SS red, S orange, A yellow, B light blue, C blue, and D deep blue. The heatmap recolors trails only; orb core colors remain unchanged. The premium trail sheet is a visual design reference, not a production sprite atlas. Final in-app effects require layered shader/sprite implementation and measured performance tuning. Final sprites should use transparent backgrounds, separable material layers, and multiple resolution or level-of-detail variants.
