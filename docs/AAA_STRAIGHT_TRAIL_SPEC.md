# AAA Straight-Line Liquidity Trail Specification

**Status:** Technical & Visual Architecture Standard  
**Repository:** `amfitrite/Liquidity-Map`  
**Master Artwork:** [`assets/sprites/trails/trail_effects_showcase.svg`](../assets/sprites/trails/trail_effects_showcase.svg)  
**Interactive Laboratory:** [`assets/sprites/trails/trail_studio.html`](../assets/sprites/trails/trail_studio.html)  

---

## 1. Core Principle: Liquidity Trails are Straight Horizontal Levels

In institutional order-flow and candlestick price action (XAUUSD, Forex, Crypto), **liquidity is anchored to specific price levels** (BSL, SSL, Previous Day High/Low, Session High/Low, Equal Highs/Lows).

```text
[Formation Origin: t_start]                                     [Current Price: t_now]
             ---------------------------------------------------------( ORB HEAD )
             <------------- Historical Residual Trail --------------->
             (Smooth mathematical dissipation falloff to the left)
```

### Key Rules:
1. **Zero Curvature / Zero Sine Waves**: The trail is **never** a curved ribbon, wavy snake, slash arc, or directional arrow. It is a straight, horizontal ray aligned with the underlying price coordinate.
2. **Head & Origin**: The **Live Orb Head** is located at the current time ($t_{\text{now}}$) on the right. The trail extends **horizontally backwards** into history ($t_{\text{start}}$).
3. **Mathematical Dissipation**: Visual intensity and thickness diminish as a function of age towards $t_{\text{start}}$:
   $$\alpha(x) = \alpha_{\max} \cdot \left(\frac{x - x_{\text{start}}}{x_{\text{now}} - x_{\text{start}}}\right)^{1.8}$$
4. **Independent Dimensions**:
   - **Tier** defines the **Trail Heatmap Hue** (SSS White $\to$ D Deep Blue).
   - **Preset** defines the **Material Silhouette** (Quantum Beam, Plasma Conduit, Cyber Rail, etc.).
   - **Quality** defines shader passes and GPU bloom budgets.

---

## 2. Fixed Tier Heatmap Palette

| Tier | Heat Level | Trail Hue | Hex Code | Visual Metaphor |
|---|---|---|---|---|
| **SSS** | **Hottest** | Imperial White | `#FFFFFF` | Sovereign Diamond Laser / High-Energy Quantum Core |
| **SS** | **Very Hot** | Crimson Ruby | `#FF303B` | Dynastic Fusion Plasma / Thermal Ionization |
| **S** | **Hot** | Solar Orange | `#FF7900` | Celestial Starlight Ray / Stellar Constellation |
| **A** | **Warm** | Cyber Yellow | `#FFD52A` | Optical Glass Fiber / Knightly Precision Telemetry |
| **B** | **Cool** | Neon Cyan | `#73E6FF` | Cryo-Prismatic Crystal Filament / Sub-Zero Caustics |
| **C** | **Colder** | Cobalt Blue | `#2787E5` | Heavy Electromagnetic Flux Channel / Industrial Rails |
| **D** | **Coldest** | Deep Blue | `#092B68` | Minimalist Horizon Ray / Ultra-Clean Baseline |

> [!IMPORTANT]
> The trail hue is strictly tied to the Liquidity Tier. The orb's own body material (gold, ruby, jade, clay) remains untouched.

---

## 3. AAA Layered Construction Architecture

Every high-fidelity straight trail is composited from 5 distinct GPU render passes:

```text
+--------------------------------------------------------------------------------+
| Layer 1: Volumetric Atmosphere Envelope (Broad Gaussian bloom, 20-32px height)  |
| Layer 2: Harmonic Containment Rails (Subtle parallel guidance lines +/- 5-7px) |
| Layer 3: Coordinate Telemetry Ticks (Precision vertical calibration notches)   |
| Layer 4: Micro-Packets / Photonic Diamond Nodes (Drifting sub-atomic motes)   |
| Layer 5: Razor-Sharp Incandescent Beam Core (1.2px - 3.5px white-hot center)    |
+--------------------------------------------------------------------------------+
```

### Breakdown:
- **Layer 1 (Volumetric Glow)**: Wide, low-opacity blur (`stdDeviation: 10-14px`) that makes the liquidity level stand out without obscuring candlestick wicks.
- **Layer 2 (Harmonic Rails)**: Thin dashed or solid parallel lines that evoke high-tech energy confinement.
- **Layer 3 (Telemetry Ticks)**: Discrete vertical tick marks along the ray, showing institutional price grid calibration.
- **Layer 4 (Photonic Nodes)**: Diamond-shaped photonic packets positioned at golden-ratio intervals along the line.
- **Layer 5 (Incandescent Core)**: The focal straight ray with an ultra-bright white specular core at the live head, tapering smoothly towards the origin.

---

## 4. WebGL / Fragment Shader Reference Implementation

For 60–120 FPS performance in web and native charts under a 120-object budget:

```glsl
// Horizontal Straight Liquidity Trail Fragment Shader
precision mediump float;

uniform vec2  u_resolution;
uniform vec2  u_head_pos;       // Orb position (x_now, y_price)
uniform float u_origin_x;       // Origin timestamp position (x_start)
uniform vec3  u_tier_color;     // Normalized RGB from Heatmap
uniform float u_intensity;      // 0.0 to 1.0 (State factor)

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution;
    
    // Check if within horizontal segment [x_start, x_now]
    if (gl_FragCoord.x < u_origin_x || gl_FragCoord.x > u_head_pos.x) {
        discard;
    }
    
    // Normalized distance along trail (0.0 at origin, 1.0 at live head)
    float u_age = (gl_FragCoord.x - u_origin_x) / (u_head_pos.x - u_origin_x);
    float age_decay = pow(u_age, 1.8);
    
    // Vertical distance from center price level
    float dist_y = abs(gl_FragCoord.y - u_head_pos.y);
    
    // Core beam (1.5px radius)
    float core = smoothstep(1.5, 0.0, dist_y);
    
    // Secondary glow envelope (14px radius)
    float glow = smoothstep(14.0, 0.0, dist_y) * 0.35;
    
    // Harmonic rails (+/- 6px)
    float rails = smoothstep(1.0, 0.0, abs(dist_y - 6.0)) * 0.4;
    
    // Combine passes
    float alpha = (core * 0.95 + glow + rails) * age_decay * u_intensity;
    vec3 final_color = mix(u_tier_color, vec3(1.0), core * 0.75);
    
    gl_FragColor = vec4(final_color, alpha);
}
```

---

## 5. Performance & Render Budgets

1. **Active Live Objects**: Up to 120 simultaneous straight trails.
2. **Batching**: Render all horizontal line trails in a single batched instanced quad call.
3. **Historical / Mitigated Levels**: When a level is swept or mitigated, freeze the trail length to the sweep candle timestamp, desaturate to grayscale, and set opacity to 25%.
