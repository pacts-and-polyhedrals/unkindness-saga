"""Ironfist Legacy map kit: subterranean / dwarven textures and props on top of the shared vector map kit."""
import math, random
from mapkit import Map, INK, GRID
import props as pr


class ILMap(Map):
    WALL_STYLE = dict(Map.WALL_STYLE)
    WALL_STYLE.update({
        "rock": ("#3a3532", "#5a524a", 40),
        "dwarf": ("#4a4440", "#8a7a62", 34),
        "fungal": ("#2a3424", "#4e6a34", 36),
        "basalt": ("#262426", "#4a4448", 36),
    })

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.defs.append('<linearGradient id="lg-water" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a6a8a"/>'
                         '<stop offset="1" stop-color="#123a52"/></linearGradient>')
        self.defs.append('<radialGradient id="rg-steam"><stop offset="0" stop-color="#e8eef4" stop-opacity="0.75"/>'
                         '<stop offset="1" stop-color="#e8eef4" stop-opacity="0"/></radialGradient>')
        self.defs.append('<radialGradient id="rg-fungal"><stop offset="0" stop-color="#b8ff7a" stop-opacity="0.7"/>'
                         '<stop offset="1" stop-color="#4aff5a" stop-opacity="0"/></radialGradient>')
        self.defs.append('<radialGradient id="rg-lamp"><stop offset="0" stop-color="#ffd890" stop-opacity="0.75"/>'
                         '<stop offset="1" stop-color="#ff9a3a" stop-opacity="0"/></radialGradient>')

    def wall(self, pts, style="stone", closed=False, kind="wall", draw=True, sight="normal"):
        super().wall(pts, style, closed, kind, draw, sight)
        if draw and style in ("rock", "fungal", "basalt"):
            if closed:
                pts = list(pts) + [pts[0]]
            d = "M" + " L".join(f"{self.P(a):.1f} {self.P(b):.1f}" for a, b in pts)
            light = self.WALL_STYLE[style][1]
            self.add("walls", f'<path d="{d}" fill="none" stroke="{light}" stroke-width="10" stroke-dasharray="6 22 14 30" stroke-linejoin="round" opacity="0.8"/>')
        if draw and style == "dwarf":
            if closed:
                pts = list(pts) + [pts[0]]
            d = "M" + " L".join(f"{self.P(a):.1f} {self.P(b):.1f}" for a, b in pts)
            self.add("walls", f'<path d="{d}" fill="none" stroke="#8a7a62" stroke-width="12" stroke-dasharray="40 10" stroke-linejoin="round" opacity="0.8"/>')
            self.add("walls", f'<path d="{d}" fill="none" stroke="#c8963a" stroke-width="4" stroke-dasharray="4 96" stroke-linecap="round"/>')

    def pattern(self, name):
        if name in self.pat_done:
            return f"url(#pt-{name})"
        r = random.Random(sum(map(ord, name)) * 7)
        T = 400
        body = []
        if name == "rock":
            body.append(f'<rect width="{T}" height="{T}" fill="#3a3430"/>')
            for _ in range(60):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(20,70):.0f}" ry="{r.uniform(12,40):.0f}" transform="rotate({r.uniform(0,180):.0f} {x:.0f} {y:.0f})" '
                            f'fill="{r.choice(["#463e38", "#4e453e", "#342e2a", "#3e3632", "#52483f"])}" opacity="0.9"/>')
            for _ in range(26):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(-30,30):.0f} {r.uniform(-30,30):.0f} l{r.uniform(-20,20):.0f} {r.uniform(-20,20):.0f}" stroke="#1e1a18" stroke-width="2.5" fill="none" opacity="0.7"/>')
            for _ in range(40):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(2,6):.0f}" fill="#6a5e52" opacity="0.6"/>')
        elif name == "hexstone":
            body.append(f'<rect width="{T}" height="{T}" fill="#2a2624"/>')
            s = 50
            h = s * math.sqrt(3) / 2
            row = 0
            y = -h
            while y < T + h:
                x0 = 0 if row % 2 == 0 else s * 0.75
                x = x0 - s * 1.5
                while x < T + s:
                    pts = " ".join(f"{x + s/2*math.cos(a):.1f},{y + s/2*math.sin(a):.1f}" for a in [i * math.pi / 3 for i in range(6)])
                    c = r.choice(["#5a524a", "#544c45", "#605850", "#4c4540", "#665c52"])
                    body.append(f'<polygon points="{pts}" fill="{c}" stroke="{INK}" stroke-width="3"/>')
                    x += s * 1.5
                y += h / 2 * 1.0 + h / 2
                row += 1
        elif name == "dwarfslab":
            body.append(f'<rect width="{T}" height="{T}" fill="#26221f"/>')
            for gy in range(0, T, 100):
                for gx in range(-200, T, 200):
                    off = 100 if (gy // 100) % 2 else 0
                    c = r.choice(["#5e564c", "#585046", "#645a50", "#524a42"])
                    body.append(f'<rect x="{gx+off+3}" y="{gy+3}" width="194" height="94" rx="4" fill="{c}" stroke="{INK}" stroke-width="3"/>')
                    body.append(f'<path d="M{gx+off+20} {gy+20} h40 m-40 0 v14" stroke="#7a6e5e" stroke-width="3" opacity="0.6"/>')
            for gy in range(0, T, 100):
                body.append(f'<rect x="-200" y="{gy}" width="0" height="0"/>')
        elif name == "water":
            body.append(f'<rect width="{T}" height="{T}" fill="#1c4a62"/>')
            for _ in range(36):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<path d="M{x:.0f} {y:.0f} q15 -8 30 0 t30 0" stroke="#5aa0c0" stroke-width="3" fill="none" opacity="0.7"/>')
            for _ in range(16):
                body.append(f'<ellipse cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" rx="{r.uniform(20,60):.0f}" ry="{r.uniform(6,14):.0f}" fill="#2a6a8a" opacity="0.6"/>')
        elif name == "foulwater":
            body.append(f'<rect width="{T}" height="{T}" fill="#2a3a2a"/>')
            for _ in range(36):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<path d="M{x:.0f} {y:.0f} q15 -8 30 0 t30 0" stroke="#6a8a4a" stroke-width="3" fill="none" opacity="0.7"/>')
            for _ in range(18):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(3,9):.0f}" fill="#8aa04a" opacity="0.6"/>')
        elif name == "moss":
            body.append(f'<rect width="{T}" height="{T}" fill="#2a3022"/>')
            for _ in range(70):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(15,50):.0f}" ry="{r.uniform(10,30):.0f}" fill="{r.choice(["#34402a", "#3e4c30", "#2e3826", "#465636"])}" opacity="0.85"/>')
            for _ in range(30):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(2,5):.0f}" fill="#9adf5a" opacity="0.55"/>')
        elif name == "metal":
            body.append(f'<rect width="{T}" height="{T}" fill="#2a2a30"/>')
            for gy in range(0, T, 100):
                for gx in range(0, T, 100):
                    c = r.choice(["#46464e", "#4c4c54", "#40404a", "#50505a"])
                    body.append(f'<rect x="{gx+2}" y="{gy+2}" width="96" height="96" fill="{c}" stroke="{INK}" stroke-width="3"/>')
                    for cx, cy in ((10, 10), (90, 10), (10, 90), (90, 90)):
                        body.append(f'<circle cx="{gx+cx}" cy="{gy+cy}" r="4.5" fill="#8a7a5a" stroke="{INK}" stroke-width="1.5"/>')
                    if r.random() < 0.35:
                        body.append(f'<path d="M{gx+20} {gy+r.randint(25,75)} l{r.randint(20,60)} {r.randint(-8,8)}" stroke="#6a4a2a" stroke-width="4" opacity="0.5"/>')
        elif name == "dirt":
            body.append(f'<rect width="{T}" height="{T}" fill="#6a5a44"/>')
            for _ in range(80):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(8,30):.0f}" ry="{r.uniform(5,16):.0f}" fill="{r.choice(["#7a6a50", "#5e5040", "#84745a", "#64563f"])}" opacity="0.8"/>')
            for _ in range(50):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(2,5):.0f}" fill="#4a4034"/>')
        elif name == "grass":
            body.append(f'<rect width="{T}" height="{T}" fill="#3e5230"/>')
            for _ in range(60):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(20,60):.0f}" ry="{r.uniform(12,30):.0f}" fill="{r.choice(["#46603a", "#4e6a3e", "#384a2c", "#5a7044"])}" opacity="0.8"/>')
            for _ in range(120):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<path d="M{x:.0f} {y:.0f} l-3 -10 M{x:.0f} {y:.0f} l3 -9" stroke="#6a8a4a" stroke-width="2"/>')
            for _ in range(30):
                body.append(f'<ellipse cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" rx="{r.uniform(8,22):.0f}" ry="5" fill="#e8eef4" opacity="0.7"/>')
        elif name == "gravel":
            body.append(f'<rect width="{T}" height="{T}" fill="#4a4440"/>')
            for _ in range(260):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(3,9):.0f}" fill="{r.choice(["#5e5650", "#6a625a", "#3e3834", "#706860"])}" stroke="{INK}" stroke-width="1"/>')
        elif name == "ember":
            body.append(f'<rect width="{T}" height="{T}" fill="#2a1410"/>')
            for _ in range(50):
                x, y = r.uniform(0, T), r.uniform(0, T)
                body.append(f'<path d="M{x:.0f} {y:.0f} l{r.uniform(-40,40):.0f} {r.uniform(-40,40):.0f}" stroke="#ff7a1a" stroke-width="{r.uniform(2,5):.1f}" opacity="0.7"/>')
            for _ in range(40):
                body.append(f'<circle cx="{r.uniform(0,T):.0f}" cy="{r.uniform(0,T):.0f}" r="{r.uniform(3,10):.0f}" fill="#ffb35a" opacity="0.5"/>')
        else:
            return super().pattern(name)
        self.pat_done.add(name)
        self.defs.append(f'<pattern id="pt-{name}" width="{T}" height="{T}" patternUnits="userSpaceOnUse">{"".join(body)}</pattern>')
        return f"url(#pt-{name})"

    # ---------------------------------------------------------------- helpers
    def cave(self, pts, tex="rock", style="rock", seed=0, jag=0.25, draw_floor=True, wall=True):
        """Irregular cave outline: polygon floor + rock wall along a jittered outline."""
        rr = random.Random(seed)
        jp = []
        for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1]):
            n = max(1, int(math.hypot(c - a, d - b) / 1.5))
            for i in range(n):
                t = i / n
                jp.append((a + (c - a) * t + rr.uniform(-jag, jag), b + (d - b) * t + rr.uniform(-jag, jag)))
        if draw_floor:
            self.floor_poly(jp, tex, stroke=False)
        if wall:
            self.wall(jp, style, closed=True)
        else:
            d = "M" + " L".join(f"{self.P(a):.1f} {self.P(b):.1f}" for a, b in jp) + " Z"
            light = self.WALL_STYLE[style][1]
            self.add("walls", f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="16" stroke-linejoin="round" filter="url(#sh)"/>'
                              f'<path d="{d}" fill="none" stroke="{light}" stroke-width="6" stroke-dasharray="6 22 14 30" stroke-linejoin="round" opacity="0.8"/>')
        return jp

    def open(self, x1, y1, x2, y2, tex="rock"):
        """Cut every wall segment out of the rectangle (grid units) and paint floor over the drawn rock."""
        X1, Y1, X2, Y2 = map(self.P, (x1, y1, x2, y2))
        out = []
        for w in self.walls:
            ax, ay, bx, by = w["c"]
            dx, dy = bx - ax, by - ay
            t0, t1 = 0.0, 1.0
            ok = True
            for p_, q_ in ((-dx, ax - X1), (dx, X2 - ax), (-dy, ay - Y1), (dy, Y2 - ay)):
                if p_ == 0:
                    if q_ < 0:
                        ok = False
                        break
                else:
                    t = q_ / p_
                    if p_ < 0:
                        t0 = max(t0, t)
                    else:
                        t1 = min(t1, t)
            if not ok or t0 >= t1 or w.get("kind") in ("door", "secret"):
                out.append(w)
                continue
            for (s0, s1) in ((0.0, t0), (t1, 1.0)):
                if s1 - s0 > 1e-3 and math.hypot(dx * (s1 - s0), dy * (s1 - s0)) > 4:
                    nw = dict(w)
                    nw["c"] = [ax + dx * s0, ay + dy * s0, ax + dx * s1, ay + dy * s1]
                    out.append(nw)
        self.walls = out
        if tex:
            self.add("walls", f'<rect x="{X1}" y="{Y1}" width="{X2-X1}" height="{Y2-Y1}" fill="{self.pattern(tex)}"/>')

    def fill_rock(self):
        """Solid rock everywhere (the void between caves)."""
        self.add("floor", f'<rect width="{self.W}" height="{self.H}" fill="#151312"/>')
        self.add("floor", f'<rect width="{self.W}" height="{self.H}" fill="url(#hatch-void)" opacity="0.6"/>')
        if "hv" not in self.pat_done:
            self.pat_done.add("hv")
            self.defs.append(f'<pattern id="hatch-void" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(40)">'
                             f'<line x1="0" y1="0" x2="0" y2="22" stroke="#2a2624" stroke-width="5"/></pattern>')

    def water_poly(self, pts, foul=False):
        d = " ".join(f"{self.P(a):.0f},{self.P(b):.0f}" for a, b in pts)
        self.add("decal", f'<polygon points="{d}" fill="{self.pattern("foulwater" if foul else "water")}" stroke="{INK}" stroke-width="6"/>')

    def chasm(self, x, y, w, h):
        self.add("floor", f'<rect x="{self.P(x)}" y="{self.P(y)}" width="{self.P(w)}" height="{self.P(h)}" fill="#050404"/>')
        self.add("floor", f'<rect x="{self.P(x)}" y="{self.P(y)}" width="{self.P(w)}" height="{self.P(h)}" fill="url(#hatch-void)" opacity="0.35"/>')

    def steam(self, x, y, r=1.2):
        self.add("high", f'<circle cx="{self.P(x)}" cy="{self.P(y)}" r="{self.P(r)}" fill="url(#rg-steam)"/>')

    def glow(self, x, y, r=1.0, grad="rg-lamp", layer="decal"):
        self.add(layer, f'<circle cx="{self.P(x)}" cy="{self.P(y)}" r="{self.P(r)}" fill="url(#{grad})"/>')

    def label(self, x, y, s, size=34, color="#e8d8a8", rot=0):
        self.text(x, y, s, size=size, color=color, rot=rot)

    def elev(self, x, y, s):
        self.text(x, y, s, size=24, color="#9ad0ff", font="EB Garamond", weight=600, layer="label")

    def pipe(self, pts, w=26, fill="#6e5a3a"):
        self.add("lowprop", pr.pipe_run([(self.P(a), self.P(b)) for a, b in pts], w, fill))

    def stair(self, x, y, w, h, n=6, vertical=True):
        """Staircase drawn in grid units; steps run across the shorter side."""
        out = [f'<rect x="{self.P(x)}" y="{self.P(y)}" width="{self.P(w)}" height="{self.P(h)}" fill="#5a524a" stroke="{INK}" stroke-width="5"/>']
        for i in range(1, n):
            if vertical:
                yy = self.P(y + h * i / n)
                out.append(f'<line x1="{self.P(x)}" y1="{yy:.0f}" x2="{self.P(x+w)}" y2="{yy:.0f}" stroke="{INK}" stroke-width="4"/>'
                           f'<line x1="{self.P(x)}" y1="{yy+6:.0f}" x2="{self.P(x+w)}" y2="{yy+6:.0f}" stroke="#7a6e62" stroke-width="3"/>')
            else:
                xx = self.P(x + w * i / n)
                out.append(f'<line x1="{xx:.0f}" y1="{self.P(y)}" x2="{xx:.0f}" y2="{self.P(y+h)}" stroke="{INK}" stroke-width="4"/>'
                           f'<line x1="{xx+6:.0f}" y1="{self.P(y)}" x2="{xx+6:.0f}" y2="{self.P(y+h)}" stroke="#7a6e62" stroke-width="3"/>')
        self.add("decal", "".join(out))

    def railing(self, x1, y1, x2, y2):
        self.add("props", f'<line x1="{self.P(x1)}" y1="{self.P(y1)}" x2="{self.P(x2)}" y2="{self.P(y2)}" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
                          f'<line x1="{self.P(x1)}" y1="{self.P(y1)}" x2="{self.P(x2)}" y2="{self.P(y2)}" stroke="#8a7a5a" stroke-width="7" stroke-linecap="round" stroke-dasharray="30 6"/>')

    def walkway(self, x, y, w, h, tex="metal"):
        self.floor_rect(x, y, w, h, tex, layer="lowprop")

    def mark_zone(self, x, y, w, h, color="#ff7a1a", label=None):
        self.add("decal", f'<rect x="{self.P(x)}" y="{self.P(y)}" width="{self.P(w)}" height="{self.P(h)}" fill="{color}" fill-opacity="0.12" '
                          f'stroke="{color}" stroke-width="8" stroke-dasharray="30 18"/>')
        if label:
            self.text(x + w / 2, y + h / 2 + 0.15, label, size=26, color=color, layer="decal")


