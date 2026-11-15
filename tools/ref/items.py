"""Magic items, gifts, evidence and rewards."""
from lib5e import *


def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


ITEMS = {}  # folder -> list


def put(folder, doc):
    ITEMS.setdefault(folder, []).append(doc)
    return doc


EXPIRES = ("<p class='rc-fine'><em>Terms and conditions apply.</em> The benefit expires at the end of the adventure if "
           "unused. Accepting this gift binds the recipient to the Certificate of Festive Entitlement (Form H-25). The "
           "gift itself carries no hidden drawback.</p>")


def gift(key, name, desc, reveal, *, img, itype="consumable", subtype="trinket", activities=None, uses_=None,
         effects=None, extra=None):
    d = desc + f"<div class='rc-secret'><h4>Later Revelation</h4><p>{reveal}</p></div>" + EXPIRES
    doc = item(key, name, itype, d, img=icon(img), rarity="uncommon", activities=activities, uses_=uses_,
               subtype=subtype, effects=effects, extra=extra, weight=0.5)
    doc["flags"][MOD] = {"gift": True}
    return put("The Nine Gifts of Midwinter", doc)


e_warm = effect("everwarm", "Everwarm Scarf", icon("it-scarf"), duration={"seconds": 3600},
                changes=[("system.traits.dr.value", 2, "cold")],
                description="<p>Resistance to cold damage for 1 hour.</p>")
gift("everwarm-scarf", "The Everwarm Scarf",
     P("A long scarf of red and white wool that never quite stops being warm. As an action you can wrap it tight: for 1 "
       "hour you have resistance to cold damage. Single use."),
     "Woven by debtors trapped in an endless winter.", img="it-scarf", uses_=uses(1),
     effects=[e_warm],
     activities=[utility("everwarm", 0, name="Wrap Up", consumption=consume_item_uses(), effects=[e_warm["_id"]])])
gift("candy-cane-mercy", "The Candy Cane of Mercy",
     P("A peppermint cane as long as a forearm. As an action, snap it over a creature you touch: it regains "
       "[[/heal 5d8 + 5]] hit points. Single use."),
     "Manufactured using confiscated healing magic.", img="it-candycane", subtype="food", uses_=uses(1),
     activities=[heal_act("candy-cane", 0, formula_part=dmg(5, 8, 5), consumption=consume_item_uses(),
                          tgt=target(1, "creature"), rng_=rng("", "touch"))])
gift("bell-perfect-timing", "The Bell of Perfect Timing",
     P("A silver hand-bell no bigger than a thimble. When you fail an ability check or saving throw, you can ring it "
       "(no action required) and add [[/roll 1d8]] to the roll, possibly turning it into a success. Single use."),
     "Its recorded ring can be used as evidence: the bell remembers when and where it was rung.",
     img="it-bell", uses_=uses(1),
     activities=[utility("bell-timing", 0, name="Ring", act=activation("special", None), consumption=consume_item_uses(),
                         roll=("1d8", "Perfect Timing"))])
gift("jolly-soldier", "The Jolly Soldier",
     P("A painted toy soldier in a gift box. As an action you can wind its key: it grows to the size of a halfling and "
       "follows your simple commands for 1 hour, using the " + uuid_actor("toy-soldier", "Festive Toy Soldier") +
       " statistics. It won't attack you unless someone independently uses a command override. Single use."),
     "The other soldiers serve as enforcement units, and the Red Clause can override unprotected ones.",
     img="it-soldier", uses_=uses(1),
     activities=[utility("jolly-soldier", 0, name="Wind the Key", consumption=consume_item_uses())])
gift("stocking-holding", "The Stocking of Holding",
     P("A fat red stocking that holds up to 50 pounds in a miniature extradimensional space without getting heavier. "
       "Retrieving an item takes an action."),
     "It uses the workshop's own storage network. Anything inside on Midwinter night ends up in Workshop Nine's "
     "intake.", img="it-stocking", itype="container", subtype="",
     extra={"capacity": {"weight": {"value": 50, "units": "lb"}, "volume": {"value": None, "units": "cubicFoot"}},
            "properties": ["weightlessContents"]})
gift("gingerbread-champion", "The Gingerbread Champion",
     P("A gingerbread warrior with icing armour. As an action you can eat it: you gain [[/heal 15 type=temphp]] "
       "temporary hit points for 1 hour. Single use."),
     "Originally designed as a workforce stimulant.", img="it-gingerbread", subtype="food", uses_=uses(1),
     activities=[heal_act("gingerbread", 0, formula_part=dmg_formula("15"), temp=True, consumption=consume_item_uses(),
                          tgt=target("", "self"))])
