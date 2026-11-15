"""Kharad-Varr: the Hold. A painted cutaway of the whole mountain that links every place in Part II.

Gridless overview scene. Every new venue is pinned to its own page (hold:<venue>), and every story
location is pinned to its district page (hold:d-<district>), which carries scene links to every map.
Geography follows the soldier's sketch (Gate Crown at the top, Lowhearth two lifts down, the Ninth
Sluice to the right, Treaty Stair and the Cinder Warrens to the left, Redoubt and Heartworks deep right).
"""
import io, json, math, random, sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw
import resvg_py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paintlib import fbm, shade_from_height, stone_blocks, finish
import il_mapkit as k

ROOT = "/home/claude/saga/il"
FONTS = f"{ROOT}/art/ttf"
W, H = 4200, 2800
KEY = "hold-map"

PROFILE = [(0, 700), (300, 670), (700, 560), (1100, 420), (1450, 270), (1800, 150), (2050, 95), (2300, 165),
           (2700, 300), (3050, 255), (3300, 195), (3600, 315), (3950, 420), (4200, 470)]

# ------------------------------------------------------------------ chambers
# key, (x0,y0,x1,y1), kind, glow, label, sub, pin page
CH = [
    ("gate-crown", (1390, 320, 1640, 450), "gate", (255, 170, 90), "Gate Crown", "upper gate · Front I", "hold:d-gate"),
    ("hammerhall", (1690, 330, 2450, 570), "hall", (255, 170, 90), "Hammerhall", "council · feast hall · offices", "hold:d-gate"),
    ("records-annex", (2510, 400, 2860, 545), "archive", (255, 200, 120), "Military Archive", "Runa's workshop", "hold:d-gate"),
    ("gilded-nail", (2200, 700, 2620, 880), "officers", (255, 190, 110), "The Gilded Nail", "officers' tavern", "hold:gilded-nail"),
    ("turning-gear", (2700, 700, 3120, 880), "casino", (255, 205, 110), "The Turning Gear", "gaming house", "hold:turning-gear"),
    ("glimmerhall", (3200, 720, 3580, 880), "enchant", (180, 130, 255), "Glimmerhall", "enchantments & wards", "hold:glimmerhall"),
    ("deep-script", (880, 1040, 1350, 1220), "rune", (230, 170, 80), "Hall of Deep Script", "rune smiths", "hold:deep-script"),
    ("anvilsong-forge", (1440, 1030, 1900, 1220), "forge", (255, 120, 40), "Anvilsong Forge", "smiths of Forge Row", "hold:anvilsong-forge"),
    ("mossbeard-remedies", (1440, 1390, 1870, 1560), "apoth", (140, 255, 150), "Mossbeard & Fernspit", "remedies · apothecary", "hold:mossbeard-remedies"),
    ("lowhearth", (1950, 1370, 2560, 1560), "hall", (255, 160, 80), "Lowhearth", "Heddra's kitchen · shrine · lifts", "hold:d-lowhearth"),
    ("low-lantern", (2630, 1390, 3020, 1560), "tavern", (255, 170, 80), "The Low Lantern", "Lowhearth tavern", "hold:low-lantern"),
    ("ember-baths", (2800, 1700, 3340, 1860), "baths", (255, 130, 60), "The Ember Baths", "Steamstair", "hold:ember-baths"),
    ("ninth-sluice", (2190, 1910, 3140, 2080), "sluice", (120, 180, 230), "The Ninth Sluice", "three galleries · the river", "hold:d-deep"),
    ("pump-bridge", (1760, 1960, 2150, 2050), "bridge", (255, 170, 90), "Pump Bridge", "the bridge both peoples need", "hold:d-deep"),
    ("treaty-stair", (1330, 1950, 1700, 2140), "stair", (255, 170, 90), "Treaty Stair", "filter station", "hold:d-deep"),
    ("pump-galleries", (3260, 2090, 3680, 2220), "sluice", (255, 150, 70), "Pump Galleries", "lower exchange · Front III", "hold:d-deep"),
    ("vanguard-redoubt", (2600, 2280, 3160, 2440), "military", (255, 120, 80), "Vanguard Redoubt", "guards the final approach", "hold:d-redoubt"),
    ("heartworks", (3290, 2440, 3980, 2700), "heart", (255, 90, 30), "The Heartworks", "regulators · Last Bastion", "hold:d-redoubt"),
]
WARRENS = [(420, 2300), (560, 2210), (820, 2190), (1080, 2230), (1340, 2280), (1380, 2420), (1250, 2530), (960, 2560),
           (640, 2540), (430, 2470)]
