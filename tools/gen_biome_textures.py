# Biome-specific block sprites for SCORCHED DEPTHS and THE ANOMALY.
# Unlike the grayscale+tint base set, these bake their palette directly:
# tight per-biome color schemes so ground, hazards and accents stop clashing.
# Opaque full tiles (part color fully covered). Same 32x32 -> x8 pipeline.
#
# Usage: python gen_biome_textures.py  -> assets/textures/*.png
#        plus assets/biome_preview.png contact sheet for review.
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

GRID = 32
SCALE = 8
ROOT = Path(__file__).resolve().parent.parent / "assets"
OUT = ROOT / "textures"

# === Palettes (deliberately narrow) ===
SCORCHED = {
    "base": [(58, 48, 46, 255), (74, 62, 58, 255), (66, 55, 51, 255)],
    "light": (92, 76, 68, 255),
    "ash": (108, 94, 84, 255),
    "crack": (38, 32, 31, 255),
    "ember": (255, 120, 40, 255),
    "ember_hot": (255, 200, 90, 255),
    "ember_deep": (170, 55, 18, 255),
}
ANOMALY = {
    "base": [(42, 34, 58, 255), (54, 44, 74, 255), (48, 39, 66, 255)],
    "light": (74, 60, 98, 255),
    "crack": (28, 22, 40, 255),
    "glow": (86, 226, 255, 255),
    "glow_soft": (52, 140, 168, 255),
    "accent": (122, 92, 160, 255),
}


def new_canvas(fill=(0, 0, 0, 0)):
    return Image.new("RGBA", (GRID, GRID), fill)


def px(img, x, y, color):
    if 0 <= x < GRID and 0 <= y < GRID:
        img.putpixel((int(x), int(y)), color)