# =========================================================================== props (pixels; 100 px = 5 ft)
def S(w=5):
    return f'stroke="{INK}" stroke-width="{w}"'


def fist_sigil(s=1.0, c="#efe2c0"):
    return (f'<g transform="scale({s})"><rect x="-6" y="-70" width="12" height="140" fill="#5a5660" {S(4)}/>'
            f'<path d="M-40 -30 h80 v46 q0 26 -30 26 h-20 q-30 0 -30 -26 Z" fill="{c}" {S(5)}/>'
            + "".join(f'<path d="M{-40+k*20} -30 v-16 q10 -10 20 0 v16" fill="{c}" {S(4)}/>' for k in range(4)) + '</g>')


def tusk_sigil(s=1.0):
    return (f'<g transform="scale({s})"><circle r="44" fill="#3a2a14" {S(5)}/>'
            f'<path d="M-22 22 Q-32 -14 -8 -36 Q-16 0 -4 22 Z M22 22 Q32 -14 8 -36 Q16 0 4 22 Z" fill="#efe2c0" {S(4)}/></g>')


def forge(w=220, h=160):
    return (pr.rect(w, h, "#3a3640", 14, 7)
            + f'<rect x="{-w/2+20}" y="{-h/2+20}" width="{w-40}" height="{h-40}" rx="10" fill="#1a0c08" {S(5)}/>'
            + f'<rect x="{-w/2+30}" y="{-h/2+30}" width="{w-60}" height="{h-60}" rx="8" fill="url(#rg-fire)"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="8" fill="#ffd27a"/>' for x, y in ((-30, 0), (10, -16), (34, 10), (-6, 20))))


