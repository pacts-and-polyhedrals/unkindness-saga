"""The ten battlemaps of The Night of the Red Clause."""
import math, random, sys, json, os
from mapkit import Map, INK
import props as pr

MAPS = {}


def register(fn):
    MAPS[fn.__name__] = fn
    return fn


def building(m, x, y, w, h, style="stone", roof="roof", doors=(), sign=None):
    m.floor_rect(x, y, w, h, roof, layer="high", stroke=False)
    m.room(x, y, w, h, style)
    for (dx, dy, rot) in doors:  # decorative shopfront doors on the facade (not usable)
        m.g("high", dx, dy, f'<rect x="-30" y="-10" width="60" height="20" fill="#5a3416" stroke="{INK}" stroke-width="4"/>', rot=rot, shadow=False)
    if sign:
        m.text(x + w / 2, y + h / 2 + 0.15, sign, size=34, color="#e8dcc0", layer="label")


def snow_drift(m, x, y, w, h, seed=0):
    r = random.Random(seed)
    for _ in range(int(w * h / 2) + 2):
        cx, cy = x + r.uniform(0, w), y + r.uniform(0, h)
        m.add("decal", f'<ellipse cx="{cx*100:.0f}" cy="{cy*100:.0f}" rx="{r.uniform(40,120):.0f}" ry="{r.uniform(20,50):.0f}" fill="#e8eef6" opacity="0.85"/>')


def footprints(m, pts, seed=0):
    r = random.Random(seed)
    for (a, b), (c, d) in zip(pts, pts[1:]):
        n = int(math.hypot(c - a, d - b) * 2.2)
        for i in range(n):
            t = i / max(1, n)
            x, y = a + (c - a) * t, b + (d - b) * t
            off = 0.12 if i % 2 else -0.12
            ang = math.atan2(d - b, c - a)
            px, py = x + math.cos(ang + math.pi / 2) * off, y + math.sin(ang + math.pi / 2) * off
            m.add("decal", f'<ellipse cx="{px*100:.0f}" cy="{py*100:.0f}" rx="9" ry="5" fill="#8f9bb0" opacity="0.6" transform="rotate({math.degrees(ang):.0f} {px*100:.0f} {py*100:.0f})"/>')


def lamp(m, x, y, night_only=True):
    m.g("props", x, y, pr.lamppost())
    m.light(x, y, 5, 1.5, color="#ffc46a", alpha=0.32, anim="torch", speed=2, intensity=2,
            luminosity=0.45)
    if night_only:
        m.lights[-1]["darkness"] = {"min": 0.35, "max": 1}