gift("star-good-fortune", "The Star of Good Fortune",
     P("A golden tree-topper star stamped with a tiny serial number. Once, when you make an attack roll, ability check "
       "or saving throw, you can reroll the d20 (no action required) and use either result."),
     "Its serial number identifies the legal issuer: Nicholas Red Clause, Executive Director of Seasonal Obligations.",
     img="it-star", uses_=uses(1),
     activities=[utility("star-fortune", 0, name="Reroll", act=activation("special", None), consumption=consume_item_uses())])
mirror = gift("mirror-merriment", "The Mirror of Merriment",
              P("A hand mirror framed in holly. Once, as an action, you can cast <em>disguise self</em> from it without "
                "a spell slot."),
              "The mirror also stores a record of its original owner's face, which can prove who accepted the gift.",
              img="it-mirror", uses_=uses(1),
              activities=[utility("mirror", 0, name="Cast Disguise Self", consumption=consume_item_uses())])
mirror["system"]["activities"][next(iter(mirror["system"]["activities"]))].update({})
mirror["system"]["description"]["value"] = mirror["system"]["description"]["value"].replace(
    "<em>disguise self</em>", "@UUID[Compendium.dnd5e.spells.Item.A3q2gTNqG6fvNGrv]{disguise self}")
e_candle = effect("candle", "Hearthlight Candle", icon("it-candle"), duration={"seconds": 600},
                  description="<p>You see invisible creatures and objects as if they were visible, and you can see into "
                              "the Ethereal Plane. Hidden infernal lettering on documents glows red.</p>")
gift("hearthlight-candle", "The Hearthlight Candle",
     P("A fat beeswax candle in a brass holder. Once, as an action, you can light it: for 10 minutes you gain the "
       "benefits of " + "@UUID[Compendium.dnd5e.spells.Item.DQzlB5Y3k791W5bH]{see invisibility}" + "."),
     "Its light reveals hidden infernal lettering on documents, including the HOLIDAY_OVERRIDE revisions.",
     img="it-candle", uses_=uses(1), effects=[e_candle],
     activities=[utility("candle", 0, name="Light", consumption=consume_item_uses(), effects=[e_candle["_id"]])])

# ---------------------------------------------------------------------------
# Evidence & key items
# ---------------------------------------------------------------------------


def evidence(key, name, desc, *, img, writ="", handout=""):
    d = desc
    if handout:
        d += f"<p><strong>Handout:</strong> {handout}</p>"
    doc = item(key, name, "loot", d, img=icon(img), subtype="", weight=0.1)
    doc["flags"][MOD] = {"evidence": True, "writ": writ}
    return put("Evidence & Documents", doc)


evidence("certificate-h25", "Certificate of Festive Entitlement (Form H-25)",
         P("The gift contract every recipient signs. Read carefully, it protects the recipient: it requires only a "
           "witnessed act of kindness, limits the penalty to one night of service ending at Waterdeep's sunrise, "
           "forbids seizing anything else, conveys no interest in the soul, requires written notice at a Material Plane "
           "address, and names the independent Brass Arbiter."),
         img="it-certificate", handout=uuid_journal("handouts", "certificate", "Certificate of Festive Entitlement"))
evidence("edda-receipt", "Edda's Reciprocity Record",
         P("A Hearthlight receipt recovered from Edda Hearth's basket. It shows her deed recorded as FULFILLED, then "
           "revised to DEFAULT by central audit, with notice served to Nessus, Ninth Circle, Docket 666-H."),
         img="it-receipt", handout=uuid_journal("handouts", "receipt", "Edda's Reciprocity Record"))
evidence("exhibit-a", "Exhibit A: Evidence of Falsified Defaults",
         P("A certified copy of the original verification ledger, bearing the foundation's own magical seal. Thousands "
           "of fulfilled kindness obligations were changed to defaults by the automated command "
           "<code>HOLIDAY_OVERRIDE</code>.", "<strong>Counters:</strong> Writ I — The Presumption of Default."),
         img="it-exhibit-a", writ="I", handout=uuid_journal("handouts", "exhibit-a", "Exhibit A"))
