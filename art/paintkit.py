"""Painterly renderer for Ironfist Legacy maps.

Uses the exact geometry from il_maps.py (floors, walls, doors, props, lights) but paints the result
in the same textured top-down style as the Castle Ravenloft / Last Road maps: material textures,
bevelled stone and rock walls with cast shadows, ambient occlusion, shaded sprites, blooms and mist.
Baked text labels and GM zone marks are left off the player-facing art (journal pins carry them).
"""
import re, io, math, random, json, sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import resvg_py
sys.path.insert(0, os.path.dirname(__file__))
import il_mapkit as k
from mapkit import Map
import paintlib as P
from paintlib import fbm, lerp, col, composite, smooth, voronoi_stones, ground_strokes, pine_sprite, dome_sprite, rock_sprite, paste_sprite, shade_from_height

FONTS = "/home/claude/saga/il/art/fonts"
# ------------------------------------------------------------------ interception
_orig_wall, _orig_door, _orig_window = k.ILMap.wall, Map.door, Map.window
_orig_g, _orig_glow, _orig_steam = Map.g, k.ILMap.glow, k.ILMap.steam
def _wall(self, pts, style="stone", closed=False, kind="wall", draw=True, sight="normal"):
    self.__dict__.setdefault("wallpaths", []).append((list(pts) + ([pts[0]] if closed else []), style, draw, kind))
    return _orig_wall(self, pts, style, closed, kind, draw, sight)
def _door(self, x1, y1, x2, y2, style="wood", secret=False, locked=False):
    self.__dict__.setdefault("doorlist", []).append((x1, y1, x2, y2, style, secret))
    return _orig_door(self, x1, y1, x2, y2, style, secret, locked)
def _window(self, x1, y1, x2, y2):
    self.__dict__.setdefault("windows", []).append((x1, y1, x2, y2))
    return _orig_window(self, x1, y1, x2, y2)
def _g(self, layer, x, y, inner, rot=0, scale=1, shadow=True):
    mm = re.match(r"<!--SPRITE (\w+) ([\d.]+) (\d+)-->", inner or "")
    if mm:
        self.__dict__.setdefault("sprites", []).append((mm.group(1), x, y, float(mm.group(2)) * scale, int(mm.group(3)), layer))
        return
    return _orig_g(self, layer, x, y, inner, rot, scale, shadow)
def _glow(self, x, y, r=1.0, grad="rg-lamp", layer="decal"):
    self.__dict__.setdefault("glows", []).append((x, y, r, grad))
def _steam(self, x, y, r=1.2):
    self.__dict__.setdefault("steams", []).append((x, y, r))
k.ILMap.wall = _wall; Map.door = _door; Map.window = _window; Map.g = _g; k.ILMap.glow = _glow; k.ILMap.steam = _steam
k.pine_plain = lambda r=80, seed=0: f"<!--SPRITE pine {r} {seed}-->"
k.boulder = lambda r=50, seed=0: f"<!--SPRITE boulder {r} {seed}-->"
_orig_mush = k.mushrooms
k.mushrooms = lambda n=5, spread=60, seed=0, c=None: f"<!--SPRITE mush {spread} {seed*10+n}-->"

