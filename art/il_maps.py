"""Ironfist Legacy battlemaps. Authoring in grid squares (1 square = 5 ft = 100 px).

Each map draws its walls from the same geometry that is exported as Foundry wall segments,
keeps lighting low (lamps, braziers, forges, fungus), pins each keyed scene to its journal
page, and places the cast (hidden where they arrive later).
"""
import math, random, sys, json, os
from il_mapkit import ILMap as Map, INK
import il_mapkit as k
import props as pr

MAPS = {}
OUT = "/home/claude/saga/il/module/assets/maps"
PREV = "/home/claude/saga/il/art/preview"
DATA = "/home/claude/saga/il/src/scenes.json"


def register(fn):
    MAPS[fn.__name__.replace("_", "-")] = fn
    return fn


def lamp(m, x, y, color="#ffb35a", dim=4, bright=1, wall=True):
    m.g("props", x, y, '<circle r="16" fill="url(#lg-iron)" stroke="#150b0b" stroke-width="4"/><circle r="9" fill="#ffd890"/>')
    m.glow(x, y, 0.9)
    m.light(x, y, dim, bright, color, alpha=0.32, anim="torch", speed=2, intensity=2)


def brazier(m, x, y, dim=6, bright=2):
    m.g("props", x, y, k.brazier(40))
    m.light(x, y, dim, bright, "#ff9a3a", alpha=0.4, anim="torch", speed=3, intensity=4)


def fungus(m, x, y, n=5, spread=60, seed=0, light=True):
    m.g("lowprop", x, y, k.mushrooms(n, spread, seed), shadow=False)
    if light:
        m.light(x, y, 2.5, 0.5, "#7aff8a", alpha=0.28, anim="pulse", speed=1, intensity=2)


def ladder(m, x, y, l=2, vertical=True):
    if vertical:
        m.add("lowprop", f'<g><line x1="{m.P(x-0.2)}" y1="{m.P(y)}" x2="{m.P(x-0.2)}" y2="{m.P(y+l)}" stroke="#5a3416" stroke-width="10"/>'
                         f'<line x1="{m.P(x+0.2)}" y1="{m.P(y)}" x2="{m.P(x+0.2)}" y2="{m.P(y+l)}" stroke="#5a3416" stroke-width="10"/>'
                         + "".join(f'<line x1="{m.P(x-0.2)}" y1="{m.P(y+i*0.25)}" x2="{m.P(x+0.2)}" y2="{m.P(y+i*0.25)}" stroke="#8a5a2a" stroke-width="7"/>' for i in range(int(l / 0.25) + 1)) + '</g>')
    else:
        m.add("lowprop", f'<g><line x1="{m.P(x)}" y1="{m.P(y-0.2)}" x2="{m.P(x+l)}" y2="{m.P(y-0.2)}" stroke="#5a3416" stroke-width="10"/>'
                         f'<line x1="{m.P(x)}" y1="{m.P(y+0.2)}" x2="{m.P(x+l)}" y2="{m.P(y+0.2)}" stroke="#5a3416" stroke-width="10"/>'
                         + "".join(f'<line x1="{m.P(x+i*0.25)}" y1="{m.P(y-0.2)}" x2="{m.P(x+i*0.25)}" y2="{m.P(y+0.2)}" stroke="#8a5a2a" stroke-width="7"/>' for i in range(int(l / 0.25) + 1)) + '</g>')


def crates(m, x, y, seed=0, n=4):
    r = random.Random(seed)
    for i in range(n):
        m.g("props", x + r.uniform(-0.6, 0.6), y + r.uniform(-0.6, 0.6), pr.crate(r.choice([60, 70, 80])), rot=r.uniform(-20, 20))


def barrels(m, x, y, seed=0, n=3):
    r = random.Random(seed)
    for i in range(n):
        m.g("props", x + r.uniform(-0.5, 0.5), y + r.uniform(-0.5, 0.5), pr.barrel(r.choice([24, 28])))


def banner_wall(m, x, y, rot=0, cinder=False):
    sig = k.tusk_sigil(0.9) if cinder else k.fist_sigil(0.8)
    col = "#3a5014" if cinder else "#7a1a18"
    m.g("high", x, y, f'<rect x="-60" y="-14" width="120" height="28" fill="{col}" stroke="#150b0b" stroke-width="5"/><g transform="translate(0,-2) scale(0.45)">{sig}</g>', rot=rot)


# =========================================================================== 1. THE ROAD AND THE FIFTH FINGER
@register
def fifth_finger():
    m = Map("fifth-finger", "The Mountain Road and the Fifth Finger", 40, 28, seed=101, bg="#2a3022")
    m.fill_all("grass")
    # road from the mist (SW) to the gatehouse (N)
    road = [(0, 25), (6, 23.5), (11, 22.5), (15, 20), (19, 19.5), (24, 19.2), (28.5, 18.5), (29, 16.5)]
    d = "M" + " L".join(f"{m.P(a):.0f} {m.P(b):.0f}" for a, b in road)
    m.add("floor", f'<path d="{d}" fill="none" stroke="#150b0b" stroke-width="{m.P(3.4)}" stroke-linecap="round" stroke-linejoin="round"/>')
    m.add("floor", f'<path d="{d}" fill="none" stroke="{m.pattern("dirt")}" stroke-width="{m.P(3.0)}" stroke-linecap="round" stroke-linejoin="round"/>')
    m.add("decal", f'<path d="{d}" fill="none" stroke="#5a4a36" stroke-width="10" stroke-dasharray="4 60" stroke-linecap="round"/>')
    # mountain cliff along the west/north
    cliff = [(0, 0), (20, 0), (19, 2.5), (14, 4), (9, 5.5), (5, 9), (2, 12), (0, 13)]
    m.floor_poly(cliff, "rock")
    m.wall([(0, 13), (2, 12), (5, 9), (9, 5.5), (14, 4), (19, 2.5), (20, 0)], "rock")
    for i, (x, y) in enumerate([(4, 4), (8, 2.5), (12, 1.5), (2, 8)]):
        m.g("props", x, y, k.boulder(60, i))
    # the last mist
    for i in range(14):
        rr = random.Random(i)
        m.add("high", f'<ellipse cx="{m.P(rr.uniform(0,7)):.0f}" cy="{m.P(rr.uniform(22,28)):.0f}" rx="{m.P(rr.uniform(1.5,3)):.0f}" ry="{m.P(rr.uniform(0.8,1.4)):.0f}" fill="#e8eef4" opacity="0.32"/>')
    m.text(3.2, 26.8, "THE LAST OF THE MIST", size=30, color="#e8eef4")
    # pines
    for i, (x, y) in enumerate([(3, 16), (6, 18.5), (9, 16.5), (12, 18), (14, 25), (18, 24), (21, 26), (25, 23.5), (33, 23.5), (37, 21),
                                (36, 26), (10, 26.5), (23, 15.5), (17, 15), (8, 13.5), (39, 18), (1, 20), (30.5, 26.5)]):
        m.g("props", x, y, k.pine_plain(rr := 70 + (i % 4) * 14, seed=i))
    # road crew at work
    m.g("props", 13.6, 21.1, pr.cart(170, 90), rot=-25)
    for i, (x, y) in enumerate([(12.2, 23.2), (12.8, 23.6), (16.6, 21.6)]):
        m.g("props", x, y, k.boulder(26, i + 9))
    m.text(14, 24.7, "ROAD CREW", size=24, color="#efe2c0")
    # ---- the Fifth Finger
    fx, fy, fw, fh = 22, 3, 15, 12
    m.floor_rect(fx, fy, fw, fh, "gravel")
    m.room(fx, fy, fw, fh, "dwarf", doors=[("S", 7, 2, "iron")])  # gate passage x 28-30, between the towers
    # gatehouse towers
    for tx in (fx + 4, fx + 8):
        m.floor_rect(tx, fy + fh - 0.5, 2, 2, "dwarfslab")
        m.wall([(tx, fy + fh - 0.5), (tx, fy + fh + 1.5), (tx + 2, fy + fh + 1.5), (tx + 2, fy + fh)], "dwarf")
    m.g("high", fx + 7, fy + fh + 0.2, k.portcullis(200))
    # keep (Edda's office + barracks)
    m.floor_rect(fx + 0.5, fy + 0.5, 7, 5, "dwarfslab")
    m.room(fx + 0.5, fy + 0.5, 7, 5, "dwarf", doors=[("S", 3, 1, "wood")])
    m.wall([(fx + 4, fy + 0.5), (fx + 4, fy + 3)], "dwarf")
    m.door(fx + 4, fy + 3, fx + 4, fy + 4, "wood")
    m.wall([(fx + 4, fy + 4), (fx + 4, fy + 5.5)], "dwarf")
    for i in range(3):
        m.g("props", fx + 1.4, fy + 1.3 + i * 1.4, k.bunk(80, 180), rot=90)
    m.g("props", fx + 6, fy + 1.6, pr.desk(140, 80))
    m.g("props", fx + 6, fy + 2.4, pr.chair(), rot=180)
    m.g("props", fx + 6.6, fy + 4.6, pr.filing_cabinet(80, 50))
    m.text(fx + 2.2, fy + 6.4, "BARRACKS", size=22)
    m.text(fx + 5.8, fy + 6.4, "WARDEN", size=22)
    # watchtower, NE
    m.floor_circle(fx + fw - 2, fy + 2, 1.8, "dwarfslab")
    m.wall([(fx + fw - 2 + 1.8 * math.cos(a * math.pi / 8), fy + 2 + 1.8 * math.sin(a * math.pi / 8)) for a in range(16)], "dwarf", closed=True)
    m.g("high", fx + fw - 2, fy + 2, f'<circle r="60" fill="#7a1a18" stroke="#150b0b" stroke-width="6"/><g transform="scale(0.7)">{k.fist_sigil(1)}</g>')
    m.text(fx + fw - 2, fy + 4.4, "WATCHTOWER", size=22)
    # supply yard with damaged winch
    m.g("props", fx + 11, fy + 8, pr.cart(200, 110), rot=8)
    m.g("props", fx + 12.8, fy + 6.5, k.valve_wheel(46, "#8a5a2a"))
    m.add("decal", f'<path d="M{m.P(fx+12.8)} {m.P(fy+6.5)} L{m.P(fx+11)} {m.P(fy+8)}" stroke="#8a7a5a" stroke-width="6" stroke-dasharray="12 8"/>')
    crates(m, fx + 10.5, fy + 10.2, 3, 4)
    barrels(m, fx + 13.6, fy + 10.4, 4, 3)
    m.mark_zone(fx + 9.5, fy + 6, 5, 4, "#e8c35a", "BROKEN WINCH")
    m.g("props", fx + 3, fy + 9, pr.table(160, 90, "#6e4527"))
    for x in (fx + 2.2, fx + 3.8):
        m.g("props", x, fy + 10, pr.chair(), rot=180)
    brazier(m, fx + 6, fy + 9.5, 5, 1.5)
    banner_wall(m, fx + 7, fy + 0.15)
    m.text(fx + fw / 2, fy - 0.4, "THE FIFTH FINGER", size=40, color="#e8d8a8")
    # lights (day scene — only braziers and the office lamp)
    lamp(m, fx + 6, fy + 1.2)
    m.env = {"darkness": 0.0, "globalLight": True}
    m.note(5, 22.5, "ch1:s11", "1.1 Beyond the Last Mist")
    m.note(fx + 7, fy + fh + 2.2, "ch1:s12", "1.2 Recognition at the Fifth Finger")
    m.note(fx + 12, fy + 5.6, "ch1:s12", "Broken Winch (work challenge)")
    m.token("edda", fx + 6.2, fy + 2.4)
    m.token("ironfist-trooper", fx + 5, fy + fh + 0.8)
    m.token("ironfist-trooper", fx + 9, fy + fh + 0.8)
    m.token("ironfist-courier", fx + 3, fy + 8.2)
    m.token("lowhearth-worker", fx + 11.4, fy + 9.6)
    m.token("lowhearth-worker", fx + 12.4, fy + 7.4)
    m.token("lowhearth-worker", 14.4, 22.6)
    m.token("lowhearth-worker", 12.4, 22.2)
    return m


