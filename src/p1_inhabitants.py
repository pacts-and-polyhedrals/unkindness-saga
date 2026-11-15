"""The castle's (and Barovia's) other inhabitants, for every Part I map.

Stat blocks come from the dnd5e system's SRD monster compendium at setup (imported once into
"The Cat and the Unkindness / 07 — Castle Inhabitants"), so they are complete. Each group has an anchor in
map fractions (0–1); at placement the module spreads the group over free squares in the same room as the
anchor (it never crosses a wall). All start hidden.

The story the groups tell: Strahd's household is frightened and divided (letter); the War of Broken Gods
has Orcus's dead rising from the cellars and crypts and Vampyr's blood cult inside the walls; Finn's chapel
stays empty on purpose ("no spawn, no bride, no disposable minions").
"""
import json

# monster key -> SRD names to look for (2014 and 2024 SRD spellings)
MONSTERS = {
    "vampire-spawn": ["Vampire Spawn"], "zombie": ["Zombie"], "skeleton": ["Skeleton"], "ghoul": ["Ghoul"], "ghast": ["Ghast"],
    "wight": ["Wight"], "specter": ["Specter"], "shadow": ["Shadow"], "ghost": ["Ghost"], "wraith": ["Wraith"],
    "animated-armor": ["Animated Armor"], "flying-sword": ["Flying Sword", "Animated Flying Sword"],
    "rug": ["Rug of Smothering", "Animated Rug of Smothering"], "bats": ["Swarm of Bats"], "rats": ["Swarm of Rats"],
    "wolf": ["Wolf"], "dire-wolf": ["Dire Wolf"], "gargoyle": ["Gargoyle"], "cultist": ["Cultist"], "fanatic": ["Cult Fanatic", "Cultist Fanatic"],
    "guard": ["Guard"], "commoner": ["Commoner"], "mastiff": ["Mastiff"], "priest": ["Priest"], "acolyte": ["Acolyte", "Priest Acolyte"],
    "nightmare": ["Nightmare"], "ochre-jelly": ["Ochre Jelly"], "wisp": ["Will-o'-Wisp", "Will-o’-Wisp"],
}


def G(m, n, x, y, label=None):
    return {"m": m, "n": n, "x": x, "y": y, **({"label": label} if label else {})}


GROUNDS = [
    G("dire-wolf", 1, 0.55, 0.21, "Strahd's Wolf (pack leader)"), G("wolf", 3, 0.55, 0.21, "Strahd's Wolf"),
    G("nightmare", 1, 0.68, 0.19, "Beucephalus"),
    G("gargoyle", 1, 0.30, 0.11, "Wall Gargoyle"), G("gargoyle", 1, 0.77, 0.87, "Wall Gargoyle"),
    G("vampire-spawn", 1, 0.87, 0.50, "Gate Warden (vampire spawn)"),
    G("zombie", 3, 0.30, 0.22, "Risen Dead of Orcus"), G("skeleton", 2, 0.25, 0.70, "Risen Dead of Orcus"),
    G("cultist", 3, 0.56, 0.66, "Blood Choir Thrall"), G("fanatic", 1, 0.56, 0.66, "Blood Choir Cantor"),
]
STREETS = [
    G("guard", 3, 0.80, 0.30, "Vallaki Watch"), G("mastiff", 2, 0.80, 0.30, "Watch Hound"),
    G("commoner", 3, 0.25, 0.50, "Frightened Vallakian"),
    G("zombie", 3, 0.76, 0.80, "Corpse Facing West"),
    G("priest", 1, 0.88, 0.42, "Priest of St. Andral's"), G("acolyte", 2, 0.88, 0.42, "Acolyte"),
]
LARDERS = lambda P: [
    G("ghoul", 3, *P["hall"], "Larder Ghoul"), G("ghast", 1, *P["hall"], "Larder Ghast"),
    G("zombie", 2, *P["top"], "Risen Dead of Orcus"), G("rats", 1, *P["store"], None),
    G("zombie", 2, *P["mid"], "Risen Dead of Orcus"), G("ochre-jelly", 1, *P["green"], None),
    G("ghoul", 1, *P["corr"], "Larder Ghoul"), G("zombie", 2, *P["east"], "Risen Dead of Orcus"),
    G("commoner", 2, *P["cells"], "Prisoner in the Cells"), G("ghoul", 1, *P["cells"], "Larder Ghoul"),
]
CATACOMBS = lambda P: [
    G("vampire-spawn", 2, *P["a"], "Crypt Guard (vampire spawn)"), G("vampire-spawn", 2, *P["b"], "Crypt Guard (vampire spawn)"),
    G("wight", 1, *P["c"], "Crypt Wight"), G("skeleton", 2, *P["c"], "Crypt Skeleton"),
    G("specter", 2, *P["d"], "Restless Dead"), G("ghost", 1, *P["top"], "Weeping Ghost"),
    G("wight", 1, *P["bottom"], "Crypt Wight"), G("ghoul", 2, *P["west"], "Ghoul of Orcus"),
    G("skeleton", 2, *P["cells"], "Crypt Skeleton"), G("specter", 1, *P["round"], "Restless Dead"),
    G("zombie", 2, *P["cave"], "Risen Dead of Orcus"),
]