# ------------------------------------------------------------------ materials
def rect_slabs(h, w, bw, bh, seed, base, var=12, mortar=(30, 27, 25), stagger=0.5, crack=True):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    row = (yy // bh).astype(int)
    off = (row % 2) * bw * stagger
    colx = ((xx + off) // bw).astype(int)
    cid = row * 10007 + colx
    lx = ((xx + off) % bw) / bw; ly = (yy % bh) / bh
    edge = np.minimum(np.minimum(lx, 1 - lx) * bw, np.minimum(ly, 1 - ly) * bh)
    tone = (np.sin(cid * 12.9898) * 43758.5453) % 1
    tone2 = (np.sin(cid * 78.233) * 12345.678) % 1
    base = np.array(base, np.float32)
    c = base[None, None] * (1 + (tone[..., None] - 0.5) * var / 50) + (tone2[..., None] - 0.5) * 6
    bevel = np.clip(edge / 7, 0, 1)
    lit = 1 + 0.18 * (np.clip(1 - lx * 6, 0, 1) + np.clip(1 - ly * 6, 0, 1)) - 0.22 * (np.clip(lx * 6 - 5, 0, 1) + np.clip(ly * 6 - 5, 0, 1))
    c = c * lit[..., None]
    c = c * bevel[..., None] + np.array(mortar, np.float32) * (1 - bevel[..., None])
    c *= (0.82 + 0.36 * fbm(h, w, 10, 3, seed + 1))[..., None]
    c *= (0.9 + 0.2 * fbm(h, w, 160, 3, seed + 2))[..., None]
    if crack:
        cr = np.zeros((h, w), np.uint8); r = random.Random(seed)
        for _ in range(int(h * w / 90000)):
            x, y = r.uniform(0, w), r.uniform(0, h); pts = [(x, y)]
            for _ in range(r.randint(2, 5)): x += r.uniform(-40, 40); y += r.uniform(-40, 40); pts.append((x, y))
            cv2.polylines(cr, [np.array(pts, np.int32)], False, 255, 2)
        c = composite(c, c * 0.45, cr.astype(np.float32) / 255 * 0.8)
    return c
def planks(h, w, seed, base=(92, 62, 38), bw=34, vertical=False):
    rng = random.Random(seed)
    if vertical: h, w = w, h
    out = np.zeros((h, w, 3), np.float32); y = 0
    grain = cv2.resize(fbm(max(2, h // 4), max(2, w // 40), 3, 2, seed), (w, h))
    while y < h:
        t = rng.uniform(0.72, 1.12); out[y:y + bw] = np.array(base, np.float32) * t
        x = rng.randint(-200, 0)
        while x < w:
            L = rng.randint(180, 420); out[y:y + bw, max(0, x):max(0, x) + 3] *= 0.35; x += L
        out[y:y + 3] *= 0.3; y += bw
    out *= (0.78 + 0.45 * grain)[..., None]
    out *= (0.88 + 0.24 * fbm(h, w, 8, 2, seed + 3))[..., None]
    return out.transpose(1, 0, 2).copy() if vertical else out
def metal(h, w, seed, base=(70, 70, 76), plate=200, grate=False):
    c = rect_slabs(h, w, plate, plate, seed, base, 8, (24, 24, 28), 0, False)
    yy, xx = np.mgrid[0:h, 0:w]
    if grate:
        g = ((xx % 22 < 5) | (yy % 22 < 5)).astype(np.float32)
        c = c * (0.25 + 0.75 * g[..., None])
    riv = (((xx % plate) - 14) ** 2 + ((yy % plate) - 14) ** 2 < 30).astype(np.float32)
    c = composite(c, np.broadcast_to(col((120, 118, 124)), c.shape), riv * 0.8)
    c *= (0.8 + 0.4 * fbm(h, w, 40, 3, seed + 9))[..., None]
    rust = np.clip(fbm(h, w, 90, 4, seed + 7) * 2 - 1.15, 0, 1)
    return composite(c, np.broadcast_to(col((86, 46, 26)), c.shape), rust * 0.6)
def cave_floor(h, w, seed, a=(46, 42, 38), b=(70, 62, 54)):
    c = lerp(col(a), col(b), fbm(h, w, 120, 5, seed))
    c *= (0.8 + 0.4 * fbm(h, w, 12, 3, seed + 1))[..., None]
    c = ground_strokes(c, np.ones((h, w), np.float32), seed, int(h * w / 160), (3, 9), (tuple(int(v * 0.7) for v in a), b, a), 2)
    peb = (np.random.default_rng(seed).random((h, w)) > 0.9992).astype(np.float32)
    peb = cv2.dilate(peb, np.ones((5, 5), np.uint8)); c = composite(c, c * 1.4, peb * 0.7)
    return c
def water(h, w, seed, foul=False):
    a, b = ((30, 42, 30), (58, 70, 40)) if foul else ((14, 34, 46), (34, 70, 86))
    c = lerp(col(a), col(b), fbm(h, w, 140, 5, seed))
    rip = np.sin((fbm(h, w, 60, 3, seed + 2) * 30)) * 0.5 + 0.5
    c *= (0.85 + 0.25 * rip ** 3)[..., None]
    spec = np.clip(fbm(h, w, 25, 3, seed + 4) * 3 - 2.1, 0, 1)
    return c + spec[..., None] * np.array([40, 52, 56], np.float32)
def carpet(h, w, seed, base=(96, 18, 24)):
    c = np.broadcast_to(col(base), (h, w, 3)).copy()
    yy, xx = np.mgrid[0:h, 0:w]
    weave = ((xx // 3 + yy // 3) % 2) * 0.06 + 0.97
    motif = (np.sin(xx / 34.0) * np.sin(yy / 34.0) > 0.6).astype(np.float32) * 0.25
    c *= (weave + motif)[..., None]
    c *= (0.85 + 0.3 * fbm(h, w, 60, 3, seed))[..., None]
    return c
def grassy(h, w, seed):
    c = lerp(col((32, 40, 28)), col((54, 58, 38)), fbm(h, w, 300, 5, seed))
    return ground_strokes(c, np.ones((h, w), np.float32), seed, int(h * w / 130), (5, 14), ((40, 50, 32), (66, 70, 46), (28, 34, 24)), 2)
def dirt(h, w, seed):
    c = lerp(col((62, 52, 40)), col((88, 76, 58)), fbm(h, w, 14, 3, seed))
    return ground_strokes(c, np.ones((h, w), np.float32), seed, int(h * w / 200), (3, 8), ((50, 42, 34), (96, 84, 66), (40, 34, 28)), 2)
def hexstone(h, w, seed):
    c = voronoi_stones(h, w, 70, seed, (44, 40, 40), 10, (16, 14, 14))
    ember = np.clip(fbm(h, w, 70, 4, seed + 3) * 2.2 - 1.3, 0, 1)
    return c + ember[..., None] * np.array([70, 20, 4], np.float32)
def ember_floor(h, w, seed):
    c = lerp(col((30, 14, 10)), col((120, 40, 10)), np.clip(fbm(h, w, 40, 4, seed) * 1.8 - 0.5, 0, 1))
    return c
def snow(h, w, seed, slush=False):
    c = lerp(col((150, 156, 164)), col((196, 200, 206)), fbm(h, w, 80, 4, seed))
    if slush: c = composite(c, np.broadcast_to(col((90, 86, 80)), c.shape), np.clip(fbm(h, w, 40, 4, seed + 1) * 1.6 - 0.4, 0, 1))
    return c * 0.8
def moss(h, w, seed):
    c = cave_floor(h, w, seed, (40, 38, 34), (62, 58, 50))
    m_ = np.clip(fbm(h, w, 70, 4, seed + 5) * 1.8 - 0.45, 0, 1)
    mos = lerp(col((26, 40, 24)), col((48, 70, 36)), fbm(h, w, 8, 3, seed + 6))
    return composite(c, mos, m_ * 0.85)
def mountain(h, w, seed):
    c = lerp(col((44, 42, 42)), col((86, 82, 80)), np.clip(fbm(h, w, 30, 4, seed) * 0.6 + fbm(h, w, 160, 4, seed + 1) * 0.6 - 0.1, 0, 1))
    hgt = fbm(h, w, 70, 5, seed + 2) * 1.2
    c *= (1 + 0.45 * shade_from_height(hgt, 6))[..., None]
    return ground_strokes(c, np.ones((h, w), np.float32), seed, int(h * w / 300), (4, 10), ((36, 36, 40), (74, 72, 74), (54, 52, 54)), 2)
MAT = {
    "dwarfslab": lambda h, w, s: rect_slabs(h, w, 200, 100, s, (74, 68, 60), 14, (28, 25, 22)),
    "flagstone": lambda h, w, s: voronoi_stones(h, w, 70, s, (72, 68, 62), 14, (28, 26, 24)),
    "cobble": lambda h, w, s: voronoi_stones(h, w, 32, s, (70, 66, 60), 14, (30, 27, 24)),
    "gravel": lambda h, w, s: voronoi_stones(h, w, 12, s, (72, 68, 62), 18, (40, 36, 32), gap=0.2),
    "marble": lambda h, w, s: rect_slabs(h, w, 100, 100, s, (120, 116, 112), 10, (60, 56, 54), 0, False),
    "hexstone": hexstone, "rock": cave_floor, "moss": moss, "grass": grassy, "dirt": dirt,
    "planks": lambda h, w, s: planks(h, w, s), "roof": lambda h, w, s: planks(h, w, s, (64, 40, 30), 26),
    "metal": lambda h, w, s: metal(h, w, s), "grate": lambda h, w, s: metal(h, w, s, (60, 60, 66), 100, True),
    "brass": lambda h, w, s: metal(h, w, s, (120, 90, 40), 160),
    "factory": lambda h, w, s: rect_slabs(h, w, 100, 100, s, (60, 58, 56), 12, (24, 22, 22), 0),
    "water": lambda h, w, s: water(h, w, s), "foulwater": lambda h, w, s: water(h, w, s, True),
    "carpet": lambda h, w, s: carpet(h, w, s), "rug": lambda h, w, s: carpet(h, w, s, (70, 40, 20)),
    "hellstone": lambda h, w, s: voronoi_stones(h, w, 50, s, (70, 30, 26), 14, (20, 8, 8)),
    "ember": ember_floor, "snow": lambda h, w, s: snow(h, w, s), "slush": lambda h, w, s: snow(h, w, s, True),
    "canvas": lambda h, w, s: lerp(col((120, 100, 72)), col((150, 130, 96)), fbm(h, w, 30, 3, s)),
}
WALLTEX = {"stone": "block", "dwarf": "block", "brick": "brick", "hell": "rock", "rock": "rock", "basalt": "rock", "fungal": "rock",
           "brass": "metal", "iron": "metal", "timber": "wood", "shelf": "wood", "canvas": "cloth"}
WALL_BASE = {"stone": (78, 74, 72), "dwarf": (84, 76, 66), "brick": (92, 52, 40), "hell": (70, 30, 26), "rock": (66, 60, 54),
             "basalt": (44, 42, 44), "fungal": (48, 60, 40), "brass": (128, 96, 44), "iron": (58, 56, 62), "timber": (84, 56, 34),
             "shelf": (70, 46, 28), "canvas": (120, 30, 36)}

# ------------------------------------------------------------------ helpers
def _strip(s):
    s = re.sub(r"<text\b.*?</text>", "", s, flags=re.S)
    return s
def is_floor_item(s):
    s = s.strip()
    return bool(re.fullmatch(r'<(rect|polygon|circle|path|ellipse)\b[^<>]*url\(#pt-[a-z]+\)[^<>]*/>', s))
def _is_zone(s): return 'fill-opacity="0.12"' in s and "stroke-dasharray" in s
def _svg(m, items, defs=True, bg=None, extra_attr=""):
    d = "".join(m.defs) if defs else ""
    b = f'<rect width="{m.W}" height="{m.H}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{m.W}" height="{m.H}" viewBox="0 0 {m.W} {m.H}" {extra_attr}>'
            f'<defs>{d}</defs>{b}{"".join(items)}</svg>')
def _render(svg):
    png = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], skip_system_fonts=False)
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")
def material_map(m):
    names = sorted({n for L in ("floor", "decal", "lowprop", "walls") for it in m.L[L] if is_floor_item(it) for n in re.findall(r"url\(#pt-([a-z]+)\)", it)})
    ids = {n: i + 2 for i, n in enumerate(names)}  # 0 solid/background, 1 void
    items = []
    for L in ("floor", "decal", "lowprop", "walls"):
        for it in m.L[L]:
            if is_floor_item(it):
                s = re.sub(r'(fill|stroke)="url\(#pt-([a-z]+)\)"', lambda q: f'{q.group(1)}="#{ids[q.group(2)]:02x}0000"', it)
                s = re.sub(r'stroke="#(?!..0000)[0-9a-fA-F]{6}"', 'stroke="none"', s)
                s = re.sub(r'filter="[^"]*"', "", s); s = _strip(s)
                items.append(s)
            elif re.search(r'fill="#(050404|151312)"', it) and "<text" not in it:
                items.append(re.sub(r'fill="#(050404|151312)"', 'fill="#010000"', re.sub(r'fill="url\(#hatch-void\)"', 'fill="none"', it)))
    svg = _svg(m, items, defs=False, bg="#000000", extra_attr='shape-rendering="crispEdges"')
    a = np.asarray(_render(svg))[..., 0]
    return a, ids
def bloom(img, pts, color, strength):
    h, w, _ = img.shape; acc = np.zeros((h, w), np.float32)
    for x, y, r in pts:
        cv2.circle(acc, (int(x), int(y)), max(2, int(r)), 1.0, -1)
    if not pts: return img
    acc = cv2.GaussianBlur(acc, (0, 0), max(8, np.mean([p[2] for p in pts]) * 0.6))
    return img + acc[..., None] * np.array(color, np.float32) * strength

# ------------------------------------------------------------------ main render
def paint(m, out_webp, preview=None, outdoor=None, quality=82):
    H, W, S = m.H, m.W, 100
    seed = sum(map(ord, m.key))
    lab, ids = material_map(m)
    inv = {v: n for n, v in ids.items()}
    solid = (lab == 0).astype(np.float32); void = (lab == 1).astype(np.float32)
    if outdoor is None: outdoor = "grass" in ids and (lab == ids["grass"]).mean() > 0.3
    img = np.zeros((H, W, 3), np.float32)
    # solid rock (the mass between rooms) or outdoor ground
    if outdoor:
        img[:] = grassy(H, W, seed)
    else:
        rk = lerp(col((20, 19, 18)), col((40, 37, 34)), fbm(H, W, 90, 5, seed + 1))
        rk *= (0.8 + 0.35 * fbm(H, W, 10, 3, seed + 2))[..., None]
        hgt = fbm(H, W, 60, 4, seed + 3)
        rk *= (1 + 0.35 * shade_from_height(hgt, 8))[..., None]
        img[:] = rk
    for v, n in inv.items():
        msk = (lab == v).astype(np.float32)
        if msk.sum() < 10: continue
        ys, xs = np.nonzero(msk); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        fn = (mountain if (outdoor and n == "rock") else MAT.get(n)) or (lambda h, w, s: cave_floor(h, w, s))
        tex = fn(y1 - y0, x1 - x0, seed + v * 31)
        sub = cv2.GaussianBlur(msk[y0:y1, x0:x1], (0, 0), 1.2)
        img[y0:y1, x0:x1] = composite(img[y0:y1, x0:x1], tex, sub)
    # chasms / void: depth falls away from the edge, with mist far down
    if void.sum() > 0:
        dist = cv2.distanceTransform((void > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / S
        face = np.clip(1 - dist / 1.6, 0, 1)
        strat = fbm(H, W, 7, 3, seed + 31) * 0.45 + fbm(H, W, 26, 3, seed + 32) * 0.55
        band = 0.5 + 0.5 * np.sin(dist * S / 12 + fbm(H, W, 60, 3, seed + 33) * 6)
        lum = (0.5 + 0.8 * strat) * (0.75 + 0.35 * band) * (0.3 + 0.7 * face) * 0.75
        facecol = np.stack([lum * 112, lum * 104, lum * 100], -1)
        deep = lerp(col((10, 9, 10)), col((2, 2, 3)), np.clip((dist - 1.2) / 4, 0, 1))
        vimg = composite(deep, facecol, smooth(0, 0.12, face))
        fogA = np.clip((dist - 2.5) / 4, 0, 1) * np.clip(fbm(H, W, 200, 4, seed + 41) * 1.6 - 0.35, 0, 1)
        vimg = composite(vimg, np.broadcast_to(col((70, 74, 82)), vimg.shape), fogA * 0.45)
        img = composite(img, vimg, void)
    # ---- walls
    wm = {}
    for pts, style, draw, kind in m.__dict__.get("wallpaths", []):
        if not draw: continue
        th = m.WALL_STYLE[style][2] + 16
        grp = WALLTEX.get(style, "block")
        key = (grp, style)
        if key not in wm: wm[key] = np.zeros((H, W), np.uint8)
        cv2.polylines(wm[key], [np.array([(a * S, b * S) for a, b in pts], np.int32)], False, 255, int(th), lineType=cv2.LINE_AA)
    allw = np.zeros((H, W), np.float32)
    for v in wm.values(): allw = np.maximum(allw, v.astype(np.float32) / 255)
    # ambient occlusion along walls and solid rock, then cast shadows (light from the north-west)
    occl = np.clip(allw + solid * (0 if outdoor else 1), 0, 1)
    ao = cv2.GaussianBlur(occl, (0, 0), 22); img *= (1 - 0.5 * np.clip(ao * 1.6, 0, 1) * (1 - occl))[..., None]
    sh = np.roll(np.roll(cv2.GaussianBlur(allw, (0, 0), 9), 14, 0), 11, 1)
    img *= (1 - 0.55 * sh * (1 - allw))[..., None]
    for (grp, style), mk in wm.items():
        mf = mk.astype(np.float32) / 255
        ys, xs = np.nonzero(mf > 0)
        if len(ys) == 0: continue
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        h, w = y1 - y0, x1 - x0; base = WALL_BASE.get(style, (78, 74, 72)); sd = seed + hash(style) % 999
        if grp == "block": tex = voronoi_stones(h, w, 26, sd, base, 14, (26, 24, 22), mask=mf[y0:y1, x0:x1])
        elif grp == "brick": tex = rect_slabs(h, w, 40, 20, sd, base, 14, (40, 26, 22), crack=False)
        elif grp == "rock":
            tex = lerp(col(tuple(v * 0.55 for v in base)), col(tuple(v * 1.15 for v in base)), fbm(h, w, 16, 4, sd))
            tex *= (0.8 + 0.4 * fbm(h, w, 5, 2, sd + 1))[..., None]
        elif grp == "metal": tex = metal(h, w, sd, base, 120)
        elif grp == "wood": tex = planks(h, w, sd, base, 20)
        else: tex = lerp(col(tuple(v * 0.7 for v in base)), col(base), fbm(h, w, 20, 3, sd))
        hgt = cv2.GaussianBlur(mf[y0:y1, x0:x1], (0, 0), 5)
        lit = 1 + 0.9 * shade_from_height(hgt, 30) * np.clip(1 - hgt, 0.15, 1)
        edge = np.clip(cv2.GaussianBlur(mf[y0:y1, x0:x1], (0, 0), 2.5) * 1.6, 0, 1)
        tex = tex * lit[..., None] * (0.55 + 0.45 * edge)[..., None]
        img[y0:y1, x0:x1] = composite(img[y0:y1, x0:x1], tex, mf[y0:y1, x0:x1])
    # ---- overlays: decals (stairs, rails), low props, props (SVG, labels and GM zones removed)
    def overlay(layers):
        items = []
        for L in layers:
            for it in m.L[L]:
                if is_floor_item(it) or _is_zone(it) or "rg-lamp" in it or "rg-steam" in it or "rg-fungal" in it: continue
                if re.search(r'fill="#(050404|151312)"', it): continue
                if 'fill="#e8eef4"' in it and "<ellipse" in it:
                    q = re.search(r'cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"', it)
                    if q: mists.append(tuple(float(v) for v in q.groups()))
                    continue
                items.append(_strip(it))
        if not items: return None
        return np.asarray(_render(_svg(m, items)), np.float32)
    mists = []
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    def integrate(ov, desat=0.25, dark=0.82):
        if ov is None: return
        rgb, a = ov[..., :3], ov[..., 3:] / 255
        g = rgb.mean(-1, keepdims=True); rgb = rgb * (1 - desat) + g * desat
        rgb = rgb * dark * (0.85 + 0.3 * fbm(H, W, 6, 2, seed + 77))[..., None]
        base = np.asarray(im, np.float32)
        base[..., :3] = base[..., :3] * (1 - a) + rgb * a
        im.paste(Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)))
    integrate(overlay(["decal"]), 0.3, 0.8)
    # ---- doors and windows (painted)
    d = ImageDraw.Draw(im)
    for x1, y1, x2, y2, style, secret in m.__dict__.get("doorlist", []):
        if secret: continue
        X1, Y1, X2, Y2 = x1 * S, y1 * S, x2 * S, y2 * S; L = math.hypot(X2 - X1, Y2 - Y1); ang = math.degrees(math.atan2(Y2 - Y1, X2 - X1))
        dw, dh = int(L), 26
        if style == "wood": dt = planks(dh, dw, 5, (96, 62, 34), 9, vertical=True)
        elif style == "red": dt = planks(dh, dw, 6, (110, 26, 30), 9, vertical=True)
        elif style == "brass": dt = metal(dh, dw, 7, (140, 104, 46), 60)
        else: dt = metal(dh, dw, 8, (64, 62, 68), 60)
        dimg = Image.fromarray(np.clip(dt, 0, 255).astype(np.uint8)).convert("RGBA"); dd = ImageDraw.Draw(dimg)
        dd.rectangle([0, 0, dw - 1, dh - 1], outline=(18, 12, 10, 255), width=3)
        for fx in (0.22, 0.78): dd.rectangle([int(dw * fx) - 3, 0, int(dw * fx) + 3, dh], fill=(36, 34, 38, 255))
        dd.ellipse([dw - 22, dh // 2 - 5, dw - 12, dh // 2 + 5], fill=(170, 130, 60, 255))
        dimg = dimg.rotate(-ang, expand=True, resample=Image.BICUBIC)
        paste_sprite(im, dimg, (X1 + X2) / 2, (Y1 + Y2) / 2, blur=5, sa=140)
    for x1, y1, x2, y2 in m.__dict__.get("windows", []):
        d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=(20, 16, 14, 255), width=20)
        d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=(70, 96, 112, 255), width=8)
    integrate(overlay(["lowprop"]), 0.25, 0.82)
    # ---- painted sprites (pines, boulders, glowing fungus)
    r = random.Random(seed); mushpts = []
    sprites = m.__dict__.get("sprites", [])
    pines = {}
    for kind, x, y, rad, sd, layer in sorted(sprites, key=lambda t: t[2]):
        if kind == "pine":
            R = int(rad * 0.95); key = (R // 8, sd % 6)
            if key not in pines: pines[key] = pine_sprite(max(30, key[0] * 8), sd % 6 + 3, (30, 44, 34))
            paste_sprite(im, pines[key], x * S, y * S, blur=12)
        elif kind == "boulder":
            paste_sprite(im, rock_sprite(int(rad * 0.55), sd), x * S, y * S, blur=6, sa=150)
        elif kind == "mush":
            rr = random.Random(sd)
            for i in range(rr.randint(4, 7)):
                px, py = x * S + rr.uniform(-rad, rad), y * S + rr.uniform(-rad, rad); cr = rr.uniform(8, 20)
                paste_sprite(im, dome_sprite(cr, cr * 0.9, sd + i, rr.choice([(90, 150, 70), (110, 170, 90), (70, 130, 110)]), 0.25, 0.1, 3), px, py, blur=3, sa=120)
                mushpts.append((px, py, cr * 3))
    if outdoor and "grass" in ids:
        gm = (lab == ids["grass"]).astype(np.uint8)
        busy = np.zeros((H, W), np.uint8)
        for L_ in ("lowprop", "props", "high", "decal"):
            pass
        keep = cv2.erode(gm, np.ones((150, 150), np.uint8))
        for x_, y_ in [(n_["x"], n_["y"]) for n_ in m.notes] + [(t_["x"], t_["y"]) for t_ in m.tokens]:
            cv2.circle(keep, (int(x_), int(y_)), 260, 0, -1)
        for _, x_, y_, rad_, _, _ in sprites: cv2.circle(keep, (int(x_ * S), int(y_ * S)), int(rad_ * 1.4), 0, -1)
        pts_ = []
        for _ in range(int(H * W / 9000)):
            x_, y_ = r.uniform(0, W), r.uniform(0, H)
            if keep[int(min(H - 1, y_)), int(min(W - 1, x_))] and r.random() < 0.55 and all(math.hypot(x_ - a_, y_ - b_) > 95 for a_, b_ in pts_[-40:]):
                pts_.append((x_, y_))
        for x_, y_ in sorted(pts_, key=lambda p_: p_[1]):
            R_ = r.choice(list(pines.values()) or [pine_sprite(70, 3, (30, 44, 34))]) if pines and r.random() < 0.6 else pine_sprite(int(r.uniform(56, 100)) // 8 * 8, r.randint(0, 5), (30, 44, 34))
            paste_sprite(im, R_, x_, y_, blur=12)
    integrate(overlay(["props"]), 0.22, 0.85)
    integrate(overlay(["high"]), 0.2, 0.88)
    a = np.asarray(im.convert("RGB"), np.float32)
    # ---- blooms (lamps, braziers, fungus) and steam
    lampglows = [(x * S, y * S, r_ * S) for x, y, r_, gr in m.__dict__.get("glows", [])]
    for L in m.lights:
        if L["dim"] >= 2: lampglows.append((L["x"], L["y"], min(L["dim"], 6) * 18))
    a = bloom(a, lampglows, (60, 30, 10), 0.6)
    a = bloom(a, mushpts, (20, 60, 24), 0.7)
    if mists:
        acc = np.zeros((H, W), np.float32)
        for cx_, cy_, rx_, ry_ in mists: cv2.ellipse(acc, (int(cx_), int(cy_)), (int(rx_), int(ry_)), 0, 0, 360, 1.0, -1)
        acc = cv2.GaussianBlur(acc, (0, 0), 60) * np.clip(fbm(H, W, 90, 4, seed + 8) * 1.7 - 0.25, 0, 1)
        a = composite(a, np.broadcast_to(col((176, 182, 190)), a.shape), np.clip(acc * 1.2, 0, 0.8))
    stm = m.__dict__.get("steams", [])
    if stm:
        acc = np.zeros((H, W), np.float32)
        for x, y, r_ in stm: cv2.circle(acc, (int(x * S), int(y * S)), int(r_ * S), 1.0, -1)
        acc = cv2.GaussianBlur(acc, (0, 0), 40) * np.clip(fbm(H, W, 60, 3, seed + 5) * 1.6 - 0.2, 0, 1)
        a = composite(a, np.broadcast_to(col((170, 174, 180)), a.shape), np.clip(acc, 0, 0.6))
    a = cv2.detailEnhance(np.clip(a, 0, 255).astype(np.uint8), sigma_s=6, sigma_r=0.12).astype(np.float32) * 0.65 + a * 0.35
    out = Image.fromarray(P.finish(a, seed, 0.45))
    out.save(out_webp, "WEBP", quality=quality, method=5)
    if preview:
        t = out.copy(); t.thumbnail((1600, 1600)); t.save(preview, quality=82)
    return out

# ------------------------------------------------------------------ darker light palette (same placement)
DARK = [((255, 154, 58), "#6e3412"), ((255, 216, 144), "#6b4c22"), ((255, 179, 90), "#6b4416"), ((122, 255, 138), "#1c4a2a"),
        ((255, 122, 26), "#7a3410"), ((255, 210, 122), "#5e4a18"), ((159, 198, 232), "#27344f"), ((154, 208, 255), "#1b2c52"),
        ((255, 60, 40), "#5c0f14"), ((200, 120, 255), "#3b1d5a")]
def darken_light(L):
    c = L["color"].lstrip("#"); rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    best = min(DARK, key=lambda t: sum((a - b) ** 2 for a, b in zip(t[0], rgb)))[1]
    lum = sum(rgb) / 3
    if lum < 120: best = L["color"]  # already dark
    n = dict(L); n["color"] = best; n["alpha"] = round(min(L.get("alpha", 0.35), 0.4), 2)
    n["bright"] = round(min(L["bright"], max(0.5, L["dim"] * 0.25)), 2); n["luminosity"] = 0.35
    return n