# =========================================================================== 2. LOWHEARTH
@register
def lowhearth():
    m = Map("lowhearth", "Lowhearth: Heddra's Kitchen and the Lift Street", 36, 26, seed=102, bg="#151312")
    m.fill_rock()
    street = [(1, 9), (35, 9), (35, 15), (1, 15)]
    m.floor_poly(street, "dwarfslab")
    # drainage channel
    m.water_poly([(1, 11.6), (35, 11.6), (35, 12.4), (1, 12.4)], foul=True)
    for x in (6, 17, 28):
        m.g("lowprop", x, 12, pr.rect(120, 110, "#5a524a", 4, 5))
    m.text(30.5, 12.15, "DRAIN", size=20, color="#9ab84a")
    # Heddra's home (west)
    hx, hy = 1, 2
    m.floor_rect(hx, hy, 12, 7, "planks")
    m.room(hx, hy, 12, 7, "dwarf", doors=[("S", 5, 1.5, "wood")])
    m.wall([(hx + 6.5, hy), (hx + 6.5, hy + 3)], "dwarf")
    m.door(hx + 6.5, hy + 3, hx + 6.5, hy + 4.2, "wood")
    m.wall([(hx + 6.5, hy + 4.2), (hx + 6.5, hy + 7)], "dwarf")
    m.g("props", hx + 3.2, hy + 3.5, k.feast_table(380, 110, 2, "#8a6a3a"))
    for x in (hx + 1.8, hx + 2.8, hx + 3.8, hx + 4.8):
        m.g("props", x, hy + 2.6, pr.chair(), rot=180)
        m.g("props", x, hy + 4.4, pr.chair())
    m.g("props", hx + 1.0, hy + 1.0, k.forge(140, 100))
    m.light(hx + 1.0, hy + 1.0, 5, 1.5, "#ff9a3a", alpha=0.4, anim="torch", speed=2, intensity=3)
    m.g("props", hx + 5.3, hy + 0.8, pr.jar_shelf(200, 40, 1))
    m.g("props", hx + 9.5, hy + 1.3, k.bunk(), rot=90)
    m.g("props", hx + 9.5, hy + 5.5, k.bunk(), rot=90)
    m.g("props", hx + 11.2, hy + 3.5, pr.chest() if hasattr(pr, "chest") else pr.crate(60))
    m.g("decal", hx + 3.2, hy + 6.1, '<rect x="-70" y="-14" width="140" height="28" fill="#8a3a2a" stroke="#150b0b" stroke-width="4"/>')
    m.text(hx + 3.2, hy - 0.35, "HEDDRA'S KITCHEN", size=26)
    m.text(hx + 9.3, hy - 0.35, "FAMILY ROOMS", size=22)
    # damp marks & ration stamps
    for (x, y) in ((hx + 0.6, hy + 6.2), (hx + 11.4, hy + 0.7), (hx + 7.2, hy + 6.4)):
        m.add("decal", f'<ellipse cx="{m.P(x)}" cy="{m.P(y)}" rx="60" ry="34" fill="#1a2a1a" opacity="0.5"/>')
    # shrine of Sister Yrsa (north centre)
    sx, sy = 15, 2
    m.floor_rect(sx, sy, 7, 7, "hexstone")
    m.room(sx, sy, 7, 7, "dwarf", doors=[("S", 2.75, 1.5, "brass")])
    m.g("props", sx + 3.5, sy + 2.4, k.shrine(80))
    m.light(sx + 3.5, sy + 2.4, 5, 1.5, "#ffd27a", alpha=0.35, anim="pulse", speed=1, intensity=2)
    for i in range(4):
        m.g("props", sx + 1.4 + i * 1.4, sy + 5.0, k.bunk(70, 160))
    m.text(sx + 3.5, sy - 0.35, "SHRINE & INFIRMARY", size=24)
    # communal workshop (east)
    wx, wy = 24, 2
    m.floor_rect(wx, wy, 8, 7, "dwarfslab")
    m.room(wx, wy, 8, 7, "dwarf", doors=[("S", 3, 2, "wood")])
    m.g("props", wx + 2, wy + 1.6, k.forge(160, 110))
    m.light(wx + 2, wy + 1.6, 5, 1.5, "#ff9a3a", alpha=0.4, anim="torch")
    m.g("props", wx + 3.8, wy + 1.6, k.anvil())
    m.g("props", wx + 6, wy + 3.8, pr.table(180, 100, "#6e4527"))
    m.g("props", wx + 2.5, wy + 5.2, k.pump(160, 100))
    m.g("props", wx + 7, wy + 1.0, k.weapon_rack(160), rot=0)
    m.text(wx + 4, wy - 0.35, "COMMUNAL WORKSHOP", size=24)
    # the lifts (NE) up to Hammerhall
    lx, ly = 32.5, 2
    m.floor_rect(lx, ly, 3.5, 7, "metal")
    m.wall([(lx, ly), (lx + 3.5, ly), (lx + 3.5, ly + 7)], "dwarf")
    m.wall([(lx, ly), (lx, ly + 7)], "iron", kind="terrain", sight="limited")
    m.g("props", lx + 1.75, ly + 1.8, k.lift_cage(200, 200))
    m.g("props", lx + 1.75, ly + 4.7, k.lift_cage(200, 200))
    m.text(lx + 1.75, ly - 0.35, "LIFTS ▲ HAMMERHALL", size=20)
    # south row: service stair, ration hall, housing
    m.floor_rect(1, 15, 9, 9, "planks")
    m.room(1, 15, 9, 9, "dwarf", doors=[("N", 3.5, 2, "wood")])
    for i in range(3):
        m.g("props", 5.5, 17 + i * 2.4, k.feast_table(600, 90, i, "#4a3a2a"))
    m.text(5.5, 24.6, "RATION HALL", size=24)
    for i, x in enumerate((11, 16, 21)):
        m.floor_rect(x, 15, 4.5, 6, "planks")
        m.room(x, 15, 4.5, 6, "dwarf", doors=[("N", 1.5, 1.4, "wood")])
        m.g("props", x + 1, 18, k.bunk(80, 180))
        m.g("props", x + 3.4, 19.5, pr.barrel(22))
    m.text(16.5, 21.9, "HOUSEHOLDS", size=22)
    m.stair(28, 15, 3, 8, 8)
    m.wall([(27.5, 15), (27.5, 24), (31.5, 24), (31.5, 15)], "dwarf")
    m.text(29.5, 24.7, "SERVICE STAIR ▼", size=22)
    m.text(33.6, 19, "▼ TO THE NINTH SLUICE", size=22, rot=90)
    m.floor_rect(32, 15, 3, 10, "rock")
    m.wall([(35, 15), (35, 25.5)], "rock")
    # street lamps
    for x in (3, 9, 14, 20, 26, 32):
        lamp(m, x, 9.6)
    for x in (6, 23):
        lamp(m, x, 14.4)
    m.env = {"darkness": 0.85, "globalLight": False}
    m.note(hx + 3.2, hy + 5.5, "ch1:s13", "1.3 The Door That Still Opens")
    m.note(hx + 3.2, hy + 2.0, "ch3:s35", "3.5 Dinner with the Missing Places Filled")
    m.note(sx + 3.5, sy + 4.0, "ch2:s21", "2.1 What the Wounded Actually Saw")
    m.note(18, 13.6, "ch7:s72", "7.2 The Cost of an Order (shelter line)")
    m.token("heddra", hx + 3.2, hy + 5.4)
    m.token("runa", wx + 4, wy + 3)
    m.token("yrsa", sx + 3.5, sy + 3.8)
    m.token("tovik", sx + 2, sy + 4.0, hidden=True)
    m.token("lowhearth-worker", 10, 10.2)
    m.token("lowhearth-worker", 22, 13.8)
    m.token("lowhearth-worker", 26.5, 7.2)
    return m


