"""Spells: the Asmodeun Scriptorium's contract magic plus Midwinter spells for the adventure.

Rules pass against the 2014 PHB conventions; every change is recorded in SPELL_NOTES.
"""
from lib5e import *

SPELL_NOTES = []


def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


def dur(value, units, conc=False):
    return {"value": str(value) if value != "" else "", "units": units}


def ACTD(value, units, conc=False):
    return {"concentration": conc, "value": str(value), "units": units, "special": "", "override": False}


SCH_ICON = {"abj": "sp-abj", "con": "sp-con", "div": "sp-div", "enc": "sp-enc", "evo": "sp-evo", "ill": "sp-ill",
            "nec": "sp-nec", "trs": "sp-trs"}

LISTS = {}  # spell key -> class list text


def add(key, *, classes, notes=None, **kw):
    LISTS[key] = classes
    if notes:
        SPELL_NOTES.append(f"<strong>{kw['name']}:</strong> {notes}")
    name = kw.pop("name")
    desc = kw.pop("desc")
    desc += f"<p class='rc-spell-classes'><strong>Spell Lists.</strong> {classes}</p>"
    return spell(key, name, desc, img=icon(kw.pop("img")), **kw)


INFERNAL = "Cleric, Paladin, Wizard, Warlock (The Fiend)"
SPELLS = []

# ---------------------------------------------------------------------------
# THE ASMODEUN SCRIPTORIUM
# ---------------------------------------------------------------------------
e_seal = effect("sp-seal", "Seal of the First Pact", icon("sp-seal"), duration={"seconds": 86400},
                description="<p>Bound to a spoken vow. Knowingly breaking it shatters the seal: 2d10 psychic damage and "
                            "the Mark of the Malefactor.</p>")
e_malefactor = effect("sp-malefactor", "Mark of the Malefactor", icon("sp-mark"),
                      description="<p>Disadvantage on Charisma checks and Charisma saving throws until you atone or the "
                                  "curse is ended by <em>remove curse</em> or similar magic.</p>")
SPELLS.append(add("seal-first-pact", name="Seal of the First Pact", img="sp-seal", level=1, school="enc",
                  classes=INFERNAL, comps=("vocal", "somatic", "material"),
                  materials="a drop of your blood and a tiny scroll of parchment",
                  rng_=rng(30), duration=dur(24, "hour"), tgt=target(1, "willing"),
                  effects=[e_seal, e_malefactor],
                  desc=P("You inscribe a glowing infernal seal in the air and affix it to a willing creature within "
                         "range. As the seal takes hold, the creature must speak aloud a vow or agreement, whose terms "
                         "imprint into the seal.",
                         "For the duration, if the creature knowingly and willfully breaks those terms, the seal "
                         "shatters. The creature takes [[/damage 2d10 type=psychic]] and is marked with a minor curse: "
                         "it has disadvantage on Charisma checks and Charisma saving throws until it atones or the curse "
                         "is lifted by <em>remove curse</em> or similar magic.",
                         "If the creature keeps its vow for the full duration, the seal fades harmlessly at the next "
                         "dawn. The DM may grant a small boon, such as a one-time +1 to a roll.",
                         "<em>Ecclesiastical Note.</em> Clerics call this \"the simplest form of contract\", a temporary "
                         "test of one's word. When it is broken, nearby fiends see the shattering seal like a flare."),
                  activities=[utility("seal-first-pact", 0, name="Affix the Seal", effects=[e_seal["_id"]]),
                              damage_act("seal-first-pact-break", 1, name="The Seal Shatters",
                                         parts=[dmg(2, 10, "", ["psychic"])], act=SPECIAL_ACT if False else activation("special", None),
                                         effects=[e_malefactor["_id"]])]))