# =============================================================================
@register
def market():
    m = Map("market", "The Market, Castle Ward", 40, 30, seed=11)
    m.fill_all("cobble")
    snow_drift(m, 0, 0, 40, 30, seed=2)
    # buildings ring
    building(m, 0, 0, 9, 5, sign="CASTLE WARD")
    building(m, 9.5, 0, 6.5, 4, style="brick")
    building(m, 16.5, 0, 8, 3.5)
    building(m, 25, 0, 6, 4, style="brick")
    building(m, 31.5, 0, 8.5, 4.5)
    building(m, 0, 5, 5, 8, style="brick")
    building(m, 0, 17, 5, 13)
    building(m, 35.5, 4.5, 4.5, 7.5, style="brick")
    building(m, 35.5, 16, 4.5, 14)
    building(m, 5, 26, 12, 4, style="brick")
    building(m, 22.5, 26.5, 13, 3.5)
    m.text(2.5, 15.2, "TO THE DOCK WARD", size=30, rot=-90)
    m.text(37.8, 14.2, "TO THE CASTLE", size=30, rot=90)
    m.text(19.7, 29.3, "TO THE SEA WARD", size=30)
    # banner across the north
    m.g("high", 20, 5.0, pr.banner(1300, "THE HEARTHLIGHT FOUNDATION — HAPPINESS GUARANTEED!"))
    m.text(20, 5.75, "Terms and conditions apply.", size=20, font="EB Garamond", weight=400, color="#f0d890", layer="high")
    # Foundation Pavilion (exterior): canvas walls + striped roof, flap door south
    px, py, pw, ph = 26, 6.5, 8, 6
    m.floor_rect(px, py, pw, ph, "carpet")
    tent = []
    cx, cy = px + pw / 2, py + ph / 2
    n = 16
    for i in range(n):
        a0, a1 = i * 2 * math.pi / n, (i + 1) * 2 * math.pi / n
        rx, ry = pw / 2 * 100 * 1.12, ph / 2 * 100 * 1.12
        p0 = (cx * 100 + math.cos(a0) * rx, cy * 100 + math.sin(a0) * ry)
        p1 = (cx * 100 + math.cos(a1) * rx, cy * 100 + math.sin(a1) * ry)
        tent.append(f'<polygon points="{cx*100:.0f},{cy*100:.0f} {p0[0]:.0f},{p0[1]:.0f} {p1[0]:.0f},{p1[1]:.0f}" fill="{"#a3182a" if i%2 else "#eee4cc"}" stroke="{INK}" stroke-width="4"/>')
    m.add("high", f'<g filter="url(#sh)">{"".join(tent)}</g>')
    m.add("high", f'<circle cx="{cx*100}" cy="{cy*100}" r="28" fill="#d8aa52" stroke="{INK}" stroke-width="5"/>')
    m.room(px, py, pw, ph, "canvas", doors=[("S", 3.5, 1.5, "red")])
    m.text(cx, py + ph + 0.95, "FOUNDATION PAVILION", size=30, color="#f0d890")
    # Great Midwinter Tree
    m.g("props", 20, 15, pr.pine(230, seed=4))
    m.terrain_wall([(20 + 1.6 * math.cos(a * math.pi / 6), 15 + 1.6 * math.sin(a * math.pi / 6)) for a in range(12)], closed=True)
    for i in range(10):
        a = i * 2 * math.pi / 10
        m.g("lowprop", 20 + 3.1 * math.cos(a), 15 + 3.1 * math.sin(a), pr.present_pile(3, 18, i), shadow=False)
    # Bureau of Festive Compliance
    m.g("props", 10.5, 8, pr.table(320, 90, "#5e0b18", "#efe2c0"))
    m.g("props", 10.5, 7.2, f'<rect x="-170" y="-26" width="340" height="52" fill="#2f7a46" stroke="{INK}" stroke-width="5"/>'
                         f'<text y="10" font-family="Cinzel" font-weight="900" font-size="24" text-anchor="middle" fill="#f0d890">BUREAU OF FESTIVE COMPLIANCE</text>')
    for i, x in enumerate((9, 10.5, 12)):
        m.g("props", x, 8.75, pr.chair(), rot=180)
    for k in range(5):  # queue rope posts
        m.g("lowprop", 8.5 + k * 1.0, 10.2, '<circle r="9" fill="#d8aa52" stroke="#150b0b" stroke-width="3"/>')
    m.add("lowprop", '<path d="M850 1020 Q900 1050 950 1020 Q1000 1050 1050 1020 Q1100 1050 1150 1020 Q1200 1050 1250 1020" fill="none" stroke="#8e1424" stroke-width="7"/>')
    # Snowman choir
    for i in range(5):
        a = math.pi * (0.15 + 0.17 * i)
        m.g("props", 15 + 2.4 * math.cos(a + math.pi), 10 - 1.2 * math.sin(a), pr.snowman())
    m.g("props", 13.6, 11.9, f'<rect x="-34" y="-20" width="68" height="40" fill="#3b2314" stroke="{INK}" stroke-width="4"/>'
                           f'<text y="7" font-family="Cinzel" font-size="14" font-weight="700" text-anchor="middle" fill="#f0d890">CHOIR</text>')
    # stall rows
    cols = [("#b51f30", "#efe6d0"), ("#2f7a46", "#efe6d0"), ("#d8aa52", "#7a1424"), ("#2c4f8a", "#efe6d0")]
    for i, (x, y) in enumerate([(8, 18.2), (11, 18.2), (8, 21.4), (11, 21.4), (27.5, 18.2), (30.5, 18.2), (27.5, 21.4), (30.5, 21.4), (33, 9.2)]):
        a, b = cols[i % 4]
        m.g("props", x, y, pr.stall(240, 140, a, b, seed=i))
    # Harl's pastry stall (wrecked later by DASH-ER)
    m.g("props", 14.4, 21.5, pr.stall(240, 140, "#e8c35a", "#7a4a22", seed=99))
    m.g("lowprop", 15.2, 23.2, pr.puddle(150, 60), shadow=False)
    m.g("props", 16.0, 22.6, pr.cart(170, 90), rot=-15)
    m.text(14.4, 20.2, "BRAMBLE'S PASTRIES", size=22, color="#f0d890", layer="high")
    # sleigh landing ring
    m.add("decal", f'<circle cx="2050" cy="2200" r="250" fill="none" stroke="#d8aa52" stroke-width="12" stroke-dasharray="40 26" opacity="0.85"/>')
    m.add("decal", f'<circle cx="2050" cy="2200" r="200" fill="none" stroke="#8e1424" stroke-width="5" opacity="0.6"/>')
    m.text(20.5, 22.15, "SLEIGH LANDING", size=26, color="#e8c35a", layer="decal")
    # candy canes growing from the cobbles
    for i, (x, y, r) in enumerate([(6.5, 11.5, -20), (17.5, 7.2, 15), (24, 9.3, -35), (24.5, 13.8, 40), (6.6, 15.6, 10),
                                   (33.6, 14.5, -15), (18.2, 24.8, 25), (25.5, 24.6, -10), (16.5, 13, 70), (23.5, 17.8, -60)]):
        m.g("props", x, y, pr.candy_cane(140), rot=r)
    # lamps
    for x, y in [(6, 6), (14.5, 4.5), (25.5, 5), (34.5, 13), (6, 16.5), (34.5, 16.5), (8, 25), (20, 12.2), (32, 25), (17, 18)]:
        lamp(m, x, y)
    # eggnog barrels, crates
    for x, y in [(33.7, 6.0), (34.3, 6.6), (6.2, 23.8), (6.9, 24.3)]:
        m.g("props", x, y, pr.barrel(28))
    m.g("props", 23.2, 24.6, pr.crate(70), rot=12)
    m.g("props", 24.1, 25.2, pr.present_pile(5, 30, 8))
    footprints(m, [(2, 15), (12, 14), (17, 16), (19, 20), (20, 28)], seed=1)
    footprints(m, [(38, 14), (30, 14.2), (29.8, 12.6)], seed=3)
    m.env = {"darkness": 0.1, "globalLight": True, "night": 0.62}
    # notes
    m.note(10.5, 9.3, "act1-bureau", "Encounter A: Bureau of Festive Compliance")
    m.note(18.2, 13.2, "act1-gifts", "Encounter B: The Nine Gifts of Midwinter")
    m.note(15.6, 23.6, "act1-dasher", "Encounter C: The Runaway Reindeer")
    m.note(21.8, 23.5, "act1-arrival", "The Arrival of Nicholas Red Clause")
    m.note(9.6, 23.0, "act2", "Act II: The First Collections (Edda)")
    m.note(30, 13.6, "lead-a", "Lead A: Foundation Pavilion (and the Service Elevator)")
    # tokens
    m.token("sprocket-jingles", 10.5, 9.5)
    m.token("festive-clerk", 9.0, 9.6)
    m.token("festive-clerk", 12.0, 9.6)
    m.token("festive-clerk", 29.5, 13.9)
    m.token("carolling-snowman", 12.6, 9.5)
    m.token("carolling-snowman", 17.4, 9.5)
    m.token("edda-hearth", 9.5, 23.4)
    m.token("agna-vell", 10.4, 24.1)
    m.token("harl-bramble", 14.4, 22.9)
    m.token("waterdeep-citizen", 17.5, 19.5)
    m.token("waterdeep-citizen", 23.5, 20.5)
    m.token("waterdeep-citizen", 25.3, 15.5)
    m.token("waterdeep-citizen", 9.7, 11.2)
    m.token("watch-constable", 3.5, 15.5)
    m.token("watch-constable", 36.8, 14.5)
    m.token("dash-er", 21.5, 25.0, hidden=True)
    m.token("red-clause", 20.5, 21.5, hidden=True, name="Nicholas Red Clause (Festive Projection)")
    m.token("hellforged-reindeer", 24, 21.5, hidden=True)
    m.token("jingle-bailiff", 7.5, 20.0, hidden=True)
    m.token("jingle-bailiff", 12.5, 24.5, hidden=True)
    m.token("toy-soldier", 8.0, 24.0, hidden=True)
    m.token("toy-soldier", 11.5, 22.8, hidden=True)
    m.token("marta-quill", 3.6, 14.4, hidden=True)
    return m