TUNNELS = [  # polylines, width
    ([(1640, 410), (1700, 450)], 46), ([(2450, 500), (2510, 480)], 40),
    ([(2070, 860), (3580, 860)], 44),           # Crown Market street
    ([(880, 1200), (1990, 1200)], 44),          # Forge Row street
    ([(1440, 1540), (3020, 1540)], 44),         # Lift Street, Lowhearth
    ([(2960, 1560), (3060, 1610), (2900, 1655), (3020, 1705)], 34),   # the Steamstair
    ([(2380, 1560), (2380, 1915)], 54),         # Lift Shaft IX (the Broken Descent)
    ([(2150, 2010), (2195, 2010)], 40), ([(1700, 2040), (1765, 2010)], 40),
    ([(1480, 2140), (1400, 2210), (1330, 2270)], 40),      # treaty stair down to the warrens
    ([(3140, 2030), (3260, 2150)], 40), ([(3260, 2210), (3160, 2340)], 40), ([(3160, 2420), (3300, 2520)], 44),
    ([(1360, 2440), (1960, 2450), (2120, 2440), (2600, 2370)], 42),   # the deep road and the lower bridge
]
SHAFTS = [(1985, 570, 1385), (2065, 570, 1385)]  # the two great lifts
CHASM = [(1955, 1990), (2010, 2060), (2000, 2250), (2050, 2500), (2010, 2800), (2150, 2800), (2120, 2480), (2140, 2240), (2120, 2050), (2140, 1990)]
RIVER = [(4200, 1985), (3140, 2030), (2190, 2045), (2150, 2050)]
PINS_EXTRA = [  # story locations without their own chamber
    ((620, 600), "Fifth Finger", "road fortress · 9 miles by road", "hold:d-road"),
    ((2380, 1740), "The Broken Descent", "Lift Shaft IX", "hold:d-steamstair"),
    ((2060, 2440), "The Lower Bridge", "Front II", "hold:d-deep"),
    ((860, 2370), "The Cinder Warrens", "dwellings · wells · fungal gardens", "hold:d-warrens"),
    ((620, 2470), "Korga's Command Bridge", "", "hold:d-warrens"),
    ((2900, 860), "Crown Market", "", "hold:d-market"),
    ((1180, 1200), "Forge Row", "", "hold:d-forge"),
]


def poly_mask(pts, blur=0, closed=True):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.polygon(pts, fill=255)
    a = np.asarray(m, np.float32) / 255
    return cv2.GaussianBlur(a, (0, 0), blur) if blur else a


def ragged(pts, amp, step, seed):
    r = random.Random(seed); out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step)); nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        for i in range(n):
            t = i / n; j = r.uniform(-amp, amp)
            out.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
    out.append(pts[-1]); return out


def render_svg(body, defs=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>{body}</svg>')
    png = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], skip_system_fonts=False)
    return np.asarray(Image.open(io.BytesIO(bytes(png))).convert("RGBA"), np.float32)


def over(img, rgba):
    a = rgba[..., 3:4] / 255
    return img * (1 - a) + rgba[..., :3] * a