SPELLS.append(add("true-name-revelation", name="True Name Revelation", img="sp-truename", level=1, school="div",
                  classes="Cleric, Wizard, Warlock (The Fiend)", comps=("vocal", "somatic", "material"),
                  materials="a vial of quicksilver and a pinch of powdered vellum", ritual=True, concentration=True,
                  act=activation("minute", 10), rng_=rng(30), duration=dur(1, "hour"), tgt=target(1, "creature"),
                  notes="The original said the spell ends early 'if you lose concentration' but listed no "
                        "concentration; it is now Concentration, up to 1 hour.",
                  desc=P("You speak the proper infernal incantation and coax a creature's or object's hidden True Name "
                         "into your mind. Choose one creature or object within range; you learn its True Name, and for "
                         "the duration you gain these benefits:",
                         "<strong>Advantage on Influence.</strong> You have advantage on Charisma checks made to "
                         "interact with the named creature, and on checks to persuade, deceive or intimidate anyone who "
                         "knows or respects it.",
                         "<strong>Arcane Insight.</strong> If the target is a magic item, you have advantage on "
                         "Intelligence (Arcana) checks to identify its properties or command it.",
                         "<strong>Bypass Concealment.</strong> Magic that hides or alters a name, such as "
                         "<em>nondetection</em>, is suppressed for these checks.",
                         "The spell ends early if the target moves more than 30 feet from you. The spell grants "
                         "knowledge only; it does not bind or compel. If you cast it on the same subject every day for "
                         "seven days, its duration becomes 8 hours (still concentration).",
                         "<em>Invocation.</em> \"Nomen verum aperiatur, ut verba mea vincula frangant.\""),
                  activities=[utility("true-name-revelation", 0, name="Reveal the Name",
                                      duration=ACTD(1, "hour", True))]))

SPELLS.append(add("quill-of-binding", name="Quill of Binding", img="sp-quill", level=2, school="con",
                  classes=INFERNAL, comps=("vocal", "somatic", "material"),
                  materials="iron filings and a raven feather", ritual=True, concentration=True,
                  rng_=rng("", "self"), duration=dur(1, "hour"),
                  notes="Listed as '1 action (ritual 10 minutes)'; it now carries the ritual tag, which adds 10 "
                        "minutes as normal.",
                  desc=P("You conjure an infernal quill of black iron and a sheet of parchment. For the duration the "
                         "quill writes a contract or oath with supernatural speed; what would take an hour by hand "
                         "takes one minute. When a creature other than you signs a document written with the quill, "
                         "you can impose one of these effects on that signatory:",
                         "<strong>Binding Signature.</strong> At the moment of signing, the signatory cannot knowingly "
                         "lie about its intention to uphold the terms, as if in a <em>zone of truth</em> (no save).",
                         "<strong>Clause of Arcane Accountability.</strong> For the next 7 days, whenever the signatory "
                         "knowingly speaks falsely about the terms or tries to evade its obligations, the ink on its "
                         "hand glows red and it takes [[/damage 1d6 type=psychic]]. It also has disadvantage on "
                         "Charisma checks made that day to negotiate, deceive or conceal its breach.",
                         "<strong>Witness of Asmodeus.</strong> Until the contract is fulfilled or dissolved, you know "
                         "immediately if the signatory breaks a major term, even on another plane.",
                         "If you lose concentration while writing, the text vanishes. Contracts written with the quill "
                         "glow faintly to infernal sight. The Asmodeun Scriptorium keeps a legendary permanent version, "
                         "<em>Golgorath's Quill</em>."),
                  activities=[utility("quill-of-binding", 0, name="Conjure the Quill", duration=ACTD(1, "hour", True)),
                              damage_act("quill-accountability", 1, name="Clause of Arcane Accountability",
                                         parts=[dmg(1, 6, "", ["psychic"])], act=activation("special", None))]))

e_fury = effect("sp-fury", "Infernal Fury", icon("sp-fury"), duration={"seconds": 60},
                changes=[("system.bonuses.mwak.damage", 2, "1d6[fire]"), ("system.bonuses.rwak.damage", 2, "1d6[fire]")],
                description="<p>Your weapon attacks deal an extra 1d6 fire damage on a hit.</p>")