# =============================================================================
@register
def pavilion():
    m = Map("pavilion", "The Foundation Pavilion", 20, 16, seed=12, bg="#1a1214")
    m.floor_rect(1, 1, 18, 14, "carpet")
    m.room(1, 1, 18, 14, "canvas", doors=[("S", 8, 2, "red")])
    # back alcove for the service elevator (curtained), secret
    m.floor_rect(7, 1.5, 6, 3, "brass", layer="decal")
    m.wall([(7, 4.5), (9.2, 4.5)], "canvas")
    m.wall([(10.8, 4.5), (13, 4.5)], "canvas")
    m.wall([(7, 1), (7, 4.5)], "canvas")
    m.wall([(13, 1), (13, 4.5)], "canvas")
    m.door(9.2, 4.5, 10.8, 4.5, secret=True)
    m.g("props", 10, 2.8, pr.elevator(110))
    m.text(10, 4.1, "SERVICE ONLY", size=22, color="#e8c35a", layer="label")
    # public ledger + verification register
    m.g("props", 4.5, 4, pr.table(260, 110, "#5a3418", "#efe2c0"))
    m.g("props", 4.5, 4, pr.ledger_book(150, 90).split('<rect')[0] if False else pr.rect(150, 90, "#efe2c0", 4, 4))
    m.text(4.5, 2.4, "PUBLIC LEDGER", size=24, color="#e8c35a")
    m.g("props", 15.5, 4, pr.desk(220, 110))
    m.g("props", 15.5, 2.3, pr.filing_cabinet(160, 50))
    m.text(15.5, 5.6, "VERIFICATION REGISTER", size=20, color="#e8c35a")
    # gift crates
    for i, (x, y) in enumerate([(3, 8), (3.7, 9.2), (2.8, 10.6), (16.6, 8), (17.2, 9.4), (16.3, 10.8)]):
        m.g("props", x, y, pr.crate(80), rot=(i * 13) % 30 - 15)
    m.g("props", 10, 9.5, pr.present_pile(12, 120, 5))
    m.g("props", 6, 12.5, pr.table(220, 80, "#5e0b18"))
    m.g("props", 14, 12.5, pr.table(220, 80, "#5e0b18"))
    for x in (5.2, 6.8, 13.2, 14.8):
        m.g("props", x, 13.4, pr.chair())
    m.g("props", 10, 7.0, pr.rug(500, 140, "#2f7a46", "#d8aa52"), shadow=False)
    m.light(10, 7.5, 7, 2, color="#ffcf8a", alpha=0.3, anim="torch", speed=2, intensity=2)
    m.light(4.5, 4.5, 3, 1, color="#ffcf8a", alpha=0.28)
    m.light(15.5, 4.5, 3, 1, color="#ffcf8a", alpha=0.28)
    m.env = {"darkness": 0.45, "globalLight": False}
    m.note(4.5, 5.4, "lead-a", "Lead A: the public ledger")
    m.note(15.5, 6.2, "lead-a", "The hidden verification register (HOLIDAY_OVERRIDE)")
    m.note(10, 3.4, "finding-workshop", "The Service Elevator: GOODWILL-999")
    m.token("festive-clerk", 4.5, 5.6)
    m.token("festive-clerk", 15.5, 6.6)
    m.token("toy-soldier", 10, 14.0)
    return m


