"""Spellcasting for every creature that should cast (both parts).

The spells themselves are taken at install time from the dnd5e system's own compendiums (and this
module's rune spells), so they arrive with the system's full activities; this file only says who
knows what, how (prepared with slots, innate x/day, at will), the casting ability and caster level.
Keys: Part II actor keys, Part I sourceIds.
"""
import json

# (name, method, uses)  method: "spell" (prepared, uses slots) | "innate" (uses/day) | "atwill"
def P(*names): return [(n, "spell", None) for n in names]
def AW(*names): return [(n, "atwill", None) for n in names]
def D(n, *names): return [(x, "innate", n) for x in names]

SPELLBOOKS = {
    # ---------------------------------------------------------------- Part II
    "sigrun": dict(ability="int", level=6, note="6th-level spellcaster (wizard). Spell save DC and attack from Intelligence.",
                   spells=P("Light", "Mage Hand", "Shocking Grasp", "Shield", "Magic Missile", "Alarm", "Detect Magic",
                            "Hold Person", "Misty Step", "Counterspell", "Dispel Magic", "Glyph of Warding")),
    "kharn": dict(ability="int", level=7, note="7th-level spellcaster (rune scholar). Knows the Deep Script rune spells.",
                  spells=P("Chisel-Sign", "Mending", "Message", "Stoneward Script", "Comprehend Languages", "Shield",
                           "Echoes in the Masonry", "Arcane Lock", "Hammerfall Sigil", "Seal the Breach", "Glyph of Warding",
                           "Dispel Magic", "Runegate Traverse", "Stoneskin")),
    "yrsa": dict(ability="wis", level=7, note="7th-level spellcaster (priest of the hearth). Spell save DC and attack from Wisdom.",
                 spells=P("Sacred Flame", "Spare the Dying", "Guidance", "Cure Wounds", "Bless", "Healing Word",
                          "Lesser Restoration", "Prayer of Healing", "Spiritual Weapon", "Mass Healing Word", "Revivify",
                          "Spirit Guardians", "Death Ward")),
    "runa": dict(ability="int", level=5, note="5th-level spellcaster (rune engineer).",
                 spells=P("Chisel-Sign", "Mending", "Stoneward Script", "Rune of the Returning Hammer", "Detect Magic",
                          "Oath-Rune of the Shieldmates", "Echoes in the Masonry", "Seal the Breach", "Rune of Shared Burden")),
    # ---------------------------------------------------------------- Part I
    "cu.actor.ludmilla": dict(ability="int", level=11, note="Innate spellcasting (Intelligence). Her Counterspell Reserve is a separate feature.",
                              spells=AW("Mage Hand", "Minor Illusion", "Chill Touch") + D(3, "Darkness", "Hold Person") + D(1, "Blight", "Dimension Door", "Cone of Cold")),
    "cu.actor.strahd1": dict(ability="int", level=9, note="9th-level spellcaster (wizard). <strong>Spell slots are shared by all three phases:</strong> when the fight moves to Phase II, copy the slots he has left onto that sheet. Phase III no longer casts.",
                             spells=P("Mage Hand", "Prestidigitation", "Ray of Frost", "Comprehend Languages", "Fog Cloud", "Sleep",
                                      "Detect Thoughts", "Gust of Wind", "Mirror Image", "Animate Dead", "Fireball", "Nondetection",
                                      "Blight", "Greater Invisibility", "Polymorph", "Animate Objects", "Scrying")),
    "cu.actor.strahd2": dict(ability="int", level=9, note="Same spells as Phase I; use the slots he had left at the end of Phase I.",
                             spells=P("Mage Hand", "Prestidigitation", "Ray of Frost", "Comprehend Languages", "Fog Cloud", "Sleep",
                                      "Detect Thoughts", "Gust of Wind", "Mirror Image", "Animate Dead", "Fireball", "Nondetection",
                                      "Blight", "Greater Invisibility", "Polymorph", "Animate Objects", "Scrying")),
    "cu.actor.abbot": dict(ability="cha", level=0, note="Innate spellcasting (Charisma).",
                           spells=AW("Detect Evil and Good") + D(1, "Commune", "Raise Dead")),
    "cu.actor.arl": dict(ability="cha", level=0, note="Innate spellcasting (Charisma). His spells obey the contract's mutual non-harm.",
                         spells=AW("Detect Magic", "Fireball") + D(3, "Hold Monster", "Wall of Fire")),
    "cu.actor.orcus": dict(ability="cha", level=0, note="Innate spellcasting (Charisma).",
                           spells=AW("Chill Touch", "Detect Magic") + D(3, "Blight", "Darkness") + D(1, "Finger of Death")),
    "cu.actor.vampyr": dict(ability="cha", level=0, note="Innate spellcasting (Charisma).",
                            spells=AW("Darkness") + D(3, "Dominate Person", "Blight")),
    "cu.actor.saraphene": dict(ability="cha", level=0, note="Innate spellcasting (Charisma).", spells=D(1, "Darkness", "Misty Step")),
}


def write(path):
    out = {k: {"ability": v["ability"], "level": v["level"], "note": v["note"],
               "spells": [{"name": n, "method": m, "uses": u} for n, m, u in v["spells"]]} for k, v in SPELLBOOKS.items()}
    json.dump(out, open(path, "w"), indent=1)
    return len(out), sum(len(v["spells"]) for v in out.values())
