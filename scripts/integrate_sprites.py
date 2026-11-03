"""Helper script to embed authentic base64 vector SVG sprites into chrome_ui.html."""
import base64
import json
from pathlib import Path

orb_files = {
    "SSS": "assets/sprites/orbs/tier_sss_sovereign.svg",
    "SS": "assets/sprites/orbs/tier_ss_dynast.svg",
    "S": "assets/sprites/orbs/tier_s_duke.svg",
    "A": "assets/sprites/orbs/tier_a_knight.svg",
    "B": "assets/sprites/orbs/tier_b_merchant.svg",
    "C": "assets/sprites/orbs/tier_c_crafter.svg",
    "D": "assets/sprites/orbs/tier_d_peasant.svg",
}

b64_dict = {}
for tier, rel_path in orb_files.items():
    p = Path(rel_path)
    b64_dict[tier] = base64.b64encode(p.read_bytes()).decode("ascii")

js_sprites = f"""
    // Authentic 7-Tier Royal Social Hierarchy Vector SVG Sprites
    const tierSvgBase64 = {json.dumps(b64_dict)};
    const tierSpriteImages = {{}};
    for (const [t, b64] of Object.entries(tierSvgBase64)) {{
      const img = new Image();
      img.src = "data:image/svg+xml;base64," + b64;
      tierSpriteImages[t] = img;
    }}
"""

ui_path = Path("liquidity_map/gui/templates/chrome_ui.html")
content = ui_path.read_text(encoding="utf-8")

target_anchor = 'let activeRenderQuality = "ultra";'
if target_anchor not in content:
    print("Error: target_anchor not found")
    exit(1)

if "const tierSvgBase64" in content:
    print("Already injected!")
    exit(0)

new_content = content.replace(target_anchor, target_anchor + "\n" + js_sprites)
ui_path.write_text(new_content, encoding="utf-8")
print("Authentic SVG sprites successfully injected into chrome_ui.html!")
