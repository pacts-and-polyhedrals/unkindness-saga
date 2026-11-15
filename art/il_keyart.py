"""Title card, journal banner, Kharad-Varr cross-section and card faces."""
import random, math, io, os, sys, textwrap
import resvg_py
from PIL import Image
from chibi import DEFS, humanoid, INK, FONTS
from il_cast import CAST, fist_emblem, tusk_emblem, i_shield
import il_icons
from icons import G

sys.path.insert(0, "/home/claude/il/src")
from cards_data import DECKS

OUT = "/home/claude/il/module/assets/art"
CARDS = "/home/claude/il/module/assets/cards"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def png(svg, w=None, h=None):
    b = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], width=w, height=h) if w else resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS])
    return Image.open(io.BytesIO(bytes(b)))


def mountains(w, h, base, seed=3, color="#0a0808", peak=380):
    r = random.Random(seed)
    pts = [f"0,{h}", f"0,{base}"]
    x = 0
    while x < w:
        x += r.randint(80, 200)
        pts.append(f"{x},{base - r.randint(60, peak)}")
        x += r.randint(60, 160)
        pts.append(f"{x},{base - r.randint(0, 80)}")
    pts.append(f"{w},{h}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'


def embers(w, h, n, seed=1):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.uniform(0,w):.0f}" cy="{r.uniform(0,h):.0f}" r="{r.uniform(1.5,4.5):.1f}" fill="{r.choice(["#ffb35a", "#ff7a1a", "#ffd27a"])}" opacity="{r.uniform(0.3,0.9):.2f}"/>' for _ in range(n))


def title():
    W, H = 1920, 1080
    bald = humanoid(CAST["baldrik"][0])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}'
           '<radialGradient id="sky" cx="0.72" cy="0.4" r="0.9"><stop offset="0" stop-color="#8a3a14"/><stop offset="0.45" stop-color="#3a1408"/><stop offset="1" stop-color="#080404"/></radialGradient>'
           f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
           '<circle cx="1380" cy="420" r="320" fill="#ff9a3a" opacity="0.18" filter="url(#glw2)"/>'
           + mountains(W, H, 760, 5, "#1e0e0a", 420) + mountains(W, H, 900, 9, "#0c0606", 260)
           + f'<g transform="translate(1560,520) scale(1.25)">{i_shield(True, x=0, y=0, rot=0)}</g>'
           + f'<g transform="translate(1060,300) scale(0.68)">{bald}</g>'
           + f'<rect y="{H-110}" width="{W}" height="110" fill="#060303" opacity="0.65"/>' + embers(W, H, 260, 2)
           + f'<text x="90" y="250" font-family="Cinzel" font-weight="700" font-size="44" fill="#ffb38a" letter-spacing="10">IRONFIST LEGACY</text>'
           + f'<text x="80" y="430" font-family="Cinzel Decorative" font-weight="900" font-size="150" fill="#f3d48a" stroke="{INK}" stroke-width="10" paint-order="stroke">The Shield</text>'
           + f'<text x="80" y="600" font-family="Cinzel Decorative" font-weight="900" font-size="150" fill="#f3d48a" stroke="{INK}" stroke-width="10" paint-order="stroke">Between Us</text>'
           + f'<text x="90" y="690" font-family="IM FELL English" font-style="italic" font-size="38" fill="#f4dcc0">A Curse of Strahd continuation · Kharad-Varr · Levels 11–13</text>'
           + f'<text x="90" y="740" font-family="IM FELL English" font-style="italic" font-size="32" fill="#d8c0a0">Twelve Sundays beneath the mountain · 29 November – 14 February</text>'
           + f'<text x="90" y="1030" font-family="Cinzel" font-weight="700" font-size="30" fill="#d8aa52" letter-spacing="4">ASMO, PACTS &amp; POLYHEDRALS (BEN VALE)</text>'
           + f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="#d8aa52" stroke-width="4" opacity="0.7"/></svg>')
    im = png(svg).convert("RGB")
    im.save(f"{OUT}/title.webp", "WEBP", quality=84)
    t = im.copy(); t.thumbnail((400, 400)); t.save(f"{OUT}/cover-thumb.webp", "WEBP", quality=80)