evidence("exhibit-b", "Exhibit B: Evidence of Falsified Service Addresses",
         P("Certified Waterdeep residence records, set beside the foundation's notice log. Every seized recipient is "
           "listed as residing in Nessus; the addresses were changed immediately before the notices were issued.",
           "<strong>Counters:</strong> Writ III — The Doctrine of Abandoned Souls."),
         img="it-exhibit-b", writ="III", handout=uuid_journal("handouts", "exhibit-b", "Exhibit B"))
evidence("exhibit-c", "Exhibit C: The Endless-Night Mechanism",
         P("Mizzle's maintenance schematic and the Midnight Engine's calibration settings, proving the workshop "
           "artificially overrides Waterdeep's real sunrise. Clause III ends service at sunrise <em>as observed in "
           "Waterdeep</em>.", "<strong>Counters:</strong> Writ II — The Perpetuity of Service."),
         img="it-exhibit-c", writ="II", handout=uuid_journal("handouts", "exhibit-c", "Exhibit C"))
evidence("exhibit-d", "Exhibit D: Testimony and Records of Unauthorised Soul Transfers",
         P("Tilda Marr's testimony, and the archive records showing that no one on the assembly line ever signed a "
           "separate soul-transfer agreement. The category <em>unclaimed personal essence</em> appears in no contract.",
           "<strong>Counters:</strong> Writ III — The Doctrine of Abandoned Souls."),
         img="it-exhibit-d", writ="III", handout=uuid_journal("handouts", "exhibit-d", "Exhibit D"))
evidence("nessus-memo", "Confidential Nessus Memorandum (Project Yuletide)",
         P("Executive correspondence from Asmodeus's court. A precedent achieved through invalid documentation "
           "\"shall be considered a failure of your appointment.\" Proof that the Red Clause is afraid of his employer."),
         img="it-memo", handout=uuid_journal("handouts", "memo", "Project Yuletide memorandum"))
evidence("dasher-manifest", "DASH-ER 3000 Delivery Manifest",
         P("Sixteen barrels of enchanted eggnog. True destination: <strong>Workshop Nine, Nessus Distribution "
           "Network.</strong> At first it sounds like a joke."), img="it-manifest",
         handout=uuid_journal("handouts", "manifest", "DASH-ER manifest"))
evidence("access-token", "Service Access Token",
         P("A brass token stamped GOODWILL-999 from Mizzle. It opens the concealed service elevator behind the "
           "Foundation Pavilion and lets the bearer pass the Intake checkpoint without an alarm."), img="it-token")
evidence("maintenance-schematic", "Maintenance Schematic",
         P("Mizzle's copy of the Midnight Engine schematic. With it, disabling the clock in the Department of "
           "Perpetual Midnight succeeds automatically, and it serves as Exhibit C."), img="it-schematic", writ="II")
evidence("valid-soul-bargain", "A Genuine Soul Bargain",
         P("Found in the Ledger of Abandoned Souls: a real contract in which a mortal knowingly signed away their soul "
           "for a miracle. It is valid under infernal law, and it shows exactly what the foundation's certificates are "
           "<em>not</em>."), img="it-scroll")
evidence("sprocket-citation", "A Citation from Sprocket Jingles",
         P("A tiny brass-edged ticket for an offence such as <em>Premeditated Carolling Without a Licence</em>. "
           "Unenforceable. Faint infernal signature."), img="it-citation")

# ---------------------------------------------------------------------------
# Wondrous items & rewards
# ---------------------------------------------------------------------------


def wondrous(key, name, desc, *, img, rarity, attune="", activities=None, uses_=None, effects=None, folder="Rewards & Relics",
             itype="equipment", subtype="trinket", extra=None, price=0):
    return put(folder, item(key, name, itype, desc, img=icon(img), rarity=rarity, attune=attune, activities=activities,
                            uses_=uses_, effects=effects, subtype=subtype, extra=extra, price=price, weight=1))


wondrous("infernal-signet", "Infernal Signet of the Red Clause",
         P("A heavy signet ring of black iron set with a ruby that ticks like a clock. Left behind when the Red "
           "Clause's avatar is destroyed.",
           "<strong>Emergency Cancellation.</strong> During the adventure, a creature holding the signet can use an "
           "action to stamp an emergency cancellation on the Master Ledger, ending the soul transfer.",
           "<strong>Afterwards.</strong> While attuned, you know whether any written contract you touch has been "
           "altered since it was signed. Once per dawn you can cast <em>zone of truth</em> (save DC 15) from the ring.",
           "<strong>Curse of the Ninth Court.</strong> Asmodeus's clerks always know where the ring is."),
         img="it-signet", rarity="rare", attune="required", uses_=uses(1, ["dawn"]),
         activities=[utility("signet-cancel", 0, name="Emergency Cancellation"),
                     utility("signet-zot", 1, name="Zone of Truth (1/dawn)", consumption=consume_item_uses())])
