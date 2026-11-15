"""Kharad-Varr, the Hold: eight side-quest venues (two taverns, baths, gaming house, smith, enchanter,
apothecary, rune smiths). Same authoring API as il_maps.py: walls drawn from the exported geometry,
low dark lighting, journal pins (hold:<page>) and placed proprietors.

Shared walls are drawn once: the neighbouring room opens that side with a full-length gap.
room() offsets: N from the left, E from the top, S from the right, W from the bottom."""
import math
from il_maps import register, lamp, brazier, fungus, crates, barrels, banner_wall, Map
import il_mapkit as k
import props as pr


def BOOK(w, h):
    return (f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="6" fill="#5a1a14" stroke="#150b0b" stroke-width="5"/>'
            f'<rect x="{-w/2+8}" y="{-h/2+8}" width="{w/2-12}" height="{h-16}" fill="#efe2c0"/>'
            f'<rect x="{4}" y="{-h/2+8}" width="{w/2-12}" height="{h-16}" fill="#e6d6b0"/>'
            f'<line x1="0" y1="{-h/2+6}" x2="0" y2="{h/2-6}" stroke="#150b0b" stroke-width="4"/>')


def table4(m, x, y, round_=False):
    m.g("props", x, y, pr.round_table(46, "#6e4527") if round_ else pr.table(110, 80, "#6e4527"))
    for dx, dy, r in ((-0.75, 0, 90), (0.75, 0, 270), (0, -0.65, 180), (0, 0.65, 0)):
        m.g("props", x + dx, y + dy, pr.chair(), rot=r)