def banner():
    W, H = 1600, 240
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}'
           '<linearGradient id="bn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a2a10"/><stop offset="1" stop-color="#120806"/></linearGradient>'
           f'<rect width="{W}" height="{H}" fill="url(#bn)"/>' + mountains(W, H, 230, 7, "#0a0604", 160) + embers(W, H, 120, 4)
           + "".join(f'<g transform="translate({x},{70}) scale(0.45)">{fist_emblem(0, 0, 1)}</g>' for x in range(100, W, 280))
           + f'<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="none" stroke="#d8aa52" stroke-width="3" opacity="0.6"/></svg>')
    png(svg).convert("RGB").save(f"{OUT}/banner.webp", "WEBP", quality=80)


def section():
    """Kharad-Varr vertical sketch — the player handout the GM shows at arrival."""
    W, H = 1920, 1080
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}',
         '<linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3a4a"/><stop offset="1" stop-color="#6a5a4a"/></linearGradient>',
         f'<rect width="{W}" height="{H}" fill="#e8dcc0"/>',
         f'<rect width="{W}" height="{H}" fill="url(#hatch2)" opacity="0.06"/>',
         '<path d="M0 260 L300 240 L560 120 L760 40 L980 30 L1240 90 L1500 160 L1700 240 L1920 250 L1920 1080 L0 1080 Z" fill="#c8b898" stroke="#3a2a1a" stroke-width="6"/>',
         '<path d="M0 260 L300 240 L560 120 L760 40 L980 30 L1240 90 L1500 160 L1700 240 L1920 250" fill="none" stroke="#3a2a1a" stroke-width="3" stroke-dasharray="4 8" transform="translate(0,14)"/>']
    for i in range(70):
        r = random.Random(i)
        x, y = r.uniform(0, W), r.uniform(300, H)
        s.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(20,60):.0f} {r.uniform(-6,6):.0f}" stroke="#8a7a5a" stroke-width="2"/>')
    nodes = [
        (300, 220, "THE FIFTH FINGER", "road fortress · 9 miles by road", "#7a1a18"),
        (900, 150, "GATE CROWN & HAMMERHALL", "council · feast hall · military offices", "#7a1a18"),
        (900, 380, "LOWHEARTH", "two lifts down · Heddra's kitchen · shrine", "#5a3a14"),
        (1150, 560, "NINTH SLUICE", "half a day below · three galleries", "#2c4f8a"),
        (760, 650, "TREATY STAIR", "one hour by the side route", "#a86f32"),
        (560, 850, "CINDER WARRENS", "dwellings · wells · fungal gardens", "#3a5014"),
        (1300, 820, "VANGUARD REDOUBT", "two hours · guards the final approach", "#4a0c10"),
        (1600, 960, "THE HEARTWORKS", "one hour beyond · regulator · reservoir", "#3a2a50"),
    ]
    links = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
    for a, b in links:
        (x1, y1, *_), (x2, y2, *_) = nodes[a], nodes[b]
        s.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#3a2a1a" stroke-width="8" stroke-dasharray="20 12"/>')
    s.append('<path d="M900 150 L900 380" stroke="#a86f32" stroke-width="14"/><text x="920" y="270" font-family="EB Garamond" font-style="italic" font-size="26" fill="#3a2a1a">the lifts</text>')
    for (x, y, t, sub, c) in nodes:
        s.append(f'<circle cx="{x}" cy="{y}" r="34" fill="{c}" stroke="{INK}" stroke-width="7"/><circle cx="{x}" cy="{y}" r="14" fill="#efe2c0"/>')
        s.append(f'<text x="{x+50}" y="{y-4}" font-family="Cinzel" font-weight="900" font-size="34" fill="#2a1a0a" stroke="#e8dcc0" stroke-width="8" paint-order="stroke">{esc(t)}</text>')
        s.append(f'<text x="{x+50}" y="{y+30}" font-family="EB Garamond" font-style="italic" font-size="26" fill="#3a2a1a" stroke="#e8dcc0" stroke-width="6" paint-order="stroke">{esc(sub)}</text>')
    s.append(f'<g transform="translate(150,860) scale(1.1)">{fist_emblem(0, 0, 1)}</g>')
    s.append(f'<text x="70" y="1040" font-family="Cinzel" font-weight="900" font-size="46" fill="#2a1a0a">KHARAD-VARR</text>')
    s.append(f'<text x="70" y="70" font-family="IM FELL English" font-style="italic" font-size="34" fill="#3a2a1a">A soldier\'s sketch of the hold — not to scale. Lower routes are added as you learn them.</text>')
    s.append(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="#3a2a1a" stroke-width="8"/></svg>')
    png("".join(s)).convert("RGB").save(f"{OUT}/kharad-varr-section.webp", "WEBP", quality=84)


def wrap(text, width):
    return textwrap.wrap(text, width)


def card_face(deck_key, deck, card):
    key, title, icon, tag, body, foot = card
    W, H = 750, 1050
    col = deck["color"]
    spec = il_icons.ICONS[icon]
    fn = G[spec[0]]
    inner = fn(spec[1], spec[3]) if len(spec) > 3 else fn(spec[1])
    t_lines = wrap(title, 22)
    b_lines = wrap(body, 40)
    f_lines = wrap(foot, 48)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}',
         f'<radialGradient id="cb" cx="0.5" cy="0.3" r="0.9"><stop offset="0" stop-color="{col}"/><stop offset="1" stop-color="#0a0405"/></radialGradient>',
         f'<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="40" fill="url(#cb)" stroke="{INK}" stroke-width="12"/>',
         f'<rect x="28" y="28" width="{W-56}" height="{H-56}" rx="26" fill="none" stroke="#c8963a" stroke-width="5"/>',
         f'<g transform="translate({W/2-150},70) scale(1.17)">{inner}</g>']
    y = 450
    for ln in t_lines:
        s.append(f'<text x="{W/2}" y="{y}" font-family="Cinzel" font-weight="900" font-size="44" text-anchor="middle" fill="#f3d48a" stroke="{INK}" stroke-width="6" paint-order="stroke">{esc(ln)}</text>')
        y += 52
    s.append(f'<text x="{W/2}" y="{y+6}" font-family="Cinzel" font-weight="700" font-size="24" text-anchor="middle" fill="#ffb38a" letter-spacing="2">{esc(tag.upper())}</text>')
    y += 30
    s.append(f'<rect x="56" y="{y}" width="{W-112}" height="{H-y-140}" rx="16" fill="#efe2c0" stroke="{INK}" stroke-width="6"/>')
    yy = y + 52
    for ln in b_lines:
        s.append(f'<text x="80" y="{yy}" font-family="EB Garamond" font-size="32" fill="#1e140c">{esc(ln)}</text>')
        yy += 40
    fy = H - 92
    for ln in f_lines:
        s.append(f'<text x="{W/2}" y="{fy}" font-family="IM FELL English" font-style="italic" font-size="26" text-anchor="middle" fill="#e8d8b8">{esc(ln)}</text>')
        fy += 30
    s.append("</svg>")
    png("".join(s), W, H).convert("RGBA").save(f"{CARDS}/{deck_key}-{key}.webp", "WEBP", quality=86)