wondrous("dawnglass", "Tilda's Dawnglass",
         P("A shard of the glass sphere that held the workshop's stolen sun. It is always faintly warm.",
           "The dawnglass has 3 charges and regains [[/roll 1d3]] expended charges daily at dawn. While holding it you "
           "can use an action to expend charges:",
           "<strong>Morning (1 charge).</strong> You cast <em>daylight</em>.",
           "<strong>Sunrise (3 charges).</strong> Each fiend and undead of your choice within 20 feet of you makes a "
           "DC 15 Constitution saving throw, taking 4d10 radiant damage on a failure, or half as much on a success."),
         img="it-dawnglass", rarity="rare", attune="required", uses_=uses(3, [{"period": "dawn", "type": "formula",
                                                                                "formula": "1d3"}]),
         activities=[utility("dawn-morning", 0, name="Morning (daylight)", consumption=consume_item_uses(1)),
                     save("dawn-sunrise", 1, ability="con", dc=15, parts=[dmg(4, 10, "", ["radiant"])],
                          name="Sunrise", consumption=consume_item_uses(3), tgt=target("", "creature", "radius", 20))])
e_ticket = effect("clipboard", "Cited", icon("rc-citation"), changes=[("system.attributes.movement.walk", 2, -10)],
                  duration={"rounds": 1}, description="<p>Speed reduced by 10 feet until the end of your next turn.</p>")
wondrous("sprocket-clipboard", "Sprocket's Clipboard of Citations",
         P("A tiny brass clipboard, still warm from three centuries of terrified paperwork. It has 3 charges and regains "
           "all of them at dawn.",
           "As a bonus action you can expend 1 charge to write a citation for a creature within 30 feet. It must succeed "
           "on a DC 13 Wisdom saving throw or its speed is reduced by 10 feet until the end of its next turn.",
           "The clipboard also generates a ridiculous fine on request (" + uuid_table("festive-fines", "Festive "
                                                                                       "Compliance Fines") + ")."),
         img="it-clipboard", rarity="uncommon", uses_=uses(3, ["dawn"]), effects=[e_ticket],
         activities=[save("clipboard", 0, ability="wis", dc=13, on_save="none", act=activation("bonus", 1),
                          rng_=rng(30), tgt=target(1, "creature"), consumption=consume_item_uses(),
                          effects=[e_ticket["_id"]])])
e_bell9 = effect("bell9", "Toll of the Ninth Hour", icon("it-bell9"), statuses=["frightened"], duration={"rounds": 1},
                 description="<p>Frightened of the bell-ringer until the end of its next turn.</p>")
wondrous("bell-ninth-hour", "Bell of the Ninth Hour",
         P("One of the nine bells of the Midnight Docket, small enough to hold. Once per dawn you can ring it as an "
           "action. Each fiend of your choice within 60 feet that can hear it must succeed on a DC 15 Wisdom saving "
           "throw or be frightened of you until the end of its next turn. Devils who hear it remember Waterdeep."),
         img="it-bell9", rarity="rare", uses_=uses(1, ["dawn"]), effects=[e_bell9],
         activities=[save("bell9", 0, ability="wis", dc=15, on_save="none", consumption=consume_item_uses(),
                          tgt=target("", "creature", "radius", 60), effects=[e_bell9["_id"]])])
wondrous("arbiter-gavel", "Gavel of the Brass Arbiter",
         P("A small brass gavel that the Arbiter strikes once, after a just verdict, and leaves on the lectern for the "
           "party.",
           "<strong>Order!</strong> Once per dawn, as an action, you strike the gavel and cast <em>command</em> (save "
           "DC 15) targeting up to three creatures, giving all of them the same one-word command.",
           "<strong>Precedent.</strong> You have advantage on Charisma (Persuasion) checks made to argue a point of law "
           "before any court that recognises the Pact Primeval."),
         img="it-gavel", rarity="rare", attune="required", uses_=uses(1, ["dawn"]),
         activities=[utility("gavel", 0, name="Order!", consumption=consume_item_uses())])