def anvil():
    return (f'<path d="M-70 -24 H40 Q90 -24 84 -4 Q50 -4 40 10 V24 H-50 V10 Q-70 0 -70 -24 Z" fill="#4a4650" {S(5)}/>'
            f'<path d="M-60 -20 H30" stroke="#8a8f99" stroke-width="5"/>')


def valve_wheel(r=60, c="#c0283a"):
    return (f'<circle r="{r}" fill="none" stroke="{INK}" stroke-width="22"/><circle r="{r}" fill="none" stroke="{c}" stroke-width="11"/>'
            + "".join(f'<line x1="0" y1="0" x2="{math.cos(a)*r:.0f}" y2="{math.sin(a)*r:.0f}" stroke="{INK}" stroke-width="16"/><line x1="0" y1="0" x2="{math.cos(a)*r:.0f}" y2="{math.sin(a)*r:.0f}" stroke="{c}" stroke-width="7"/>' for a in [i*math.pi/3 for i in range(6)])
            + f'<circle r="{r*0.28:.0f}" fill="url(#lg-brass)" {S(5)}/>')


def gauge(r=34):
    return (f'<circle r="{r}" fill="#efe2c0" {S(5)}/><circle r="{r}" fill="none" stroke="url(#lg-brass)" stroke-width="6"/>'
            f'<path d="M0 0 L{r*0.7:.0f} {-r*0.4:.0f}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{r*0.5:.0f} {-r*0.6:.0f} A{r*0.78:.0f} {r*0.78:.0f} 0 0 1 {r*0.78:.0f} {r*0.1:.0f}" stroke="#c0283a" stroke-width="6" fill="none"/>')


