"""Where Part I's creatures stand on its maps (token centres in scene pixels). All start hidden.

Placed in the rooms the finale journals use. Coordinates were read off downscaled copies of each map
and are scaled here: (thumb_x, thumb_y) * factor.
"""
import json

def S(f, pts):
    return [{"actor": a, "x": round(x * f), "y": round(y * f), **({"name": n} if n else {})} for a, x, y, n in pts]

GROUNDS = 8100 / 1600
COURT = 8150 / 1600
SPIRE = 8150 / 1400
CAT = 8160 / 1600
MIST = 4000 / 1200
ROAD = 5000 / 1200
VAL = 4000 / 1200

grounds = S(GROUNDS, [
    # The War of Broken Gods: Orcus rises in the west yard, Vampyr bleeds into the east yard
    ("cu.actor.orcus", 300, 620, None),
    ("cu.actor.anchor.orcus", 300, 280, "Grave Horn (north)"),
    ("cu.actor.anchor.orcus", 300, 1020, "Grave Horn (south)"),
    ("cu.actor.anchor.orcus", 560, 1020, "Grave Horn (yard)"),
    ("cu.actor.vampyr", 940, 1010, None),
    ("cu.actor.anchor.vampyr", 770, 920, "Blood Heart (west)"),
    ("cu.actor.anchor.vampyr", 1110, 920, "Blood Heart (east)"),
    ("cu.actor.anchor.vampyr", 1029, 1046, "Blood Heart (south)"),
])
streets = S(VAL, [
    ("cu.actor.vallaki-vampyr-cult", 560, 470, None),
    ("cu.actor.vallaki-vampyr-cult", 620, 505, None),
    ("cu.actor.vallaki-vampyr-cult", 520, 525, None),
    ("cu.actor.vallaki-orcus-cult", 880, 525, None),
    ("cu.actor.vallaki-orcus-cult", 1080, 480, None),
])

TOKENS = {
    "cu.scene.ravenloft-00-grounds-roofed": grounds,
    "cu.scene.ravenloft-01-grounds-open": grounds,
    # Movement I in the great hall (the "ballroom"); the Abbot, Finn, Tatyana and Strahd Phase I in the chapel
    "cu.scene.ravenloft-03-court-of-the-count": S(COURT, [
        ("cu.actor.anastrasya", 460, 700, None),
        ("cu.actor.volenta", 450, 880, None),
        ("cu.actor.abbot", 1435, 690, None),
        ("cu.actor.finn", 1330, 690, None),
        ("cu.actor.tatyana", 1460, 600, None),
        ("cu.actor.strahd1", 1290, 830, None),
    ]),
    # Movement II: Ludmilla's Laboratory of Night in the witches' workroom, three pylons around her
    "cu.scene.ravenloft-07-spires-2": S(SPIRE, [
        ("cu.actor.ludmilla", 730, 905, None),
        ("cu.actor.pylon", 650, 915, "Nightglass Pylon 1"),
        ("cu.actor.pylon", 812, 915, "Nightglass Pylon 2"),
        ("cu.actor.pylon", 748, 832, "Nightglass Pylon 3"),
    ]),
    # Phase II at the Heart of Sorrow: Strahd on the landing, the three Heart Chains around the Heart
    "cu.scene.ravenloft-08-spires-3-heart": S(SPIRE, [
        ("cu.actor.strahd2", 735, 482, None),
        ("cu.actor.chain.blood", 612, 372, None),
        ("cu.actor.chain.stone", 858, 372, None),
        ("cu.actor.chain.dominion", 735, 248, None),
    ]),
    # Phase III in the catacombs; the coffin in Strahd's tomb
    "cu.scene.ravenloft-14-dungeons-catacombs": S(CAT, [
        ("cu.actor.strahd3", 780, 600, None),
        ("cu.actor.coffin", 1170, 600, None),
    ]),
    "cu.scene.ravenloft-16-catacombs-mist": S(MIST, [
        ("cu.actor.strahd3", 720, 445, None),
        ("cu.actor.coffin", 1000, 445, None),
    ]),
    "cu.scene.vallaki-01-streets-a": streets,
    "cu.scene.vallaki-02-streets-b": streets,
    "cu.scene.vallaki-03-streets-c": streets,
    # Arl waits on the castle approach
    "cu.scene.ravenloft-00a-the-last-road": S(ROAD, [("cu.actor.arl", 640, 372, None)]),
    # Van Richten's workshop (final briefing and supplies)
    "cu.scene.vallaki-04-arcane-outfitter": S(2500 / 1200, [("cu.actor.van-richten", 520, 450, None)]),
}

# Map pins: (journal sourceId, page sourcePageId, thumb x, thumb y, label). The first pin's journal becomes the scene's journal.
def N(f, pts):
    return [{"journal": j, "page": p, "x": round(x * f), "y": round(y * f), "label": l} for j, p, x, y, l in pts]