SPELLS.append(add("contract-infernal-fury", name="Contract of the Infernal Fury", img="sp-fury", level=2, school="evo",
                  classes=INFERNAL, comps=("vocal", "somatic", "material"),
                  materials="a small iron chain and a pinch of brimstone", ritual=False, concentration=True,
                  rng_=rng("", "touch"), duration=dur(1, "minute"), tgt=target(1, "willing"), effects=[e_fury],
                  notes="Listed as divination with a range of 'Self (summons a tool)' and 1-hour duration, but its own "
                        "terms grant fire damage for one minute. It is now evocation, Touch, Concentration up to 1 "
                        "minute, and the two different material lists are merged into one.",
                  desc=P("<em>We, the Invoker and the Empowered, call upon Asmodeus' wrath to fuel our might.</em>",
                         "You and a willing creature you touch agree the terms below. For the duration, the Empowered's "
                         "weapon attacks deal an extra [[/damage 1d6 type=fire]] on a hit.",
                         "<table class='rc-terms'><tr><th>Purpose</th><td>Infernal ferocity: +1d6 fire damage on weapon "
                         "hits.</td></tr><tr><th>Invoker's Duty</th><td>Channel Hell's flames.</td></tr><tr><th>"
                         "Empowered's Duty</th><td>Wield the power only in true service of the contract.</td></tr><tr>"
                         "<th>Forbidden</th><td>No mercy toward those who stand against the Archfiend.</td></tr><tr>"
                         "<th>Breach</th><td>The spell ends at once.</td></tr><tr><th>Termination</th><td>After one "
                         "minute or when the objective is fulfilled.</td></tr></table>",
                         "<em>Invocation.</em> \"By Hell's fury and Asmodeus' will, let our rage burn before His "
                         "throne.\""),
                  activities=[utility("contract-infernal-fury", 0, name="Seal the Contract", effects=[e_fury["_id"]],
                                      duration=ACTD(1, "minute", True), tgt=target(1, "willing"), rng_=rng("", "touch"))]))

SPELLS.append(add("contract-seers-vigil", name="Contract of the Seer's Vigil", img="sp-vigil", level=3, school="div",
                  classes=INFERNAL, comps=("vocal", "somatic", "material"),
                  materials="parchment sealed with two drops of blood", ritual=True,
                  rng_=rng("", "touch"), duration=dur(24, "hour"), tgt=target(1, "willing"),
                  notes="The school was misprinted ('Divinbat') and the header said 1 hour concentration while the "
                        "terms said 24 hours. It is now divination, ritual, Touch, 24 hours, no concentration.",
                  desc=P("<em>We, the Seer and the Bonded, invoke Asmodeus' insight to join our minds.</em>",
                         "You and a willing creature you touch are linked telepathically for the duration while on the "
                         "same plane. Once during the spell, when the Bonded makes an attack roll, ability check or "
                         "saving throw, you can grant it advantage on that roll (no action required); the spell then "
                         "ends.",
                         "<table class='rc-terms'><tr><th>Seer's Duty</th><td>Keep communication clear; grant aid "
                         "once.</td></tr><tr><th>Bonded's Duty</th><td>Use the aid in devotion to the contract.</td></tr>"
                         "<tr><th>Forbidden</th><td>No compulsion against the Bonded's free will.</td></tr><tr><th>"
                         "Breach</th><td>Immediate severance; the spell can't be cast on the pair again until dawn."
                         "</td></tr></table>",
                         "<em>Invocation.</em> \"By Asmodeus' gaze beyond the veil, our minds unite in infernal accord.\""),
                  activities=[utility("contract-seers-vigil", 0, name="Join Minds")]))

