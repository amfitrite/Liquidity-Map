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

target_fn = "function drawOrbSprite(ctx, x, y, obj, isSwept, isTested) {"
idx_target = content.find(target_fn)
if idx_target == -1:
    print("Error: target_fn not found")
    exit(1)

proc_marker = 'if (obj.tier === "SSS" || obj.tier === "SS") {'
idx_proc = content.find(proc_marker, idx_target)
if idx_proc == -1:
    print("Error: proc_marker not found")
    exit(1)

replacement = f"""{js_sprites}
    function drawOrbSprite(ctx, x, y, obj, isSwept, isTested) {{
      const size = obj.nominal_size;
      const r = size / 2;

      ctx.save();
      ctx.translate(x, y);

      if (isSwept) {{
        ctx.globalAlpha = 0.30;
        ctx.fillStyle = "#64748b";
        ctx.strokeStyle = "#94a3b8";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(-r * 0.7, -r * 0.7); ctx.lineTo(r * 0.7, r * 0.7);
        ctx.moveTo(r * 0.7, -r * 0.7); ctx.lineTo(-r * 0.7, r * 0.7);
        ctx.stroke();
        ctx.restore();
        return;
      }}

      // 1. Draw Authentic Vector SVG Sprite if ready
      if (tierSpriteImages[obj.tier] && tierSpriteImages[obj.tier].complete && tierSpriteImages[obj.tier].naturalWidth > 0) {{
        const spriteDiam = r * 2.8;
        if (isTested) {{
          ctx.save();
          ctx.fillStyle = obj.core_color;
          ctx.globalAlpha = 0.35;
          ctx.beginPath();
          ctx.arc(0, 0, spriteDiam * 0.6, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }}
        ctx.drawImage(tierSpriteImages[obj.tier], -spriteDiam / 2, -spriteDiam / 2, spriteDiam, spriteDiam);
        ctx.restore();
        return;
      }}
"""

new_content = content[:idx_target] + replacement + "\n      " + content[idx_proc:]
ui_path.write_text(new_content, encoding="utf-8")
print("Authentic SVG sprites successfully injected into chrome_ui.html!")