def line(img, x0, y0, x1, y1, color, thick=1):
    steps = int(max(abs(x1 - x0), abs(y1 - y0), 1)) * 2
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        for dy in range(-(thick // 2), thick - thick // 2):
            for dx in range(-(thick // 2), thick - thick // 2):
                px(img, round(x + dx), round(y + dy), color)


def jagged(img, sx, sy, ex, ey, color, rng, jitter=2.0, thick=1):
    pts = [(sx, sy)]
    n = 4
    for i in range(1, n):
        t = i / n
        pts.append((sx + (ex - sx) * t + rng.uniform(-jitter, jitter),
                    sy + (ey - sy) * t + rng.uniform(-jitter, jitter)))
    pts.append((ex, ey))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(img, x0, y0, x1, y1, color, thick)


def noise_base(pal, seed):
    """Opaque speckled ground tile from a narrow palette."""
    rng = random.Random(seed)
    img = new_canvas(pal["base"][0])
    for y in range(GRID):
        for x in range(GRID):
            r = rng.random()
            if r < 0.24:
                px(img, x, y, pal["base"][1])
            elif r < 0.34:
                px(img, x, y, pal["base"][2])
            elif r < 0.38:
                px(img, x, y, pal["light"])
    return img, rng


def blotches(img, rng, color, count, rmin=1, rmax=3):
    for _ in range(count):
        cx, cy = rng.uniform(3, GRID - 3), rng.uniform(3, GRID - 3)
        r = rng.uniform(rmin, rmax)
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if math.hypot(x - cx, y - cy) <= r * (0.8 + rng.random() * 0.4):
                    px(img, x, y, color)


# === SCORCHED DEPTHS ===

def scorched_dirt(seed, embers=False):
    img, rng = noise_base(SCORCHED, seed)
    blotches(img, rng, SCORCHED["ash"], 4, 1.5, 3.0)
    jagged(img, rng.uniform(2, 10), rng.uniform(2, 12), rng.uniform(20, 30), rng.uniform(18, 30), SCORCHED["crack"], rng)
    if embers:
        # short glowing seam
        x0, y0 = rng.uniform(6, 14), rng.uniform(14, 24)
        jagged(img, x0, y0, x0 + rng.uniform(8, 12), y0 + rng.uniform(-4, 4), SCORCHED["ember_deep"], rng, 1.2)
        jagged(img, x0 + 1, y0, x0 + rng.uniform(6, 9), y0 + rng.uniform(-3, 3), SCORCHED["ember"], rng, 1.0)
        px(img, x0 + 3, y0, SCORCHED["ember_hot"])
        px(img, x0 + 6, y0 - 1, SCORCHED["ember_hot"])
    return img


def scorched_rock(seed, glow=False):
    """Dark basalt slabs with deep joints; optional ember glow in a joint."""
    rng = random.Random(seed)
    dark = (44, 38, 38, 255)
    img = new_canvas(dark)
    for y in range(GRID):
        for x in range(GRID):
            if rng.random() < 0.18:
                px(img, x, y, (52, 45, 44, 255))
    # slab joints: 2 horizontal-ish, 2 vertical-ish
    for i in range(2):
        yy = rng.uniform(8 + i * 12, 12 + i * 12)
        jagged(img, 0, yy, 31, yy + rng.uniform(-3, 3), SCORCHED["crack"], rng, 1.5)
    for i in range(2):
        xx = rng.uniform(6 + i * 14, 12 + i * 14)
        jagged(img, xx, 0, xx + rng.uniform(-3, 3), 31, SCORCHED["crack"], rng, 1.5)
    # slab top highlights
    for _ in range(24):
        x, y = rng.randrange(GRID), rng.randrange(GRID)
        px(img, x, y, (68, 58, 55, 255))
    if glow:
        yy = rng.uniform(14, 22)
        jagged(img, rng.uniform(4, 8), yy, rng.uniform(22, 28), yy + rng.uniform(-2, 2), SCORCHED["ember_deep"], rng, 1.0)
        for _ in range(4):
            px(img, rng.uniform(8, 24), yy + rng.uniform(-1, 1), SCORCHED["ember"])
    return img


def scorched_gas(seed):
    """Sulfur smoke: pale yellow-grey bubbles on smoky base (opaque; the part's
    transparency makes the whole block translucent)."""
    rng = random.Random(seed)
    img = new_canvas((84, 78, 64, 255))
    for y in range(GRID):
        for x in range(GRID):
            if rng.random() < 0.2:
                px(img, x, y, (96, 90, 74, 255))
    sulfur = (198, 178, 92, 255)
    pale = (226, 212, 150, 255)
    for _ in range(7):
        cx, cy, r = rng.uniform(4, 28), rng.uniform(4, 28), rng.uniform(1.5, 3.5)
        for a in range(0, 360, 12):
            px(img, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), sulfur)
        px(img, cx - r * 0.4, cy - r * 0.4, pale)
    return img


# === THE ANOMALY ===

def anomaly_ground(seed):
    img, rng = noise_base(ANOMALY, seed)
    blotches(img, rng, ANOMALY["accent"], 3, 1.0, 2.2)
    jagged(img, rng.uniform(2, 10), rng.uniform(4, 14), rng.uniform(20, 30), rng.uniform(16, 28), ANOMALY["crack"], rng)
    return img


def anomaly_rock(seed, veins=True):
    """Indigo slab rock with cyan glow veins."""
    rng = random.Random(seed)
    img = new_canvas((36, 29, 50, 255))
    for y in range(GRID):
        for x in range(GRID):
            r = rng.random()
            if r < 0.2:
                px(img, x, y, (44, 36, 60, 255))
            elif r < 0.26:
                px(img, x, y, (52, 42, 70, 255))
    for i in range(2):
        yy = rng.uniform(7 + i * 13, 12 + i * 13)
        jagged(img, 0, yy, 31, yy + rng.uniform(-3, 3), ANOMALY["crack"], rng, 1.5)
    xx = rng.uniform(10, 22)
    jagged(img, xx, 0, xx + rng.uniform(-4, 4), 31, ANOMALY["crack"], rng, 1.5)
    if veins:
        # one main cyan vein + soft echo
        sx, sy = rng.uniform(2, 8), rng.uniform(18, 28)
        ex, ey = rng.uniform(22, 30), rng.uniform(4, 12)
        jagged(img, sx, sy, ex, ey, ANOMALY["glow_soft"], rng, 2.0)
        jagged(img, sx + 1, sy, (sx + ex) / 2, (sy + ey) / 2, ANOMALY["glow"], rng, 1.2)
        for _ in range(3):
            px(img, rng.uniform(sx, ex), rng.uniform(min(sy, ey), max(sy, ey)), ANOMALY["glow"])
    return img


def anomaly_gas(seed):
    """Cyan vapor bubbles on deep indigo."""
    rng = random.Random(seed)
    img = new_canvas((30, 34, 56, 255))
    for y in range(GRID):
        for x in range(GRID):
            if rng.random() < 0.18:
                px(img, x, y, (36, 42, 66, 255))
    for _ in range(7):
        cx, cy, r = rng.uniform(4, 28), rng.uniform(4, 28), rng.uniform(1.5, 3.5)
        for a in range(0, 360, 12):
            px(img, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), ANOMALY["glow_soft"])
        px(img, cx - r * 0.4, cy - r * 0.4, ANOMALY["glow"])
    return img


def anomaly_glyph(seed):
    """Deco overlay: cyan glyph etched into rock (transparent bg)."""
    rng = random.Random(seed)
    img = new_canvas()
    cx, cy = 16, 16
    # ring
    r = rng.uniform(6, 8)
    for a in range(0, 360, 6):
        px(img, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), ANOMALY["glow_soft"])
    # inner strokes
    for _ in range(rng.randrange(3, 5)):
        a0, a1 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
        line(img, cx + (r - 2) * math.cos(a0), cy + (r - 2) * math.sin(a0),
             cx + (r - 2) * math.cos(a1), cy + (r - 2) * math.sin(a1), ANOMALY["glow"])
    px(img, cx, cy, ANOMALY["glow"])
    return img


def ember_shards(seed):
    """Deco overlay: obsidian shards with ember edges (transparent bg)."""
    rng = random.Random(seed)
    img = new_canvas()
    for _ in range(3):
        bx, by = rng.uniform(6, 26), rng.uniform(10, 28)
        h = rng.uniform(5, 9)
        lean = rng.uniform(-0.4, 0.4)
        for i in range(int(h) + 1):
            t = i / h
            y = by - i
            half = max(1, (1 - t) * 2.5)
            cxx = bx + lean * i
            for x in range(round(cxx - half), round(cxx + half) + 1):
                px(img, x, y, (30, 26, 28, 255) if x < cxx else (48, 40, 42, 255))
        px(img, bx + lean * h, by - h, SCORCHED["ember"])
        px(img, bx - 1, by + 1, SCORCHED["ember_deep"])
    return img


# === Backwall deco (transparent overlays on the tunnel background wall) ===
# NOTE for wiring: BackwallColor currently multiplies deco Decal.Color3 with
# the wall color — these baked sprites must be excluded from that tint loop.

def scorched_bw_flow(seed):
    """Hardened lava flow running down the backwall, ember core."""
    rng = random.Random(seed)
    img = new_canvas()
    x = rng.uniform(10, 22)
    y = 2.0
    pts = [(x, y)]
    while y < 29:
        y += rng.uniform(2, 4)
        x += rng.uniform(-2.5, 2.5)
        pts.append((x, y))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(img, x0, y0, x1, y1, (52, 40, 38, 255), 3)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(img, x0, y0, x1, y1, SCORCHED["ember_deep"], 1)
    for _ in range(4):
        i = rng.randrange(len(pts) - 1)
        px(img, pts[i][0], pts[i][1], SCORCHED["ember"])
    # cooled bulb at the bottom
    bx, by = pts[-1]
    for dy in range(-1, 3):
        for dx in range(-3, 4):
            if abs(dx) + abs(dy) < 4:
                px(img, bx + dx, by + dy, (52, 40, 38, 255))
    px(img, bx, by, SCORCHED["ember"])
    return img


def scorched_bw_vent(seed):
    """Fumarole: dark vent cone with rising sulfur wisps."""
    rng = random.Random(seed)
    img = new_canvas()
    bx = rng.uniform(12, 20)
    by = 28
    for i in range(7):
        half = 6 - i * 0.7
        for x in range(round(bx - half), round(bx + half) + 1):
            px(img, x, by - i, (58, 48, 46, 255) if x < bx else (44, 38, 38, 255))
    px(img, bx, by - 7, SCORCHED["ember_deep"])
    # wisps
    wy = by - 9
    wx = bx
    for _ in range(9):
        px(img, wx, wy, (198, 178, 92, 180))
        wx += rng.uniform(-1.5, 1.5)
        wy -= rng.uniform(1.5, 2.5)
        if wy < 3:
            break
    return img


def anomaly_bw_conduit(seed):
    """Alien conduit: segmented pipe with cyan node lights."""
    rng = random.Random(seed)
    img = new_canvas()
    y = rng.uniform(10, 20)
    pts = [(2, y)]
    x = 2
    while x < 29:
        x += rng.uniform(4, 7)
        y += rng.uniform(-4, 4)
        pts.append((min(x, 30), max(4, min(28, y))))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(img, x0, y0, x1, y1, (60, 48, 82, 255), 3)
        line(img, x0, y0 - 1, x1, y1 - 1, (78, 62, 104, 255), 1)
    for (jx, jy) in pts[1:-1]:
        px(img, jx, jy, ANOMALY["glow"])
        px(img, jx, jy - 1, ANOMALY["glow_soft"])
    return img


def anomaly_bw_crystals(seed):
    """Cyan crystal cluster growing out of the backwall."""
    rng = random.Random(seed)
    img = new_canvas()
    bx, by = rng.uniform(12, 20), rng.uniform(20, 27)
    for _ in range(4):
        h = rng.uniform(6, 11)
        lean = rng.uniform(-0.5, 0.5)
        ox = rng.uniform(-5, 5)
        for i in range(int(h) + 1):
            t = i / h
            yy = by - i
            half = max(1, (1 - t) * 2.2)
            cxx = bx + ox + lean * i
            for x in range(round(cxx - half), round(cxx + half) + 1):
                px(img, x, yy, ANOMALY["glow_soft"] if x < cxx else (40, 90, 110, 255))
        px(img, bx + ox + lean * h, by - h, ANOMALY["glow"])
    for dx in range(-6, 7):
        px(img, bx + dx, by + 1, (36, 29, 50, 255))
    return img


def anomaly_bw_tendril(seed):
    """Violet organic tendril crawling across the wall."""
    rng = random.Random(seed)
    img = new_canvas()
    x, y = 3, rng.uniform(8, 24)
    prev = (x, y)
    while x < 29:
        nx = x + rng.uniform(3, 5)
        ny = max(5, min(27, y + rng.uniform(-5, 5)))
        line(img, prev[0], prev[1], nx, ny, ANOMALY["accent"], 2)
        # thin offshoot
        if rng.random() < 0.5:
            line(img, nx, ny, nx + rng.uniform(-2, 2), ny - rng.uniform(3, 5), (96, 72, 122, 200), 1)
        prev = (nx, ny)
        x, y = nx, ny
    for _ in range(3):
        px(img, rng.uniform(8, 26), rng.uniform(6, 26), ANOMALY["glow"])
    return img


SPRITES = {
    # Scorched Depths
    "scorched_dirt_v1": lambda: scorched_dirt(101),
    "scorched_dirt_v2": lambda: scorched_dirt(102),
    "scorched_dirt_v3": lambda: scorched_dirt(103, embers=True),
    "scorched_rock_v1": lambda: scorched_rock(111),
    "scorched_rock_v2": lambda: scorched_rock(112),
    "scorched_rock_v3": lambda: scorched_rock(113, glow=True),
    "scorched_gas_v1": lambda: scorched_gas(121),
    "scorched_gas_v2": lambda: scorched_gas(122),
    "scorched_deco_shards_v1": lambda: ember_shards(131),
    "scorched_deco_shards_v2": lambda: ember_shards(132),
    # The Anomaly
    "anomaly_ground_v1": lambda: anomaly_ground(201),
    "anomaly_ground_v2": lambda: anomaly_ground(202),
    "anomaly_rock_v1": lambda: anomaly_rock(211),
    "anomaly_rock_v2": lambda: anomaly_rock(212),
    "anomaly_rock_v3": lambda: anomaly_rock(213),
    "anomaly_gas_v1": lambda: anomaly_gas(221),
    "anomaly_gas_v2": lambda: anomaly_gas(222),
    "anomaly_deco_glyph_v1": lambda: anomaly_glyph(231),
    "anomaly_deco_glyph_v2": lambda: anomaly_glyph(232),
    # Backwall deco (foreground deco pools double as backwall pools too)
    "scorched_bw_flow_v1": lambda: scorched_bw_flow(301),
    "scorched_bw_flow_v2": lambda: scorched_bw_flow(302),
    "scorched_bw_vent_v1": lambda: scorched_bw_vent(311),
    "scorched_bw_vent_v2": lambda: scorched_bw_vent(312),
    "anomaly_bw_conduit_v1": lambda: anomaly_bw_conduit(321),
    "anomaly_bw_conduit_v2": lambda: anomaly_bw_conduit(322),
    "anomaly_bw_crystals_v1": lambda: anomaly_bw_crystals(331),
    "anomaly_bw_crystals_v2": lambda: anomaly_bw_crystals(332),
    "anomaly_bw_tendril_v1": lambda: anomaly_bw_tendril(341),
    "anomaly_bw_tendril_v2": lambda: anomaly_bw_tendril(347),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    imgs = {}
    for name, fn in SPRITES.items():
        img = fn()
        imgs[name] = img
        img.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST).save(OUT / f"{name}.png")
        print("wrote", name)

    # contact sheet: 5 columns, labeled, dark background
    cols = 5
    cell = 140
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * cell + 20), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(imgs.items()):
        cx = (i % cols) * cell
        cy = (i // cols) * cell
        big = img.resize((128, 128), Image.NEAREST)
        sheet.paste(big, (cx + 6, cy + 6), big)
        d.text((cx + 6, cy + 128 + 6), name.replace("_v", " v"), fill=(200, 200, 205))
    sheet.save(ROOT / "biome_preview.png")
    print("wrote biome_preview.png")


if __name__ == "__main__":
    main()