INHABITANTS = {
    "cu.scene.ravenloft-00-grounds-roofed": GROUNDS,
    "cu.scene.ravenloft-01-grounds-open": GROUNDS,
    # Main Floor: the dinner hall stays unattended
    "cu.scene.ravenloft-02-main-floor": [
        G("animated-armor", 2, 0.40, 0.52, "Hall Armour"), G("vampire-spawn", 2, 0.54, 0.33, "Household Guard (vampire spawn)"),
        G("shadow", 3, 0.85, 0.40), G("bats", 1, 0.095, 0.19), G("rats", 1, 0.095, 0.81),
        G("rug", 1, 0.62, 0.11), G("commoner", 2, 0.67, 0.22, "Frightened Servant"), G("flying-sword", 2, 0.66, 0.44, "Hall Blade"),
        G("animated-armor", 1, 0.165, 0.67, "Hall Armour"),
    ],
    # Court of the Count: the chapel and the great hall belong to the finale; the rest of the floor is lived in
    "cu.scene.ravenloft-03-court-of-the-count": [
        G("vampire-spawn", 1, 0.095, 0.19, "Household Guard (vampire spawn)"), G("commoner", 3, 0.30, 0.33, "Frightened Servant"),
        G("animated-armor", 2, 0.54, 0.54, "Hall Armour"), G("vampire-spawn", 1, 0.64, 0.12, "Household Guard (vampire spawn)"),
        G("wight", 1, 0.42, 0.72), G("skeleton", 2, 0.42, 0.72), G("bats", 1, 0.095, 0.83), G("specter", 1, 0.16, 0.72, "Restless Dead"),
    ],
    "cu.scene.ravenloft-04-rooms-of-weeping": [
        G("specter", 2, 0.25, 0.30, "Weeping Spirit"), G("ghost", 1, 0.20, 0.51, "Weeping Ghost"), G("shadow", 2, 0.34, 0.52),
        G("shadow", 2, 0.20, 0.72), G("rug", 1, 0.34, 0.72), G("vampire-spawn", 1, 0.60, 0.52, "Household Guard (vampire spawn)"),
        G("bats", 1, 0.70, 0.40),
    ],
    "cu.scene.ravenloft-05-rooftops": [
        G("gargoyle", 2, 0.30, 0.37, "Roof Gargoyle"), G("gargoyle", 1, 0.25, 0.85, "Roof Gargoyle"),
        G("vampire-spawn", 1, 0.52, 0.31, "Roof Watch (vampire spawn)"), G("bats", 1, 0.52, 0.31), G("bats", 2, 0.52, 0.77),
        G("gargoyle", 1, 0.095, 0.20, "Roof Gargoyle"), G("gargoyle", 1, 0.095, 0.85, "Roof Gargoyle"),
    ],
    "cu.scene.ravenloft-06-spires-1": [
        G("vampire-spawn", 1, 0.44, 0.72, "Tower Guard (vampire spawn)"), G("rats", 1, 0.52, 0.80),
        G("bats", 1, 0.43, 0.35), G("gargoyle", 2, 0.23, 0.37, "Roof Gargoyle"),
    ],
    "cu.scene.ravenloft-07-spires-2": [G("bats", 1, 0.53, 0.30)],
    "cu.scene.ravenloft-08-spires-3-heart": [G("bats", 1, 0.50, 0.72)],
    "cu.scene.ravenloft-09-spires-4": [G("wraith", 1, 0.53, 0.31, "Tower Wraith"), G("shadow", 2, 0.53, 0.31), G("gargoyle", 2, 0.50, 0.77, "Spire Gargoyle")],
    "cu.scene.ravenloft-10-spires-5": [G("gargoyle", 2, 0.52, 0.31, "Spire Gargoyle"), G("bats", 1, 0.50, 0.77), G("vampire-spawn", 1, 0.50, 0.77, "Tower Guard (vampire spawn)")],
    "cu.scene.ravenloft-11-spires-6": [G("bats", 2, 0.52, 0.31), G("wight", 1, 0.65, 0.66, "Tower Wight")],
    "cu.scene.ravenloft-12-spires-7": [G("gargoyle", 1, 0.65, 0.66, "Spire Gargoyle"), G("bats", 1, 0.65, 0.66)],
    "cu.scene.ravenloft-13-larders": LARDERS({"hall": (0.38, 0.56), "top": (0.38, 0.30), "store": (0.46, 0.30), "mid": (0.48, 0.43), "green": (0.60, 0.43),
                                              "corr": (0.58, 0.53), "east": (0.76, 0.52), "cells": (0.26, 0.76)}),
    "cu.scene.ravenloft-15-larders-mist": LARDERS({"hall": (0.37, 0.53), "top": (0.36, 0.20), "store": (0.47, 0.23), "mid": (0.48, 0.40), "green": (0.61, 0.40),
                                                   "corr": (0.60, 0.52), "east": (0.80, 0.56), "cells": (0.22, 0.81)}),
    "cu.scene.ravenloft-14-dungeons-catacombs": CATACOMBS({"a": (0.437, 0.35), "b": (0.537, 0.713), "c": (0.437, 0.647), "d": (0.587, 0.35), "top": (0.49, 0.12),
                                                         "bottom": (0.49, 0.88), "west": (0.09, 0.60), "cells": (0.21, 0.69), "round": (0.09, 0.39), "cave": (0.08, 0.85)}),
    "cu.scene.ravenloft-16-catacombs-mist": CATACOMBS({"a": (0.562, 0.349), "b": (0.662, 0.647), "c": (0.562, 0.713), "d": (0.662, 0.349), "top": (0.59, 0.107),
                                                     "bottom": (0.60, 0.88), "west": (0.20, 0.67), "cells": (0.34, 0.67), "round": (0.21, 0.49), "cave": (0.15, 0.91)}),
    "cu.scene.vallaki-01-streets-a": STREETS,
    "cu.scene.vallaki-02-streets-b": STREETS,
    "cu.scene.vallaki-03-streets-c": STREETS,
    "cu.scene.vallaki-04-arcane-outfitter": [G("commoner", 2, 0.22, 0.30, "Refugee Sheltering with Van Richten"), G("mastiff", 1, 0.48, 0.80, "Workshop Hound")],
    "cu.scene.ravenloft-00a-the-last-road": [
        G("dire-wolf", 1, 0.42, 0.32, "Strahd's Wolf (pack leader)"), G("wolf", 3, 0.42, 0.32, "Strahd's Wolf"),
        G("zombie", 4, 0.15, 0.53, "Risen Dead of Orcus"), G("gargoyle", 1, 0.31, 0.42, "Gate Gargoyle"), G("gargoyle", 1, 0.31, 0.66, "Gate Gargoyle"),
        G("bats", 1, 0.82, 0.45), G("vampire-spawn", 1, 0.96, 0.36, "Gate Warden (vampire spawn)"),
    ],
    "cu.scene.barovia-01-unravelling-mistway": [
        G("shadow", 3, 0.15, 0.25, "Mist-Shadow"), G("wolf", 3, 0.20, 0.75, "Starving Wolf"), G("wisp", 3, 0.47, 0.30),
        G("zombie", 2, 0.25, 0.52, "Wandering Dead"), G("specter", 2, 0.82, 0.30, "Soul Lost in the Mist"),
        G("commoner", 3, 0.60, 0.66, "Barovian Refugee"),
    ],
}


def write(path):
    json.dump({"monsters": MONSTERS, "scenes": INHABITANTS}, open(path, "w"), indent=1)
    return len(INHABITANTS), sum(g["n"] for v in INHABITANTS.values() for g in v)