# =========================================================================== 3. HAMMERHALL
@register
def hammerhall():
    m = Map("hammerhall", "Hammerhall and the Council Chamber", 44, 30, seed=103, bg="#151312")
    m.fill_rock()
    # great hall
    m.floor_rect(8, 4, 28, 22, "dwarfslab")
    m.room(8, 4, 28, 22, "dwarf", doors=[("S", 12, 4, "iron"), ("E", 9, 2, "wood"), ("W", 9, 2, "wood"), ("N", 12.5, 3, "brass")])
    # dais + high table
    m.floor_rect(14, 4, 16, 4, "hexstone", layer="lowprop")
    m.stair(14, 8, 16, 0.8, 1, vertical=True)
    m.g("props", 22, 5.8, k.feast_table(1300, 120, 7, "#7a1a18"))
    for i in range(12):
        m.g("props", 16.2 + i * 1.05, 5.0, pr.chair(), rot=180)
    m.text(22, 7.5, "HIGH TABLE", size=22, color="#e8c35a", layer="decal")
    # long feast tables
    for i, x in enumerate((12, 18, 26, 32)):
        m.g("props", x, 14, k.feast_table(800, 110, i + 2), rot=90)
        m.g("props", x - 0.85, 14, k.bench_row(780), rot=90)
        m.g("props", x + 0.85, 14, k.bench_row(780), rot=90)
    # pillars
    for x in (10.5, 15, 22, 29, 33.5):
        for y in (9.5, 19.5):
            m.g("props", x, y, pr.pillar(46, "#5a524a"))
            m.terrain_wall([(x - 0.45, y - 0.45), (x + 0.45, y - 0.45), (x + 0.45, y + 0.45), (x - 0.45, y + 0.45)], closed=True)
    # public gallery (rails + benches) along the south
    m.railing(9, 21.5, 19.5, 21.5)
    m.railing(24.5, 21.5, 35, 21.5)
    for y in (22.4, 23.4, 24.4):
        m.g("props", 14, y, k.bench_row(800))
        m.g("props", 30, y, k.bench_row(800))
    m.text(22, 25.4, "PUBLIC GALLERY", size=26)
    # hearths
    for x in (8.6, 35.4):
        m.g("props", x, 14, k.forge(120, 260), rot=0)
        m.light(x, 14, 8, 2.5, "#ff9a3a", alpha=0.45, anim="torch", speed=2, intensity=3)
    # banners and braziers
    for x in (12, 18, 26, 32):
        banner_wall(m, x, 4.15)
    for x, y in ((14, 11.5), (30, 11.5), (14, 18), (30, 18), (22, 20.5)):
        brazier(m, x, y, 6, 2)
    # side chamber (west) — 1.5 "Two Mismatched Rivets"
    m.floor_rect(1, 10, 7, 9, "planks")
    m.room(1, 10, 7, 9, "dwarf", gaps=[("E", 0, 9)])  # shared wall (and its door) drawn by the hall
    m.g("props", 3.5, 13.2, pr.round_table(60))
    for a in range(4):
        m.g("props", 3.5 + 1.0 * math.cos(a * math.pi / 2), 13.2 + 1.0 * math.sin(a * math.pi / 2), pr.chair(), rot=a * 90 + 90)
    m.g("props", 2, 17.4, k.weapon_rack(160))
    m.g("props", 5.6, 17.6, k.brazier(34))
    m.light(5.6, 17.6, 4, 1, "#ff9a3a", alpha=0.35, anim="torch")
    m.text(4.5, 9.6, "SIDE CHAMBER", size=22)
    # council offices (north, behind the dais)
    m.floor_rect(15, 0.6, 14, 3.4, "carpet")
    m.room(15, 0.6, 14, 3.4, "dwarf", gaps=[("S", 5.5, 3)])
    m.g("props", 22, 1.9, k.war_table(400, 180))
    m.text(17.4, 3.5, "COUNCIL", size=20, color="#e8c35a")
    # east antechamber (to the lifts)
    m.floor_rect(36, 10, 7, 9, "dwarfslab")
    m.room(36, 10, 7, 9, "dwarf", gaps=[("W", 0, 9)], doors=[("E", 3, 3, "iron")])
    m.g("props", 39.5, 11.3, k.statue(60))
    m.text(39.5, 9.6, "TO GATE CROWN", size=22)
    # exterior bridge (south)
    m.floor_rect(19, 26, 6, 4, "dwarfslab")
    m.wall([(19, 26), (19, 30)], "dwarf")
    m.wall([(25, 26), (25, 30)], "dwarf")
    m.text(22, 29.6, "▼ PARADE BRIDGE", size=22)
    m.env = {"darkness": 0.7, "globalLight": False}
    m.note(22, 9, "ch1:s14", "1.4 A Table Above Their Station")
    m.note(4.5, 15.5, "ch1:s15", "1.5 Two Mismatched Rivets")
    m.note(22, 2.4, "ch5:s54", "5.4 Three Generals, Actual Consequences")
    m.note(22, 23.6, "ch5:s52", "5.2 The Public Roll")
    m.note(35, 23.6, "ch8:s84", "8.4 The Record Nobody Gets to Edit")
    m.token("hadrik", 22, 5.0)
    m.token("brynja", 19.9, 5.0)
    m.token("odran", 24.1, 5.0)
    m.token("heddra", 21, 5.0)
    m.token("dagnner", 27, 6.8)
    m.token("runa", 12.8, 12.5)
    m.token("ironfist-trooper", 20.5, 25.0)
    m.token("ironfist-trooper", 23.5, 25.0)
    m.token("shield-warden", 22, 3.3)
    m.token("baldrik", 22, 27.5, hidden=True)
    m.token("venn", 25.6, 2.0, hidden=True)
    m.token("lowhearth-worker", 17.2, 12.8)
    m.token("lowhearth-worker", 25.2, 16.3)
    return m


# =========================================================================== 4. THE BROKEN DESCENT
@register
def broken_descent():
    m = Map("broken-descent", "The Broken Descent: Lift Shaft IX", 28, 22, seed=104, bg="#151312")
    m.fill_rock()
    # upper landing (west)
    m.floor_rect(1, 4, 9, 14, "dwarfslab")
    m.wall([(10, 4), (1, 4), (1, 18), (10, 18)], "dwarf")
    m.g("props", 3, 6, k.hand_brake())
    m.text(3, 7.4, "HAND BRAKE", size=20)
    crates(m, 3, 15, 5, 4)
    m.g("props", 6, 16.5, k.rails(500), rot=0)
    m.g("props", 4.5, 16.5, k.minecart())
    lamp(m, 2, 10)
    lamp(m, 8, 5)
    # the shaft
    m.chasm(10, 5, 9, 12)
    m.wall([(10, 4), (19, 4)], "dwarf")
    m.wall([(10, 18), (19, 18)], "dwarf")
    m.add("decal", f'<rect x="{m.P(10)}" y="{m.P(5)}" width="{m.P(9)}" height="{m.P(12)}" fill="none" stroke="#c8963a" stroke-width="10" stroke-dasharray="30 20"/>')
    m.g("props", 14.5, 11, k.lift_cage(400, 400, jammed=True), scale=1.0)
    m.text(14.5, 13.8, "CAGE JAMMED — 40 FT BELOW", size=26, color="#ff9a3a")
    m.g("props", 17.3, 6.3, k.counterweight())
    m.text(17.3, 7.6, "COUNTERWEIGHT", size=18)
    for y in (5.5, 16.5):
        for x in (11, 13, 16, 18):
            m.g("lowprop", x, y, '<circle r="14" fill="none" stroke="#c8ccd6" stroke-width="7"/>')
    m.text(14.5, 4.5, "ANCHOR RINGS", size=18, color="#c8ccd6")
    ladder(m, 10.4, 6, 10)
    ladder(m, 18.6, 6, 10)
    m.add("lowprop", f'<path d="M{m.P(14.5)} {m.P(4)} L{m.P(14.5)} {m.P(9)}" stroke="#8a7a5a" stroke-width="10" stroke-dasharray="14 6"/>')
    # lower landing (east) — 40 ft down
    m.floor_rect(19, 3, 8, 16, "rock")
    m.cave([(19, 3), (27, 3), (27, 19), (19, 19)], tex="rock", seed=4, draw_floor=False)
    m.text(23, 2.4, "LOWER LANDING (−40 FT)", size=24, color="#9ad0ff")
    m.open(18.5, 6, 19.7, 16, None)
    m.g("props", 24, 8, k.ration_sacks(6, 2))
    m.g("props", 23, 14, k.pump(160, 110))
    m.steam(25, 16, 1.5)
    m.steam(21, 5, 1.2)
    lamp(m, 25.5, 10, "#ffb35a", 4, 1)
    m.env = {"darkness": 0.9, "globalLight": False}
    m.note(5, 12, "ch2:s23", "2.3 The Broken Descent")
    m.token("tovik", 5.5, 11)
    m.token("lowhearth-worker", 22.5, 9.5)
    m.token("lowhearth-worker", 24.5, 10.8)
    m.token("lowhearth-worker", 21.5, 12.4)
    m.token("goblin-sapper", 25.5, 17.2, hidden=True)
    return m


