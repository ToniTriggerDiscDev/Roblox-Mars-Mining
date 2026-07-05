# Builds a labeled overview grid of all generated sprites for review.
from pathlib import Path

from PIL import Image, ImageDraw

TEX = Path(__file__).resolve().parent.parent / "assets" / "textures"
OUT = TEX.parent / "contact_sheet.png"
CELL, LABEL, COLS = 96, 14, 8

files = sorted(TEX.glob("*.png"))
rows = -(-len(files) // COLS)
sheet = Image.new("RGB", (COLS * CELL, rows * (CELL + LABEL)), (45, 45, 50))
draw = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    x = (i % COLS) * CELL
    y = (i // COLS) * (CELL + LABEL)
    img = Image.open(f).convert("RGBA").resize((CELL, CELL), Image.NEAREST)
    # checkerboard behind transparency
    for cy in range(0, CELL, 12):
        for cx in range(0, CELL, 12):
            if (cx // 12 + cy // 12) % 2:
                draw.rectangle([x + cx, y + cy, x + cx + 11, y + cy + 11], fill=(62, 62, 68))
    sheet.paste(img, (x, y), img)
    draw.text((x + 2, y + CELL + 1), f.stem, fill=(235, 235, 235))
sheet.save(OUT)
print("wrote", OUT, "-", len(files), "sprites")