SPELLS.append(add("devils-due", name="Devil's Due", img="sp-due", level=3, school="nec", classes=INFERNAL,
                  comps=("vocal", "somatic", "material"), materials="a small scale from a balance and a pinch of sulfur",
                  rng_=rng(60), duration=dur("", "inst"), tgt=target(1, "creature"),
                  desc=P("You call on the weight of a contract to collect an owed debt in blood and spirit. Choose one "
                         "creature within range that is bound by a magical oath or contract, or that has willingly made "
                         "a deal with you or an allied devil. It makes a Charisma saving throw, taking "
                         "[[/damage 6d6 type=necrotic average]] on a failure, or half as much on a success.",
                         "If the creature is in willful breach of a contract (the DM decides), the damage is maximised "
                         "to 36 on a failed save and ignores resistance (immunity still applies). A successful save is "
                         "never maximised.",
                         "If this damage kills the target, the spell tries to tear its soul away to the Nine Hells. "
                         "Only <em>wish</em>, <em>true resurrection</em> or divine intervention can restore it. A "
                         "survivor is branded with a spectral mark visible to fiends: disadvantage on saving throws "
                         "against fear effects created by devils until it fulfils the contract or the mark is removed "
                         "by <em>remove curse</em> cast by a good-aligned cleric.",
                         "<em>Thematic Description.</em> \"All debts must be paid!\" A ghostly scale or chain overlays "
                         "the target, and observers hear a phantom <em>clink</em> of coin."),
                  notes="'Resurrection' in the original could not overcome a soul held in Hell under the Pact Primeval; "
                        "the escape clause now names wish, true resurrection or divine intervention.",
                  activities=[save("devils-due", 0, ability="cha", spell=True, parts=[dmg(6, 6, "", ["necrotic"])],
                                   name="Collect the Debt"),
                              damage_act("devils-due-max", 1, name="Willful Breach (failed save)",
                                         parts=[dmg_formula("36", ["necrotic"])], act=activation("special", None))]))

SPELLS.append(add("binding-clause", name="Binding Clause", img="sp-clause", level=4, school="abj", classes=INFERNAL,
                  comps=("vocal", "somatic", "material"),
                  materials="rare ink worth 100 gp, which the spell consumes, and a pair of miniature iron manacles",
                  mat_cost=100, mat_consumed=True, ritual=True, act=activation("hour", 1), rng_=rng("", "touch"),
                  duration={"value": "", "units": "disp"},
                  desc=P("Over an hour you inscribe a binding clause onto a contract, or onto two willing creatures "
                         "as sigils on their skin. The clause enforces one term of an agreement with a conditional curse "
                         "or boon, defined when you cast it (\"If X does not fulfil Y by Z, then...\"). Choose one:",
                         "<strong>Curse of Breach.</strong> A curse of up to 3rd-level strength (such as <em>bestow "
                         "curse</em>) befalls a creature that violates the clause. It saves against the curse with "
                         "disadvantage when the breach occurs. The curse lasts until the contract is amended or the "
                         "curse is lifted by magic.",
                         "<strong>Geas Enforcement.</strong> The creature is under a <em>geas</em> to fulfil the clause, "
                         "taking [[/damage 5d10 type=psychic]] each day it strays. <em>Remove curse</em> doesn't end "
                         "it; only dispelling the clause or fulfilling the task does.",
                         "<strong>Hellish Boon.</strong> A creature that upholds the clause gains the benefits of "
                         "<em>bless</em> for a time you set (up to 1 hour), or a one-time benefit such as advantage on "
                         "one attack roll made in service of the contract.",
                         "Only one clause per casting. The clause can be dispelled by <em>dispel magic</em> cast at 4th "
                         "level or higher, which causes both parties a sharp pain but no damage. The caster is never "
                         "subject to its own clause."),
                  activities=[utility("binding-clause", 0, name="Inscribe the Clause"),
                              damage_act("binding-clause-geas", 1, name="Geas Enforcement (daily)",
                                         parts=[dmg(5, 10, "", ["psychic"])], act=activation("special", None))]))