COURT14 = 8150 / 1400
GROUNDS_P = N(GROUNDS, [
    ("cu.journal.darkwar", "war.arrival", 300, 470, "The War of Broken Gods"),
    ("cu.journal.orcus", "orcus.interventions", 420, 620, "Orcus front"),
    ("cu.journal.vampyr", "vamp.interventions", 1060, 1010, "Vampyr front"),
    ("cu.journal.allies", "ally.az", 180, 560, "Deploy allies"),
])
STREETS_P = N(VAL, [
    ("cu.journal.vallaki-prelude", "vallaki.arrival", 600, 470, "A city already at war"),
    ("cu.journal.vallaki-prelude", "vallaki.choice", 900, 470, "One last choice in Vallaki"),
    ("cu.journal.vallaki-prelude", "vallaki.departure", 1080, 300, "Departure for Ravenloft"),
])
PINS = {
    "cu.scene.ravenloft-00-grounds-roofed": GROUNDS_P,
    "cu.scene.ravenloft-01-grounds-open": GROUNDS_P,
    "cu.scene.ravenloft-02-main-floor": N(8150 / 1100, [
        ("cu.journal.approach", "app.dinner", 300, 600, "The Unattended Dinner"),
        ("cu.journal.lair", "lair.actions", 440, 470, "Strahd as the invisible lair boss"),
    ]),
    "cu.scene.ravenloft-03-court-of-the-count": N(COURT14, [
        ("cu.journal.brides1", "b1.setup", 390, 650, "Movement I: the Ballroom"),
        ("cu.journal.abbot", "abbot.social", 1230, 600, "The Abbot at the altar"),
        ("cu.journal.finn", "finn.setup", 1150, 600, "Finn: the last door"),
        ("cu.journal.tatyana", "tat.choice", 1250, 520, "Ireena / Tatyana"),
        ("cu.journal.rest", "rest.offer", 1150, 470, "Strahd's courtesy"),
        ("cu.journal.phase1", "p1.run", 1130, 690, "Strahd Phase I"),
    ]),
    "cu.scene.ravenloft-07-spires-2": N(COURT14, [("cu.journal.brides2", "b2.lab", 730, 860, "Movement II: the Laboratory of Night")]),
    "cu.scene.ravenloft-08-spires-3-heart": N(COURT14, [
        ("cu.journal.phase2", "p2.run", 735, 520, "Strahd Phase II: the Heart"),
        ("cu.journal.integration", "int.p2", 800, 520, "Phase II: three masters"),
    ]),
    "cu.scene.ravenloft-14-dungeons-catacombs": N(CAT, [
        ("cu.journal.phase3", "p3.run", 780, 570, "Strahd Phase III"),
        ("cu.journal.coffin", "coffin.chase", 900, 600, "The coffin chase"),
        ("cu.journal.coffin", "coffin.final", 1130, 600, "The last anchor"),
    ]),
    "cu.scene.ravenloft-16-catacombs-mist": N(MIST, [
        ("cu.journal.phase3", "p3.run", 720, 420, "Strahd Phase III"),
        ("cu.journal.coffin", "coffin.chase", 830, 445, "The coffin chase"),
        ("cu.journal.coffin", "coffin.final", 980, 445, "The last anchor"),
    ]),
    "cu.scene.vallaki-01-streets-a": STREETS_P,
    "cu.scene.vallaki-02-streets-b": STREETS_P,
    "cu.scene.vallaki-03-streets-c": STREETS_P,
    "cu.scene.vallaki-04-arcane-outfitter": N(2500 / 1200, [
        ("cu.journal.vallaki-prelude", "vallaki.van-richten", 600, 520, "Van Richten: the warning"),
        ("cu.journal.strahd-letter", "letter.text", 560, 260, "Strahd's sealed letter"),
        ("cu.journal.vallaki-prelude", "vallaki.knowledge", 760, 520, "What Van Richten knows"),
    ]),
    "cu.scene.ravenloft-00a-the-last-road": N(ROAD, [
        ("cu.journal.prelude", "road.manifest", 250, 380, "The prisoners reach the castle"),
        ("cu.journal.approach", "app.dragon", 500, 380, "Azrathox and the storm"),
        ("cu.journal.allies", "ally.fiend", 700, 372, "Arl"),
    ]),
    "cu.scene.barovia-01-unravelling-mistway": N(5000 / 1200, [
        ("cu.journal.collapse", "collapse.domain", 200, 370, "The domain collapses"),
        ("cu.journal.collapse", "collapse.dark", 560, 370, "Resolve the cosmic shadow"),
        ("cu.journal.collapse", "collapse.box", 860, 430, "The keepsake box reacts"),
        ("cu.journal.collapse", "collapse.transition", 1040, 380, "The first sound is an anvil"),
    ]),
}


def write(path):
    json.dump(TOKENS, open(path, "w"), indent=1)
    json.dump(PINS, open(path.replace("tokens.json", "pins.json"), "w"), indent=1)
    return len(TOKENS), sum(len(v) for v in TOKENS.values()), sum(len(v) for v in PINS.values())