# =========================================================================== 5. THE NINTH SLUICE
@register
def ninth_sluice():
    m = Map("ninth-sluice", "Battle at the Ninth Sluice", 32, 24, seed=105, bg="#151312")
    m.fill_rock()
    # approach tunnel (W) held by allied soldiers
    m.cave([(0, 9), (9, 9.5), (9, 14.5), (0, 15)], seed=2)
    m.text(3.5, 8.4, "UPPER APPROACH (ALLIED SOLDIERS)", size=20)
    # the gallery: 70 x 50 ft = 14 x 10 squares, three levels
    gx, gy = 9, 6
    m.floor_rect(gx, gy, 18, 13, "dwarfslab")
    m.room(gx, gy, 18, 13, "dwarf", gaps=[("W", 3.5, 5)])
    # upper walkway (north, +20 ft)
    m.walkway(gx, gy, 18, 3)
    m.railing(gx + 0.2, gy + 3, gx + 17.8, gy + 3)
    m.elev(gx + 9, gy + 1.0, "UPPER WALKWAY  +20 FT")
    m.stair(gx + 1, gy + 3, 2, 3, 5)
    ladder(m, gx + 16, gy + 3, 3)
    # control station NE
    m.g("props", gx + 15.2, gy + 1.5, k.war_table(220, 120))
    m.g("props", gx + 12.6, gy + 1.5, k.valve_wheel(70, "#c0283a"))
    m.text(gx + 12.6, gy + 2.7, "PRESSURE WHEEL", size=18, color="#ff9a3a")
    for x in (gx + 10.5, gx + 11.3):
        m.g("props", x, gy + 0.6, k.gauge(28))
    # lower channel (south, −10 ft) with the sluice gate east
    m.water_poly([(gx, gy + 9.5), (gx + 18, gy + 9.5), (gx + 18, gy + 13), (gx, gy + 13)])
    m.elev(gx + 6, gy + 11.4, "LOWER CHANNEL  −10 FT")
    m.railing(gx + 0.2, gy + 9.5, gx + 15, gy + 9.5)
    m.stair(gx + 15.2, gy + 8.5, 2.6, 1.0, 3, vertical=True)
    # sabotaged gate + exposed chain
    m.g("high", gx + 17.6, gy + 11.25, k.portcullis(340), rot=90)
    m.add("lowprop", f'<path d="M{m.P(gx+17.4)} {m.P(gy+9.4)} L{m.P(gx+14)} {m.P(gy+3.2)}" stroke="#c8ccd6" stroke-width="14" stroke-dasharray="20 6"/>')
    m.text(gx + 14.8, gy + 7.0, "EXPOSED CHAIN (AC 15, 35 HP)", size=18, color="#ff9a3a", rot=-58)
    m.text(gx + 16.2, gy + 13.6, "SABOTAGED GATE", size=20, color="#ff9a3a")
    # pipes across the hall
    m.pipe([(gx, gy + 4), (gx + 18, gy + 4)], 30, "#6e5a3a")
    m.pipe([(gx + 6, gy + 3), (gx + 6, gy + 9.5)], 26, "#5a4a3a")
    m.pipe([(gx + 12, gy + 3), (gx + 12, gy + 9.5)], 26, "#5a4a3a")
    m.g("props", gx + 6, gy + 6.5, k.pump(170, 110))
    m.g("props", gx + 12, gy + 6.5, k.pump(170, 110))
    # trapped shift (SE bay)
    m.cave([(27, 13), (31, 13), (31, 19), (27, 19)], seed=6)
    m.text(29, 12.4, "TRAPPED SHIFT", size=20, color="#efe2c0")
    m.g("props", 29.5, 17.5, k.ration_sacks(5, 4))
    # raiders' route (south tunnel)
    m.cave([(13, 19), (17, 19), (16.5, 24), (13.5, 24)], seed=7)
    m.open(8.3, 9.7, 9.7, 14.3)
    m.open(26.3, 13.7, 27.7, 18.6)
    m.open(13.4, 18.3, 16.6, 19.7)
    m.text(15, 23.4, "▼ CINDER-TUSK TUNNEL", size=20)
    for (x, y) in ((gx + 4, gy + 7.5), (gx + 9, gy + 8.4), (gx + 15, gy + 5.5), (gx + 2, gy + 11)):
        m.steam(x, y, 1.4)
    for (x, y) in ((gx + 0.6, gy + 0.6), (gx + 17.4, gy + 0.6), (gx + 0.6, gy + 8.6), (gx + 17.4, gy + 8.6)):
        lamp(m, x, y)
    lamp(m, 4, 12)
    m.env = {"darkness": 0.85, "globalLight": False}
    m.note(gx + 9, gy + 5.2, "ch2:s24", "2.4 Battle at the Ninth Sluice")
    m.note(29, 15.5, "ch2:s25", "2.5 People on the Other Side")
    m.note(gx + 15.2, gy + 2.4, "ch2:s26", "2.6 The Signature")
    m.token("brakk", gx + 12.6, gy + 2.0)
    m.token("shock-trooper", gx + 8, gy + 7.6)
    m.token("shock-trooper", gx + 14.3, gy + 6.2)
    m.token("goblin-sapper", gx + 16.6, gy + 8.4)
    m.token("ketta", gx + 13.2, gy + 0.8)
    m.token("lowhearth-worker", 28.6, 15.2)
    m.token("lowhearth-worker", 29.8, 16.4)
    m.token("lowhearth-worker", 28.2, 17.4)
    m.token("ironfist-trooper", 2.5, 11.5)
    m.token("ironfist-trooper", 2.5, 12.8)
    m.token("baldrik", 4.2, 12, hidden=True)
    return m


# =========================================================================== 6. RECORDS ANNEX & RUNA'S WORKSHOP
@register
def records_annex():
    m = Map("records-annex", "The Military Archive and Runa's Workshop", 34, 22, seed=106, bg="#151312")
    m.fill_rock()
    # corridor
    m.floor_rect(1, 9, 32, 4, "dwarfslab")
    m.wall([(1, 9), (1, 13)], "dwarf")
    m.wall([(33, 9), (33, 13)], "dwarf")
    # archive (north-west)
    ax, ay = 1, 1
    m.floor_rect(ax, ay, 15, 8, "hexstone")
    m.room(ax, ay, 15, 8, "dwarf", doors=[("S", 6, 1.5, "iron")])
    for i in range(4):
        m.wall([(ax + 2 + i * 3, ay + 1), (ax + 2 + i * 3, ay + 5)], "shelf")
    m.g("props", ax + 13.2, ay + 2.0, k.reinforced_desk())
    m.text(ax + 13.2, ay + 3.3, "LOCKED CABINET", size=18, color="#e8c35a")
    m.wall([(ax + 12, ay + 1.2), (ax + 14.4, ay + 1.2)], "iron")
    crates(m, ax + 12.5, ay + 6, 6, 3)
    m.text(ax + 12.5, ay + 7.4, "TRANSFER CRATES", size=18)
    m.g("props", ax + 6.5, ay + 6.6, pr.desk(150, 80))
    m.g("props", ax + 6.5, ay + 5.9, pr.chair(), rot=180)
    m.text(ax + 7.5, ay - 0.35, "THE MILITARY ARCHIVE", size=26)
    lamp(m, ax + 6.5, ay + 7.2)
    lamp(m, ax + 0.6, ay + 0.6)
    # Odran's provisioning office (north-east)
    ox, oy = 17, 1
    m.floor_rect(ox, oy, 7, 8, "carpet")
    m.room(ox, oy, 7, 8, "dwarf", doors=[("S", 2.5, 1.5, "wood")])
    m.g("props", ox + 3.5, oy + 3, pr.desk(180, 90))
    m.g("props", ox + 3.5, oy + 2.2, pr.chair(), rot=180)
    m.g("props", ox + 1, oy + 5, pr.scroll_rack(160, 46), rot=90)
    m.g("props", ox + 5.5, oy + 6.5, k.ration_sacks(6, 9))
    m.text(ox + 3.5, oy - 0.35, "PROVISIONING", size=22)
    lamp(m, ox + 5.8, oy + 1.5)
    # guard post
    m.floor_rect(25, 1, 8, 8, "dwarfslab")
    m.room(25, 1, 8, 8, "dwarf", doors=[("S", 3, 2, "iron")])
    m.g("props", 29, 3, pr.table(160, 90, "#6e4527"))
    m.g("props", 31.5, 6.5, k.weapon_rack(160), rot=90)
    m.g("props", 26.5, 6.5, k.bunk(), rot=0)
    brazier(m, 29, 5, 5, 1.5)
    m.text(29, 0.65, "GUARD POST", size=22)
    # Runa's workshop (south)
    rx, ry = 6, 13
    m.floor_rect(rx, ry, 18, 8, "dwarfslab")
    m.room(rx, ry, 18, 8, "dwarf", doors=[("N", 8, 2, "wood")])
    m.g("props", rx + 2, ry + 2, k.forge(180, 130))
    m.light(rx + 2, ry + 2, 6, 2, "#ff9a3a", alpha=0.42, anim="torch", speed=2, intensity=3)
    m.g("props", rx + 4.2, ry + 2.2, k.anvil())
    m.g("props", rx + 9, ry + 5, k.war_table(360, 200))
    m.text(rx + 9, ry + 6.4, "DRAFTING TABLE", size=18, color="#e8c35a")
    m.g("props", rx + 14.5, ry + 2.5, k.pump(220, 140))
    m.g("props", rx + 14.5, ry + 5.6, pr.machine(200, 140, 3))
    m.g("props", rx + 17, ry + 6.6, pr.jar_shelf(160, 40, 2), rot=90)
    m.pipe([(rx + 12, ry + 0.3), (rx + 12, ry + 7.7)], 22)
    m.text(rx + 9, ry + 8.6, "RUNA'S WORKSHOP", size=26)
    lamp(m, rx + 9, ry + 3)
    for x in (4, 12, 20, 28):
        lamp(m, x, 11)
    m.env = {"darkness": 0.8, "globalLight": False}
    m.note(ax + 7, ay + 4, "ch3:s34", "3.4 The Record That Survives")
    m.note(ox + 3.5, oy + 4.5, "ch3:s32", "3.2 Three Routes to the Same Lie")
    m.note(rx + 9, ry + 3, "ch3:s33", "3.3 Runa's Commission")
    m.note(16, 11, "ch3:s31", "3.1 Competing Invitations")
    m.token("venn", ax + 6.5, ay + 5.9)
    m.token("odran", ox + 3.5, oy + 2.2)
    m.token("runa", rx + 9, ry + 3.8)
    m.token("shield-warden", ax + 6.2, ay + 8.6)
    m.token("shield-warden", ax + 8.2, ay + 8.6)
    m.token("ironfist-trooper", 28, 4)
    m.token("ironfist-trooper", 30, 4)
    m.token("ironfist-trooper", 27.5, 8.4, hidden=True)
    m.token("ironfist-trooper", 30.5, 8.4, hidden=True)
    m.token("dagnner", 29, 2.2, hidden=True)
    return m