SPELLS.append(add("soulforged-blade", name="Contract of the Soulforged Blade", img="sp-blade", level=4, school="nec",
                  classes="Cleric, Paladin, Wizard", comps=("vocal", "somatic", "material"),
                  materials="a weapon worth at least 100 gp, 10 gp of iron filings and a sliver of blood-soaked vellum",
                  ritual=True, act=activation("hour", 1), rng_=rng("", "touch"), duration=dur(24, "hour"),
                  desc=P("You forge an infernal compact into a melee weapon you touch. For the duration the blade "
                         "harvests souls.",
                         "<strong>Soul Tithe Capacity.</strong> The blade holds a number of souls equal to your "
                         "spellcasting ability modifier (minimum 1). <strong>Harvesting.</strong> When you reduce a "
                         "creature to 0 hit points with the weapon, its soul is drawn in and you gain temporary hit "
                         "points equal to its CR (minimum 1). Souls beyond capacity are flung to Avernus as lemures.",
                         "<strong>Souls as Spell Slots.</strong> You can expend N souls to cast a spell of Nth level "
                         "without a slot. Make an Intelligence saving throw (DC 12 + 2 × (N − 1)). On a success you cast "
                         "the spell; on a failure the souls combust, you take 2d8 psychic damage per soul, and the "
                         "blade can't be used until you finish a rest. Either way the souls are consumed.",
                         "<strong>Attunement Progression.</strong> Renewing the ritual daily on the same weapon for 7 "
                         "days lets you renew it weekly instead; after 28 days, monthly. If a renewal lapses, the spell "
                         "ends and any held souls go to Avernus.",
                         "<strong>At Higher Levels.</strong> For each slot level above 4th: +24 hours duration, +1 soul "
                         "capacity, and +1 to the Intelligence save DC.",
                         "<em>DM's note.</em> This is a campaign-scale spell; approve it before a player prepares it."),
                  activities=[utility("soulforged-blade", 0, name="Forge the Compact"),
                              damage_act("soulforged-combust", 1, name="Souls Combust (per soul)",
                                         parts=[dmg(2, 8, "", ["psychic"])], act=activation("special", None))]))

SPELLS.append(add("soul-covenant", name="Soul Covenant", img="sp-covenant", level=5, school="enc", classes=INFERNAL,
                  comps=("vocal", "somatic", "material"),
                  materials="diamond dust worth 200 gp and a sliver of a soul coin, which the spell consumes",
                  mat_cost=200, mat_consumed=True, rng_=rng(15), duration={"value": "", "units": "perm"},
                  desc=P("You speak a covenant that binds up to two willing creatures (which can include you) under "
                         "the eyes of Hell. All parties must agree to the terms before the casting ends. Each signature "
                         "burns into the air and brands an Infernal Mark on the signer's body.",
                         "<strong>Bond of Obligation.</strong> Each party is under a <em>geas</em> with no time limit to "
                         "fulfil the terms: [[/damage 5d10 type=psychic]] per day of defiance, and an attempt to betray "
                         "the covenant ignites the mark for [[/damage 8d6 type=fire]] as a warning. Only <em>wish</em> "
                         "or divine intervention breaks the bond early.",
                         "<strong>Shared Fate (optional).</strong> The parties cannot harm one another until the "
                         "covenant is fulfilled. If one dies first, each survivor takes [[/damage 10d6 type=necrotic]].",
                         "<strong>Infernal Witness.</strong> Asmodeus or an archdevil agent knows of the covenant. "
                         "Fiends with Intelligence 6 or higher recognise a marked creature as under contract, and you "
                         "gain a +5 bonus to Charisma (Persuasion) checks with lawful evil fiends on matters relevant to "
                         "the covenant.",
                         "<strong>Breach.</strong> A party who grossly violates the terms is struck as if by "
                         "<em>flame strike</em> ([[/damage 6d6 type=fire]] and [[/damage 6d6 type=radiant]]) and its "
                         "soul is forfeit to Hell.",
                         "The covenant ends when all terms are fulfilled; the marks glow and fade."),
                  activities=[utility("soul-covenant", 0, name="Speak the Covenant"),
                              damage_act("soul-covenant-defy", 1, name="Defiance (daily)", parts=[dmg(5, 10, "", ["psychic"])],
                                         act=activation("special", None)),
                              damage_act("soul-covenant-betray", 2, name="Betrayal Warning", parts=[dmg(8, 6, "", ["fire"])],
                                         act=activation("special", None)),
                              damage_act("soul-covenant-fate", 3, name="Shared Fate", parts=[dmg(10, 6, "", ["necrotic"])],
                                         act=activation("special", None)),
                              damage_act("soul-covenant-breach", 4, name="Breach: Hell's Judgment",
                                         parts=[dmg(6, 6, "", ["fire"]), dmg(6, 6, "", ["radiant"])],
                                         act=activation("special", None))]))