# =============================================================================
@register
def records():
    m = Map("records", "The Font of Knowledge: City Records", 24, 18, seed=13, bg="#141012")
    m.floor_rect(1, 1, 22, 16, "flagstone")
    m.room(1, 1, 22, 16, "stone", doors=[("S", 10, 3, "wood")])
    for x in (4, 9, 15, 20):
        m.window(x, 1, x + 1.5, 1)
    # archive room NE
    m.room(15, 1, 8, 6, "stone", doors=[("W", 2.5, 1.5, "iron")])
    m.floor_rect(15, 1, 8, 6, "darkplanks", layer="decal", stroke=False)
    for i in range(3):
        m.g("props", 19, 2.2 + i * 1.6, pr.scroll_rack(560, 46, ), shadow=True)
    m.text(19, 6.6, "RESIDENCE ROLLS", size=24, color="#e8c35a")
    # shelves (walls block sight)
    for i, y in enumerate((9, 12)):
        for x0 in (2.5, 8.5):
            m.g("props", x0 + 2, y, pr.bookshelf(400, 40, seed=i * 10 + int(x0)))
            m.wall([(x0, y), (x0 + 4, y)], "shelf", draw=False)
    # Oghma shrine
    m.g("lowprop", 5.5, 4, pr.rug(400, 260, "#2c3f6a", "#d8aa52"), shadow=False)
    m.g("props", 5.5, 3.2, pr.lectern())
    m.g("props", 5.5, 2.0, '<circle r="34" fill="#efe2c0" stroke="#150b0b" stroke-width="5"/><text y="12" font-family="Cinzel" font-size="34" font-weight="900" text-anchor="middle" fill="#2c3f6a">✦</text>')
    m.text(5.5, 5.6, "SHRINE OF OGHMA", size=22, color="#e8c35a")
    # clerk counter
    m.g("props", 11, 6, pr.table(380, 80, "#5a3418"))
    m.g("props", 11, 5.3, pr.desk(160, 70))
    m.g("props", 16.5, 11, pr.table(260, 120, "#6e4527"))
    m.g("props", 16.5, 14, pr.table(260, 120, "#6e4527"))
    for x, y in [(15.6, 10), (17.4, 10), (15.6, 15), (17.4, 15)]:
        m.g("props", x, y, pr.chair(), rot=0 if y < 12 else 180)
    m.g("props", 21, 13, pr.filing_cabinet(100, 60), rot=90)
    m.g("props", 21, 15, pr.filing_cabinet(100, 60), rot=90)
    for x, y in [(3, 15.5), (21.5, 9)]:
        m.g("props", x, y, pr.pillar(30))
    for x, y in [(5.5, 4.5), (11, 7), (19, 4), (16.5, 12.5), (4.5, 11.0), (10.5, 14.5)]:
        m.light(x, y, 4, 1, color="#ffd08a", alpha=0.28, anim="torch", speed=2, intensity=1)
    m.env = {"darkness": 0.5, "globalLight": False}
    m.note(11, 6.9, "lead-b", "Lead B: City Records")
    m.note(19, 4.0, "lead-b", "The residence rolls (Exhibit B)")
    m.note(5.5, 4.6, "carol-callback", "The Christmas Carol callback")
    m.token("ossian-pell", 11, 5.0)
    m.token("watch-constable", 11.5, 15.4)
    m.token("midwinter-ghost", 5.5, 4.4, hidden=True)
    return m


# =============================================================================
@register
def depot():
    m = Map("depot", "The Hidden Delivery Depot", 28, 20, seed=14, bg="#121014")
    m.fill_all("slush")
    m.floor_rect(1, 1, 24, 18, "planks")
    m.room(1, 1, 24, 18, "brick", doors=[("W", 8, 2, "wood"), ("E", 4, 3, "iron"), ("E", 11, 3, "iron")])
    # Mizzle's office
    m.room(17, 1, 8, 5, "timber", doors=[("S", 1.5, 1.4, "wood")])
    m.floor_rect(17, 1, 8, 5, "darkplanks", layer="decal", stroke=False)
    m.g("props", 21, 3, pr.desk(200, 100))
    m.g("props", 23.8, 2.5, pr.filing_cabinet(80, 50), rot=90)
    m.g("props", 18.3, 2.1, pr.scroll_rack(150, 40))
    m.text(21, 5.4, "MANIFESTS", size=22, color="#e8c35a")
    # conveyor snake
    m.g("props", 9, 4, pr.conveyor(1200, 80, 8, 1))
    m.g("props", 15, 7, pr.conveyor(80 * 1.0, 300, 0, 2))
    m.g("props", 11, 10, pr.conveyor(900, 80, 6, 3))
    m.g("props", 3.5, 12.5, pr.chute(70))
    m.g("props", 15.2, 10, pr.chute(60))
    # parcel stacks
    for i, (x, y) in enumerate([(4, 15), (5.2, 15.4), (4.5, 16.6), (8, 16), (9.2, 16.4), (12, 15.8), (13, 16.5)]):
        m.g("props", x, y, pr.crate(80), rot=(i * 17) % 30 - 15)
    m.g("props", 19.5, 15, pr.present_pile(10, 100, 2))
    # sleigh bay (east)
    m.g("props", 21.5, 10.5, pr.sleigh(240, 140), rot=0)
    m.text(21.5, 8.2, "SLEIGH BAY", size=26, color="#e8c35a")
    m.add("decal", '<rect x="2550" y="500" width="250" height="1000" fill="#d8dfea" opacity="0.8"/>')
    for x, y in [(5, 3), (12, 3), (19, 9), (8, 13), (14, 14), (21, 13), (21, 3.5)]:
        m.light(x, y, 4, 1, color="#ffc070", alpha=0.3, anim="torch", speed=2, intensity=1)
    m.light(15.2, 10, 2, 0, color="#ff3b3b", alpha=0.35, anim="pulse", speed=2, intensity=3)
    m.env = {"darkness": 0.55, "globalLight": False}
    m.note(21, 4.2, "lead-c", "Lead C: Mizzle's office")
    m.note(9, 5, "lead-c", "The parcel line (Parcel Route to the Workshop)")
    m.note(21.5, 11.8, "finding-workshop", "The Sleigh Route")
    m.token("mizzle", 21, 3.9)
    m.token("festive-clerk", 9, 5.3)
    m.token("festive-clerk", 11, 11.3)
    m.token("toy-soldier", 5, 9)
    m.token("toy-soldier", 18, 15.8)
    m.token("brass-supervisor", 15, 13, hidden=True)
    m.token("hellforged-reindeer", 24, 10.5)
    return m


