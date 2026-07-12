# Painterly Texture Workflow

How to turn hand-painted (AI-generated) painterly textures into game-ready
Roblox block textures for Mars Miner 2D. This is the alternative art direction
to the procedural pixel textures in `tools/gen_textures.py` — **not yet a
committed decision**; it lives as a probe in the SEDIMENT BASIN biome.

The core idea is **painterly base + procedural layering**, not one fully-unique
tile per block: a few uniform base tiles, recombined at runtime with tint
jitter and stacked overlay motifs, yield hundreds of distinct-looking blocks.

---

## 1. Generate (external: Gemini / Nano Banana / AI Studio)

Generate at **1024×1024**, one sprite per image, and **attach the style
reference sheet** (`assets/painterly_style_contact_sheet_test_v2.png`) to every
prompt so 100 sprites stay consistent. On-screen a block is only ~60–90px, so
the final size is 256 — we generate big only for brushwork quality.

Every prompt starts with the **style anchor**:

> hand-painted 2D game texture, painterly style with visible brushstrokes,
> stylized semi-realistic, soft flat lighting, muted mars palette, no
> photorealism, no text, orthographic top-down view, single 1024x1024 tile

### Three categories

| Category | Examples | Background | Key rule |
|----------|----------|------------|----------|
| **base** (opaque full-bleed) | dirt, rock, lava, gas | filled edge-to-edge | uniform, **no focal shapes** |
| **overlay** (transparent motif) | pebbles, cracks, bands, dust, roots | solid magenta `#FF00FF` | sparse, "NO ground surface" |
| **ore** (transparent, tintable) | ore_nuggets, ore_crystals | solid magenta `#FF00FF` | **pale / near-greyscale** (engine tints it) |

**Base — uniform is the whole point.** A base tile with a distinct rock reads
as a repeated stamp across the block grid. Generate boring, even coverage:

> [anchor] + full-bleed edge-to-edge surface, uniform even coverage, martian
> regolith dirt, only fine small pebbles and subtle brushwork, NO large focal
> rocks, no central point of interest, consistent texture across the entire tile

Rock: same, `solid martian bedrock, fine hairline fracture network, NO large
boulders, greyer and harder-looking than dirt`. Generate **4 variants** each
(reseed, same prompt).

**Overlay — hammer "NO ground surface, magenta background"** or the model
paints a full dirt tile with the motif on top instead of motif-on-magenta.
Pools: `pebbles ×4`, `cracks ×3`, `bands ×3` (sediment character), `dust ×2`.

**Ore — pale/greyscale** so `Texture.Color3` tinting produces every ore colour
from 2 sprites.

Filenames follow `painterly_<family>_v<N>.png` (e.g. `painterly_pebbles_v1.png`).
The pipeline infers category from the family name.

---

## 2. Watermarks

- **Visible sparkle** (bottom-right, semi-transparent): consumer Gemini stamps
  it on every image. On **base** tiles it lands on the texture → the pipeline
  heals it (feathered interior clone, edges untouched). On **overlay/ore** it
  lands on magenta → keyed out for free.
- **SynthID** (invisible): in every Gemini image, survives downscaling, harms
  nothing visually. Roblox allows AI assets; leave it.
- **Cleanest fix:** generate via **Google AI Studio / Vertex** (free) — no
  visible sparkle, only SynthID. Then base tiles need no healing either.

---

## 3. Process (`tools/painterly_pipeline.py`)

```bash
# process everything in assets/painterly_textures/ -> *_256.png
python tools/painterly_pipeline.py

# one file / a family
python tools/painterly_pipeline.py --only painterly_dirt_v3
python tools/painterly_pipeline.py --kind overlay painterly_mystery_v1.png

# switches
python tools/painterly_pipeline.py --no-seamless   # base: skip self-seamless
python tools/painterly_pipeline.py --no-heal       # base: skip watermark heal (AI Studio)
```