SPELLS.append(add("infernal-binding", name="Infernal Binding", img="sp-binding", level=5, school="con",
                  classes="Wizard (School of Infernal Contracts)", comps=("vocal", "somatic", "material"),
                  materials="a nine-pointed star drawn in brimstone dust worth 50 gp, which the spell consumes",
                  mat_cost=50, mat_consumed=True, ritual=True, act=activation("hour", 1), rng_=rng(30),
                  duration=dur(1, "hour"),
                  notes="Called a 5th-level ritual with no components in the subclass text. It now has a 50 gp "
                        "consumed material so the 14th-level feature (cast it without material components) means "
                        "something, and the targets follow planar binding's rule that the creature must already be "
                        "present or arrive through the circle you prepare.",
                  desc=P("You inscribe a grand sigil of the Nine Hells and speak the clause <em>\"Foedus aeternum, vos "
                         "liget.\"</em> One fiend, elemental or celestial of CR 10 or lower appears in an unoccupied "
                         "space within range, drawn through the sigil from its home plane. It is bound to obey your "
                         "spoken commands for 1 hour, or until it completes one service you name when the casting "
                         "ends. When the binding ends the creature returns to its plane.",
                         "<strong>At Higher Levels.</strong> With a slot of 6th level or higher you can bind one "
                         "additional creature whose CR is no higher than half the slot's level (rounded down).",
                         "A creature bound this way knows it was compelled. Hell keeps records; so do celestials."),
                  activities=[utility("infernal-binding", 0, name="Bind the Fiend")]))

# ---------------------------------------------------------------------------
# MIDWINTER SPELLS (new for the adventure)
# ---------------------------------------------------------------------------
SPELLS.append(add("read-the-fine-print", name="Read the Fine Print", img="sp-fineprint", level=0, school="div",
                  classes="Bard, Cleric, Paladin, Warlock, Wizard", comps=("vocal", "somatic"),
                  rng_=rng("", "touch"), duration=dur("", "inst"),
                  desc=P("You run a finger along a document. You learn whether it contains any hidden, invisible, "
                         "erased or magically altered text, and roughly where on the page it is, though not what it "
                         "says. You have advantage on the next Intelligence check you make within 1 minute to interpret "
                         "that document.",
                         "In <em>The Night of the Red Clause</em>, this reveals the foundation's <code>HOLIDAY_OVERRIDE</code> "
                         "revisions and the altered service addresses at a touch, though the party still needs a "
                         "certified copy to use as evidence."),
                  activities=[utility("read-the-fine-print", 0, name="Read")]))

e_witness = effect("sp-witness", "Kindness Witnessed", icon("sp-witness"),
                   description="<p>A deed of kindness recorded in light. Any lawful arbiter treats the record as "
                               "authentic.</p>")
