"""Title card and journal banner."""
import random, math, io
from chibi import DEFS, humanoid, INK, FONTS
from cast import CAST
import resvg_py
from PIL import Image

OUT = "/home/claude/il/module/assets/art"


def skyline(w, h, base, seed=3, color="#0a0406"):
    r = random.Random(seed)
    pts = [f"0,{h}"]
    x = 0
    while x < w:
        bw = r.randint(40, 120)
        bh = r.randint(60, 220)
        if r.random() < 0.18:
            pts += [f"{x},{base-bh}", f"{x+bw/2:.0f},{base-bh-r.randint(80,180)}", f"{x+bw},{base-bh}"]
        else:
            pts += [f"{x},{base-bh}", f"{x+bw},{base-bh}"]
        x += bw
    pts += [f"{w},{h}"]
    win = "".join(f'<rect x="{r.randint(0,w)}" y="{r.randint(base-200, base-20)}" width="8" height="12" fill="#ffb84a" opacity="{r.uniform(0.4,0.9):.2f}"/>' for _ in range(int(w / 25)))
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>' + win


def snow(w, h, n, seed=1):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.uniform(0,w):.0f}" cy="{r.uniform(0,h):.0f}" r="{r.uniform(1.5,5):.1f}" fill="#fff" opacity="{r.uniform(0.3,0.9):.2f}"/>' for _ in range(n))


def title():
    W, H = 1920, 1080
    boss = humanoid(CAST["red-clause"][0])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}'
           '<radialGradient id="sky" cx="0.7" cy="0.35" r="0.9"><stop offset="0" stop-color="#b3122a"/><stop offset="0.45" stop-color="#4a0610"/><stop offset="1" stop-color="#0a0204"/></radialGradient>'
           f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
           '<circle cx="1360" cy="380" r="300" fill="#ffd27a" opacity="0.18" filter="url(#glw2)"/>'
           + skyline(W, H, 900, 5, "#1a0408") + skyline(W, H, 1000, 9, "#070203")
           + f'<g transform="translate(980,60) scale(0.95)">{boss}</g>'
           + f'<rect y="{H-200}" width="{W}" height="200" fill="#070203" opacity="0.6"/>'
           + snow(W, H, 380, 2)
           + f'<text x="90" y="300" font-family="Cinzel" font-weight="700" font-size="44" fill="#ffb38a" letter-spacing="10">THE NIGHT OF THE</text>'
           + f'<text x="80" y="470" font-family="Cinzel Decorative" font-weight="900" font-size="190" fill="#f3d48a" stroke="{INK}" stroke-width="10" paint-order="stroke">Red</text>'
           + f'<text x="80" y="650" font-family="Cinzel Decorative" font-weight="900" font-size="190" fill="#f3d48a" stroke="{INK}" stroke-width="10" paint-order="stroke">Clause</text>'
           + f'<text x="90" y="735" font-family="IM FELL English" font-style="italic" font-size="38" fill="#f4dcc0">A Midwinter one-shot of infernal law · Waterdeep · Level 11</text>'
           + f'<text x="90" y="1030" font-family="Cinzel" font-weight="700" font-size="30" fill="#d8aa52" letter-spacing="4">PACTS &amp; POLYHEDRALS · ASMO &amp; BEN VALE</text>'
           + f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="#d8aa52" stroke-width="4" opacity="0.7"/></svg>')
    png = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS])
    im = Image.open(io.BytesIO(bytes(png))).convert("RGB")
    im.save(f"{OUT}/title.webp", "WEBP", quality=84)
    t = im.copy(); t.thumbnail((400, 400)); t.save(f"{OUT}/cover-thumb.webp", "WEBP", quality=80)


def banner():
    W, H = 1600, 260
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{DEFS}'
           '<linearGradient id="bn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5e0b18"/><stop offset="1" stop-color="#140406"/></linearGradient>'
           f'<rect width="{W}" height="{H}" fill="url(#bn)"/>' + skyline(W, H, 250, 7, "#0a0204") + snow(W, H, 160, 4)
           + "".join(f'<g transform="translate({x},{18}) scale(0.28)"><path d="M128 40 C80 40 70 90 70 130 C70 160 52 172 46 186 L210 186 C204 172 186 160 186 130 C186 90 176 40 128 40 Z" fill="#d8aa52" stroke="{INK}" stroke-width="8"/></g>' for x in range(60, W, 180))
           + f'<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="none" stroke="#d8aa52" stroke-width="3" opacity="0.6"/></svg>')
    png = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS])
    Image.open(io.BytesIO(bytes(png))).convert("RGB").save(f"{OUT}/banner.webp", "WEBP", quality=80)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    title(); banner(); print("ok")