# =============================================================================
@register
def rooftops():
    m = Map("rooftops", "Castle Ward Rooftops (Sleigh Chase)", 36, 24, seed=15, bg="#0e1016")
    m.fill_all("slush")
    m.add("floor", f'<rect width="{m.W}" height="{m.H}" fill="#0c0e14" opacity="0.6"/>')
    blocks = [(0, 0, 8, 7), (9, 0, 7, 6), (17, 0, 9, 7.5), (27, 0, 9, 6), (0, 8, 6, 8), (7, 7.5, 9, 9), (17, 9, 6, 7),
              (24, 7, 12, 8), (0, 17, 10, 7), (11, 17.5, 8, 6.5), (20, 16.5, 7, 7.5), (28, 16, 8, 8)]
    r = random.Random(3)
    for i, (x, y, w, h) in enumerate(blocks):
        m.floor_rect(x + 0.2, y + 0.2, w - 0.4, h - 0.4, "roof")
        # ridge line
        if w >= h:
            m.add("lowprop", f'<line x1="{(x+0.4)*100}" y1="{(y+h/2)*100}" x2="{(x+w-0.4)*100}" y2="{(y+h/2)*100}" stroke="{INK}" stroke-width="14"/><line x1="{(x+0.4)*100}" y1="{(y+h/2)*100}" x2="{(x+w-0.4)*100}" y2="{(y+h/2)*100}" stroke="#eef3f8" stroke-width="7"/>')
        else:
            m.add("lowprop", f'<line x1="{(x+w/2)*100}" y1="{(y+0.4)*100}" x2="{(x+w/2)*100}" y2="{(y+h-0.4)*100}" stroke="{INK}" stroke-width="14"/><line x1="{(x+w/2)*100}" y1="{(y+0.4)*100}" x2="{(x+w/2)*100}" y2="{(y+h-0.4)*100}" stroke="#eef3f8" stroke-width="7"/>')
        for _ in range(2):
            cx, cy = x + r.uniform(1, w - 1), y + r.uniform(1, h - 1)
            m.g("props", cx, cy, pr.chimney(80, 60))
            m.wall([(cx - 0.4, cy - 0.3), (cx + 0.4, cy - 0.3), (cx + 0.4, cy + 0.3), (cx - 0.4, cy + 0.3)], "brick",
                   closed=True, draw=False)
            m.light(cx, cy, 2, 0, color="#ff8a3a", alpha=0.22, anim="torch", speed=2, intensity=2)
    m.text(18, 12.5, "ALLEYS: A LONG WAY DOWN", size=26, color="#9fb0c6", layer="label")
    m.g("props", 4, 3.5, pr.sleigh(240, 140), rot=20)
    m.light(4, 3.5, 6, 2, color="#ffd27a", alpha=0.3, anim="torch")
    m.env = {"darkness": 0.5, "globalLight": True}
    m.note(4, 5.0, "sleigh-chase", "The Rooftop Sleigh Chase")
    m.token("yule-engine", 30, 20)
    m.token("hellforged-reindeer", 27, 12)
    m.token("hellforged-reindeer", 31, 4)
    return m


# =============================================================================
def workshop_lamps(m, pts, color="#ffc46a", dim=5, bright=1.5):
    for x, y in pts:
        m.g("high", x, y, '<circle r="16" fill="#26232a" stroke="#150b0b" stroke-width="4"/><circle r="8" fill="#ffd27a"/>')
        m.light(x, y, dim, bright, color=color, alpha=0.3, anim="torch", speed=2, intensity=1)


@register
def intake():
    m = Map("intake", "Workshop Nine: The Intake Department", 26, 20, seed=16, bg="#0d0b0c")
    m.floor_rect(1, 1, 24, 18, "factory")
    m.room(1, 1, 24, 18, "iron", doors=[("E", 8, 2, None)])
    m.door(25, 9, 25, 11, style="iron", locked=True)
    m.text(23.8, 8.4, "RESTRICTED", size=24, color="#ff6a5a", rot=90)
    m.g("props", 3, 10, pr.chute(110))
    m.text(3, 12.0, "DELIVERY INTAKE", size=22, color="#e8c35a")
    m.g("props", 12.5, 10, pr.conveyor(1500, 90, 9, 7))
    for i, (x, label, c) in enumerate([(8, "ACCEPTED", "#5aa05a"), (12.5, "DEFAULTED", "#d8aa52"), (17, "REPOSSESSED", "#c0283a")]):
        m.g("props", x, 10, pr.stamp_press())
        m.text(x, 8.6, label, size=26, color=c)
    r = random.Random(8)
    for i in range(16):
        x, y = r.uniform(5, 21), r.choice([r.uniform(3, 6.5), r.uniform(13.5, 17)])
        m.g("props", x, y, pr.mech_arm(180, r.uniform(0, 360)))
    # floating certificates (decals)
    for i in range(40):
        x, y = r.uniform(4, 22), r.uniform(2, 18)
        m.add("high", f'<rect x="{x*100:.0f}" y="{y*100:.0f}" width="34" height="24" fill="#efe2c0" stroke="{INK}" stroke-width="2" opacity="0.85" transform="rotate({r.uniform(-40,40):.0f} {x*100:.0f} {y*100:.0f})"/>')
    m.g("props", 21.5, 3.2, pr.desk(200, 100))
    m.g("props", 21.5, 16.5, pr.machine(220, 130, 2))
    m.text(21.5, 18.1, "AUDIT DISPLAY", size=20, color="#e8c35a")
    m.g("props", 22.6, 10, pr.hatch(60, 120))
    m.add("label", f'<text x="1300" y="160" font-family="Cinzel" font-weight="900" font-size="40" text-anchor="middle" fill="#d8aa52" stroke="{INK}" stroke-width="7" paint-order="stroke">THANK YOU FOR YOUR ACCEPTANCE</text>')
    workshop_lamps(m, [(5, 4), (12.5, 4), (20, 6), (5, 16), (12.5, 16), (20, 13), (8, 10), (17, 10)])
    m.light(3, 10, 3, 0.5, color="#d8aa52", alpha=0.3, anim="pulse")
    m.env = {"darkness": 0.62, "globalLight": False}
    m.note(12.5, 11.4, "area-a", "Area A: The Intake Department")
    m.note(23.7, 10, "area-a", "The restricted door (AC 17, 30 HP)")
    m.note(21.5, 17.4, "area-a", "Horror detail: UNASSIGNED MATERNAL AFFECTION")
    m.token("festive-clerk", 8, 12)
    m.token("festive-clerk", 17, 12)
    m.token("collared-worker", 10, 8.2)
    m.token("collared-worker", 15, 8.2)
    m.token("collared-worker", 20, 11.8)
    m.token("intake-lock", 24.3, 10)
    m.token("jingle-bailiff", 21.5, 4.6, hidden=True)
    return m