wondrous("golgorath-quill", "Golgorath's Quill",
         P("The Asmodeun Scriptorium's legendary notary quill: a permanent, more powerful "
           + uuid_spell("quill-of-binding", "Quill of Binding") + ".",
           "While attuned, you can cast <em>quill of binding</em> at will without components, and once per dawn you can "
           "cast " + uuid_spell("binding-clause", "binding clause") + " without material components.",
           "<strong>Sentience (optional).</strong> The quill hums disapprovingly when a contract is badly drafted."),
         img="it-quill", rarity="very rare", attune="required by a spellcaster", uses_=uses(1, ["dawn"]),
         activities=[utility("golgorath-quill", 0, name="Quill of Binding (at will)"),
                     utility("golgorath-clause", 1, name="Binding Clause (1/dawn)", consumption=consume_item_uses(),
                             act=activation("hour", 1))])
e_collar = effect("collar", "Collar of Compulsory Cheer", icon("it-collar"), transfer=True,
                  description="<p>Cursed. You can't show negative emotion. Disadvantage on saving throws against being "
                              "charmed; advantage on Charisma (Deception) checks to appear happy.</p>")
wondrous("collar-cheer", "Collar of Compulsory Cheer",
         P("A brass collar with a small wheel at the throat, worn by every worker in the Workshop of Good Intentions.",
           "<strong>Curse.</strong> A creature wearing the collar can't remove it and can't show negative emotion; its "
           "smile never changes. It has disadvantage on saving throws against being charmed and advantage on Charisma "
           "(Deception) checks made to appear happy. A Brass Supervisor can turn the wheel to suppress tears.",
           "<em>Remove curse</em>, <em>dispel magic</em> (DC 13) or breaking the collar (AC 15, 5 HP; the wearer takes "
           "any damage beyond that) frees the wearer."),
         img="it-collar", rarity="uncommon", effects=[e_collar], folder="Workshop Curios")
wondrous("soul-coin", "Hearthlight Soul-Coin", P(
    "A coin of red iron minted in Workshop Nine, stamped with the face of whoever it was struck from. The registry "
    "values UNASSIGNED MATERNAL AFFECTION at 14,000 of these.",
    "A soul-coin hums with a trapped voice. Freed captives' coins crumble to ash at dawn."),
    img="it-soulcoin", rarity="uncommon", folder="Workshop Curios", itype="loot", subtype="")
wondrous("memory-music-box", "Music Box of a Final Happy Thought", P(
    "A little music box from the Assembly Line of Eternal Gratitude. It plays a tune that makes anyone who hears it "
    "smile, powered by the last happy thought of a debtor. Opening it in sunlight releases the thought back to its "
    "owner, wherever they are."), img="it-musicbox", rarity="common", folder="Workshop Curios", itype="loot", subtype="")
wondrous("laughing-toy", "Toy That Laughs in a Loved One's Voice", P(
    "A stuffed bear that giggles when squeezed, in the voice of someone's grandmother. Somebody, somewhere, can no "
    "longer remember what she sounded like."), img="it-toybear", rarity="common", folder="Workshop Curios",
    itype="loot", subtype="")

# Clause Chain whip (weapon)
CHAIN = item("clause-chain-whip", "Length of Clause Chain", "weapon", P(
    "A barbed length of the Red Clause's beard, unravelled into chain when the smile disappeared. You have a +1 bonus to "
    "attack and damage rolls made with this magic weapon. On a hit it deals an extra 1d6 psychic damage as the target "
    "hears every clause it has ever broken read aloud."),
    img=icon("it-chainwhip"), rarity="rare", attune="required", subtype="martialM", weight=3,
    props=("fin", "rch", "mgc"),
    extra={"damage": {"base": {"number": 1, "denomination": 4, "bonus": "", "types": ["slashing"],
                               "custom": {"enabled": False, "formula": ""},
                               "scaling": {"mode": "", "number": None, "formula": ""}},
                      "versatile": {"number": None, "denomination": None, "bonus": "", "types": [],
                                    "custom": {"enabled": False, "formula": ""},
                                    "scaling": {"mode": "", "number": None, "formula": ""}}},
           "magicalBonus": 1, "range": {"value": None, "long": None, "reach": 10, "units": "ft"},
           "type": {"value": "martialM", "baseItem": "whip"}, "proficient": None, "mastery": "slow"},
    activities=[attack("clause-chain-whip", 0, ability="", reach=10, classification="weapon",
                       parts=[dmg(1, 6, "", ["psychic"])])])
CHAIN["system"]["activities"][next(iter(CHAIN["system"]["activities"]))]["damage"]["includeBase"] = True
put("Rewards & Relics", CHAIN)