# ------------------------------------------------------------------ interior silhouettes
INK = "#120c0a"
def furnish(kind, x0, y0, x1, y1, seed):
    r = random.Random(seed); s = []; fy = y1 - 22; cx = (x0 + x1) / 2; w = x1 - x0
    def pillar(x):
        s.append(f'<rect x="{x-9}" y="{y0+28}" width="18" height="{fy-y0-28}" fill="#3a3430" stroke="{INK}" stroke-width="4"/>'
                 f'<rect x="{x-15}" y="{y0+24}" width="30" height="10" fill="#4a4440"/>')
    def lamp(x, y, c="#ffd890"):
        s.append(f'<line x1="{x}" y1="{y0+10}" x2="{x}" y2="{y-8}" stroke="{INK}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="{INK}" stroke-width="3"/>')
    def table(x, tw=50):
        s.append(f'<rect x="{x-tw/2}" y="{fy-24}" width="{tw}" height="7" fill="#5a3418" stroke="{INK}" stroke-width="3"/>'
                 f'<rect x="{x-tw/2+4}" y="{fy-18}" width="5" height="18" fill="{INK}"/><rect x="{x+tw/2-9}" y="{fy-18}" width="5" height="18" fill="{INK}"/>')
    def barrel(x):
        s.append(f'<ellipse cx="{x}" cy="{fy-16}" rx="13" ry="17" fill="#6a4020" stroke="{INK}" stroke-width="3"/><line x1="{x-13}" y1="{fy-20}" x2="{x+13}" y2="{fy-20}" stroke="{INK}" stroke-width="2"/>')
    def figure(x, c="#2a2220"):
        s.append(f'<circle cx="{x}" cy="{fy-38}" r="7" fill="{c}"/><path d="M{x-9} {fy} L{x-8} {fy-30} Q{x} {fy-36} {x+8} {fy-30} L{x+9} {fy} Z" fill="{c}"/>')
    def shelf(x, sw=70, c=("#7aff8a", "#ffd27a", "#b88aff", "#ff8a6a")):
        for row in range(3):
            yy = y0 + 46 + row * 26
            s.append(f'<rect x="{x}" y="{yy}" width="{sw}" height="5" fill="#5a3418"/>')
            for j in range(5):
                s.append(f'<rect x="{x+4+j*13}" y="{yy-12}" width="8" height="12" rx="2" fill="{r.choice(c)}" opacity="0.85"/>')
    if kind in ("hall", "officers"):
        for x in np.linspace(x0 + 40, x1 - 40, 6 if w > 500 else 4):
            pillar(x)
        for x in np.linspace(x0 + 90, x1 - 90, 5 if w > 500 else 3):
            table(x, 70); lamp(x, y0 + 60)
        for x in np.linspace(x0 + 120, x1 - 120, 3):
            s.append(f'<rect x="{x-14}" y="{y0+34}" width="28" height="46" fill="#7a1a18" stroke="{INK}" stroke-width="3"/>'
                     f'<g transform="translate({x},{y0+52}) scale(0.16)">{k.fist_sigil(1.0)}</g>')
        for x in (x0 + 70, x1 - 140, cx + 30):
            figure(x)
    elif kind == "gate":
        s.append(f'<rect x="{x0+20}" y="{y0+30}" width="46" height="{fy-y0-30}" fill="#2a2a30" stroke="{INK}" stroke-width="4"/>')
        for i in range(5):
            s.append(f'<line x1="{x0+26+i*9}" y1="{y0+30}" x2="{x0+26+i*9}" y2="{fy}" stroke="#5a5660" stroke-width="3"/>')
        figure(cx - 20, "#3a2a20"); figure(cx + 40, "#3a2a20"); lamp(cx + 10, y0 + 60)
    elif kind == "archive":
        for x in np.arange(x0 + 20, x1 - 70, 80):
            shelf(x, 70, ("#c8b48a", "#a88a5a", "#e8d8b0"))
        table(cx, 80); lamp(cx, y0 + 50)
    elif kind in ("tavern",):
        s.append(f'<rect x="{x0+20}" y="{fy-34}" width="{w*0.35}" height="34" fill="#5a3418" stroke="{INK}" stroke-width="4"/>')
        for x in np.arange(x0 + 24, x0 + 20 + w * 0.35, 30):
            barrel(x) if False else None
        for x in np.linspace(x0 + w * 0.45, x1 - 40, 4):
            table(x, 46); lamp(x, y0 + 56 + r.uniform(-8, 8))
        for x in (x1 - 30, x1 - 58):
            barrel(x)
        s.append(f'<rect x="{x0+30}" y="{y0+40}" width="40" height="30" fill="#ff9a3a" opacity="0.9" stroke="{INK}" stroke-width="4"/>')
        for x in (x0 + w * 0.55, x0 + w * 0.75):
            figure(x)
    elif kind == "casino":
        s.append(f'<circle cx="{cx}" cy="{y0+80}" r="40" fill="#c8963a" stroke="{INK}" stroke-width="5"/><circle cx="{cx}" cy="{y0+80}" r="12" fill="{INK}"/>')
        for a in range(12):
            t = a * math.pi / 6
            s.append(f'<rect x="{cx+math.cos(t)*40-6}" y="{y0+80+math.sin(t)*40-6}" width="12" height="12" fill="#c8963a" stroke="{INK}" stroke-width="2"/>')
        for x in (x0 + 70, x1 - 70):
            s.append(f'<rect x="{x-40}" y="{fy-26}" width="80" height="9" fill="#2a5a2a" stroke="{INK}" stroke-width="3"/><rect x="{x-34}" y="{fy-17}" width="6" height="17" fill="{INK}"/><rect x="{x+28}" y="{fy-17}" width="6" height="17" fill="{INK}"/>')
            lamp(x, y0 + 46, "#ffe39a")
        for x in (x0 + 120, x1 - 130, cx + 60):
            figure(x)
    elif kind == "enchant":
        s.append(f'<circle cx="{cx+40}" cy="{fy-50}" r="44" fill="none" stroke="#b88aff" stroke-width="5" opacity="0.9"/>'
                 f'<rect x="{cx+30}" y="{fy-40}" width="20" height="40" fill="#3a2a40" stroke="{INK}" stroke-width="3"/>'
                 f'<circle cx="{cx+40}" cy="{fy-50}" r="10" fill="#e0c8ff"/>')
        shelf(x0 + 20, 80, ("#b88aff", "#8ac8ff", "#e0c8ff")); figure(cx - 30, "#2a2030")
    elif kind == "apoth":
        shelf(x0 + 20, 70); shelf(x0 + 100, 70)
        s.append(f'<path d="M{x1-120} {fy} q0 -48 45 -48 q45 0 45 48 Z" fill="#2a2a2a" stroke="{INK}" stroke-width="4"/>'
                 f'<ellipse cx="{x1-75}" cy="{fy-46}" rx="40" ry="8" fill="#7aff8a" opacity="0.9"/>')
        for x in np.arange(x1 - 60, x1 - 10, 14):
            s.append(f'<circle cx="{x}" cy="{y0+40}" r="6" fill="#9adf5a"/>')
        figure(cx, "#2a2a20"); figure(cx + 40, "#2a3a20")
    elif kind == "rune":
        for x in np.linspace(x0 + 40, x1 - 40, 5):
            pillar(x)
        for i in range(7):
            x = x0 + 70 + i * (w - 140) / 6
            glyph = ["M-10 0 l10 -24 l10 24 m-20 -8 h20", "M-8 -24 v24 m0 -12 l14 -12 m-14 12 l14 12", "M0 -24 v24 m-10 -18 l10 6 l10 -6",
                     "M-10 -24 l20 24 m0 -24 l-20 24", "M-8 0 v-24 h14 l-14 12 l14 12", "M0 -24 v24 m-10 -24 l20 12 l-20 12"][i % 6]
            s.append(f'<path transform="translate({x},{y0+96})" d="{glyph}" fill="none" stroke="#ffcf6a" stroke-width="4" stroke-linecap="round"/>')
        s.append(f'<circle cx="{cx}" cy="{fy-8}" rx="80" r="60" fill="none" stroke="#c8963a" stroke-width="4" stroke-dasharray="12 6"/>')
        figure(cx, "#2a2420")
    elif kind == "forge":
        for x in np.linspace(x0 + 70, x1 - 70, 3):
            s.append(f'<rect x="{x-38}" y="{fy-56}" width="76" height="56" fill="#3a3430" stroke="{INK}" stroke-width="4"/>'
                     f'<rect x="{x-24}" y="{fy-40}" width="48" height="22" fill="#ff8a2a"/>'
                     f'<rect x="{x-16}" y="{y0}" width="32" height="{fy-56-y0}" fill="#2a2420" stroke="{INK}" stroke-width="3"/>')
            s.append(f'<path d="M{x+44} {fy-20} h34 l-6 10 h-22 Z" fill="#4a4650" stroke="{INK}" stroke-width="3"/>')
            figure(x + 60, "#2a1a14")
    elif kind == "baths":
        for (a, b, c) in ((x0 + 30, x0 + 180, "#2a6a8a"), (x0 + 210, x1 - 30, "#2a5a7a")):
            s.append(f'<rect x="{a}" y="{fy-14}" width="{b-a}" height="22" fill="{c}" stroke="{INK}" stroke-width="3"/>')
        for x in (x0 + 280, x0 + 380, x1 - 90):
            s.append(f'<ellipse cx="{x}" cy="{fy-50}" rx="40" ry="26" fill="#e8eef4" opacity="0.18"/>')
        for x in np.linspace(x0 + 30, x1 - 30, 5):
            pillar(x)
        s.append(f'<path d="M{x0+10} {y0+40} H{x1-10}" stroke="#8a5a2a" stroke-width="10"/>')
    elif kind == "sluice":
        for x in np.linspace(x0 + 60, x1 - 60, 6 if w > 600 else 3):
            s.append(f'<rect x="{x-18}" y="{y0+26}" width="36" height="{fy-y0-60}" fill="#3a3a40" stroke="{INK}" stroke-width="4"/>'
                     f'<circle cx="{x}" cy="{y0+60}" r="14" fill="#c0283a" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<path d="M{x0+20} {y0+36} H{x1-20}" stroke="#6e5a3a" stroke-width="14"/>')
    elif kind == "military":
        for x in np.linspace(x0 + 50, x1 - 50, 5):
            s.append(f'<path d="M{x-28} {fy} l28 -60 l28 60 Z" fill="#4a2a20" stroke="{INK}" stroke-width="3"/>')
        for x in (x0 + 120, x1 - 120):
            s.append(f'<rect x="{x-14}" y="{y0+34}" width="28" height="44" fill="#7a1a18" stroke="{INK}" stroke-width="3"/>')
    elif kind == "heart":
        for x in np.linspace(x0 + 90, x1 - 90, 4):
            s.append(f'<rect x="{x-44}" y="{y0+50}" width="88" height="{fy-y0-50}" fill="#3a3430" stroke="{INK}" stroke-width="5"/>'
                     f'<circle cx="{x}" cy="{y0+110}" r="30" fill="#c8963a" stroke="{INK}" stroke-width="4"/><circle cx="{x}" cy="{y0+110}" r="10" fill="#ff7a1a"/>')
    elif kind == "stair":
        for i in range(8):
            s.append(f'<rect x="{x0+20+i*40}" y="{y0+40+i*15}" width="44" height="12" fill="#5a524a" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<rect x="{x1-90}" y="{fy-60}" width="60" height="60" fill="#3a4a5a" stroke="{INK}" stroke-width="4"/>')
    elif kind == "bridge":
        s.append(f'<rect x="{x0}" y="{fy-12}" width="{w}" height="14" fill="#5a3418" stroke="{INK}" stroke-width="4"/>')
        for x in np.arange(x0 + 10, x1, 36):
            s.append(f'<line x1="{x}" y1="{fy-12}" x2="{x}" y2="{fy-40}" stroke="{INK}" stroke-width="4"/>')
        s.append(f'<line x1="{x0}" y1="{fy-38}" x2="{x1}" y2="{fy-38}" stroke="{INK}" stroke-width="4"/>')
    return "".join(s)