@register
def assembly():
    m = Map("assembly", "Workshop Nine: The Assembly Line of Eternal Gratitude", 32, 22, seed=17, bg="#0d0b0c")
    m.floor_rect(1, 1, 30, 20, "factory")
    m.room(1, 1, 30, 20, "brass", doors=[("W", 10, 2, "iron"), ("E", 9, 2, "iron"), ("N", 14, 2, "brass")])
    m.add("label", f'<text x="1600" y="190" font-family="Cinzel" font-weight="900" font-size="46" text-anchor="middle" fill="#ffd27a" stroke="{INK}" stroke-width="8" paint-order="stroke">A HAPPY WORKER IS A PRODUCTIVE WORKER</text>')
    m.g("props", 14, 6.5, pr.conveyor(2200, 90, 12, 11))
    m.g("props", 14, 12.5, pr.conveyor(2200, 90, 12, 12))
    r = random.Random(9)
    for row_y in (5.4, 7.6, 11.4, 13.6):
        for i in range(8):
            x = 5 + i * 2.6
            m.g("props", x, row_y, pr.rect(90, 46, "#4a3a2a", 4, 4) + pr.rect(50, 24, "#efe2c0", 2, 2))
    # supervisor platform
    m.floor_rect(25, 3, 5, 5, "brass", layer="lowprop")
    m.g("props", 27.5, 5.5, pr.machine(300, 200, 5))
    m.text(27.5, 8.6, "OVERSEER", size=24, color="#e8c35a")
    # prisoner pens
    for i, x in enumerate((19, 23.5, 28)):
        m.g("props", x, 17.5, pr.cage(360, 280))
        m.wall([(x - 1.8, 16.1), (x + 1.8, 16.1), (x + 1.8, 18.9), (x - 1.8, 18.9)], "iron", closed=True, draw=False,
               sight="none")
    m.text(23.5, 15.6, "AWAITING PROCESSING", size=26, color="#ff7a6a")
    # records desk west
    m.g("props", 4.5, 17, pr.desk(260, 120))
    m.g("props", 4.5, 18.8, pr.filing_cabinet(200, 50))
    m.text(4.5, 15.6, "INTAKE RECORDS", size=22, color="#e8c35a")
    # music boxes & laughing toys piles
    m.g("props", 10, 17.5, pr.present_pile(9, 90, 21))
    m.g("props", 13.5, 17.5, pr.present_pile(9, 90, 22))
    # emergency stop levers
    for x, y in ((2.2, 6.5), (25.8, 12.5)):
        m.g("props", x, y, '<rect x="-24" y="-40" width="48" height="80" fill="#26232a" stroke="#150b0b" stroke-width="5"/><circle cy="-18" r="14" fill="#c0283a" stroke="#150b0b" stroke-width="3"/>')
    m.text(2.2, 5.3, "STOP", size=20, color="#ff6a5a")
    workshop_lamps(m, [(5, 3), (14, 3), (23, 3), (5, 9.5), (14, 9.5), (23, 9.5), (5, 15), (14, 15), (23.5, 13.8), (28, 15.2)])
    m.env = {"darkness": 0.62, "globalLight": False}
    m.note(14, 9.5, "area-b", "Area B: The Assembly Line of Eternal Gratitude")
    m.note(23.5, 16.0, "area-b-dilemma", "The dilemma: save the workers or secure the records")
    m.note(4.5, 15.9, "area-b-dilemma", "Records to copy (DC 16)")
    m.token("tilda-marr", 10.2, 13.6)
    for i, (x, y) in enumerate([(5, 7.6), (7.6, 5.4), (12.8, 11.4), (15.4, 13.6), (18, 7.6), (20.6, 11.4)]):
        m.token("collared-worker", x, y)
    m.token("brass-supervisor", 27.5, 4.2)
    m.token("jingle-bailiff", 24, 10)
    m.token("jingle-bailiff", 24, 14.8)
    m.token("toy-soldier", 21, 9.5, hidden=True)
    m.token("toy-soldier", 21, 15.5, hidden=True)
    m.token("edda-hearth", 19, 17.6, hidden=True)
    return m


