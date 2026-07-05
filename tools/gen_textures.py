# Procedural block decal generator for Mars Miner 2D.
# Draws on a 32x32 pixel grid, upscales x8 nearest-neighbor to 256x256.
# Grayscale sprites (nuggets, crystals, cracks) are tinted in Roblox via
# Decal.Color3; colored sprites (lava, gas, grass, artifact) are fixed.
import math
import random
from pathlib import Path

from PIL import Image

GRID = 32
SCALE = 8
OUT = Path(__file__).resolve().parent.parent / "assets" / "textures"

CLEAR = (0, 0, 0, 0)


def new_canvas():
    return Image.new("RGBA", (GRID, GRID), CLEAR)


def px(img, x, y, color):
    if 0 <= x < GRID and 0 <= y < GRID:
        img.putpixel((int(x), int(y)), color)


def blob(img, cx, cy, r, color, rng, rough=0.35):
    """Rough filled circle (nugget-like)."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d <= r * (1 - rough / 2 + rng.random() * rough):
                px(img, x, y, color)


def line(img, x0, y0, x1, y1, color, thick=1):
    steps = int(max(abs(x1 - x0), abs(y1 - y0), 1)) * 2
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        for dy in range(-(thick // 2), thick - thick // 2):
            for dx in range(-(thick // 2), thick - thick // 2):
                px(img, round(x + dx), round(y + dy), color)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    big = img.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST)
    big.save(OUT / f"{name}.png")
    print("wrote", name)


# Grayscale palette (tinted by Decal.Color3 in Roblox: white stays brightest)
HI = (255, 255, 255, 255)
MID = (200, 200, 200, 255)
LO = (140, 140, 140, 255)
SHADOW = (90, 90, 90, 255)


def ore_nuggets():
    """Cluster of rough metal nuggets (Ironium..Platinium, tinted)."""
    rng = random.Random(7)
    img = new_canvas()
    spots = [(9, 10, 3.2), (21, 8, 2.4), (16, 18, 3.8), (7, 23, 2.6), (24, 22, 3.0), (27, 14, 1.8)]
    for cx, cy, r in spots:
        blob(img, cx + 1, cy + 1, r, SHADOW, rng)          # drop shadow
        blob(img, cx, cy, r, MID, rng)
        blob(img, cx - r * 0.3, cy - r * 0.3, r * 0.45, HI, rng, rough=0.2)  # highlight
    return img


def ore_crystals():
    """Sharp crystal shards (Einsteinium/gems, tinted)."""
    img = new_canvas()
    rng = random.Random(3)
    shards = [(8, 22, 8, -0.5), (16, 26, 12, 0.0), (24, 21, 7, 0.45), (12, 24, 6, 0.25)]
    for bx, by, h, lean in shards:
        tipx, tipy = bx + lean * h, by - h
        w = max(2, h // 3)
        # two facets: light left, mid right
        for i in range(h + 1):
            t = i / h
            y = by - i
            half = w * (1 - t)
            cx = bx + lean * i
            for x in range(round(cx - half), round(cx + half) + 1):
                px(img, x, y, HI if x < cx else MID)
        px(img, round(tipx), round(tipy), HI)
        # base shadow
        for x in range(round(bx - w), round(bx + w) + 1):
            px(img, x, by + 1, SHADOW)
    return img


def rock_cracks():
    """Crack lines for undiggable rock (tinted dark gray)."""
    img = new_canvas()
    rng = random.Random(11)
    for sx, sy, ex, ey in [(3, 6, 14, 16), (14, 16, 10, 29), (14, 16, 27, 20), (20, 2, 27, 20), (27, 20, 30, 30)]:
        # jitter the segment into a jagged polyline
        pts = [(sx, sy)]
        n = 4
        for i in range(1, n):
            t = i / n
            pts.append((sx + (ex - sx) * t + rng.uniform(-2, 2), sy + (ey - sy) * t + rng.uniform(-2, 2)))
        pts.append((ex, ey))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            line(img, x0, y0, x1, y1, (40, 40, 44, 255))
            line(img, x0 + 1, y0 + 1, x1 + 1, y1 + 1, (70, 70, 76, 160))  # soft edge
    return img


def lava():
    """Glowing lava blobs on darker crust (fixed colors)."""
    img = new_canvas()
    rng = random.Random(5)
    crust = (140, 30, 0, 255)
    glow = (255, 140, 20, 255)
    hot = (255, 230, 120, 255)
    for x in range(GRID):
        for y in range(GRID):
            px(img, x, y, crust)
    for cx, cy, r in [(8, 8, 5), (22, 12, 6), (12, 24, 7), (26, 26, 4)]:
        blob(img, cx, cy, r, glow, rng, rough=0.4)
        blob(img, cx, cy, r * 0.45, hot, rng, rough=0.3)
    return img


def gas_bubbles():
    """Bubble rings (fixed pale green, semi-transparent block anyway)."""
    img = new_canvas()
    ring = (220, 255, 160, 255)
    for cx, cy, r in [(9, 9, 4), (22, 7, 3), (16, 18, 5), (7, 25, 3), (25, 24, 4)]:
        for a in range(0, 360, 6):
            px(img, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), ring)
        px(img, cx - r * 0.4, cy - r * 0.4, (255, 255, 255, 255))  # shine
    return img


def grass_top():
    """Surface row: reddish mars soil with a lighter crusty top edge."""
    img = new_canvas()
    rng = random.Random(13)
    top = (200, 90, 50, 255)
    tuft = (230, 120, 70, 255)
    for x in range(GRID):
        h = 3 + int(rng.random() * 2)
        for y in range(h):
            px(img, x, y, top)
        if rng.random() < 0.3:
            px(img, x, h, tuft)
            px(img, x, h + 1, tuft)
    return img


def dirt_noise():
    """Subtle speckle overlay for dirt (mostly transparent)."""
    img = new_canvas()
    rng = random.Random(17)
    for _ in range(60):
        x, y = rng.randrange(GRID), rng.randrange(GRID)
        shade = rng.choice([(0, 0, 0, 45), (255, 255, 255, 30)])
        px(img, x, y, shade)
        if rng.random() < 0.5:
            px(img, x + 1, y, shade)
    return img


def artifact_fossil():
    """Ammonite spiral fossil, always the same look in the level."""
    img = new_canvas()
    bone = (225, 210, 180, 255)
    edge = (150, 130, 100, 255)
    cx, cy = 16, 17
    # archimedean spiral, ~2.5 turns
    prev = None
    a = 0.0
    while a < math.pi * 5:
        r = 1.1 + a * 1.55
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a) * 0.9
        if prev:
            line(img, prev[0], prev[1], x, y, bone, thick=2)
        prev = (x, y)
        a += 0.12
    # rib lines across the outer whorl
    for a_deg in range(0, 360, 30):
        a = math.radians(a_deg) + math.pi * 3
        r0 = 1.1 + (a - math.pi * 2) * 1.55
        r1 = 1.1 + a * 1.55
        x0 = cx + r0 * math.cos(a)
        y0 = cy + r0 * math.sin(a) * 0.9
        x1 = cx + r1 * math.cos(a)
        y1 = cy + r1 * math.sin(a) * 0.9
        line(img, x0, y0, x1, y1, edge)
    return img


def bone():
    """Classic bone, diagonal (alternative fossil marker)."""
    img = new_canvas()
    bone_c = (235, 225, 200, 255)
    shade = (170, 155, 125, 255)
    x0, y0, x1, y1 = 9, 23, 23, 9
    line(img, x0 + 1, y0 + 1, x1 + 1, y1 + 1, shade, thick=3)
    line(img, x0, y0, x1, y1, bone_c, thick=3)
    rng = random.Random(1)
    for ex, ey in ((x0, y0), (x1, y1)):
        # two knobs per end, perpendicular to the shaft
        blob(img, ex - 1.6, ey - 1.6, 2.2, bone_c, rng, rough=0.15)
        blob(img, ex + 1.6, ey + 1.6, 2.2, bone_c, rng, rough=0.15)
    return img


SPRITES = {
    "ore_nuggets": ore_nuggets,
    "ore_crystals": ore_crystals,
    "rock_cracks": rock_cracks,
    "lava": lava,
    "gas_bubbles": gas_bubbles,
    "grass_top": grass_top,
    "dirt_noise": dirt_noise,
    "artifact_fossil": artifact_fossil,
    "bone": bone,
}

if __name__ == "__main__":
    for name, fn in SPRITES.items():
        save(fn(), name)