def card_back(deck_key, deck):
    W, H = 750, 1050
    col = deck["color"]
    fn = G[deck["back_icon"]]
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}'
         f'<radialGradient id="cb" cx="0.5" cy="0.5" r="0.8"><stop offset="0" stop-color="{col}"/><stop offset="1" stop-color="#0a0405"/></radialGradient>'
         f'<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="40" fill="url(#cb)" stroke="{INK}" stroke-width="12"/>'
         f'<rect x="28" y="28" width="{W-56}" height="{H-56}" rx="26" fill="none" stroke="#c8963a" stroke-width="5"/>'
         f'<rect x="50" y="50" width="{W-100}" height="{H-100}" rx="20" fill="url(#hatch2)" opacity="0.25"/>'
         f'<circle cx="{W/2}" cy="{H/2-40}" r="230" fill="#0a0405" stroke="#c8963a" stroke-width="8"/>'
         f'<g transform="translate({W/2-192},{H/2-232}) scale(1.5)">{fn()}</g>'
         f'<text x="{W/2}" y="{H-150}" font-family="Cinzel" font-weight="900" font-size="38" text-anchor="middle" fill="#f3d48a">THE SHIELD</text>'
         f'<text x="{W/2}" y="{H-104}" font-family="Cinzel" font-weight="900" font-size="38" text-anchor="middle" fill="#f3d48a">BETWEEN US</text></svg>')
    png(s, W, H).convert("RGBA").save(f"{CARDS}/{deck_key}-back.webp", "WEBP", quality=86)


def cards():
    os.makedirs(CARDS, exist_ok=True)
    for dk, d in DECKS.items():
        card_back(dk, d)
        for c in d["cards"]:
            card_face(dk, d, c)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    title(); banner(); section(); cards(); print("ok")