@register
def midnight():
    m = Map("midnight", "Workshop Nine: The Department of Perpetual Midnight", 24, 24, seed=18, bg="#07070c")
    cx, cy, R = 12, 12, 11
    pts = [(cx + R * math.cos(i * math.pi / 12), cy + R * math.sin(i * math.pi / 12)) for i in range(24)]
    m.floor_poly(pts, "grate")
    m.floor_circle(cx, cy, 8.5, "hellstone", layer="floor")
    # walls with three doors: W, N, E
    door_idx = {12: "W", 18: "N", 0: "E"}
    seg = list(zip(pts, pts[1:] + pts[:1]))
    for i, (a, b) in enumerate(seg):
        if i in (11, 17, 23):  # segment ending at the door vertex: split the next one
            pass
    for i, (a, b) in enumerate(seg):
        if i in (12, 18, 0):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ux, uy = (b[0] - a[0]), (b[1] - a[1])
            L = math.hypot(ux, uy)
            ux, uy = ux / L, uy / L
            d0 = (mx - ux * 0.8, my - uy * 0.8)
            d1 = (mx + ux * 0.8, my + uy * 0.8)
            m.wall([a, d0], "brass")
            m.wall([d1, b], "brass")
            m.door(*d0, *d1, style="brass")
        else:
            m.wall([a, b], "brass")
    m.g("lowprop", cx, cy, pr.clock_face(560, (11, 59)))
    # gears around the rim
    r = random.Random(4)
    for i in range(10):
        a = i * 2 * math.pi / 10 + 0.3
        gx, gy = cx + 9.3 * math.cos(a), cy + 9.3 * math.sin(a)
        if any(abs(a % (2 * math.pi) - t) < 0.35 for t in (0, math.pi, 1.5 * math.pi, 2 * math.pi)):
            continue
        m.g("props", gx, gy, pr.gear(r.uniform(70, 110), r.randint(10, 16)), rot=r.uniform(0, 360))
        m.terrain_wall([(gx + 0.8 * math.cos(t * math.pi / 4), gy + 0.8 * math.sin(t * math.pi / 4)) for t in range(8)], closed=True)
    m.g("high", cx, cy - 4.2, pr.trapped_sun(95))
    m.add("label", f'<text x="1200" y="2150" font-family="Cinzel" font-weight="900" font-size="30" text-anchor="middle" fill="#ffd27a" stroke="{INK}" stroke-width="6" paint-order="stroke">SERVICE CONCLUDES AT DAWN. DAWN IS CURRENTLY UNAVAILABLE.</text>')
    m.light(cx, cy - 4.2, 7, 2.5, color="#ffd060", alpha=0.32, anim="pulse", speed=1, intensity=2)
    for i in range(6):
        a = i * math.pi / 3 + 0.5
        m.light(cx + 7.2 * math.cos(a), cy + 7.2 * math.sin(a), 3, 0.5, color="#7aa0ff", alpha=0.22)
    m.env = {"darkness": 0.72, "globalLight": False}
    m.note(cx, cy + 1.5, "area-c", "Area C: The Department of Perpetual Midnight")
    m.note(cx + 1.4, cy - 4.2, "area-c", "The trapped sun")
    m.token("midnight-engine", cx, cy)
    m.token("toy-soldier", cx - 4, cy + 4)
    m.token("toy-soldier", cx + 4, cy + 4)
    m.token("brass-supervisor", cx, cy + 6.5, hidden=True)
    return m


@register
def ledger():
    m = Map("ledger", "Workshop Nine: The Ledger of Abandoned Souls", 24, 20, seed=19, bg="#090708")
    m.floor_rect(1, 1, 22, 18, "darkplanks")
    m.room(1, 1, 22, 18, "stone", doors=[("S", 10, 2, "brass")])
    for row, y in enumerate((3.5, 6.5, 9.5, 12.5)):
        for x0, x1 in ((2, 9), (13, 20)):
            mid = (x0 + x1) / 2
            m.g("props", mid, y, pr.jar_shelf((x1 - x0) * 100, 46, seed=row * 7 + x0))
            m.wall([(x0, y), (x1, y)], "shelf", draw=False)
    for y in (2, 15):
        m.g("props", 5.5, y + 0.5, pr.scroll_rack(500, 46, ))
    for i in range(4):
        m.g("props", 21.5, 3 + i * 1.3, pr.filing_cabinet(110, 60), rot=90)
    # reading desk and vault
    m.g("lowprop", 11, 15.5, pr.rug(600, 320, "#3a0a12", "#c99a3a"), shadow=False)
    m.g("props", 11, 15.5, pr.lectern())
    m.g("props", 11, 9, pr.machine(200, 160, 3))
    m.text(11, 10.5, "SORTING MECHANISM", size=22, color="#e8c35a")
    m.room(17, 14, 5, 4, "iron", doors=[("W", 1.5, 1.2, "iron")])
    m.g("props", 19.5, 16, pr.ledger_book(150, 90).split("<line")[0] + pr.rect(110, 70, "#efe2c0", 4, 3))
    m.text(19.5, 17.6, "GENUINE BARGAINS", size=18, color="#e8c35a")
    m.light(11, 15.5, 4, 1, color="#ffcf8a", alpha=0.3, anim="torch", speed=2, intensity=1)
    m.light(11, 9, 3, 0.5, color="#c8a0ff", alpha=0.3, anim="pulse")
    m.light(19.5, 16, 2, 0.5, color="#ff5a3a", alpha=0.3)
    for x, y in ((5.5, 5), (16.5, 5), (5.5, 11), (16.5, 11)):
        m.light(x, y, 3, 0.5, color="#9fe0c8", alpha=0.22, anim="fog")
    m.env = {"darkness": 0.75, "globalLight": False}
    m.note(11, 16.6, "area-d", "Area D: The Ledger of Abandoned Souls")
    m.note(19.5, 15.2, "area-d", "A genuine soul bargain")
    m.note(11, 7.8, "reveal", "The reveal: the Project Yuletide memorandum")
    m.token("festive-clerk", 8, 15)
    m.token("festive-clerk", 14, 8)
    return m


