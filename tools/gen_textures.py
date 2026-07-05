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


# ---------------------------------------------------------------------------
# Variant families: each takes a seed so one function yields many sprites.
# Grayscale ones (HI/MID/LO/SHADOW) are tintable via Texture.Color3 in Roblox;
# the rest use fixed colors.
# ---------------------------------------------------------------------------

BONE_C = (225, 210, 180, 255)
BONE_EDGE = (150, 130, 100, 255)


def fill_ellipse(img, cx, cy, rx, ry, color):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        dy = (y - cy) / ry
        if abs(dy) > 1:
            continue
        half = rx * math.sqrt(1 - dy * dy)
        for x in range(round(cx - half), round(cx + half) + 1):
            px(img, x, y, color)


def ore_nuggets_var(seed):
    """Random nugget cluster layout (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    for _ in range(rng.randint(4, 7)):
        cx, cy = rng.uniform(5, 27), rng.uniform(5, 27)
        r = rng.uniform(1.6, 3.6)
        blob(img, cx + 1, cy + 1, r, SHADOW, rng)
        blob(img, cx, cy, r, MID, rng)
        blob(img, cx - r * 0.3, cy - r * 0.3, r * 0.45, HI, rng, rough=0.2)
    return img


def ore_crystals_var(seed):
    """Random shard layout (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    for _ in range(rng.randint(3, 5)):
        bx, by = rng.uniform(6, 26), rng.uniform(20, 27)
        h = rng.randint(6, 13)
        lean = rng.uniform(-0.5, 0.5)
        w = max(2, h // 3)
        for i in range(h + 1):
            t = i / h
            y = by - i
            half = w * (1 - t)
            cx = bx + lean * i
            for x in range(round(cx - half), round(cx + half) + 1):
                px(img, x, y, HI if x < cx else MID)
        for x in range(round(bx - w), round(bx + w) + 1):
            px(img, x, by + 1, SHADOW)
    return img


def rock_cracks_var(seed):
    """Random jagged crack layout."""
    rng = random.Random(seed)
    img = new_canvas()
    for _ in range(rng.randint(3, 5)):
        sx, sy = rng.uniform(0, 31), rng.uniform(0, 31)
        ex, ey = rng.uniform(0, 31), rng.uniform(0, 31)
        pts = [(sx, sy)]
        for i in range(1, 4):
            t = i / 4
            pts.append((sx + (ex - sx) * t + rng.uniform(-2, 2),
                        sy + (ey - sy) * t + rng.uniform(-2, 2)))
        pts.append((ex, ey))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            line(img, x0, y0, x1, y1, (40, 40, 44, 255))
            line(img, x0 + 1, y0 + 1, x1 + 1, y1 + 1, (70, 70, 76, 160))
    return img


def ore_vein(seed):
    """Jagged vein crossing the block with offshoots (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    y = rng.uniform(8, 24)
    pts = [(-1.0, y)]
    x = -1.0
    while x < GRID:
        x += rng.uniform(3, 6)
        y = min(max(y + rng.uniform(-4, 4), 3), 28)
        pts.append((x, y))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(img, x0, y0, x1, y1, MID, thick=2)
        line(img, x0, y0 - 1, x1, y1 - 1, HI)
    for _ in range(rng.randint(2, 4)):
        bx, by = pts[rng.randrange(1, len(pts) - 1)]
        line(img, bx, by, bx + rng.uniform(-7, 7),
             by + rng.choice((-1, 1)) * rng.uniform(4, 9), LO)
    return img


def strata(seed):
    """Wavy sediment layers, semi-transparent overlay."""
    rng = random.Random(seed)
    img = new_canvas()
    shades = [(255, 255, 255, 45), (0, 0, 0, 60), (255, 255, 255, 25), (0, 0, 0, 35)]
    bounds = []
    y = rng.randint(2, 5)
    while y < GRID:
        bounds.append(y)
        y += rng.randint(3, 6)
    phase = rng.uniform(0, 6.3)
    for x in range(GRID):
        offs = [round(b + math.sin(x * 0.35 + phase + i) * 1.5) for i, b in enumerate(bounds)]
        edges = [0] + offs + [GRID]
        for i, (y0, y1) in enumerate(zip(edges, edges[1:])):
            col = shades[i % len(shades)]
            for yy in range(max(y0, 0), min(y1, GRID)):
                px(img, x, yy, col)
    return img


def geode(seed):
    """Hollow geode: crust rings with crystals pointing inward (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16 + rng.uniform(-2, 2), 16 + rng.uniform(-2, 2)
    R = rng.uniform(9, 12)
    for y in range(GRID):
        for x in range(GRID):
            d = math.hypot(x - cx, y - cy) + rng.uniform(-0.6, 0.6)
            if d > R:
                continue
            if d > R - 2:
                px(img, x, y, SHADOW)
            elif d > R - 4:
                px(img, x, y, LO)
            elif d > R * 0.45:
                px(img, x, y, MID)
    for a_deg in range(0, 360, 30):
        a = math.radians(a_deg + rng.uniform(-8, 8))
        r0 = R * 0.45 + 1
        r1 = max(R * 0.45 - rng.uniform(2, 4), 1)
        line(img, cx + r0 * math.cos(a), cy + r0 * math.sin(a),
             cx + r1 * math.cos(a), cy + r1 * math.sin(a), HI)
    return img


def agate(seed):
    """Banded agate rings (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16 + rng.uniform(-3, 3), 16 + rng.uniform(-3, 3)
    shades = [MID, LO, HI, SHADOW]
    stretch = rng.uniform(0.7, 1.3)
    for y in range(GRID):
        for x in range(GRID):
            d = math.hypot((x - cx) * stretch, y - cy) + rng.uniform(-0.5, 0.5)
            band = int(d / 2.2)
            if band < 7:
                px(img, x, y, shades[band % len(shades)])
    return img


def meteorite(seed):
    """Dark cratered fragment (fixed colors)."""
    rng = random.Random(seed)
    img = new_canvas()
    body = (75, 70, 65, 255)
    rim = (120, 110, 95, 255)
    crater = (45, 42, 40, 255)
    cx, cy = 16, 16
    R = rng.uniform(9, 11)
    blob(img, cx, cy, R, body, rng, rough=0.25)
    for a_deg in range(120, 260, 4):
        a = math.radians(a_deg)
        px(img, cx + (R - 1) * math.cos(a), cy + (R - 1) * math.sin(a), rim)
    for _ in range(rng.randint(3, 5)):
        a = rng.uniform(0, 6.3)
        r = rng.uniform(0, R * 0.6)
        mx, my = cx + r * math.cos(a), cy + r * math.sin(a)
        cr = rng.uniform(1.2, 2.4)
        blob(img, mx, my, cr, crater, rng, rough=0.2)
        px(img, mx - cr, my - cr, rim)
    return img


def ice_crystals(seed):
    """Six-armed frost stars (fixed pale blue)."""
    rng = random.Random(seed)
    img = new_canvas()
    main = (200, 235, 255, 255)
    dim = (140, 190, 230, 255)
    for _ in range(rng.randint(2, 3)):
        cx, cy = rng.uniform(8, 24), rng.uniform(8, 24)
        length = rng.uniform(5, 8)
        rot = rng.uniform(0, math.pi / 3)
        for k in range(6):
            a = rot + k * math.pi / 3
            line(img, cx, cy, cx + length * math.cos(a), cy + length * math.sin(a), main)
            bx, by = cx + length * 0.6 * math.cos(a), cy + length * 0.6 * math.sin(a)
            for s in (-1, 1):
                ta = a + s * math.pi / 3
                line(img, bx, by, bx + 2 * math.cos(ta), by + 2 * math.sin(ta), dim)
    return img


def lava_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
    crust = (140, 30, 0, 255)
    glow = (255, 140, 20, 255)
    hot = (255, 230, 120, 255)
    for x in range(GRID):
        for y in range(GRID):
            px(img, x, y, crust)
    for _ in range(rng.randint(3, 5)):
        cx, cy, r = rng.uniform(5, 27), rng.uniform(5, 27), rng.uniform(3.5, 7)
        blob(img, cx, cy, r, glow, rng, rough=0.4)
        blob(img, cx, cy, r * 0.45, hot, rng, rough=0.3)
    return img


def gas_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
    ring = (220, 255, 160, 255)
    for _ in range(rng.randint(4, 6)):
        cx, cy, r = rng.uniform(5, 27), rng.uniform(5, 27), rng.uniform(2, 5)
        for a in range(0, 360, 6):
            px(img, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), ring)
        px(img, cx - r * 0.4, cy - r * 0.4, (255, 255, 255, 255))
    return img


def dirt_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
    for _ in range(rng.randint(45, 75)):
        x, y = rng.randrange(GRID), rng.randrange(GRID)
        shade = rng.choice([(0, 0, 0, 45), (255, 255, 255, 30)])
        px(img, x, y, shade)
        if rng.random() < 0.5:
            px(img, x + 1, y, shade)
    return img


def grass_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
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


# --- fossils (fixed bone colors) -------------------------------------------

def trilobite(seed):
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16, 16
    rx, ry = rng.uniform(5.5, 7), rng.uniform(9, 11)
    fill_ellipse(img, cx, cy, rx, ry, BONE_EDGE)
    fill_ellipse(img, cx, cy, rx - 1, ry - 1, BONE_C)
    for y in range(int(cy - ry * 0.25), int(cy + ry - 1), 2):
        dy = (y - cy) / ry
        half = (rx - 1) * math.sqrt(max(1 - dy * dy, 0))
        line(img, cx - half, y, cx + half, y, BONE_EDGE)
    line(img, cx - 1, cy - ry * 0.3, cx - 1, cy + ry - 2, BONE_EDGE)
    line(img, cx + 1, cy - ry * 0.3, cx + 1, cy + ry - 2, BONE_EDGE)
    px(img, cx - 3, cy - ry + 3, BONE_EDGE)
    px(img, cx + 3, cy - ry + 3, BONE_EDGE)
    return img


def fish_skeleton(seed):
    rng = random.Random(seed)
    img = new_canvas()
    y0 = 16 + rng.randint(-3, 3)
    line(img, 6, y0, 25, y0, BONE_C)
    for x in range(8, 23, 3):
        t = (x - 6) / 19
        rib = round(5 * (1 - 0.5 * t))
        line(img, x, y0 - rib, x + 1, y0, BONE_C)
        line(img, x, y0 + rib, x + 1, y0, BONE_C)
    fill_ellipse(img, 27, y0, 3, 2.5, BONE_C)
    px(img, 27, y0 - 1, BONE_EDGE)  # eye
    line(img, 6, y0, 3, y0 - 4, BONE_C)
    line(img, 6, y0, 3, y0 + 4, BONE_C)
    return img


def fern(seed):
    """Plant imprint fossil."""
    rng = random.Random(seed)
    img = new_canvas()
    col = (120, 100, 70, 255)
    dark = (90, 72, 50, 255)
    bx, by = 16 + rng.randint(-2, 2), 29
    tipx = bx + rng.randint(-4, 4)
    n = 11
    prev = (bx, by)
    for i in range(1, n + 1):
        t = i / n
        x = bx + (tipx - bx) * t
        y = by - 26 * t
        line(img, prev[0], prev[1], x, y, dark)
        leaf = 7 * (1 - t) + 1
        for s in (-1, 1):
            line(img, x, y, x + s * leaf, y - leaf * 0.35, col)
        prev = (x, y)
    return img


def footprint(seed):
    """Three-toed dino print, pressed-in look (semi-transparent dark)."""
    rng = random.Random(seed)
    img = new_canvas()
    hole = (30, 20, 15, 200)
    cx, cy = 16 + rng.randint(-2, 2), 18 + rng.randint(-2, 2)
    blob(img, cx, cy, 4.5, hole, rng, rough=0.2)
    for a_deg in (-40, 0, 40):
        a = math.radians(a_deg - 90)
        for r in range(4, 11):
            w = 1.6 if r < 9 else 0.8
            blob(img, cx + r * math.cos(a) * 0.9, cy + r * math.sin(a), w, hole, rng, rough=0.2)
    return img


def shell(seed):
    """Scallop fan shell."""
    rng = random.Random(seed)
    img = new_canvas()
    bx, by = 16, 26
    R = rng.uniform(13, 16)
    a0, a1 = math.radians(-150), math.radians(-30)
    for i in range(7):
        a = a0 + (a1 - a0) * i / 6
        line(img, bx, by, bx + R * math.cos(a), by + R * math.sin(a),
             BONE_C, thick=2 if i % 2 == 0 else 1)
    prev = None
    a = a0
    while a <= a1:
        x, y = bx + R * math.cos(a), by + R * math.sin(a)
        if prev:
            line(img, prev[0], prev[1], x, y, BONE_EDGE)
        prev = (x, y)
        a += 0.15
    blob(img, bx, by, 2, BONE_EDGE, rng, rough=0.1)
    return img


def skull(seed):
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16, 13 + rng.randint(-1, 1)
    fill_ellipse(img, cx, cy, 7.5, 7, BONE_C)
    for y in range(int(cy + 6), int(cy + 11)):
        for x in range(cx - 4, cx + 5):
            px(img, x, y, BONE_C)
    dark = (60, 50, 40, 255)
    fill_ellipse(img, cx - 3, cy - 1, 2, 2.4, dark)
    fill_ellipse(img, cx + 3, cy - 1, 2, 2.4, dark)
    line(img, cx, cy + 2, cx, cy + 4, dark)
    for x in range(cx - 4, cx + 5, 2):
        line(img, x, cy + 7, x, cy + 10, BONE_EDGE)
    return img


def ammonite_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16, 17
    growth = rng.uniform(1.2, 1.9)
    squash = rng.uniform(0.75, 1.0)
    prev = None
    a = 0.0
    while a < math.pi * 5:
        r = 1.1 + a * growth
        if r > 15:
            break
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a) * squash
        if prev:
            line(img, prev[0], prev[1], x, y, BONE_C, thick=2)
        prev = (x, y)
        a += 0.12
    for a_deg in range(0, 360, 30):
        a = math.radians(a_deg) + math.pi * 3
        r0 = 1.1 + (a - math.pi * 2) * growth
        r1 = min(1.1 + a * growth, 15)
        line(img, cx + r0 * math.cos(a), cy + r0 * math.sin(a) * squash,
             cx + r1 * math.cos(a), cy + r1 * math.sin(a) * squash, BONE_EDGE)
    return img


def bone_var(seed):
    rng = random.Random(seed)
    img = new_canvas()
    bone_c = (235, 225, 200, 255)
    shade = (170, 155, 125, 255)
    ang = rng.uniform(0.3, 1.2)
    length = rng.uniform(8, 10)
    cx, cy = 16, 16
    x0, y0 = cx - length * math.cos(ang), cy + length * math.sin(ang)
    x1, y1 = cx + length * math.cos(ang), cy - length * math.sin(ang)
    line(img, x0 + 1, y0 + 1, x1 + 1, y1 + 1, shade, thick=3)
    line(img, x0, y0, x1, y1, bone_c, thick=3)
    nx, ny = math.sin(ang), math.cos(ang)
    for ex, ey in ((x0, y0), (x1, y1)):
        blob(img, ex - nx * 1.8, ey - ny * 1.8, 2.2, bone_c, rng, rough=0.15)
        blob(img, ex + nx * 1.8, ey + ny * 1.8, 2.2, bone_c, rng, rough=0.15)
    return img


# --- artifacts ---------------------------------------------------------------

def pottery(seed):
    """Painted terracotta shard."""
    rng = random.Random(seed)
    img = new_canvas()
    clay = (185, 95, 55, 255)
    edge = (120, 60, 35, 255)
    deco = (70, 40, 25, 255)
    cx, cy = 16, 16
    pts = []
    n = rng.randint(5, 7)
    for i in range(n):
        a = i / n * 2 * math.pi + rng.uniform(-0.2, 0.2)
        r = rng.uniform(7, 12)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for y in range(GRID):
        xs = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
        xs.sort()
        for xa, xb in zip(xs[::2], xs[1::2]):
            for x in range(round(xa), round(xb) + 1):
                px(img, x, y, clay)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        line(img, x0, y0, x1, y1, edge)
    line(img, cx - 7, cy - 3, cx + 7, cy - 3, deco)
    zig = [(cx - 7 + i * 2.4, cy + 2 + (2 if i % 2 else -1)) for i in range(7)]
    for p0, p1 in zip(zig, zig[1:]):
        line(img, p0[0], p0[1], p1[0], p1[1], deco)
    return img


def rune_stone(seed):
    """Carved angular glyphs, 2x2 arrangement."""
    rng = random.Random(seed)
    img = new_canvas()
    carve = (35, 30, 28, 255)
    lit = (255, 255, 255, 60)
    for gx in (9, 22):
        for gy in (9, 22):
            x, y = gx, gy - 4
            for _ in range(rng.randint(2, 4)):
                dx, dy = rng.choice([(-4, 2), (4, 2), (0, 5), (-4, -2), (4, -2), (-5, 0), (5, 0)])
                line(img, x, y, x + dx, y + dy, carve)
                line(img, x + 1, y + 1, x + dx + 1, y + dy + 1, lit)
                x, y = x + dx, y + dy
    return img


def gear(seed):
    """Metal gear (tinted)."""
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16, 16
    R = rng.uniform(7, 9)
    teeth = rng.choice((8, 10, 12))
    for k in range(teeth):
        a = k / teeth * 2 * math.pi
        blob(img, cx + (R + 1.5) * math.cos(a), cy + (R + 1.5) * math.sin(a), 1.6, MID, rng, rough=0.1)
    for y in range(GRID):
        for x in range(GRID):
            d = math.hypot(x - cx, y - cy)
            if d <= R:
                px(img, x, y, MID)
            if d <= R * 0.35:
                px(img, x, y, CLEAR)  # hub hole
    for a_deg in range(200, 320, 6):
        a = math.radians(a_deg)
        px(img, cx + (R - 1) * math.cos(a), cy + (R - 1) * math.sin(a), HI)
    return img


def circuit(seed):
    """Alien circuit traces with pads (fixed teal)."""
    rng = random.Random(seed)
    img = new_canvas()
    trace = (70, 220, 180, 255)
    pad = (180, 255, 230, 255)
    for _ in range(rng.randint(4, 6)):
        x, y = rng.randrange(3, 29), rng.randrange(3, 29)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            px(img, x + dx, y + dy, pad)
        for _ in range(rng.randint(2, 3)):
            length = rng.randint(4, 9)
            if rng.random() < 0.5:
                nx2, ny2 = x + rng.choice((-1, 1)) * length, y
            else:
                nx2, ny2 = x, y + rng.choice((-1, 1)) * length
            line(img, x, y, nx2, ny2, trace)
            x, y = nx2, ny2
        px(img, x, y, pad)
    return img


# --- environment -------------------------------------------------------------

def roots(seed):
    rng = random.Random(seed)
    img = new_canvas()
    col = (90, 55, 30, 255)
    thin = (70, 42, 24, 255)
    for _ in range(rng.randint(2, 3)):
        x = rng.uniform(6, 26)
        y = 0.0
        while y < 30:
            ny2 = y + rng.uniform(4, 7)
            nx2 = x + rng.uniform(-3, 3)
            line(img, x, y, nx2, ny2, col, thick=2 if y < 14 else 1)
            if rng.random() < 0.5:
                line(img, x, y, x + rng.choice((-1, 1)) * rng.uniform(3, 6),
                     y + rng.uniform(3, 6), thin)
            x, y = nx2, ny2
    return img


def worm_tunnels(seed):
    rng = random.Random(seed)
    img = new_canvas()
    hole = (25, 15, 10, 170)
    for _ in range(rng.randint(2, 3)):
        x, y = rng.uniform(4, 28), rng.uniform(4, 28)
        a = rng.uniform(0, 6.3)
        for _ in range(rng.randint(6, 10)):
            a += rng.uniform(-0.9, 0.9)
            nx2, ny2 = x + 3 * math.cos(a), y + 3 * math.sin(a)
            line(img, x, y, nx2, ny2, hole, thick=3)
            x, y = nx2, ny2
    return img


# ---------------------------------------------------------------------------
# Registry: 9 hand-tuned originals + seeded family variants (~95 total).
# Originals keep their names (already uploaded to Roblox).
# ---------------------------------------------------------------------------

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

FAMILIES = [
    # (base name, generator(seed), variant count)
    ("ore_nuggets", ore_nuggets_var, 6),
    ("ore_crystals", ore_crystals_var, 6),
    ("rock_cracks", rock_cracks_var, 5),
    ("ore_vein", ore_vein, 5),
    ("strata", strata, 4),
    ("geode", geode, 4),
    ("agate", agate, 4),
    ("meteorite", meteorite, 4),
    ("ice_crystals", ice_crystals, 4),
    ("lava", lava_var, 4),
    ("gas_bubbles", gas_var, 4),
    ("dirt_noise", dirt_var, 4),
    ("grass_top", grass_var, 3),
    ("trilobite", trilobite, 2),
    ("fish_skeleton", fish_skeleton, 2),
    ("fern", fern, 2),
    ("footprint", footprint, 2),
    ("shell", shell, 2),
    ("skull", skull, 2),
    ("ammonite", ammonite_var, 2),
    ("bone", bone_var, 1),
    ("pottery", pottery, 2),
    ("rune_stone", rune_stone, 4),
    ("gear", gear, 2),
    ("circuit", circuit, 2),
    ("roots", roots, 2),
    ("worm_tunnels", worm_tunnels, 2),
]

for _base, _fn, _count in FAMILIES:
    _start = 2 if _base in SPRITES else 1  # v1 = hand-tuned original where one exists
    for _i in range(_count):
        SPRITES[f"{_base}_v{_start + _i}"] = (lambda fn=_fn, s=_i: fn(s * 31 + 101))

if __name__ == "__main__":
    for name, fn in SPRITES.items():
        save(fn(), name)
    print(f"total: {len(SPRITES)} sprites")