def pump(w=160, h=110):
    return (pr.rect(w, h, "#3a3640", 16, 6) + f'<circle cx="{-w/4}" cy="0" r="{h/3}" fill="url(#lg-brass)" {S(5)}/>'
            + f'<circle cx="{w/4}" cy="0" r="{h/3}" fill="url(#lg-iron)" {S(5)}/>' + f'<g transform="translate({w/4},0)">{valve_wheel(h/4)}</g>')


def lift_cage(w=220, h=220, jammed=False):
    s = [pr.rect(w, h, "#2a2624", 6, 8)]
    for i in range(1, 6):
        s.append(f'<line x1="{-w/2+i*w/6:.0f}" y1="{-h/2}" x2="{-w/2+i*w/6:.0f}" y2="{h/2}" stroke="#8a7a5a" stroke-width="6"/>')
    s.append(f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" fill="none" stroke="url(#lg-brass)" stroke-width="10"/>')
    s.append(f'<circle r="24" fill="url(#lg-iron)" {S(5)}/><line x1="0" y1="0" x2="0" y2="{-h/2}" stroke="{INK}" stroke-width="8"/>')
    if jammed:
        s.append(f'<path d="M{-w/2} {-h/2} L{w/2} {h/2}" stroke="#c0283a" stroke-width="6" stroke-dasharray="18 10"/>')
    return "".join(s)


def feast_table(w=900, h=110, seed=0, cloth="#7a1a18"):
    r = random.Random(seed)
    s = [pr.rect(w, h, "#5a3418", 8, 6), f'<rect x="{-w/2+10}" y="{-h/2+16}" width="{w-20}" height="{h-32}" fill="{cloth}" opacity="0.85"/>']
    for i in range(int(w // 80)):
        x = -w / 2 + 40 + i * 80
        for sy in (-1, 1):
            s.append(f'<circle cx="{x}" cy="{sy*h*0.28:.0f}" r="14" fill="#c8ccd6" {S(3)}/><circle cx="{x}" cy="{sy*h*0.28:.0f}" r="7" fill="{r.choice(["#8a4a2a", "#d8a050", "#5a8a3a"])}"/>')
        if i % 3 == 1:
            s.append(f'<rect x="{x-12}" y="-16" width="24" height="32" rx="4" fill="url(#lg-brass)" {S(3)}/>')
    return "".join(s)


def bench_row(w=900):
    return pr.rect(w, 34, "#4a2c14", 6, 5)


def brazier(r=40, lit=True):
    return (f'<circle r="{r}" fill="url(#lg-iron)" {S(6)}/><circle r="{r*0.7:.0f}" fill="#1a0c08"/>'
            + (f'<circle r="{r*0.6:.0f}" fill="url(#rg-fire)"/>' if lit else ""))


def mushrooms(n=5, spread=60, seed=0, c=("#9adf5a", "#c8ff7a", "#5ac0a0")):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, rr = r.uniform(-spread, spread), r.uniform(-spread, spread), r.uniform(12, 30)
        col = r.choice(c)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr*1.8:.0f}" fill="{col}" opacity="0.18"/><circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.0f}" fill="{col}" {S(4)}/>'
                   f'<circle cx="{x-rr*0.3:.0f}" cy="{y-rr*0.3:.0f}" r="{rr*0.25:.0f}" fill="#efe2c0" opacity="0.8"/>')
    return "".join(out)


def bunk(w=90, h=200):
    return pr.rect(w, h, "#5a3418", 6, 5) + f'<rect x="{-w/2+8}" y="{-h/2+8}" width="{w-16}" height="{h-16}" fill="#8a7a62" {S(3)}/><rect x="{-w/2+12}" y="{-h/2+12}" width="{w-24}" height="40" rx="10" fill="#d8ccb0" {S(3)}/>'


def weapon_rack(w=200):
    return (pr.rect(w, 36, "#4a2c14", 4, 5) + "".join(
        f'<line x1="{-w/2+20+i*30}" y1="-40" x2="{-w/2+20+i*30}" y2="40" stroke="#c8ccd6" stroke-width="7"/><path d="M{-w/2+14+i*30} -40 l6 -16 l6 16 Z" fill="#c8ccd6" {S(2)}/>' for i in range(int(w // 30))))


def war_table(w=320, h=200):
    return (pr.rect(w, h, "#4a2c14", 8, 7) + f'<rect x="{-w/2+16}" y="{-h/2+16}" width="{w-32}" height="{h-32}" fill="#d8ccb0" {S(3)}/>'
            + f'<path d="M{-w/2+30} {h/4} Q0 {-h/3} {w/2-30} {h/5}" stroke="#2c4f8a" stroke-width="6" fill="none"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{c}" {S(3)}/>' for x, y, c in ((-80, -20, "#c0283a"), (-40, 30, "#c0283a"), (60, -30, "#5a8a3a"), (100, 20, "#5a8a3a"), (0, 0, "#e8c35a"))))


def shrine(r=70):
    return (f'<circle r="{r}" fill="#5a524a" {S(6)}/><circle r="{r*0.7:.0f}" fill="#3a3430" {S(4)}/>'
            + "".join(f'<circle cx="{math.cos(a)*r*0.85:.0f}" cy="{math.sin(a)*r*0.85:.0f}" r="8" fill="#ffd27a" {S(2)}/>' for a in [i*math.pi/4 for i in range(8)])
            + f'<circle r="{r*0.35:.0f}" fill="#ffd27a" opacity="0.8"/>')


def statue(r=60, c="#6a6670"):
    return (f'<rect x="{-r}" y="{-r}" width="{2*r}" height="{2*r}" fill="#4a4440" {S(6)}/>'
            f'<circle r="{r*0.7:.0f}" fill="{c}" {S(5)}/><circle cy="{-r*0.15:.0f}" r="{r*0.35:.0f}" fill="#8a8690" {S(4)}/>'
            f'<path d="M{-r*0.3:.0f} {r*0.1:.0f} Q0 {r*0.65:.0f} {r*0.3:.0f} {r*0.1:.0f}" fill="#9a9690" {S(3)}/>')


def rails(l=600, vertical=False):
    if vertical:
        return (f'<line x1="-24" y1="{-l/2}" x2="-24" y2="{l/2}" stroke="#8a8f99" stroke-width="8"/><line x1="24" y1="{-l/2}" x2="24" y2="{l/2}" stroke="#8a8f99" stroke-width="8"/>'
                + "".join(f'<rect x="-36" y="{-l/2+i*40}" width="72" height="12" fill="#4a2c14" {S(2)}/>' for i in range(int(l // 40))))
    return (f'<line x1="{-l/2}" y1="-24" x2="{l/2}" y2="-24" stroke="#8a8f99" stroke-width="8"/><line x1="{-l/2}" y1="24" x2="{l/2}" y2="24" stroke="#8a8f99" stroke-width="8"/>'
            + "".join(f'<rect x="{-l/2+i*40}" y="-36" width="12" height="72" fill="#4a2c14" {S(2)}/>' for i in range(int(l // 40))))


def minecart():
    return pr.rect(110, 80, "#5a5660", 10, 6) + '<rect x="-44" y="-30" width="88" height="60" fill="#3a3430"/>' + "".join(
        f'<circle cx="{x}" cy="{y}" r="9" fill="#26232a" {S(3)}/>' for x, y in ((-46, -40), (46, -40), (-46, 40), (46, 40)))


def boulder(r=50, seed=0):
    rr = random.Random(seed)
    pts = " ".join(f"{math.cos(a)*r*rr.uniform(0.75,1.1):.0f},{math.sin(a)*r*rr.uniform(0.75,1.1):.0f}" for a in [i*math.pi/5 for i in range(10)])
    return f'<polygon points="{pts}" fill="#5a524a" {S(5)}/><path d="M{-r*0.4:.0f} {-r*0.3:.0f} l{r*0.4:.0f} {-r*0.1:.0f}" stroke="#7a6e62" stroke-width="5"/>'


def pine_plain(r=80, seed=0):
    return pr.pine(r, decorated=False, star=False, seed=seed)


def well(r=50):
    return f'<circle r="{r}" fill="#5a524a" {S(6)}/><circle r="{r*0.7:.0f}" fill="url(#lg-water)" {S(4)}/><rect x="{-r}" y="-6" width="{2*r}" height="12" fill="#5a3418" {S(3)}/>'


def filter_tank(r=55):
    return f'<circle r="{r}" fill="#8a5a3a" {S(6)}/><circle r="{r*0.75:.0f}" fill="#c87a4a" {S(3)}/>' + "".join(
        f'<circle cx="{math.cos(a)*r*0.45:.0f}" cy="{math.sin(a)*r*0.45:.0f}" r="5" fill="{INK}"/>' for a in [i*math.pi/3 for i in range(6)])


def portcullis(w=300):
    return (f'<rect x="{-w/2}" y="-20" width="{w}" height="40" fill="#26232a" {S(6)}/>'
            + "".join(f'<rect x="{-w/2+8+i*24}" y="-26" width="10" height="52" fill="#5a5660" {S(2)}/>' for i in range(int(w // 24))))


def tent(w=200, h=160, c="#7a3a2a"):
    return (f'<path d="M{-w/2} {h/2} L0 {-h/2} L{w/2} {h/2} Z" fill="{c}" {S(6)}/><path d="M0 {-h/2} L0 {h/2}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M0 {-h/2} L{w/2} {h/2} L0 {h/2} Z" fill="url(#hatch)" opacity="0.4"/>')


def regulator(kind="wheel", r=110):
    base = f'<circle r="{r}" fill="url(#pt-metal)" {S(8)}/><circle r="{r}" fill="none" stroke="url(#lg-brass)" stroke-width="10"/>'
    if kind == "wheel":
        return base + valve_wheel(r * 0.7, "#c0283a")
    if kind == "relief":
        return base + f'<rect x="{-r*0.6:.0f}" y="{-r*0.25:.0f}" width="{r*1.2:.0f}" height="{r*0.5:.0f}" fill="url(#lg-water)" {S(5)}/>' + f'<g transform="translate(0,{-r*0.5:.0f})">{gauge(r*0.3)}</g>'
    return base + f'<rect x="-14" y="{-r*0.75:.0f}" width="28" height="{r*1.5:.0f}" fill="url(#lg-iron)" {S(5)}/><rect x="{-r*0.5:.0f}" y="{-r*0.18:.0f}" width="{r:.0f}" height="{r*0.36:.0f}" rx="10" fill="#c0283a" {S(5)}/>'


def bastion_engine(w=420, h=320):
    s = [pr.rect(w, h, "#2a2a30", 30, 10), f'<rect x="{-w/2+30}" y="{-h/2+30}" width="{w-60}" height="{h-60}" rx="20" fill="url(#lg-iron)" {S(5)}/>']
    for x, y in ((-w/2+50, -h/2+50), (w/2-50, -h/2+50), (-w/2+50, h/2-50), (w/2-50, h/2-50)):
        s.append(f'<circle cx="{x}" cy="{y}" r="34" fill="url(#lg-brass)" {S(5)}/>')
    s.append(f'<g>{gauge(90)}</g><circle r="140" fill="#ff7a1a" opacity="0.15"/>')
    s.append(f'<g transform="translate(0,{h/2-20})">{fist_sigil(0.5)}</g>')
    return "".join(s)


def ram():
    return (pr.rect(240, 140, "#5a3a1a", 12, 7) + f'<path d="M120 -40 L180 -30 L180 30 L120 40 Z" fill="url(#lg-iron)" {S(6)}/>'
            + f'<g>{tusk_sigil(0.7)}</g>')


def ration_sacks(n=6, seed=0):
    r = random.Random(seed)
    return "".join(f'<ellipse cx="{r.uniform(-50,50):.0f}" cy="{r.uniform(-40,40):.0f}" rx="28" ry="22" fill="#a88a5a" {S(4)}/>' for _ in range(n))


def chain_post():
    return f'<circle r="14" fill="url(#lg-iron)" {S(4)}/>'


def charge(lit=True):
    return (f'<rect x="-26" y="-20" width="52" height="40" rx="6" fill="#3a2a14" {S(4)}/>' + "".join(f'<rect x="{-20+i*14}" y="-16" width="10" height="32" fill="#c0283a" {S(2)}/>' for i in range(3))
            + (f'<circle cx="26" cy="-20" r="12" fill="#ffd27a"/><circle cx="26" cy="-20" r="30" fill="#ffd27a" opacity="0.35"/>' if lit else ""))


def scroll_case():
    return pr.rect(120, 60, "#5a3418", 6, 5) + "".join(f'<circle cx="{-40+i*20}" cy="0" r="9" fill="#efe2c0" {S(2)}/>' for i in range(5))


def reinforced_desk():
    return pr.desk(160, 90) + '<rect x="-60" y="-30" width="120" height="60" fill="none" stroke="url(#lg-brass)" stroke-width="8"/>' + '<circle r="12" fill="url(#lg-brass)" stroke="#150b0b" stroke-width="3"/>'


def counterweight():
    return pr.rect(120, 120, "#3a3640", 8, 7) + '<text y="14" font-family="Cinzel" font-weight="900" font-size="40" text-anchor="middle" fill="#e8c35a">IX</text>'


def hand_brake():
    return f'<rect x="-14" y="-60" width="28" height="80" rx="6" fill="url(#lg-iron)" {S(4)}/><circle cy="-64" r="18" fill="#c0283a" {S(4)}/><rect x="-40" y="16" width="80" height="30" fill="#3a3640" {S(4)}/>'
