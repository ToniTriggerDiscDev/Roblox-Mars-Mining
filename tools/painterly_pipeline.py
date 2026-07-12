#!/usr/bin/env python3
"""
painterly_pipeline.py — turn raw AI-generated painterly PNGs into game-ready
Roblox textures.

Handles three categories (detected from filename, override with --kind):
  base    (dirt, rock, lava, ...) : opaque full-bleed tile.
                                     de-watermark, self-seamless, downscale.
  overlay (pebbles, cracks, bands, dust, roots, ...) : transparent motif on a
                                     magenta #FF00FF background.
                                     key magenta -> alpha, despill, downscale.
  ore     (ore_nuggets, ore_crystals) : like overlay, but kept pale/greyscale
                                     so the in-engine tint system can recolour it.

Why these steps (see docs/painterly_workflow.md for the full rationale):
  - consumer Gemini stamps a faint sparkle bottom-right -> heal it on opaque
    tiles (on magenta it just gets keyed out, so overlays skip healing).
  - blocks show ONE tile per face and are discrete cubes, so cross-variant /
    cross-material seamlessness is neither needed nor wanted; only per-tile
    self-seamless matters, and only when two same-variant blocks touch.
  - on-screen a block is ~60-90px, so 256 is the right final size.

Usage:
  python tools/painterly_pipeline.py                # process assets/painterly_textures/*.png
  python tools/painterly_pipeline.py --dir some/dir --out some/dir
  python tools/painterly_pipeline.py --only painterly_dirt_v3
  python tools/painterly_pipeline.py --kind overlay painterly_mystery_v1.png
  python tools/painterly_pipeline.py --no-seamless   # skip self-seamless on base tiles

Outputs <name>_256.png next to the sources. Raw <name>.png is never modified.
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FINAL_SIZE = 256

# filename-stem -> category. Extend as new motif families arrive.
BASE_HINTS = ("dirt", "rock", "lava", "gas", "ground", "regolith", "basalt")
ORE_HINTS = ("ore_", "nugget", "crystal")
OVERLAY_HINTS = ("pebble", "crack", "band", "dust", "root", "vein", "fleck",
                 "streak", "glyph", "shard", "deco")


def classify(stem):
    s = stem.lower()
    if any(h in s for h in ORE_HINTS):
        return "ore"
    if any(h in s for h in OVERLAY_HINTS):
        return "overlay"
    if any(h in s for h in BASE_HINTS):
        return "base"
    return "base"  # safe default: opaque full-bleed


def heal_br_watermark(im):
    """Clone-heal the Gemini sparkle in the bottom-right of an opaque tile.

    The sparkle sits ~100px in from the corner (never on the tile edges), so a
    feathered interior clone leaves the edges — and thus tiling — untouched.
    Harmless on watermark-free tiles (clones like-for-like on uniform texture).
    """
    base = im.convert("RGBA").copy()
    W, H = base.size
    bx0, by0, bx1, by1 = int(W * .776), int(H * .776), int(W * .966), int(H * .966)
    bw, bh = bx1 - bx0, by1 - by0
    src = base.crop((bx0, by0 - int(H * .26), bx0 + bw, by0 - int(H * .26) + bh))
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).ellipse((10, 10, bw - 10, bh - 10), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(bw * .11)))
    base.paste(src, (bx0, by0), mask)
    return base


def make_seamless(im, feather_frac=0.12):
    """Make an opaque tile self-tiling.

    Roll by half so the original outer edges meet in the centre (the rolled
    tile's new edges are the original continuous middle -> already seamless),
    then heal the resulting centre cross by blending a blurred copy across a
    feathered cross-mask. Ideal for uniform low-contrast base tiles; would
    slightly soften a high-detail tile (another reason bases should be uniform).
    """
    a = np.asarray(im.convert("RGB")).astype(float)
    H, W = a.shape[:2]
    r = np.roll(np.roll(a, H // 2, 0), W // 2, 1)
    f = max(8, int(min(W, H) * feather_frac))
    blur = np.asarray(Image.fromarray(r.astype("uint8"))
                      .filter(ImageFilter.GaussianBlur(f / 3))).astype(float)
    xs = np.clip(1 - np.abs(np.arange(W) - W // 2) / f, 0, 1)[None, :]
    ys = np.clip(1 - np.abs(np.arange(H) - H // 2) / f, 0, 1)[:, None]
    mask = np.maximum(xs, ys)[..., None]
    out = r * (1 - mask) + blur * mask
    return Image.fromarray(out.astype("uint8"))


def key_magenta(im, muted=False, greyscale=False):
    """Key a magenta #FF00FF background to alpha, with magenta despill.

    'magness' = min(R,B) - G is high on pink/magenta, low on earthy/grey subject.
    muted=True loosens the threshold for AI-dulled magenta (e.g. ~187,43,164).
    greyscale=True desaturates the subject so the engine tint system can recolour
    it (ores).
    """
    a = np.asarray(im.convert("RGB")).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    magness = np.minimum(r, b) - g
    lo = 45 if muted else 40
    span = 55 if muted else 60
    alpha = np.clip(1 - (magness - lo) / span, 0, 1)
    # despill: pull the magenta cast out of semi-transparent edge pixels
    r2 = np.minimum(r, g + (r - g) * 0.6)
    b2 = np.minimum(b, g)
    rgb = np.dstack([r2, g, b2])
    if greyscale:
        lum = rgb.mean(2, keepdims=True)
        rgb = 0.15 * rgb + 0.85 * lum  # near-grey, keeps a hint of material warmth
    alpha8 = (alpha * 255).astype("uint8")
    # nuke the far-corner watermark ghost (sits on background)
    h, w = alpha8.shape
    alpha8[int(h * .93):, int(w * .93):] = np.minimum(
        alpha8[int(h * .93):, int(w * .93):], 30)
    out = np.dstack([np.clip(rgb, 0, 255).astype("uint8"), alpha8])
    return Image.fromarray(out, "RGBA")


def process(path, out_dir, kind, seamless, heal):
    stem = os.path.splitext(os.path.basename(path))[0]
    im = Image.open(path)
    if kind == "base":
        if heal:
            im = heal_br_watermark(im)
        if seamless:
            im = make_seamless(im)
        fin = im.convert("RGB").resize((FINAL_SIZE, FINAL_SIZE), Image.LANCZOS)
    elif kind == "ore":
        fin = key_magenta(im, muted=False, greyscale=True).resize(
            (FINAL_SIZE, FINAL_SIZE), Image.LANCZOS)
    else:  # overlay
        muted = np.asarray(im.convert("RGB"))[5, 5].tolist()[1] > 20  # dull-ish bg
        fin = key_magenta(im, muted=muted).resize(
            (FINAL_SIZE, FINAL_SIZE), Image.LANCZOS)
    out = os.path.join(out_dir, stem + "_256.png")
    fin.save(out)
    return stem, kind, out


def main():
    ap = argparse.ArgumentParser(description="Painterly texture pipeline")
    ap.add_argument("files", nargs="*", help="specific PNG(s); default: whole --dir")
    ap.add_argument("--dir", default="assets/painterly_textures")
    ap.add_argument("--out", default=None, help="output dir (default: same as --dir)")
    ap.add_argument("--kind", choices=["base", "overlay", "ore"],
                    help="force category (default: infer from filename)")
    ap.add_argument("--only", help="substring filter on filename")
    ap.add_argument("--no-seamless", action="store_true", help="skip self-seamless on base")
    ap.add_argument("--no-heal", action="store_true", help="skip watermark heal on base")
    args = ap.parse_args()

    out_dir = args.out or args.dir
    os.makedirs(out_dir, exist_ok=True)
    if args.files:
        paths = args.files
    else:
        paths = sorted(glob.glob(os.path.join(args.dir, "*.png")))
    # never reprocess our own outputs or scratch files
    paths = [p for p in paths if not os.path.basename(p).endswith("_256.png")
             and not os.path.basename(p).startswith("_")]
    if args.only:
        paths = [p for p in paths if args.only in os.path.basename(p)]

    if not paths:
        print("no source PNGs found")
        return
    for p in paths:
        stem = os.path.splitext(os.path.basename(p))[0]
        kind = args.kind or classify(stem)
        s, k, out = process(p, out_dir, kind, not args.no_seamless, not args.no_heal)
        print(f"  {s:32s} [{k:7s}] -> {os.path.basename(out)}")
    print(f"done: {len(paths)} texture(s) -> {out_dir}")


if __name__ == "__main__":
    main()