@register
def court():
    m = Map("court", "The High Court of Seasonal Obligations", 16, 12, seed=20, bg="#050304")
    m.fill_all("hellstone")
    cx, cy = 8, 6.4
    # outer circular wall approximated, clipped to rectangle edge
    pts = []
    for i in range(32):
        a = i * 2 * math.pi / 32
        x, y = cx + 7.7 * math.cos(a), cy + 5.9 * math.sin(a)
        pts.append((min(15.7, max(0.3, x)), min(11.7, max(0.3, y))))
    inner = pts
    m.floor_poly(inner, "marble")
    # south entrance door (great iron door)
    s_i = 8
    for i in range(32):
        a, b = pts[i], pts[(i + 1) % 32]
        if i in (7, 8):
            continue
        m.wall([a, b], "hell")
    m.wall([pts[7], (7.3, pts[8][1])], "hell")
    m.wall([(8.7, pts[8][1]), pts[9]], "hell")
    m.door(7.3, pts[8][1], 8.7, pts[8][1], style="iron")
    # dais + throne north
    m.floor_rect(5.5, 0.9, 5, 2.6, "carpet", layer="lowprop")
    m.g("lowprop", 8, 3.75, pr.steps(500, 1))
    m.g("props", 8, 1.7, pr.throne(230, 150))
    # witness lectern + Arbiter (west)
    m.g("props", 2.6, 6.4, pr.lectern(), rot=90)
    m.g("props", 1.6, 6.4, pr.scales(), rot=90)
    m.text(2.4, 8.0, "WITNESS LECTERN", size=18, color="#e8c35a")
    # bell mechanism (east)
    m.g("props", 14.2, 6.4, pr.bell_frame(300), rot=90)
    m.text(13.7, 9.2, "THE MIDNIGHT DOCKET", size=18, color="#e8c35a", rot=-90)
    # central pit with furnace and chained ledger
    m.g("lowprop", cx, cy + 0.3, pr.furnace_pit(150))
    m.g("props", cx, cy + 0.3, pr.ledger_book(150, 100))
    m.terrain_wall([(cx + 1.5 * math.cos(t * math.pi / 6), cy + 0.3 + 1.5 * math.sin(t * math.pi / 6)) for t in range(12)], closed=True)
    # writ pedestals
    for x, y in ((3.7, 2.6), (12.3, 2.6), (8, 10.0)):
        m.g("lowprop", x, y, pr.writ_frame(), shadow=False)
    # catwalks / conveyors
    m.g("lowprop", 4.6, 9.2, pr.conveyor(500, 60, 4, 31), rot=-30)
    m.g("lowprop", 11.4, 9.2, pr.conveyor(500, 60, 4, 32), rot=30)
    m.add("high", f'<rect x="500" y="420" width="600" height="40" fill="{m.pattern("grate")}" stroke="{INK}" stroke-width="4" opacity="0.9"/>')
    # hanging contracts (high layer decals)
    r = random.Random(12)
    for i in range(60):
        x, y = r.uniform(1.5, 14.5), r.uniform(1.2, 11)
        if math.hypot(x - cx, y - cy) < 2:
            continue
        m.add("high", f'<line x1="{cx*100}" y1="{(cy+0.3)*100}" x2="{x*100:.0f}" y2="{y*100:.0f}" stroke="#d8aa52" stroke-width="1.2" opacity="0.35"/>')
        m.add("high", f'<rect x="{x*100-10:.0f}" y="{y*100-7:.0f}" width="20" height="14" fill="#efe2c0" opacity="0.8" stroke="{INK}" stroke-width="1.5" transform="rotate({r.uniform(-30,30):.0f} {x*100:.0f} {y*100:.0f})"/>')
    m.light(cx, cy + 0.3, 6, 2, color="#ff5a1a", alpha=0.38, anim="torch", speed=3, intensity=4)
    m.light(5.6, 1.5, 2, 0.5, color="#ff7a2a", alpha=0.3, anim="torch")
    m.light(10.4, 1.5, 2, 0.5, color="#ff7a2a", alpha=0.3, anim="torch")
    for x, y in ((3.7, 2.6), (12.3, 2.6), (8, 10.0)):
        m.light(x, y, 1.5, 0.5, color="#ffd27a", alpha=0.3, anim="pulse")
    m.light(2.2, 6.4, 2, 0.5, color="#ffd27a", alpha=0.26)
    m.light(14.2, 6.4, 2, 0.5, color="#ffd27a", alpha=0.26)
    m.env = {"darkness": 0.7, "globalLight": False}
    m.note(8, 4.6, "act4", "Act IV: The Final Arbitration")
    m.note(2.6, 7.3, "legal-warfare", "The legal warfare system")
    m.note(14.2, 8.0, "nine-bells", "The nine bells")
    m.note(9.7, 6.7, "kill-red-clause", "If the players kill the Red Clause")
    m.token("red-clause", 8, 2.0)
    m.token("brass-arbiter", 1.5, 6.4)
    m.token("writ-1", 3.7, 2.6)
    m.token("writ-2", 12.3, 2.6)
    m.token("writ-3", 8, 10.0)
    m.token("master-ledger", 8, 6.7)
    m.token("jingle-bailiff", 5.0, 4.6)
    m.token("jingle-bailiff", 11.0, 4.6)
    m.token("jingle-bailiff", 12.6, 8.2, hidden=True)
    return m


ORDER = ["market", "pavilion", "records", "depot", "rooftops", "intake", "assembly", "midnight", "ledger", "court"]

if __name__ == "__main__":
    out = "/home/claude/il/module/assets/maps"
    prev = "/home/claude/rc/art/preview"
    os.makedirs(prev, exist_ok=True)
    which = sys.argv[1:] or ORDER
    data = {}
    if os.path.exists("/home/claude/rc/src/scenes.json"):
        data = json.load(open("/home/claude/rc/src/scenes.json"))
    for k in which:
        m = MAPS[k]()
        m.render(f"{out}/{k}.webp", f"{prev}/{k}.webp")
        data[k] = m.export()
        print(k, m.W, m.H, "walls", len(m.walls), "lights", len(m.lights), "tokens", len(m.tokens))
    json.dump(data, open("/home/claude/rc/src/scenes.json", "w"), indent=0)