Per category it does: **base** = heal watermark → self-seamless → 256 (RGB);
**overlay** = key magenta + despill → 256 (RGBA); **ore** = key + despill +
greyscale-normalise → 256 (RGBA). Raw `<name>.png` is never modified.

### Seamlessness — scope on purpose

The script makes each base tile **self-seamless** (rolls by half so the
original edges meet in the centre, then heals the centre cross). That's the
*only* seamlessness this game needs, and it barely even matters:

- **Self-seamless** only shows when two *same-variant* blocks touch — and tint
  jitter + variants + overlays already hide that. Nice-to-have.
- **Cross-variant seamless** (variant A's edge = variant B's edge) is
  deliberately **not** done: it would force all variants to share identical
  borders, killing the variety we want.
- **Cross-material** (dirt→rock blend / autotiling / Wang tiles) is a
  **non-goal**: each block is a discrete cube and hard material edges are
  *readability* — you should see where rock starts.

Because `StudsPerTileU/V = block size`, one tile fills one face and never
repeats within a block; neighbours are separate cubes with an edge break
between them. So none of the cross-tile seam problems of a continuous ground
plane apply here.

---

## 4. Upload

`mcp upload_image` needs http/https URLs, not local paths:

```bash
cd assets/painterly_textures
python -m http.server 8731 --bind 127.0.0.1 &
# then upload_image with http://127.0.0.1:8731/<name>_256.png
```

It returns `path -> rbxassetid://…`. Put the IDs in `Config.DECAL_IDS` under
`painterly_*` keys. Kill the server afterwards.

---

## 5. Wire into the game

All in `ReplicatedStorage.GameConfig` + `ServerStorage.WorldGrid`.

- **`Config.DECAL_IDS`** — add `painterly_<family>_vN = "rbxassetid://…"`.
- **Per biome** (`Config.Biomes[i]`):
  - `blockOverrides = { Dirt = {ids…}, Rock = {ids…}, Gas = {ids…} }` — opaque
    baked tiles replace the grayscale-sprite-on-tinted-part path.
  - `oreBase = {ids…}` — painterly ground drawn under ore sprites.
  - `overlays = { { pool = {ids…}, chance = 0..1 }, … }` — **the layering
    system**: independent overlay pools, each rolled per block, stacked on the
    base. Combinatorial variety from few tiles.
  - `deco = { pool = {ids…}, chance = … }` — the existing single deco layer
    (fossils etc.); still works, effectively overlay layer 0.

`WorldGrid.createBlock` applies, for Dirt/Rock: the base override texture, a
**per-block tint jitter** on its `Color3` (±10% brightness/warmth — breaks
identical-twin colouring for free), then every `overlays` layer by chance, then
`deco`. All textures are crop-halved together on dig (`halfwayVisual`), so
extra layers Just Work.

**Repetition fix = uniformity + jitter + overlays**, in that order of impact.
Jitter varies *colour* not *shape*, so the base must be shape-uniform; overlays
supply the shape variety on top.

---

## 6. Current state & next steps

- **Probe wired**: SEDIMENT BASIN uses painterly dirt/rock/oreBase + a demo
  roots overlay + tint jitter (marked `PAINTERLY PROBE` in config). Committed
  as experimental `232bdb2`.
- **Finding**: painterly reads well per tile; 2 base variants with focal shapes
  showed an obvious repeat grid. Layering + jitter verified working in play.
- **Next**: generate uniform `dirt ×4` + `rock ×4` and the overlay pools
  above; run the pipeline; re-wire SEDIMENT BASIN; screenshot. If the grid is
  gone → plan full migration (all ~100 sprites + every biome, or pixel ore/deco
  will clash). Watch instance count (+overlay textures × 21.6k blocks is near
  the current ceiling; chunk-loading makes it moot).
- **Decision still open**: commit fully to painterly vs. keep pixel.