# =========================================================================== 7. THE TREATY STAIR
@register
def treaty_stair():
    m = Map("treaty-stair", "The Treaty Stair and the Filter Station", 30, 34, seed=107, bg="#151312")
    m.fill_rock()
    # dwarf checkpoint (top)
    m.floor_rect(9, 0, 12, 5, "dwarfslab")
    m.wall([(9, 0), (9, 5)], "dwarf")
    m.wall([(21, 0), (21, 5)], "dwarf")
    m.g("high", 15, 4.6, k.portcullis(600))
    m.wall([(9, 5), (12, 5)], "dwarf")
    m.door(12, 5, 18, 5, "iron")
    m.wall([(18, 5), (21, 5)], "dwarf")
    banner_wall(m, 15, 0.3)
    m.text(15, 2, "IRONFIST CHECKPOINT", size=26)
    brazier(m, 10.2, 3.6, 5, 1.5)
    brazier(m, 19.8, 3.6, 5, 1.5)
    # the stair
    m.stair(11, 5, 8, 7, 12)
    m.wall([(11, 5), (11, 12)], "dwarf")
    m.wall([(19, 5), (19, 12)], "dwarf")
    # carved markings
    for y in (6.5, 9.5):
        m.g("decal", 11.4, y, f'<g transform="scale(0.35)">{k.fist_sigil()}</g>', shadow=False)
        m.g("decal", 18.6, y, f'<g transform="scale(0.45)">{k.tusk_sigil()}</g>', shadow=False)
    # treaty landing
    m.cave([(6, 12), (24, 12), (25, 20), (5, 20)], tex="hexstone", style="dwarf", seed=3, jag=0.1)
    m.add("decal", f'<circle cx="{m.P(15)}" cy="{m.P(16)}" r="{m.P(3)}" fill="none" stroke="#c8963a" stroke-width="10" stroke-dasharray="40 16"/>')
    m.g("props", 15, 16, k.statue(80, "#8a8690"))
    m.text(15, 17.6, "THE COMPACT STONE", size=20, color="#e8c35a")
    for a in range(8):
        m.g("props", 15 + 3.6 * math.cos(a * math.pi / 4), 16 + 3.0 * math.sin(a * math.pi / 4), k.boulder(30, a))
    m.text(15, 12.6, "TREATY LANDING", size=26)
    # lower stair down to the warrens
    m.stair(12, 20, 6, 6, 10)
    m.wall([(12, 20), (12, 26)], "rock")
    m.wall([(18, 20), (18, 26)], "rock")
    m.cave([(8, 26), (22, 26), (23, 34), (7, 34)], tex="moss", style="fungal", seed=5)
    m.text(15, 33.4, "▼ THE CINDER WARRENS", size=24)
    m.open(11.3, 11.3, 18.7, 12.8, "hexstone")
    m.open(12.3, 19.2, 17.7, 20.8, "hexstone")
    m.open(12.3, 25.2, 17.7, 26.8, "moss")
    banner_wall(m, 15, 27, cinder=True)
    # filter station (east)
    m.cave([(24, 13), (29.5, 12), (29.5, 26), (23, 25)], tex="moss", style="fungal", seed=8)
    for y in (15, 18, 21):
        m.g("props", 26.5, y, k.filter_tank(60))
    m.water_poly([(28.2, 13), (29.4, 13), (29.4, 25), (28.2, 25)])
    crates(m, 25, 23.6, 11, 3)
    m.text(26.5, 12.1, "FILTER STATION", size=22, color="#9adf5a")
    m.open(23.2, 14, 25.6, 19.5, "moss")
    # wounded (west)
    m.cave([(0.5, 13), (6, 12.5), (5.5, 22), (0.5, 22)], tex="moss", style="fungal", seed=9)
    for y in (14.5, 17, 19.5):
        m.g("props", 2.5, y, k.tent(180, 140, "#5a3a2a"))
    m.text(3, 12.2, "THE WOUNDED", size=20)
    m.open(4.6, 14, 6.8, 19.5, "moss")
    fungus(m, 4, 21, 6, 60, 2)
    fungus(m, 9, 30, 7, 70, 3)
    fungus(m, 21, 30, 6, 60, 4)
    fungus(m, 24.5, 24, 5, 50, 5)
    for (x, y) in ((7, 14), (23, 14), (7, 19), (23, 19)):
        lamp(m, x, y, "#ffd27a", 4, 1)
    m.env = {"darkness": 0.88, "globalLight": False}
    m.note(15, 3.8, "ch4:s41", "4.1 A Passage with Witnesses")
    m.note(26.5, 20, "ch4:s42", "4.2 What the Raid Was Supposed to Retrieve")
    m.note(15, 14.4, "ch4:s43", "4.3 The Terms Neither Side Likes")
    m.note(13, 18.6, "ch4:s46", "4.6 A Treaty Is an Object")
    m.token("brynja", 15, 2.8)
    m.token("ironfist-trooper", 13.5, 3.8)
    m.token("ironfist-trooper", 16.5, 3.8)
    m.token("urzha", 15, 18.7)
    m.token("skrik", 26.5, 16.6)
    m.token("cinder-civilian", 2.5, 16)
    m.token("cinder-civilian", 3.4, 18.4)
    m.token("shock-trooper", 13, 28.5)
    m.token("shock-trooper", 17, 28.5)
    m.token("ketta", 24.5, 22, hidden=True)
    return m


# =========================================================================== 8. THE PUMP BRIDGE
@register
def pump_bridge():
    m = Map("pump-bridge", "The Bridge Both Peoples Need", 36, 22, seed=108, bg="#050404")
    m.chasm(0, 0, 36, 22)
    # west shore — the shared pump house
    m.cave([(0, 4), (8, 3.5), (9, 18), (0, 18.5)], tex="dwarfslab", style="dwarf", seed=2, jag=0.15, wall=False)
    m.g("props", 4, 7, k.pump(220, 140))
    m.g("props", 4, 14, k.pump(220, 140))
    m.text(4, 3.2, "SHARED PUMP HOUSE", size=22)
    # east shore — clan tunnels
    m.cave([(27, 3.5), (36, 3), (36, 19), (27.5, 18)], tex="moss", style="fungal", seed=3, jag=0.2, wall=False)
    fungus(m, 32, 6, 6, 60, 8)
    fungus(m, 33, 15, 6, 60, 9)
    m.text(31.5, 2.7, "CINDER-TUSK TUNNELS", size=22)
    # the 90-ft bridge (18 squares), 2 squares wide
    bx0, bx1, by = 9, 27, 10
    m.floor_rect(bx0 - 0.5, by - 1, bx1 - bx0 + 1, 2, "planks")
    m.railing(bx0 - 0.5, by - 1, bx1 + 0.5, by - 1)
    m.railing(bx0 - 0.5, by + 1, bx1 + 0.5, by + 1)
    m.pipe([(bx0 - 1, by - 0.7), (bx1 + 1, by - 0.7)], 26, "#6e5a3a")
    m.pipe([(bx0 - 1, by + 0.7), (bx1 + 1, by + 0.7)], 26, "#5a4a3a")
    # raised valve platforms (+10 ft)
    for (px, py) in ((14, 6), (22, 13)):
        m.floor_rect(px - 1.5, py - 1.5, 3, 3, "metal", layer="lowprop")
        m.g("props", px, py, k.valve_wheel(60, "#c0283a"))
        m.elev(px, py + 2.0, "VALVE PLATFORM +10 FT")
        ladder(m, px, py + (1.5 if py < by else -2.5), 1.0 if py < by else 1.0)
    # charges
    for i, x in enumerate((12, 18, 24)):
        m.g("high", x, by + (0.0 if i != 1 else -0.2), k.charge(True))
        m.light(x, by, 2, 0.5, "#ffd27a", alpha=0.4, anim="pulse", speed=6, intensity=6)
        m.text(x, by + 1.8, f"CHARGE {i+1}", size=20, color="#ff9a3a")
    m.text(18, 21.4, "90-FOOT PUMP BRIDGE  —  THE CHASM IS 200 FEET DEEP", size=26, color="#c8963a")
    for (x, y) in ((8, 8), (8, 12), (28, 8), (28, 12)):
        lamp(m, x, y)
    m.env = {"darkness": 0.88, "globalLight": False}
    m.note(18, 7.5, "ch4:s44", "4.4 The Bridge Both Peoples Need")
    m.note(5, 10.5, "ch4:s45", "4.5 A Familiar Sentence")
    m.token("brakk", 26, 10, name="Loyalist Tunnel Captain")
    m.token("shock-trooper", 24.5, 9.6)
    m.token("shock-trooper", 28.5, 11)
    m.token("goblin-sapper", 21.5, 10.4)
    m.token("goblin-sapper", 14, 6)
    m.token("skrik", 5.5, 10)
    m.token("runa", 3.5, 10.6, hidden=True)
    return m