SPELLS.append(add("kindness-witnessed", name="Kindness Witnessed", img="sp-witness", level=1, school="div",
                  classes="Bard, Cleric, Paladin", comps=("vocal", "somatic", "material"),
                  materials="a scrap of ribbon and a drop of candle wax", ritual=True, act=activation("minute", 1),
                  rng_=rng(30), duration=dur("", "inst"), tgt=target(1, "creature"),
                  desc=P("You name a creature within range and describe one act of kindness it performed within the "
                         "last 24 hours. If the act happened as you describe it, a ribbon of golden light writes an "
                         "account of it onto a surface you choose (parchment, a wall, the back of a certificate). If it "
                         "did not, nothing appears, and you know the spell found no such deed.",
                         "The record cannot be forged or altered by nonmagical means. A creature that judges disputes "
                         "under law (a magistrate, a contract devil, the Brass Arbiter) recognises it as authentic "
                         "testimony. The record fades after 30 days.",
                         "In the High Court, a record made by this spell counts as authenticated evidence that one "
                         "named citizen's obligation was fulfilled; enough of them, gathered together, can stand in "
                         "for Exhibit A."),
                  activities=[utility("kindness-witnessed", 0, name="Record the Deed")]))

SPELLS.append(add("coal-for-the-wicked", name="Coal for the Wicked", img="sp-coal", level=1, school="evo",
                  classes="Cleric, Druid, Sorcerer, Warlock, Wizard", comps=("vocal", "somatic", "material"),
                  materials="a lump of coal", rng_=rng(90), duration=dur("", "inst"), tgt=target(1, "creature"),
                  desc=P("You hurl a lump of coal that blazes with judgment. Make a ranged spell attack against a "
                         "creature within range. On a hit, the target takes [[/damage 2d10 type=fire]], and if it is a "
                         "fiend it can't regain hit points until the start of your next turn.",
                         "<strong>At Higher Levels.</strong> The damage increases by 1d10 for each slot level above "
                         "1st."),
                  activities=[attack("coal-for-the-wicked", 0, kind="ranged", classification="spell",
                                     ability="spellcasting", range_=90,
                                     parts=[dmg(2, 10, "", ["fire"], "whole", 1)])]))
SPELLS[-1]["system"]["activities"][next(iter(SPELLS[-1]["system"]["activities"]))]["attack"]["ability"] = ""

e_snare = effect("sp-snare", "Wrapping Paper Snare", icon("rc-ribbon"), statuses=["restrained"],
                 description="<p>Restrained by enchanted ribbon. Repeat the Strength saving throw at the end of each "
                             "of your turns.</p>")
SPELLS.append(add("wrapping-paper-snare", name="Wrapping Paper Snare", img="sp-snare", level=2, school="con",
                  classes="Bard, Sorcerer, Warlock, Wizard", comps=("vocal", "somatic", "material"),
                  materials="a bow of red ribbon", concentration=True, rng_=rng(60), duration=dur(1, "minute"),
                  tgt=target("", "creature", "square", 20), effects=[e_snare],
                  desc=P("Ribbons of red and gold paper erupt from the ground in a 20-foot square within range. Each "
                         "creature in the area must succeed on a Dexterity saving throw or be &Reference[restrained]. "
                         "The area is difficult terrain for the duration. A restrained creature can repeat the save "
                         "(as a Strength saving throw) at the end of each of its turns, tearing free on a success.",
                         "Creatures that enter the area for the first time on a turn or start their turn there also "
                         "make the Dexterity save."),
                  activities=[save("wrapping-paper-snare", 0, ability="dex", spell=True, on_save="none",
                                   tgt=target("", "creature", "square", 20), rng_=rng(60),
                                   effects=[e_snare["_id"]], duration=ACTD(1, "minute", True))]))

e_appeal = effect("sp-appeal", "Notice of Appeal", icon("sp-appeal"), duration={"seconds": 60},
                  description="<p>You can't grapple, restrain, move or collect another creature against its will. You "
                              "can still attack. Repeat the save at the end of each of your turns.</p>")