def main():
    rng = random.Random(7)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # ---------------- sky
    sky = np.zeros((H, W, 3), np.float32)
    t = np.clip(yy / 800, 0, 1)[..., None]
    sky[:] = np.array([10, 12, 22], np.float32) * (1 - t) + np.array([34, 38, 52], np.float32) * t
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(0, 650)
        b = rng.uniform(120, 255); r = rng.choice([1, 1, 1, 2])
        cv2.circle(sky, (int(x), int(y)), r, (b, b, b * 1.05), -1)
    cv2.circle(sky, (3700, 150), 46, (226, 230, 214), -1)
    sky = cv2.GaussianBlur(sky, (0, 0), 0.8)
    moon_glow = np.exp(-((xx - 3700) ** 2 + (yy - 150) ** 2) / (2 * 260 ** 2))
    sky += moon_glow[..., None] * np.array([40, 44, 52], np.float32)
    # ---------------- mountain body
    prof = ragged(PROFILE, 16, 30, 3)
    mpoly = prof + [(W, H), (0, H)]
    mmask = poly_mask(mpoly)
    h1 = fbm(H, W, 220, 6, 11); h2 = fbm(H, W, 40, 4, 12)
    strata = (np.sin((yy + fbm(H, W, 300, 3, 13) * 260) / 26.0) * 0.5 + 0.5)
    hgt = h1 * 0.7 + h2 * 0.3 + strata * 0.08
    sh = shade_from_height(hgt * 60, 1.4, (-1, -1.2))
    depth = np.clip(yy / H, 0, 1)
    rock_a = np.array([42, 38, 36], np.float32); rock_b = np.array([92, 84, 76], np.float32)
    tone = np.clip(hgt * 1.1 - 0.05 + sh[..., None][..., 0] * 0.25, 0, 1)
    rock = rock_a + (rock_b - rock_a) * tone[..., None]
    rock *= (1 - depth * 0.35)[..., None]
    rock[..., 0] += depth * 10; rock[..., 2] -= depth * 6
    # strata lines
    band = (np.abs(np.sin((yy + fbm(H, W, 400, 3, 14) * 300) / 70.0)) < 0.04).astype(np.float32)
    rock *= (1 - band * 0.25)[..., None]
    # cracks
    crack = Image.new("L", (W, H), 0); dc = ImageDraw.Draw(crack)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(300, H); pts = [(x, y)]
        for _ in range(rng.randint(3, 9)):
            x += rng.uniform(-40, 40); y += rng.uniform(10, 50); pts.append((x, y))
        dc.line(pts, fill=255, width=rng.choice([2, 2, 3]))
    crack = np.asarray(crack, np.float32) / 255
    rock *= (1 - crack * 0.45)[..., None]
    # surface snow and the lit rim of the profile
    surf = np.zeros((H, W), np.float32)
    dist_in = cv2.distanceTransform((mmask > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    snow = np.clip(1 - dist_in / 46, 0, 1) * (yy < 520) * (fbm(H, W, 30, 3, 15) > 0.42)
    rock = rock * (1 - snow[..., None] * 0.85) + np.array([206, 212, 222], np.float32) * snow[..., None] * 0.85
    rim = np.clip(1 - dist_in / 12, 0, 1) * (mmask > 0.5)
    rock += rim[..., None] * 30
    img = sky * (1 - mmask[..., None]) + rock * mmask[..., None]
    # outside shadow of the mountain against the sky
    # ---------------- magma at the roots
    mag = np.clip((yy - 2450) / 350, 0, 1) * np.clip(1 - np.abs(xx - 3600) / 1300, 0, 1)
    img += (mag * (0.6 + 0.4 * fbm(H, W, 60, 3, 16)))[..., None] * np.array([150, 50, 10], np.float32)
    # ---------------- carved space mask (chambers, tunnels, shafts, chasm, warrens)
    carve = Image.new("L", (W, H), 0); d = ImageDraw.Draw(carve)
    for key, (x0, y0, x1, y1), *_ in CH:
        d.rounded_rectangle([x0, y0, x1, y1], radius=min(60, (y1 - y0) // 2), fill=255)
    for pts, wd in TUNNELS:
        d.line(pts, fill=255, width=wd, joint="curve")
        for x, y in pts:
            d.ellipse([x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2], fill=255)
    for x, ya, yb in SHAFTS:
        d.rectangle([x - 26, ya - 10, x + 26, yb + 10], fill=255)
    d.polygon(ragged(WARRENS + [WARRENS[0]], 22, 40, 5), fill=255)
    d.polygon(ragged(CHASM, 16, 30, 6), fill=255)
    carve = np.asarray(carve, np.float32) / 255
    cbin = (carve > 0.5).astype(np.uint8)
    din = cv2.distanceTransform(cbin, cv2.DIST_L2, 5)
    # back wall: dressed stone, lit by each chamber's glow
    blocks = stone_blocks(W, H, 64, 30, 21, base=(66, 60, 54), var=12, mortar=(26, 22, 20))
    light = np.zeros((H, W, 3), np.float32) + 0.28
    for key, (x0, y0, x1, y1), kind, glow, *_ in CH:
        cx, cy = (x0 + x1) / 2, y1 - 30
        rx, ry = (x1 - x0) * 0.65, (y1 - y0) * 0.9
        g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
        light += g[..., None] * (np.array(glow, np.float32) / 255) * 0.9
    for pts, wd in TUNNELS:
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            for tt in np.linspace(0, 1, max(2, int(math.hypot(xb - xa, yb - ya) / 220))):
                x, y = xa + (xb - xa) * tt, ya + (yb - ya) * tt
                g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * 60 ** 2)))
                light += g[..., None] * np.array([1.0, 0.65, 0.3], np.float32) * 0.35
    # warrens: green fungal light
    for (x, y) in ((600, 2400), (900, 2300), (1150, 2420), (760, 2500)):
        g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * 150 ** 2)))
        light += g[..., None] * np.array([0.35, 1.0, 0.45], np.float32) * 0.55
    cave = (np.array([40, 38, 34], np.float32) + fbm(H, W, 50, 5, 23)[..., None] * np.array([60, 56, 48], np.float32))
    cave *= (0.75 + 0.5 * (shade_from_height(fbm(H, W, 30, 4, 24) * 40, 1.0) * 0.5 + 0.5))[..., None]
    wm = Image.new("L", (W, H), 0); ImageDraw.Draw(wm).polygon(ragged(WARRENS + [WARRENS[0]], 22, 40, 5), fill=255)
    wm = cv2.GaussianBlur(np.asarray(wm, np.float32) / 255, (0, 0), 6)
    blocks = blocks * (1 - wm[..., None]) + cave * wm[..., None]
    inner = blocks * np.clip(light, 0, 1.6)
    ao = np.clip(din / 26, 0, 1) * 0.55 + 0.45
    inner *= ao[..., None]
    # floors: a dark slab band at the bottom of each chamber
    for key, (x0, y0, x1, y1), *_ in CH:
        inner[y1 - 22:y1, x0 + 10:x1 - 10] = inner[y1 - 22:y1, x0 + 10:x1 - 10] * 0.55 + np.array([30, 24, 20], np.float32) * 0.45
    # the chasm is void
    ch = Image.new("L", (W, H), 0); ImageDraw.Draw(ch).polygon(ragged(CHASM, 16, 30, 6), fill=255)
    chm = cv2.GaussianBlur(np.asarray(ch, np.float32) / 255, (0, 0), 3)
    deep = np.clip((yy - 1990) / 800, 0, 1)
    inner = inner * (1 - chm[..., None]) + (np.array([14, 12, 16], np.float32) * (1 - deep)[..., None] + np.array([40, 14, 8], np.float32) * deep[..., None]) * chm[..., None]
    # composite carved space with bevelled rim
    soft = cv2.GaussianBlur(carve, (0, 0), 1.5)
    img = img * (1 - soft[..., None]) + inner * soft[..., None]
    ring = (cv2.dilate(cbin, np.ones((15, 15), np.uint8)) - cbin).astype(np.float32)
    ringsh = cv2.GaussianBlur(ring, (0, 0), 2)
    img = img * (1 - ringsh[..., None] * 0.55) + np.array([120, 110, 96], np.float32) * ringsh[..., None] * 0.55
    ink = (cv2.dilate(cbin, np.ones((5, 5), np.uint8)) - cbin).astype(np.float32)
    img *= (1 - ink * 0.85)[..., None]
    # ---------------- the river and the falls into the chasm
    rv = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(rv)
    dr.line(RIVER, fill=255, width=26, joint="curve")
    dr.line([(2150, 2050), (2060, 2080), (2050, 2500), (2070, 2800)], fill=255, width=22, joint="curve")
    rvm = cv2.GaussianBlur(np.asarray(rv, np.float32) / 255, (0, 0), 2)
    wcol = np.array([40, 92, 120], np.float32) + (fbm(H, W, 14, 3, 17)[..., None] * np.array([60, 90, 100], np.float32))
    img = img * (1 - rvm[..., None] * 0.9) + wcol * rvm[..., None] * 0.9
    # ---------------- vector details (outside features, interiors, shafts, flues)
    body = []
    # the road from the mist and the Fifth Finger
    road = ragged([(0, 690), (300, 655), (560, 600), (700, 560), (1000, 455), (1250, 360), (1390, 330)], 6, 40, 8)
    body.append('<path d="M' + " L".join(f"{x:.0f} {y-10:.0f}" for x, y in road) + '" fill="none" stroke="#2a2420" stroke-width="20" stroke-linejoin="round"/>')
    body.append('<path d="M' + " L".join(f"{x:.0f} {y-10:.0f}" for x, y in road) + '" fill="none" stroke="#8a7a62" stroke-width="10" stroke-dasharray="26 14" stroke-linejoin="round"/>')
    fx, fy = 620, 590
    body.append(f'<g transform="translate({fx},{fy})">'
                f'<path d="M-120 0 V-70 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 V0 Z" fill="#3a3632" stroke="{INK}" stroke-width="6"/>'
                f'<path d="M-36 0 V-150 h12 v-16 h14 v16 h20 v-16 h14 v16 h12 V0 Z" fill="#46403a" stroke="{INK}" stroke-width="6"/>'
                f'<rect x="-10" y="-120" width="20" height="30" fill="#ffb35a"/><rect x="-90" y="-40" width="14" height="20" fill="#ffb35a"/>'
                f'<rect x="60" y="-40" width="14" height="20" fill="#ffb35a"/>'
                f'<path d="M-8 -166 v-40 h40 l-12 10 l12 10 h-40" fill="#7a1a18" stroke="{INK}" stroke-width="3"/></g>')
    # pines on the lower slopes
    for _ in range(70):
        x = rng.uniform(40, 1300)
        sy = np.interp(x, [p[0] for p in PROFILE], [p[1] for p in PROFILE])
        y = sy + rng.uniform(-6, 30); s = rng.uniform(26, 50)
        if abs(x - fx) < 160: continue
        body.append(f'<path d="M{x:.0f} {y-s*1.6:.0f} L{x+s*0.5:.0f} {y:.0f} L{x-s*0.5:.0f} {y:.0f} Z" fill="#1a2a22" stroke="{INK}" stroke-width="3"/>')
    # the Gate Crown's outer door on the mountain face
    body.append(f'<path d="M1370 450 V350 q20 -40 40 0 V450 Z" fill="#7a4a22" stroke="{INK}" stroke-width="6"/>')
    # forge flues to the surface with smoke
    for x, top in ((1555, 210), (1705, 170)):
        body.append(f'<line x1="{x}" y1="1035" x2="{x}" y2="{top}" stroke="{INK}" stroke-width="16"/><line x1="{x}" y1="1035" x2="{x}" y2="{top}" stroke="#4a3a30" stroke-width="8"/>')
        for i in range(5):
            body.append(f'<circle cx="{x + i*22 + 8}" cy="{top - 16 - i*24}" r="{16 + i*7}" fill="#8a8a90" opacity="{0.28 - i*0.045:.2f}"/>')
    # lift shafts: cables and cages
    for x, ya, yb in SHAFTS:
        body.append(f'<line x1="{x-8}" y1="{ya}" x2="{x-8}" y2="{yb}" stroke="#8a7a62" stroke-width="3"/><line x1="{x+8}" y1="{ya}" x2="{x+8}" y2="{yb}" stroke="#8a7a62" stroke-width="3"/>')
    for x, y in ((1985, 760), (2065, 1240)):
        body.append(f'<rect x="{x-22}" y="{y-26}" width="44" height="52" fill="#3a3640" stroke="{INK}" stroke-width="4"/><line x1="{x-22}" y1="{y}" x2="{x+22}" y2="{y}" stroke="#8a7a62" stroke-width="3"/><rect x="{x-8}" y="{y-14}" width="16" height="10" fill="#ffd27a"/>')
    # broken Lift Shaft IX: a cage jammed sideways
    body.append(f'<g transform="translate(2380,1800) rotate(18)"><rect x="-22" y="-26" width="44" height="52" fill="#3a3640" stroke="{INK}" stroke-width="4"/><line x1="-22" y1="-26" x2="22" y2="26" stroke="#8a7a62" stroke-width="3"/></g>')
    body.append(f'<path d="M2370 1560 l10 60 l-14 40 l12 50" fill="none" stroke="#8a7a62" stroke-width="3"/>')
    # treaty stair, the bridges
    for i in range(6):
        body.append(f'<rect x="{1470-i*30}" y="{2140+i*20}" width="40" height="10" fill="#5a524a" stroke="{INK}" stroke-width="3"/>')
    for (xa, xb, y) in ((1940, 2160, 2440),):
        body.append(f'<rect x="{xa}" y="{y}" width="{xb-xa}" height="12" fill="#5a3418" stroke="{INK}" stroke-width="4"/>')
        for x in range(xa, xb, 30):
            body.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y-24}" stroke="{INK}" stroke-width="3"/>')
    # the warrens: huts, wells, fungus
    for (x, y) in ((560, 2500), (700, 2510), (1020, 2520), (1180, 2480), (840, 2280)):
        body.append(f'<path d="M{x-34} {y} q34 -60 68 0 Z" fill="#4a3a28" stroke="{INK}" stroke-width="4"/><rect x="{x-8}" y="{y-20}" width="16" height="20" fill="#ffb35a"/>')
    for (x, y) in ((920, 2520), (1260, 2380)):
        body.append(f'<ellipse cx="{x}" cy="{y}" rx="24" ry="9" fill="#2a3a4a" stroke="{INK}" stroke-width="4"/>')
    for _ in range(40):
        x, y = rng.uniform(480, 1320), rng.uniform(2330, 2530)
        if poly_inside(WARRENS, x, y):
            r = rng.uniform(5, 14)
            body.append(f'<path d="M{x-r} {y} q{r} {-r*1.6} {2*r} 0 Z" fill="{rng.choice(["#9adf5a", "#5ac0a0", "#c8ff7a"])}" opacity="0.9"/><rect x="{x-1.5}" y="{y}" width="3" height="{r}" fill="#cfe8b0"/>')
    # korga's command bridge (a rope-and-iron span in the warrens' roof)
    body.append(f'<path d="M520 2420 Q620 2450 720 2420" fill="none" stroke="#5a3418" stroke-width="10"/><path d="M520 2420 Q620 2450 720 2420" fill="none" stroke="{INK}" stroke-width="2"/>')
    for key, (x0, y0, x1, y1), kind, *_ in CH:
        body.append(furnish(kind, x0, y0, x1, y1, sum(map(ord, key))))
    # market stalls along the Crown Market street
    for x in range(2240, 3560, 120):
        body.append(f'<path d="M{x} 880 v-26 h60 v26" fill="none" stroke="{INK}" stroke-width="3"/><path d="M{x-6} 856 h72 l-8 -12 h-56 Z" fill="{rng.choice(["#7a1a18", "#2a4a6a", "#8a6a2a"])}" stroke="{INK}" stroke-width="3"/>')
    det = render_svg("".join(body))
    img = over(img, det)
    # blooms at lit features
    acc = np.zeros((H, W), np.float32)
    for key, (x0, y0, x1, y1), kind, glow, *_ in CH:
        cv2.circle(acc, (int((x0 + x1) / 2), int(y1 - 50)), 30, 1.0, -1)
    acc = cv2.GaussianBlur(acc, (0, 0), 50)
    img += acc[..., None] * np.array([255, 160, 80], np.float32) * 0.45
    # mist at the road's end (the edge of Barovia behind them)
    mist = np.clip(1 - xx / 900, 0, 1) * np.clip(1 - np.abs(yy - 640) / 260, 0, 1) * (0.5 + 0.5 * fbm(H, W, 120, 4, 18))
    img = img * (1 - mist[..., None] * 0.75) + np.array([196, 200, 206], np.float32) * mist[..., None] * 0.75
    img = finish(img, 9, 0.35).astype(np.float32)
    # ---------------- labels, title cartouche
    lab = []
    def label(x, y, name, sub, size=40):
        lab.append(f'<text x="{x}" y="{y}" font-family="Cinzel" font-weight="700" font-size="{size}" fill="#f0e2c0" text-anchor="middle" '
                   f'stroke="#120c0a" stroke-width="{size/5:.0f}" paint-order="stroke" stroke-linejoin="round">{name.upper()}</text>')
        if sub:
            lab.append(f'<text x="{x}" y="{y+size*0.85:.0f}" font-family="EB Garamond" font-style="italic" font-size="{size*0.72:.0f}" fill="#e8d8a8" text-anchor="middle" '
                       f'stroke="#120c0a" stroke-width="{size/6:.0f}" paint-order="stroke" stroke-linejoin="round">{sub}</text>')
    for key, (x0, y0, x1, y1), kind, glow, name, sub, page in CH:
        label((x0 + x1) / 2, y0 - 16 if key not in ("pump-bridge",) else y0 - 60, name, "", 38)
        if sub:
            lab.append(f'<text x="{(x0+x1)/2}" y="{y1+34}" font-family="EB Garamond" font-style="italic" font-size="28" fill="#e8d8a8" text-anchor="middle" '
                       f'stroke="#120c0a" stroke-width="7" paint-order="stroke">{sub}</text>')
    for (x, y), name, sub, page in PINS_EXTRA:
        if name in ("Crown Market", "Forge Row"):
            lab.append(f'<text x="{x}" y="{y+70}" font-family="Cinzel" font-weight="900" font-size="34" letter-spacing="10" fill="#c8963a" text-anchor="middle" '
                       f'stroke="#120c0a" stroke-width="8" paint-order="stroke">{name.upper()}</text>')
        elif name == "Fifth Finger":
            label(x, y - 230, "The Fifth Finger", sub, 40)
        elif name == "The Cinder Warrens":
            label(x, 2170, name, sub, 44)
        else:
            label(x + (150 if "Broken" in name else 0), y + (0 if "Broken" in name else 56), name, sub, 30)
    lab.append('<text x="200" y="770" font-family="EB Garamond" font-style="italic" font-size="40" fill="#22222c" text-anchor="start">the road out of the mists</text>')
    lab.append('<text x="3600" y="2000" font-family="EB Garamond" font-style="italic" font-size="30" fill="#bcd8e8" text-anchor="middle" stroke="#120c0a" stroke-width="6" paint-order="stroke">the underground river</text>')
    lab.append('<text x="2070" y="1000" font-family="EB Garamond" font-style="italic" font-size="28" fill="#e8d8a8" text-anchor="middle" stroke="#120c0a" stroke-width="6" paint-order="stroke" transform="rotate(-90 2070 1000)">the great lifts</text>')
    # cartouche
    cx, cy = 3720, 1440
    lab.append(f'<g transform="translate({cx},{cy})"><rect x="-430" y="-150" width="860" height="300" rx="18" fill="#1a1412" fill-opacity="0.82" stroke="#c8963a" stroke-width="6"/>'
               f'<rect x="-416" y="-136" width="832" height="272" rx="12" fill="none" stroke="#6e5a3a" stroke-width="3"/>'
               f'<g transform="translate(-340,0) scale(1.05)">{k.fist_sigil(1.0)}</g>'
               f'<text x="60" y="-46" font-family="Cinzel Decorative" font-weight="900" font-size="74" fill="#efe2c0" text-anchor="middle">Kharad-Varr</text>'
               f'<text x="60" y="6" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="6" fill="#c8963a" text-anchor="middle">THE HOLD OF THE IRONFIST</text>'
               f'<text x="60" y="60" font-family="EB Garamond" font-style="italic" font-size="30" fill="#e8d8a8" text-anchor="middle">Every pin opens a place. District pins list their maps;</text>'
               f'<text x="60" y="98" font-family="EB Garamond" font-style="italic" font-size="30" fill="#e8d8a8" text-anchor="middle">venue pins open the side quests of the Hold.</text></g>')
    img = over(img, render_svg("".join(lab).replace(" & ", " &amp; ")))
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out.save(f"{ROOT}/module/assets/maps/{KEY}.webp", quality=84, method=6)
    out.resize((W // 3, H // 3)).save(f"{ROOT}/art/preview/{KEY}.jpg", quality=82)
    # ---------------- scene export
    notes = []
    for key, (x0, y0, x1, y1), kind, glow, name, sub, page in CH:
        notes.append({"x": (x0 + x1) / 2, "y": (y0 + y1) / 2 + 10, "page": page, "label": name, "icon": "book"})
    for (x, y), name, sub, page in PINS_EXTRA:
        notes.append({"x": x, "y": y if name not in ("The Cinder Warrens",) else 2300, "page": page, "label": name, "icon": "book"})
    return {"key": KEY, "name": "Kharad-Varr: The Hold", "width": W, "height": H, "grid": 0, "walls": [], "lights": [],
            "notes": notes, "tokens": [], "env": {"darkness": 0, "globalLight": True}, "sounds": []}


def poly_inside(poly, x, y):
    c = False; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


if __name__ == "__main__":
    e = main()
    p = f"{ROOT}/src/scenes.json"
    data = json.load(open(p)); data[KEY] = e; json.dump(data, open(p, "w"))
    print(KEY, len(e["notes"]), "pins")