# =========================================================================== 9. THE CINDER WARRENS
@register
def cinder_warrens():
    m = Map("cinder-warrens", "The Cinder Warrens: The Homes Beyond the Military Map", 40, 30, seed=109, bg="#151312")
    m.fill_rock()
    m.cave([(1, 2), (14, 1.5), (15, 12), (1, 13)], tex="moss", style="fungal", seed=1)  # fungal gardens NW
    m.cave([(13, 11), (27, 10.5), (28, 21), (14, 22)], tex="rock", style="rock", seed=2)  # main cavern
    m.cave([(26, 2), (39, 1.5), (39, 13), (26.5, 12)], tex="moss", style="fungal", seed=3)  # homes NE
    m.cave([(2, 12.5), (14, 13.5), (14.5, 28), (2, 28.5)], tex="rock", style="rock", seed=4)  # damaged cavern SW
    m.cave([(27, 19.5), (38, 18.5), (38.5, 28.5), (28, 28)], tex="moss", style="fungal", seed=5)  # wells SE
    # where the caverns meet
    for (a, b, c, d, tx) in ((12.4, 9.8, 15.8, 13.3, "rock"), (25.3, 9.6, 28.2, 13.0, "moss"), (4.5, 11.6, 9.5, 14.4, "rock"),
                             (12.6, 14.6, 15.4, 19.0, "rock"), (26.0, 18.6, 29.0, 21.8, "moss"), (13.3, -0.5, 15.9, 2.8, "moss")):
        m.open(a, b, c, d, tx)
    # gardens
    for i, (x, y) in enumerate(((3, 4), (6, 6), (9, 3.5), (4, 9), (8, 10.5), (11, 7))):
        m.g("lowprop", x, y, f'<rect x="-80" y="-50" width="160" height="100" rx="10" fill="#3a2a1a" stroke="#150b0b" stroke-width="5"/>', shadow=False)
        fungus(m, x, y, 6, 55, i, light=(i % 2 == 0))
    m.text(7, 1.4, "FUNGAL GARDENS (BLIGHTED)", size=22, color="#9adf5a")
    for (x, y) in ((5, 7.5), (10, 5)):
        m.add("decal", f'<ellipse cx="{m.P(x)}" cy="{m.P(y)}" rx="90" ry="50" fill="#5a4a2a" opacity="0.6"/>')
    # homes
    for i, (x, y) in enumerate(((30, 4.5), (33.5, 4), (37, 5), (31, 9), (35, 9.5))):
        m.g("props", x, y, k.tent(200, 170, ["#6a3a2a", "#4a5a2a", "#5a3a5a", "#7a5a2a", "#3a4a5a"][i]))
    m.g("props", 34, 7, pr.round_table(55))
    m.text(33.5, 1.3, "HOUSEHOLDS", size=22)
    # main cavern: the clan council fire + requisition stores
    m.g("props", 21, 16.5, k.brazier(70))
    m.light(21, 16.5, 9, 3, "#ff9a3a", alpha=0.45, anim="torch", speed=3, intensity=4)
    for a in range(6):
        m.g("props", 21 + 2.3 * math.cos(a * math.pi / 3), 16.5 + 2.3 * math.sin(a * math.pi / 3), k.bench_row(120), rot=a * 60 + 90)
    crates(m, 17, 20, 7, 4)
    m.g("props", 25.5, 14.5, k.ration_sacks(7, 3))
    m.text(21, 12.4, "THE COUNCIL FIRE", size=24)
    m.text(17.6, 21.6, "REQUISITIONED STORES", size=18)
    # damaged cavern SW: bad water, a dwarf prisoner beside a goblin mechanic
    m.water_poly([(4, 20), (9, 19.5), (10, 24), (5, 25)], foul=True)
    m.g("props", 11, 18, k.pump(170, 110))
    m.g("props", 4, 26.5, k.tent(180, 140, "#4a3a2a"))
    m.text(7.5, 15.3, "THE BAD-WATER CAVERN", size=20)
    # wells SE
    for (x, y) in ((31, 22), (35, 22.5), (33, 26)):
        m.g("props", x, y, k.well(55))
    m.add("decal", f'<path d="M{m.P(34.2)} {m.P(22.1)} l60 60 M{m.P(34.8)} {m.P(22.1)} l-60 60" stroke="#c0283a" stroke-width="10"/>')
    m.text(33.5, 28.8, "WELLS (TWO POISONED)", size=20)
    # routes
    m.text(15, 0.6, "▲ TREATY STAIR", size=20)
    m.add("decal", f'<path d="M{m.P(38)} {m.P(13)} Q{m.P(36)} {m.P(16)} {m.P(38.5)} {m.P(18)}" stroke="#e8c35a" stroke-width="8" stroke-dasharray="16 12" fill="none"/>')
    m.text(37.2, 15.5, "SERVICE ROUTE ▶ REDOUBT", size=16, color="#e8c35a", rot=-80)
    m.add("decal", f'<path d="M{m.P(20)} {m.P(13)} L{m.P(27)} {m.P(8)}" stroke="#c0283a" stroke-width="10" stroke-dasharray="26 14" fill="none"/>')
    m.text(24.5, 11.6, "KORGA'S INVASION PATH", size=18, color="#ff7a6a", rot=-35)
    for (x, y) in ((3, 12), (12, 2.5), (30, 2.5), (38, 12), (3, 27), (37, 27), (15, 21), (27, 13)):
        lamp(m, x, y, "#9adf5a", 4, 1)
    m.env = {"darkness": 0.9, "globalLight": False}
    m.note(21, 18.8, "ch6:s62", "6.2 The Homes Beyond the Military Map")
    m.note(31, 25, "ch6:s63", "6.3 An Exchange with Names")
    m.token("urzha", 21, 14.6)
    m.token("skrik", 11, 19.4)
    m.token("lowhearth-worker", 10, 18.6, name="Dwarf Prisoner (working the pump)")
    m.token("cinder-civilian", 31.5, 6)
    m.token("cinder-civilian", 34.5, 10.6)
    m.token("cinder-civilian", 6, 8)
    m.token("cinder-civilian", 33, 24)
    m.token("shock-trooper", 26, 10.5, hidden=True)
    m.token("shock-trooper", 27.4, 11.4, hidden=True)
    m.token("brakk", 25.5, 9.4, hidden=True, name="Loyalist Tunnel Captain")
    return m