SPELLS.append(add("notice-of-appeal", name="Notice of Appeal", img="sp-appeal", level=2, school="enc",
                  classes="Bard, Cleric, Paladin, Wizard", comps=("vocal", "somatic", "material"),
                  materials="a sheet of paper with your signature on it", concentration=True, rng_=rng(30),
                  duration=dur(1, "minute"), tgt=target(1, "creature"), effects=[e_appeal],
                  desc=P("You thrust a formal appeal at a creature you can see within range. It must succeed on a "
                         "Wisdom saving throw or be unable to grapple, restrain, move or collect any creature against "
                         "that creature's will for the duration. It can still attack. Devils and constructs that "
                         "enforce a contract make this save with disadvantage.",
                         "The target repeats the save at the end of each of its turns, ending the effect on a success.",
                         "<strong>At Higher Levels.</strong> With a slot of 3rd level or higher you can target one "
                         "additional creature for each slot level above 2nd."),
                  activities=[save("notice-of-appeal", 0, ability="wis", spell=True, on_save="none",
                                   tgt=target(1, "creature"), rng_=rng(30), effects=[e_appeal["_id"]],
                                   duration=ACTD(1, "minute", True))]))

SPELLS.append(add("stay-of-execution", name="Stay of Execution", img="sp-stay", level=3, school="abj",
                  classes="Bard, Cleric, Paladin, Wizard", comps=("vocal",),
                  act=activation("reaction", 1, "when a creature you can see within 60 feet makes a saving throw against "
                                                "an effect that would restrain, imprison, banish or carry it off"),
                  rng_=rng(60), duration=dur("", "inst"), tgt=target(1, "creature"),
                  desc=P("You cry <em>\"Objection!\"</em> and the effect hesitates. The creature succeeds on the saving "
                         "throw automatically.",
                         "Alternatively, as an action, you can lodge the spell against an ongoing countdown created by a "
                         "contract, curse or court: the next advance of that countdown is delayed by one round. A given "
                         "countdown can be stayed by this spell only once.",
                         "In the High Court of Seasonal Obligations, the action version delays the next bell of the "
                         "Midnight Docket by one round; it counts toward the maximum of two delays from clever "
                         "actions."),
                  activities=[utility("stay-of-execution", 0, name="Objection! (reaction)",
                                      act=activation("reaction", 1)),
                              utility("stay-of-execution-docket", 1, name="Stay the Docket (action)")]))

SPELLS.append(add("midwinter-dawn", name="Midwinter Dawn", img="sp-dawn", level=5, school="evo",
                  classes="Cleric, Druid, Paladin, Sorcerer, Wizard", comps=("vocal", "somatic", "material"),
                  materials="a sliver of glass that has held the first light of a winter morning", rng_=rng(60),
                  duration=dur("", "inst"), tgt=target("", "creature", "sphere", 20),
                  desc=P("You call the morning early. True dawn light floods a 20-foot-radius sphere centred on a point "
                         "within range. Each fiend and undead of your choice in the area makes a Constitution saving "
                         "throw, taking [[/damage 6d8 type=radiant]] on a failure, or half as much on a success.",
                         "The light is sunlight. Any magical darkness, and any effect of 5th level or lower that holds "
                         "back time or suppresses the sunrise, is ended in the area. Creatures of your choice in the area "
                         "remember, clearly and suddenly, what morning feels like: each can end one effect on itself "
                         "that is making it charmed or frightened.",
                         "<strong>At Higher Levels.</strong> The damage increases by 1d8 for each slot level above 5th.",
                         "Cast in the Department of Perpetual Midnight, this spell counts as freeing the trapped sun."),
                  activities=[save("midwinter-dawn", 0, ability="con", spell=True,
                                   parts=[dmg(6, 8, "", ["radiant"], "whole", 1)],
                                   tgt=target("", "creature", "sphere", 20), rng_=rng(60))]))

for s in SPELLS:
    s["flags"][MOD] = {"group": "Asmodeun Scriptorium" if s["name"] in (
        "Seal of the First Pact", "True Name Revelation", "Quill of Binding", "Contract of the Infernal Fury",
        "Contract of the Seer's Vigil", "Devil's Due", "Binding Clause", "Contract of the Soulforged Blade",
        "Soul Covenant", "Infernal Binding") else "Midwinter Magic"}