def counter(m, x0, y0, x1, y1, top="#7a4a22"):
    """Bar or shop counter: hip-high, so it stops movement but not sight (terrain wall)."""
    m.add("props", f'<rect x="{m.P(x0)}" y="{m.P(y0)}" width="{m.P(x1-x0)}" height="{m.P(y1-y0)}" fill="#4a2a14" stroke="#150b0b" stroke-width="6" filter="url(#sh)"/>'
                   f'<rect x="{m.P(x0)+8}" y="{m.P(y0)+8}" width="{m.P(x1-x0)-16}" height="{m.P(y1-y0)-16}" fill="{top}"/>')
    m.terrain_wall([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True)


def pool(m, x, y, w, h, hot=False):
    m.floor_rect(x - 0.35, y - 0.35, w + 0.7, h + 0.7, "marble")
    m.water_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
    if hot:
        for i in range(3):
            m.steam(x + w * (0.25 + 0.25 * i), y + h / 2, 1.3)


def booth_row(m, x, y, w=140):
    m.g("props", x, y, pr.table(w, 80, "#4a2a18"))
    m.g("props", x, y - 0.7, pr.bench(w), rot=180)
    m.g("props", x, y + 0.7, pr.bench(w))


# ============================================================ THE LOW LANTERN (Lowhearth tavern)
@register
def low_lantern():
    m = Map("low-lantern", "The Low Lantern (Lowhearth tavern)", 28, 20, seed=201, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 17, 12, "planks")
    m.room(2, 2, 17, 12, "dwarf", doors=[("S", 7, 2, "wood"), ("E", 2, 1.5, "wood"), ("E", 8.5, 1.5, "wood")])
    m.g("props", 7, 2.35, pr.jar_shelf(800, 30, 4))
    counter(m, 3, 3.6, 11, 4.6)
    for x in range(4, 11, 2):
        m.g("props", x, 5.25, pr.chair())
    barrels(m, 12.2, 2.9, 11, 2)
    m.g("props", 18, 5.5, pr.crate(60)); m.g("props", 18.2, 6.4, pr.crate(50), rot=15)
    for (x, y) in ((4.5, 4.1), (6.8, 4.0), (9.3, 4.15)):
        m.g("high", x, y, '<circle r="9" fill="#c8963a" stroke="#150b0b" stroke-width="3"/><circle r="5" fill="#3a2410"/>')
    m.g("props", 15.5, 3.2, k.forge(170, 110))  # the great hearth
    m.light(15.5, 3.2, 6, 2, "#ff9a3a", alpha=0.4, anim="torch", speed=2, intensity=3)
    for (x, y, rd) in ((5, 8, False), (9, 8, True), (13, 7, False), (5, 11.5, False), (9, 11.5, True)):
        table4(m, x, y, rd)
    # Song Night stage
    m.floor_rect(13.5, 9.5, 5, 4, "dwarfslab", layer="lowprop")
    m.g("lowprop", 16, 11.5, pr.rug(320, 220, "#5a1a14", "#a86f32"), shadow=False)
    m.g("props", 16, 10.3, pr.lectern())
    lamp(m, 2.6, 12.8); lamp(m, 18.4, 12.8); lamp(m, 10.5, 9.8, dim=5)
    # brewery (NE) — west side shared with the taproom
    m.floor_rect(19, 2, 7, 6, "dwarfslab")
    m.room(19, 2, 7, 6, "dwarf", gaps=[("W", 0, 6)], doors=[("S", 3, 1.2, "wood")])
    for i in range(3):
        barrels(m, 21 + i * 1.6, 3.2, i, 2)
    m.g("props", 23.5, 6.2, k.filter_tank(50))
    # cellar (SE): the empty Deepcap racks
    m.floor_rect(19, 8, 7, 9, "rock")
    m.room(19, 8, 7, 9, "dwarf", gaps=[("N", 0, 7), ("W", 3, 6)])
    for (x, y) in ((21, 10), (23.5, 10), (21, 12.5)):
        barrels(m, x, y, int(x * 3 + y), 3)
    m.g("lowprop", 24, 14.6, pr.hatch(120, 120))
    m.water_poly([(22.6, 15.9), (25.8, 15.9), (25.8, 16.8), (22.6, 16.8)], foul=True)
    fungus(m, 20.2, 15.8, 4, 40, 3)
    # street (Lift Street, Lowhearth)
    m.floor_rect(0, 14, 19, 3, "dwarfslab")
    m.floor_rect(0, 17, 28, 3, "dwarfslab")
    m.water_poly([(0, 17.7), (28, 17.7), (28, 18.4), (0, 18.4)], foul=True)
    lamp(m, 6, 14.6); lamp(m, 15, 16.4); lamp(m, 24, 19.4)
    banner_wall(m, 13, 2.2)
    m.env = {"darkness": 0.75, "globalLight": False}
    m.note(9, 6.4, "hold:low-lantern", "The Low Lantern")
    m.note(16, 12.6, "hold:q-low-lantern", "Side Quest: The Missing Verse")
    m.note(24, 14.6, "hold:q-low-lantern", "Cellar hatch (Deepcap racks)")
    m.token("grimma", 7, 3.0)
    m.token("lowhearth-worker", 5, 8.7); m.token("lowhearth-worker", 9.7, 11.5); m.token("lowhearth-worker", 13, 7.7)
    m.token("old-dagny", 16, 11.0)
    return m


# ============================================================ THE GILDED NAIL (Crown Market officers' tavern)
@register
def gilded_nail():
    m = Map("gilded-nail", "The Gilded Nail (officers' tavern)", 30, 20, seed=202, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 26, 15, "marble")
    m.room(2, 2, 26, 15, "dwarf", doors=[("S", 12, 3, "brass")])
    m.floor_rect(7, 5.5, 15, 9, "carpet", layer="decal")
    m.floor_circle(15, 10, 3, "dwarfslab", layer="lowprop")
    m.add("lowprop", f'<circle cx="{m.P(15)}" cy="{m.P(10)}" r="{m.P(3)}" fill="none" stroke="#c8963a" stroke-width="10" stroke-dasharray="40 16"/>')
    m.g("props", 15, 10, k.anvil())  # the Moot Anvil
    m.g("props", 15, 2.4, pr.jar_shelf(1100, 26, 7))
    counter(m, 9, 3.3, 21, 4.3, top="#8a5a2a")
    for x in (8, 22):
        m.g("props", x, 2.4, k.weapon_rack(160))
    for y in (5, 8, 11, 14):
        booth_row(m, 4, y)
    for y in (9, 12, 15):
        booth_row(m, 26, y)
    banner_wall(m, 6, 16.8); banner_wall(m, 24, 16.8)
    for (x, y) in ((9.5, 15.5), (20.5, 15.5)):
        m.g("props", x, y, k.statue(50))
    # private card room (NE) — where officers settle their Turning Gear markers
    m.floor_rect(23, 2, 5, 4.5, "rug")
    m.wall([(23, 2), (23, 4.3)], "dwarf"); m.door(23, 4.3, 23, 5.5, "red"); m.wall([(23, 5.5), (23, 6.5), (28, 6.5)], "dwarf")
    m.g("props", 25.5, 4.2, pr.round_table(50, "#3a2a18"))
    for a in range(4):
        m.g("props", 25.5 + 1.0 * math.cos(a * math.pi / 2), 4.2 + 0.9 * math.sin(a * math.pi / 2), pr.chair(), rot=a * 90 + 90)
    m.light(25.5, 4.2, 2.5, 0.5, "#ffd27a", alpha=0.3)
    for (x, y) in ((2.6, 2.6), (27.4, 16.4), (2.6, 16.4), (15, 6.2)):
        lamp(m, x, y, "#ffd27a")
    brazier(m, 10.5, 10, 5, 1.5); brazier(m, 19.5, 10, 5, 1.5)
    m.floor_rect(12, 17, 6, 3, "dwarfslab")
    m.env = {"darkness": 0.7, "globalLight": False}
    m.note(15, 5.2, "hold:gilded-nail", "The Gilded Nail")
    m.note(15, 13.6, "hold:q-gilded-nail", "Side Quest: A Name Above Its Station")
    m.note(25.5, 3.0, "hold:q-turning-gear", "Card room (officers' markers)")
    m.token("sorvald", 15, 2.9)
    m.token("eirik", 16.6, 10)
    return m


# ============================================================ THE EMBER BATHS (Steamstair)
@register
def ember_baths():
    m = Map("ember-baths", "The Ember Baths (Steamstair)", 32, 22, seed=203, bg="#151312")
    m.fill_rock()
    # changing rooms (west), split by a timber screen
    m.floor_rect(1, 2, 6, 16, "planks")
    m.room(1, 2, 6, 16, "dwarf", doors=[("E", 3, 1.5, "wood"), ("E", 11.5, 1.5, "wood"), ("S", 2, 2, "wood")])
    m.wall([(1, 10), (7, 10)], "timber")
    for y in (3.5, 6, 12, 15.5):
        m.g("props", 2.2, y, pr.bench(160), rot=90)
    m.g("props", 6.4, 8.4, pr.jar_shelf(260, 30, 9), rot=90)
    # main bath hall
    m.floor_rect(7, 2, 18, 16, "dwarfslab")
    m.room(7, 2, 18, 16, "dwarf", gaps=[("W", 0, 16)], doors=[("E", 6, 1.5, "iron"), ("S", 8, 3, "wood")])
    pool(m, 9, 4, 5, 4)                  # cool basin
    pool(m, 9, 11, 5, 5)                 # warm basin
    pool(m, 16.5, 6, 6.5, 7, hot=True)   # the Ember Basin
    for (x, y) in ((8, 3), (24, 3), (8, 17), (24, 17)):
        m.g("props", x, y, pr.pillar(34))
    m.pipe([(16.5, 5.2), (25, 5.2)], 30, "#8a5a2a"); m.pipe([(16.5, 13.8), (25, 13.8)], 30, "#8a5a2a")
    m.g("props", 19.75, 15.6, k.valve_wheel(46, "#c0283a"))
    m.g("props", 21.2, 15.6, k.gauge(28))
    lamp(m, 15, 2.6); lamp(m, 15, 17.4); lamp(m, 24.4, 10.5)
    m.light(19.75, 9.5, 6, 1, "#ff7a1a", alpha=0.35, anim="pulse", speed=1, intensity=2)
    # pipe gallery (east) — the maintenance crawl where Pip is hiding
    m.floor_rect(25, 2, 6, 16, "metal")
    m.room(25, 2, 6, 16, "iron", gaps=[("W", 0, 16)], doors=[("S", 2, 1.2, "iron")])
    m.pipe([(26, 2.4), (26, 17.6)], 40, "#6e5a3a"); m.pipe([(29.8, 2.4), (29.8, 17.6)], 40, "#6e5a3a")
    m.pipe([(26, 11), (29.8, 11)], 30, "#8a5a2a")
    m.g("props", 27.9, 4.4, k.valve_wheel(44, "#8a5a2a"))
    m.g("props", 27.9, 14.8, pr.rubble(7, 40, 3))
    for (x, y) in ((27.2, 11.8), (28.6, 12.8)):
        m.steam(x, y, 1.0)
    m.light(27.9, 11, 3, 0.5, "#ff7a1a", alpha=0.35, anim="pulse", speed=3, intensity=4)
    # Steamstair and the drain down to the deep
    m.floor_rect(1, 18, 30, 4, "dwarfslab")
    m.stair(17.5, 18.3, 5, 3.4, 6, vertical=False)
    m.g("lowprop", 3.5, 20.2, pr.hatch(130, 130))
    m.water_poly([(6, 20.8), (16, 20.8), (16, 21.5), (6, 21.5)], foul=True)
    lamp(m, 10, 18.6); lamp(m, 27, 21.4)
    m.env = {"darkness": 0.75, "globalLight": False}
    m.note(19.75, 4.4, "hold:ember-baths", "The Ember Baths")
    m.note(27.9, 7.2, "hold:q-ember-baths", "Side Quest: Cold Water")
    m.token("fenn", 12, 9.5)
    for (x, y) in ((27.2, 12.2), (28.7, 13.4), (26.9, 16)):
        m.token("scald-mephit", x, y, hidden=True)
    m.token("pip", 28.4, 16.7, hidden=True)
    return m


# ============================================================ THE TURNING GEAR (gaming house)
@register
def turning_gear():
    m = Map("turning-gear", "The Turning Gear (gaming house)", 30, 22, seed=204, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 20, 16, "carpet")
    m.room(2, 2, 20, 16, "dwarf", doors=[("S", 4, 2.5, "brass"), ("E", 3, 1.5, "red")])
    # the Wheel of Gears
    m.g("props", 12, 7.5, pr.gear(150, 16))
    m.terrain_wall([(10.5, 6), (13.5, 6), (13.5, 9), (10.5, 9)], closed=True)
    m.light(12, 7.5, 5, 1, "#ffd27a", alpha=0.35, anim="pulse", speed=2, intensity=2)
    # Rivets & Runes dice pits and Anvil-Stakes card tables
    for (x, y) in ((5, 5), (5, 10), (19, 5), (19, 10)):
        m.g("props", x, y, pr.table(170, 100, "#2a4a2a"))
        for dx in (-0.8, 0, 0.8):
            m.g("props", x + dx, y - 0.85, pr.chair(), rot=180); m.g("props", x + dx, y + 0.85, pr.chair())
    for (x, y) in ((14, 13.2), (19, 14.4)):
        m.g("props", x, y, pr.round_table(50, "#3a2a18"))
        for a in range(5):
            m.g("props", x + 1.0 * math.cos(a * 2 * math.pi / 5), y + 1.0 * math.sin(a * 2 * math.pi / 5), pr.chair(), rot=a * 72 + 90)
    # cashier's cage (bars: see through, no passage)
    m.floor_rect(3, 14.5, 6, 3.5, "metal")
    m.wall([(3, 14.5), (8, 14.5)], "iron", kind="terrain", sight="limited")
    m.door(8, 14.5, 9, 14.5, "iron", locked=True)
    m.wall([(9, 14.5), (9, 18)], "iron")
    m.g("props", 6, 16.4, pr.scales()); m.g("props", 4, 17.2, BOOK(120, 80))
    for (x, y) in ((2.6, 2.6), (21.4, 2.6), (21.4, 17.4), (12, 2.6), (12, 17.4)):
        lamp(m, x, y, "#ffd27a")
    # Iskra's office (NE) and the marker vault beneath it (E)
    m.floor_rect(22, 2, 6, 7, "rug")
    m.room(22, 2, 6, 7, "dwarf", gaps=[("W", 0, 7), ("S", 0, 6)])
    m.wall([(22, 9), (23.5, 9)], "dwarf"); m.door(23.5, 9, 25, 9, "iron", locked=True); m.wall([(25, 9), (28, 9)], "dwarf")
    m.g("props", 25, 3.8, pr.desk(150, 80)); m.g("props", 25, 4.8, pr.chair())
    m.g("props", 27.2, 7.6, pr.filing_cabinet()); m.g("props", 23.2, 7.2, BOOK(140, 100))
    lamp(m, 27.4, 2.6, "#ffd27a")
    m.floor_rect(22, 9, 6, 7, "metal")
    m.room(22, 9, 6, 7, "iron", gaps=[("W", 0, 7), ("N", 0, 6)])
    crates(m, 24, 11.2, 5, 3); m.g("props", 26.6, 14, pr.cage(110, 100))
    m.g("props", 24.2, 14.6, BOOK(140, 90))
    m.light(25, 12.5, 2.5, 0.5, "#ffd27a", alpha=0.3)
    # street front
    m.floor_rect(0, 18, 30, 4, "cobble")
    lamp(m, 6, 18.6, "#ffb35a"); lamp(m, 24, 18.6, "#ffb35a")
    m.env = {"darkness": 0.7, "globalLight": False}
    m.note(12, 10.4, "hold:turning-gear", "The Turning Gear")
    m.note(25, 12.6, "hold:q-turning-gear", "Side Quest: The House Always Requisitions")
    m.token("iskra", 25, 5.4)
    return m


# ============================================================ ANVILSONG FORGE (Forge Row smith)
@register
def anvilsong_forge():
    m = Map("anvilsong-forge", "Anvilsong Forge (Forge Row)", 28, 20, seed=205, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 18, 14, "factory")
    m.room(2, 2, 18, 14, "dwarf", doors=[("S", 7.5, 3, "iron"), ("E", 2, 1.5, "wood"), ("E", 9, 1.5, "wood")])
    for x in (5, 11, 17):
        m.g("props", x, 3.5, k.forge(210, 140))
        m.light(x, 3.5, 6, 2, "#ff7a1a", alpha=0.45, anim="torch", speed=3, intensity=4)
        m.g("props", x, 6.2, k.anvil())
        m.terrain_wall([(x - 1.05, 2.8), (x + 1.05, 2.8), (x + 1.05, 4.2), (x - 1.05, 4.2)], closed=True)
    m.water_poly([(3.5, 9), (8.5, 9), (8.5, 10), (3.5, 10)])  # quench trough
    # the unfinished Lowhearth Lift Gate on trestles
    m.floor_rect(11, 9, 7, 4, "metal", layer="lowprop")
    for i in range(7):
        m.add("props", f'<line x1="{m.P(11.4 + i)}" y1="{m.P(9.2)}" x2="{m.P(11.4 + i)}" y2="{m.P(12.8)}" stroke="#2a2a30" stroke-width="16"/>')
    m.add("props", f'<line x1="{m.P(11.2)}" y1="{m.P(11)}" x2="{m.P(17.8)}" y2="{m.P(11)}" stroke="#2a2a30" stroke-width="16"/>')
    m.g("props", 4, 13.8, k.weapon_rack(200)); m.g("props", 7.5, 13.8, k.weapon_rack(200))
    crates(m, 17.5, 14.4, 7, 3)
    lamp(m, 2.6, 15.4); lamp(m, 19.4, 15.4)
    # coal bunker & iron store
    m.floor_rect(20, 2, 6, 7, "gravel")
    m.room(20, 2, 6, 7, "dwarf", gaps=[("W", 0, 7)])
    m.g("props", 23, 4.6, pr.rubble(14, 90, 5))
    m.g("props", 23, 7.4, k.minecart())
    # Brannoc's office with the order books
    m.floor_rect(20, 9, 6, 7, "planks")
    m.room(20, 9, 6, 7, "dwarf", gaps=[("W", 0, 7), ("N", 0, 6)])
    m.g("props", 23, 11, pr.desk(150, 80)); m.g("props", 23, 11.9, pr.chair())
    m.g("props", 23, 15.4, pr.bookshelf(220, 40, 2)); m.g("props", 22.4, 10.8, BOOK(100, 70))
    lamp(m, 25.4, 9.6)
    m.floor_rect(0, 16, 28, 4, "cobble")
    m.pipe([(0, 19.2), (28, 19.2)], 30)
    m.env = {"darkness": 0.7, "globalLight": False}
    m.note(11, 7.6, "hold:anvilsong-forge", "Anvilsong Forge")
    m.note(14.5, 13.6, "hold:q-anvilsong-forge", "Side Quest: The Last Commission")
    m.note(23, 13, "hold:q-anvilsong-forge", "Order books")
    m.token("brannoc", 11, 7.2)
    return m


# ============================================================ GLIMMERHALL (enchanter)
@register
def glimmerhall():
    m = Map("glimmerhall", "Glimmerhall, Enchantments & Wards", 26, 20, seed=206, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 4, 11, 12, "marble")
    m.room(2, 4, 11, 12, "dwarf", doors=[("S", 4.5, 2, "brass"), ("E", 6, 1.5, "wood")])
    for y in (5.6, 8.6, 11.6):
        m.g("props", 2.5, y + 0.5, pr.jar_shelf(220, 34, int(y)), rot=90)
    m.g("props", 7.5, 6.2, pr.table(240, 70, "#3a2a40")); m.g("props", 7.5, 10, pr.table(240, 70, "#3a2a40"))
    for (x, y) in ((6.5, 6.2), (8.5, 10)):
        m.light(x, y, 1.5, 0.5, "#b88aff", alpha=0.3, anim="pulse", speed=1, intensity=2)
    counter(m, 9.5, 13, 12.4, 13.9, top="#4a3a5a")
    lamp(m, 2.6, 15.4, "#ffd27a"); lamp(m, 12.4, 4.6, "#ffd27a")
    # workshop and the listening-lamp circle
    m.floor_rect(13, 4, 11, 12, "hexstone")
    m.room(13, 4, 11, 12, "dwarf", gaps=[("W", 0, 12)], doors=[("N", 8, 1.2, "iron")])
    m.add("lowprop", f'<circle cx="{m.P(18.5)}" cy="{m.P(10)}" r="{m.P(2.6)}" fill="none" stroke="#b88aff" stroke-width="10"/>'
                     f'<circle cx="{m.P(18.5)}" cy="{m.P(10)}" r="{m.P(2.0)}" fill="none" stroke="#7a5ab8" stroke-width="5" stroke-dasharray="20 14"/>')
    m.g("props", 18.5, 10, pr.lectern())
    m.light(18.5, 10, 4, 1, "#7a5ab8", alpha=0.4, anim="ghost", speed=2, intensity=3)
    m.g("props", 16, 4.5, pr.bookshelf(220, 40, 6)); m.g("props", 23.4, 9, pr.scroll_rack(200, 46), rot=90)
    m.g("props", 21.5, 14.4, pr.table(150, 80, "#4a3a2a"))
    lamp(m, 23.4, 15.4, "#ffd27a")
    # warded vault (north)
    m.floor_rect(18, 1, 6, 3, "metal")
    m.room(18, 1, 6, 3, "iron", gaps=[("S", 0, 6)])
    m.g("props", 19.5, 2.5, pr.cage(110, 90)); m.g("props", 22.6, 2.4, pr.jar_shelf(150, 30, 3))
    m.light(21, 2.5, 2, 0.5, "#7a5ab8", alpha=0.3, anim="ghost")
    m.floor_rect(0, 16, 26, 4, "cobble")
    m.env = {"darkness": 0.75, "globalLight": False}
    m.note(7.5, 8.1, "hold:glimmerhall", "Glimmerhall")
    m.note(18.5, 12.8, "hold:q-glimmerhall", "Side Quest: The Lamp That Remembers")
    m.token("sigrun", 17, 10)
    return m


# ============================================================ MOSSBEARD & FERNSPIT REMEDIES (apothecary)
@register
def mossbeard_remedies():
    m = Map("mossbeard-remedies", "Mossbeard & Fernspit Remedies (apothecary)", 26, 18, seed=207, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 10, 11, "planks")
    m.room(2, 2, 10, 11, "dwarf", doors=[("S", 4, 2, "wood"), ("E", 2.5, 1.5, "wood"), ("E", 8, 1.5, "wood")])
    counter(m, 3, 6, 10, 7)
    m.g("props", 6.5, 2.4, pr.jar_shelf(800, 34, 2))
    m.g("props", 2.5, 10, pr.jar_shelf(260, 30, 8), rot=90)
    m.g("props", 6, 9.6, pr.scales())
    lamp(m, 11.4, 2.6)
    # brewing room
    m.floor_rect(12, 2, 8, 6, "dwarfslab")
    m.room(12, 2, 8, 6, "dwarf", gaps=[("W", 0, 6), ("E", 0, 6)], doors=[("S", 4, 1.2, "wood")])
    m.g("props", 15.5, 4.6, pr.furnace_pit(70))
    m.light(15.5, 4.6, 4, 1, "#7aff8a", alpha=0.3, anim="pulse", speed=1, intensity=2)
    m.g("props", 12.5, 4.5, pr.jar_shelf(200, 30, 5), rot=90)
    # Tikka's fungus beds
    m.floor_rect(20, 2, 4, 14, "moss")
    m.room(20, 2, 4, 14, "fungal", gaps=[("W", 2, 1.5), ("W", 10, 1.5)])
    for y in (3.5, 7, 10.5, 14):
        fungus(m, 22.2, y, 6, 60, int(y * 3), light=(y in (3.5, 10.5)))
    # sick room
    m.floor_rect(12, 8, 8, 8, "planks")
    m.room(12, 8, 8, 8, "dwarf", gaps=[("N", 0, 8), ("E", 0, 8), ("W", 3, 5)], doors=[("S", 3, 1.5, "wood")])
    for (x, y) in ((13.2, 10.2), (13.2, 13.8), (18.8, 10.2), (18.8, 13.8)):
        m.g("props", x, y, k.bunk(80, 170))
    m.g("props", 16, 12, pr.table(100, 70, "#6e4527"))
    lamp(m, 16, 8.6)
    # porch and lane
    m.floor_rect(2, 13, 10, 3, "dwarfslab")
    m.floor_rect(0, 16, 26, 2, "dwarfslab")
    m.water_poly([(0, 16.9), (26, 16.9), (26, 17.5), (0, 17.5)], foul=True)
    lamp(m, 2.6, 15.4)
    m.env = {"darkness": 0.78, "globalLight": False}
    m.note(6.5, 4.4, "hold:mossbeard-remedies", "Mossbeard & Fernspit Remedies")
    m.note(16, 15, "hold:q-mossbeard-remedies", "Side Quest: The Bitter Cough")
    m.token("bera", 6.5, 5.2)
    m.token("tikka", 21.4, 8.6)
    m.token("lowhearth-worker", 13.2, 10.2, name="Coughing Patient")
    m.token("lowhearth-worker", 18.8, 13.8, name="Coughing Patient")
    return m


# ============================================================ THE HALL OF DEEP SCRIPT (rune smiths)
@register
def deep_script():
    m = Map("deep-script", "The Hall of Deep Script (rune smiths)", 30, 22, seed=208, bg="#151312")
    m.fill_rock()
    m.floor_rect(2, 2, 26, 18, "dwarfslab")
    m.room(2, 2, 26, 18, "dwarf", doors=[("S", 11.5, 3, "iron")])
    for x in (7, 12, 18, 23):
        for y in (6, 15):
            m.g("props", x, y, pr.pillar(42))
            m.wall([(x - 0.3, y - 0.3), (x + 0.3, y - 0.3), (x + 0.3, y + 0.3), (x - 0.3, y + 0.3)], "stone", closed=True, draw=False)
    for (x, y) in ((4.5, 8.5), (4.5, 12.5), (25.5, 8.5), (25.5, 12.5)):
        m.g("props", x, y, pr.table(160, 80, "#4a3a2a")); m.g("props", x, y + 0.7, pr.chair())
    # the trial circle
    m.floor_circle(15, 10.5, 3.6, "hexstone", layer="lowprop")
    for r, c in ((3.4, "#c8963a"), (2.4, "#8a6a3a"), (1.4, "#c8963a")):
        m.add("lowprop", f'<circle cx="{m.P(15)}" cy="{m.P(10.5)}" r="{m.P(r)}" fill="none" stroke="{c}" stroke-width="8" stroke-dasharray="26 10"/>')
    m.g("props", 15, 10.5, k.statue(55, "#5a5660"))
    m.light(15, 10.5, 5, 1, "#c8963a", alpha=0.35, anim="pulse", speed=1, intensity=2)
    # Kharn's study (NW) and the archive (NE) behind shelf walls
    m.wall([(2, 4.5), (5, 4.5)], "shelf"); m.wall([(25, 4.5), (28, 4.5)], "shelf")
    m.g("props", 15, 2.5, pr.scroll_rack(500, 46))
    m.g("props", 3.6, 3.1, pr.desk(130, 70)); m.g("props", 26.5, 3.1, pr.bookshelf(160, 40, 9))
    for (x, y) in ((2.6, 19.4), (27.4, 19.4), (2.5, 2.5), (27.5, 2.5)):
        lamp(m, x, y, "#ffd27a")
    brazier(m, 9.5, 10.5, 4, 1); brazier(m, 20.5, 10.5, 4, 1)
    m.floor_rect(12, 20, 6, 2, "dwarfslab")
    m.env = {"darkness": 0.8, "globalLight": False}
    m.note(15, 4.2, "hold:deep-script", "The Hall of Deep Script")
    m.note(15, 14.6, "hold:q-deep-script", "Side Quest: A Rune Nobody Taught")
    m.token("kharn", 4.2, 3.9)
    m.token("rune-warden", 15, 8.6, hidden=True)
    return m


HOLD_MAPS = ["low-lantern", "gilded-nail", "ember-baths", "turning-gear", "anvilsong-forge", "glimmerhall",
             "mossbeard-remedies", "deep-script"]


def check(m):
    """Report wall segments that overlap a door (a shared side drawn twice by mistake)."""
    probs = []
    doors = [w for w in m.walls if w["kind"] in ("door", "secret")]
    for d in doors:
        x1, y1, x2, y2 = d["c"]
        for w in m.walls:
            if w is d or w["kind"] in ("door", "secret", "invisible"):
                continue
            a1, b1, a2, b2 = w["c"]
            if x1 == x2 == a1 == a2:
                lo, hi = sorted((y1, y2)); l2, h2 = sorted((b1, b2))
                if min(hi, h2) - max(lo, l2) > 5:
                    probs.append((m.key, d["c"], w["c"]))
            if y1 == y2 == b1 == b2:
                lo, hi = sorted((x1, x2)); l2, h2 = sorted((a1, a2))
                if min(hi, h2) - max(lo, l2) > 5:
                    probs.append((m.key, d["c"], w["c"]))
    return probs