# =========================================================================== 10. THE VANGUARD REDOUBT
@register
def vanguard_redoubt():
    m = Map("vanguard-redoubt", "The Vanguard Redoubt", 28, 30, seed=110, bg="#151312")
    m.fill_rock()
    # outer approach (south) — 60 x 80 ft redoubt = 12 x 16 squares
    m.cave([(3, 20), (25, 19.5), (26, 29.5), (2, 29.5)], tex="gravel", style="rock", seed=1)
    for i, (x, y) in enumerate(((7, 24), (12, 26.5), (19, 23.5), (22, 27), (5, 28))):
        m.g("props", x, y, k.boulder(55, i))
    m.terrain_wall([(11.4, 25.9), (12.6, 25.9), (12.6, 27.1), (11.4, 27.1)], closed=True)
    m.text(14, 29.1, "OUTER APPROACH", size=24)
    m.open(12.3, 19.06, 15.7, 20.5, "gravel")
    rx, ry = 8, 3
    m.floor_rect(rx, ry, 12, 16, "dwarfslab")
    m.room(rx, ry, 12, 16, "dwarf", doors=[("S", 4.5, 3, "iron")])
    m.g("high", rx + 6, ry + 16.2, k.portcullis(300))
    # inner rooms
    m.wall([(rx, ry + 6), (rx + 5, ry + 6)], "dwarf")
    m.door(rx + 5, ry + 6, rx + 6.5, ry + 6, "wood")
    m.wall([(rx + 6.5, ry + 6), (rx + 12, ry + 6)], "dwarf")
    m.wall([(rx + 6, ry), (rx + 6, ry + 6)], "dwarf")
    # records room (NW) with reinforced desk
    m.g("props", rx + 3, ry + 2.5, k.reinforced_desk())
    m.g("props", rx + 1, ry + 4.5, pr.bookshelf(200, 40, 2), rot=90)
    m.text(rx + 3, ry + 4.2, "REINFORCED DESK", size=16, color="#e8c35a")
    m.text(rx + 3, ry - 0.4, "RECORDS ROOM", size=22)
    lamp(m, rx + 5.3, ry + 0.7)
    # duty officer (NE)
    m.g("props", rx + 9, ry + 2.2, k.war_table(260, 150))
    m.g("props", rx + 11, ry + 5, k.bunk(), rot=90)
    m.text(rx + 9, ry - 0.4, "DUTY OFFICER", size=22)
    lamp(m, rx + 7, ry + 0.7)
    # courtyard: stores + wounded
    crates(m, rx + 2, ry + 8.5, 4, 5)
    m.g("props", rx + 2, ry + 11.5, k.ration_sacks(7, 2))
    barrels(m, rx + 3.2, ry + 13.5, 8, 4)
    m.text(rx + 2.4, ry + 7.1, "STORES", size=20)
    for i in range(4):
        m.g("props", rx + 9.6 + (i % 2) * 1.4, ry + 8.5 + (i // 2) * 2.6, k.bunk(80, 180))
    m.text(rx + 10.3, ry + 7.1, "WOUNDED", size=20)
    brazier(m, rx + 6, ry + 11, 6, 2)
    # secret service passage (west)
    m.cave([(0.5, 6), (8, 6.2), (8, 8), (0.5, 8.5)], seed=4)
    m.walls = [w for w in m.walls if not (m.P(rx - 0.5) <= min(w["c"][0], w["c"][2]) and max(w["c"][0], w["c"][2]) <= m.P(rx + 0.5) and abs(w["c"][0] - w["c"][2]) < 60)]
    m.wall([(rx, ry), (rx, ry + 3.2)], "dwarf", draw=False)
    m.door(rx, ry + 3.2, rx, ry + 4.4, secret=True)
    m.wall([(rx, ry + 4.4), (rx, ry + 16)], "dwarf", draw=False)
    m.text(3.5, 5.6, "SERVICE PASSAGE", size=18, color="#e8c35a")
    banner_wall(m, rx + 6, ry + 6.2)
    m.env = {"darkness": 0.88, "globalLight": False}
    m.note(rx + 6, ry + 13.5, "ch6:s64", "6.4 The Vanguard Redoubt")
    m.note(rx + 6, ry + 18.5, "ch6:s65", "6.5 The Order He Cannot Postpone")
    m.note(rx + 9, ry + 3.6, "ch6:s66", "6.6 The Plan Everyone Can Understand")
    m.token("vanguard-officer", rx + 9, ry + 3.4, name="Redoubt Duty Officer")
    m.token("shield-warden", rx + 4.8, ry + 15)
    m.token("shield-warden", rx + 7.2, ry + 15)
    for (x, y) in ((rx + 1.5, ry + 10), (rx + 4.5, ry + 9), (rx + 7.5, ry + 9), (rx + 10.5, ry + 13.5), (rx + 1.6, ry + 14.6), (rx + 6, ry + 7.2)):
        m.token("ironfist-trooper", x, y)
    m.token("brakk", 13, 26.4, name="Loyalist Tunnel Captain")
    m.token("shock-trooper", 11, 25.2)
    m.token("shock-trooper", 15.5, 25.4)
    m.token("dagnner", 4, 7.2, hidden=True)
    m.token("baldrik", 13, 21, hidden=True)
    return m


# =========================================================================== 11. THE UPPER GATE
@register
def upper_gate():
    m = Map("upper-gate", "The Upper Gate (Front I)", 30, 24, seed=111, bg="#151312")
    m.fill_rock()
    # inside the gate (north)
    m.floor_rect(4, 0, 22, 6, "dwarfslab")
    m.wall([(4, 0), (4, 6)], "dwarf")
    m.wall([(26, 0), (26, 6)], "dwarf")
    crates(m, 7, 2.5, 1, 6)
    m.g("props", 22.5, 2.6, k.ration_sacks(8, 4))
    m.text(15, 1.4, "FOOD STORES & SURFACE ACCESS", size=24)
    # the gate wall
    m.wall([(0, 6), (12, 6)], "dwarf")
    m.door(12, 6, 18, 6, "iron", locked=True)
    m.wall([(18, 6), (30, 6)], "dwarf")
    m.g("high", 15, 6, k.portcullis(600))
    for x in (11, 19):
        m.floor_rect(x - 1.5, 4.5, 3, 3, "dwarfslab", layer="lowprop")
        m.wall([(x - 1.5, 4.5), (x + 1.5, 4.5), (x + 1.5, 7.5), (x - 1.5, 7.5), (x - 1.5, 4.5)], "dwarf")
        m.text(x, 8.3, "GATE TOWER", size=18)
    # the ramp (south) with haul chains
    m.floor_rect(9, 7.5, 12, 16.5, "dirt")
    m.cave([(0, 7.5), (9, 7.5), (9, 24), (0, 24)], tex="rock", style="rock", seed=3, wall=False)
    m.cave([(21, 7.5), (30, 7.5), (30, 24), (21, 24)], tex="rock", style="rock", seed=4, wall=False)
    m.wall([(9, 7.5), (9, 24)], "rock")
    m.wall([(21, 7.5), (21, 24)], "rock")
    m.g("props", 15, 12.5, k.ram(), scale=1.4)
    for sx in (-1, 1):
        m.add("lowprop", f'<path d="M{m.P(15+sx*1.6)} {m.P(12.5)} L{m.P(15+sx*4.5)} {m.P(19)}" stroke="#c8ccd6" stroke-width="14" stroke-dasharray="20 6"/>')
        m.text(15 + sx * 3.6, 16.6, "HAUL CHAIN", size=18, color="#ff9a3a", rot=sx * -60)
    m.text(15, 23.4, "▼ THE SIEGE RAMP", size=22)
    for i, (x, y) in enumerate(((11, 17), (19, 18), (12.5, 21), (17.5, 9.5))):
        m.g("props", x, y, k.boulder(40, i + 3))
    for (x, y) in ((6, 5), (24, 5), (15, 3.5)):
        brazier(m, x, y, 6, 2)
    m.env = {"darkness": 0.8, "globalLight": False}
    m.note(15, 4.2, "ch7:s73", "7.3 The Chosen Front: Upper Gate")
    m.token("battering-engine", 15, 12.5)
    m.token("brakk", 15, 15.5, name="Tunnel Captain")
    m.token("shock-trooper", 13, 14.5)
    m.token("shock-trooper", 17, 14.5)
    m.token("goblin-sapper", 12, 16.5)
    m.token("goblin-sapper", 18, 16.5)
    m.token("ironfist-trooper", 13, 4.8)
    m.token("ironfist-trooper", 17, 4.8)
    return m


# =========================================================================== 12. THE LOWER BRIDGE
@register
def lower_bridge():
    m = Map("lower-bridge", "The Lower Bridge (Front II)", 32, 22, seed=112, bg="#050404")
    m.chasm(0, 0, 32, 22)
    m.cave([(0, 5), (8, 4.5), (8.5, 17.5), (0, 18)], tex="dwarfslab", style="dwarf", seed=1, jag=0.15, wall=False)
    m.cave([(24, 4.5), (32, 4), (32, 18), (23.5, 17.5)], tex="rock", style="rock", seed=2, wall=False)
    m.floor_rect(7.5, 9, 17, 4, "planks")
    m.railing(7.5, 9, 24.5, 9)
    m.railing(7.5, 13, 24.5, 13)
    m.mark_zone(7.5, 10, 17, 2, "#e8c35a", "EVACUATION CORRIDOR (10 FT)")
    # ledges from which raiders strike
    m.cave([(12, 0), (20, 0), (19, 6), (13, 6.5)], tex="rock", style="rock", seed=3, wall=False)
    m.cave([(12.5, 16), (19.5, 15.5), (20, 22), (12, 22)], tex="rock", style="rock", seed=4, wall=False)
    m.text(16, 0.8, "NORTH LEDGE", size=20)
    m.text(16, 21.3, "SOUTH LEDGE", size=20)
    for x in (14, 18):
        ladder(m, x, 6.3, 2.7)
        ladder(m, x, 13, 2.8)
    m.text(4, 4, "◀ LOWHEARTH (SAFETY)", size=22)
    m.text(28, 3.6, "WARRENS ▶", size=22)
    m.g("props", 2.5, 15.5, k.tent(160, 130, "#5a3a2a"))
    for (x, y) in ((6, 6), (6, 16), (26, 6), (26, 16)):
        lamp(m, x, y)
    m.env = {"darkness": 0.88, "globalLight": False}
    m.note(16, 8.6, "ch7:s73", "7.3 The Chosen Front: Lower Bridge")
    m.token("shock-trooper", 15, 4.5)
    m.token("shock-trooper", 17, 17.5)
    m.token("goblin-sapper", 13.5, 3)
    m.token("goblin-sapper", 18.5, 3.5)
    m.token("goblin-sapper", 16, 19)
    m.token("cinder-civilian", 27, 10.5)
    m.token("cinder-civilian", 28, 11.5)
    m.token("lowhearth-worker", 26.5, 12)
    return m


# =========================================================================== 13. THE PUMP GALLERIES
@register
def pump_galleries():
    m = Map("pump-galleries", "The Pump Galleries (Front III)", 30, 22, seed=113, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 26, 18, "dwarfslab")
    m.room(2, 2, 26, 18, "dwarf", gaps=[("W", 7, 4), ("E", 7, 4)])
    m.water_poly([(2, 9.5), (28, 9.5), (28, 12.5), (2, 12.5)])
    m.floor_rect(13, 9.5, 4, 3, "metal", layer="lowprop")
    m.text(15, 11.2, "GRATED CROSSING", size=16)
    for (cx, cy, lab) in ((7, 5.5, "CONTROL A"), (23, 16.5, "CONTROL B")):
        m.floor_rect(cx - 2.5, cy - 2, 5, 4, "metal", layer="lowprop")
        m.g("props", cx, cy, k.valve_wheel(70, "#c0283a"))
        m.g("props", cx + 1.7, cy - 1.2, k.gauge(30))
        m.mark_zone(cx - 2.5, cy - 2, 5, 4, "#ff9a3a")
        m.text(cx, cy + 2.6, lab, size=22, color="#ff9a3a")
    for y in (4, 18):
        m.pipe([(2, y), (28, y)], 30)
    for x in (11, 19):
        m.pipe([(x, 2), (x, 20)], 24, "#5a4a3a")
        m.g("props", x, 7, k.pump(150, 100))
        m.g("props", x, 15, k.pump(150, 100))
    for (x, y) in ((5, 14), (25, 6), (15, 6), (15, 16)):
        m.steam(x, y, 1.6)
    for (x, y) in ((3, 3), (27, 3), (3, 19), (27, 19), (15, 3), (15, 19)):
        lamp(m, x, y)
    m.env = {"darkness": 0.85, "globalLight": False}
    m.note(15, 8.5, "ch7:s73", "7.3 The Chosen Front: Pump Galleries")
    m.token("brakk", 7, 7.2, name="Tunnel Captain")
    m.token("goblin-sapper", 6, 4.5)
    m.token("goblin-sapper", 23, 15.5)
    m.token("goblin-sapper", 24.4, 17.4)
    return m


# =========================================================================== 14. KORGA'S COMMAND BRIDGE
@register
def command_bridge():
    m = Map("command-bridge", "Korga's Command Bridge over the Reservoir", 32, 24, seed=114, bg="#0a1a24")
    m.add("floor", f'<rect width="{m.W}" height="{m.H}" fill="{m.pattern("water")}"/>')
    for i in range(30):
        rr = random.Random(i)
        m.add("decal", f'<ellipse cx="{m.P(rr.uniform(0,32)):.0f}" cy="{m.P(rr.uniform(0,24)):.0f}" rx="{m.P(rr.uniform(1,3)):.0f}" ry="{m.P(rr.uniform(0.2,0.5)):.0f}" fill="#5aa0c0" opacity="0.18"/>')
    # broad bridge, 6 squares wide, running W–E
    m.floor_rect(0, 9, 32, 6, "dwarfslab")
    m.railing(0, 9, 32, 9)
    m.railing(0, 15, 32, 15)
    # cover: barricades, crates
    for (x, y, rot) in ((8, 10.5, 0), (8, 13.5, 0), (24, 10.5, 0), (24, 13.5, 0)):
        m.g("props", x, y, pr.rect(200, 50, "#4a2c14", 6, 6), rot=rot)
        m.terrain_wall([(x - 1, y - 0.25), (x + 1, y - 0.25), (x + 1, y + 0.25), (x - 1, y + 0.25)], closed=True)
    crates(m, 15, 10, 2, 3)
    crates(m, 17.5, 14, 3, 2)
    # Korga's command post (centre): war table + banner
    m.g("props", 16, 12, k.war_table(260, 160))
    banner_wall(m, 16, 9.3, cinder=True)
    # side stairs going down at both ends
    for (x, y) in ((4, 15), (28, 15)):
        m.stair(x - 1, y, 2, 4, 6)
        m.wall([(x - 1, y), (x - 1, y + 4)], "dwarf")
        m.wall([(x + 1, y), (x + 1, y + 4)], "dwarf")
        m.text(x, y + 4.6, "SIDE STAIR ▼", size=18)
    for (x, y) in ((4, 5), (28, 5)):
        m.stair(x - 1, y, 2, 4, 6)
        m.wall([(x - 1, y), (x - 1, y + 4)], "dwarf")
        m.wall([(x + 1, y), (x + 1, y + 4)], "dwarf")
    m.text(16, 22.8, "THE UPPER RESERVOIR — 60 FEET BELOW", size=26, color="#9ad0ff")
    for (x, y) in ((1, 12), (31, 12)):
        m.text(x + (0.3 if x < 16 else -0.3), y, "◀" if x < 16 else "▶", size=40)
    for (x, y) in ((6, 9.3), (12, 9.3), (20, 9.3), (26, 9.3), (6, 14.7), (12, 14.7), (20, 14.7), (26, 14.7)):
        brazier(m, x, y, 5, 1.5)
    m.env = {"darkness": 0.8, "globalLight": False}
    m.note(16, 13.8, "ch7:s75", "7.5 Korga's Last Argument")
    m.note(4, 12, "ch7:s74", "7.4 The Shield Between Them")
    m.token("korga", 16, 12.9)
    m.token("shock-trooper", 14.3, 12.4)
    m.token("shock-trooper", 17.8, 11.4)
    m.token("urzha", 29, 12, hidden=True)
    m.token("baldrik", 2.5, 12, hidden=True)
    return m


# =========================================================================== 15. THE HEARTWORKS
@register
def heartworks():
    m = Map("heartworks", "The Heartworks: Last Bastion", 28, 22, seed=115, bg="#151312")
    m.fill_rock()
    m.pattern("metal")
    hx, hy = 5, 4  # 90 x 70 ft = 18 x 14
    m.floor_rect(hx, hy, 18, 14, "dwarfslab")
    m.room(hx, hy, 18, 14, "dwarf", gaps=[("W", 6, 2)], doors=[("E", 6, 2, "iron")])
    # vent strip grid (20 x 10 ft strips) shown faintly
    for i in range(4):
        for j in range(7):
            m.add("decal", f'<rect x="{m.P(hx+i*4.5+0.25)}" y="{m.P(hy+j*2+0.05)}" width="{m.P(4)}" height="{m.P(1.9)}" fill="none" stroke="#ff7a1a" stroke-width="3" stroke-dasharray="10 14" opacity="0.35"/>')
    # walkways
    m.walkway(hx + 1, hy + 6, 16, 2)
    m.walkway(hx + 8, hy + 1, 2, 12)
    # central engine
    m.g("props", hx + 9, hy + 7, k.bastion_engine(420, 320))
    m.terrain_wall([(hx + 7, hy + 5.4), (hx + 11, hy + 5.4), (hx + 11, hy + 8.6), (hx + 7, hy + 8.6)], closed=True)
    m.light(hx + 9, hy + 7, 7, 2, "#ff7a1a", alpha=0.45, anim="pulse", speed=2, intensity=4)
    # three regulator platforms
    for (px, py, kind, lab) in ((hx + 3, hy + 2.5, "wheel", "RESERVOIR WHEEL"), (hx + 15, hy + 2.5, "relief", "RELIEF CHANNEL"), (hx + 9, hy + 12, "brake", "REVERSAL BRAKE")):
        m.floor_circle(px, py, 1.8, "metal", layer="lowprop")
        m.g("props", px, py, k.regulator(kind, 110))
        m.text(px, py + (2.4 if py < hy + 7 else -2.2), lab, size=22, color="#ff9a3a")
        m.light(px, py, 3, 1, "#ffd27a", alpha=0.35)
    # relief channel water out to the east
    m.water_poly([(hx + 16.6, hy + 2), (hx + 18, hy + 2), (hx + 18, hy + 3), (hx + 16.6, hy + 3)])
    m.water_poly([(23, 5.8), (28, 5.8), (28, 7.2), (23, 7.2)])
    # pipes
    m.pipe([(hx, hy + 9.5), (hx + 18, hy + 9.5)], 34)
    m.pipe([(hx + 3, hy + 4.3), (hx + 3, hy + 13.5)], 26)
    m.pipe([(hx + 15, hy + 4.3), (hx + 15, hy + 13.5)], 26)
    # exits
    m.cave([(0, 8.5), (5, 9.5), (5, 12.5), (0, 13.5)], seed=3)
    m.cave([(23.6, 8.5), (28, 8), (28, 14), (23.6, 13.5)], seed=4)
    m.open(4.3, 9.9, 5.7, 12.1, "dwarfslab")
    m.open(23.05, 9.8, 24.3, 12.2, "rock")
    m.text(2.4, 8, "◀ VANGUARD APPROACH", size=18)
    m.text(25.5, 15, "SERVICE PASSAGE ▶", size=18)
    for (x, y) in ((hx + 0.6, hy + 0.6), (hx + 17.4, hy + 0.6), (hx + 0.6, hy + 13.4), (hx + 17.4, hy + 13.4)):
        lamp(m, x, y, "#ff9a3a")
    for (x, y) in ((hx + 5, hy + 5), (hx + 13, hy + 10), (hx + 13, hy + 4)):
        m.steam(x, y, 1.6)
    m.text(14, 1.6, "THE HEARTWORKS", size=40, color="#e8d8a8")
    m.env = {"darkness": 0.9, "globalLight": False}
    m.note(hx + 9, hy + 4.6, "ch8:s83", "8.3 Last Bastion")
    m.note(2.5, 11, "ch8:s81", "8.1 Before the Last Door")
    m.note(hx + 3, hy + 4.4, "ch8:s82", "8.2 The Heartworks Opens")
    m.token("bastion-engine", hx + 9, hy + 7)
    m.token("pressure-vent", hx + 4.5, hy + 10.5, hidden=True, name="Marked Vent Strip")
    m.token("hadrik", 25, 11, hidden=True)
    return m


ORDER = list(MAPS)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    which = sys.argv[1:] or ORDER
    data = json.load(open(DATA)) if os.path.exists(DATA) else {}
    for key in which:
        m = MAPS[key]()
        m.render(f"{OUT}/{key}.webp", f"{PREV}/map-{key}.webp")
        data[key] = m.export()
        print(key, m.W, m.H, "walls", len(m.walls), "lights", len(m.lights), "notes", len(m.notes), "tokens", len(m.tokens), flush=True)
    json.dump(data, open(DATA, "w"))
