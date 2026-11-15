"""Every creature and object in the adventure as a dnd5e 5.3.3 NPC actor.

Numbers follow the adventure plan; where a plan number disagreed with the
creature's own ability scores the change is listed in DESIGN_NOTES so the
audit trail is visible in the GM's journal.
"""
from lib5e import *

DESIGN_NOTES = []


def note(s):
    DESIGN_NOTES.append(s)


def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


ACT = activation
BONUS = lambda c="": activation("bonus", 1, c)
REACT = lambda c="": activation("reaction", 1, c)
LEG = lambda n=1: activation("legendary", n)
LAIR = activation("lair", 1, "Initiative count 20 (losing initiative ties)")
SPECIAL = activation("special", None)

# ===========================================================================
#  NICHOLAS RED CLAUSE
# ===========================================================================
K = "red-clause"
eff_citation = effect("rc-citation", "Crimson Citation", icon("rc-citation"),
                      changes=[("system.attributes.movement.walk", 2, -10)], duration={"rounds": 1},
                      description="<p>Speed reduced by 10 feet. The first time you attack or cast a spell before the "
                                  "end of your next turn, take 2d6 psychic damage. Remove the citation as a Bonus Action.</p>")
eff_wrapped = effect("rc-wrapped", "Gift-Wrapped", icon("rc-ribbon"), statuses=["restrained"], duration={"rounds": 1},
                     description="<p>Restrained by enchanted ribbons until the end of your next turn.</p>")
eff_noreact = effect("rc-breach", "Breach Notice", icon("rc-breach"), duration={"rounds": 1},
                     description="<p>You can't take reactions until the start of your next turn.</p>")
eff_sacked = effect("rc-sacked", "Repossessed", icon("rc-sack"), statuses=["blinded"], duration={"rounds": 2},
                    description="<p>Inside the Sack of Repossession. No line of sight or effect to anything outside. "
                                "Take 3d6 cold damage at the start of each of your turns. Escape: action, DC 17 "
                                "Athletics or Arcana; or damage the inner seam (AC 15, 25 HP). Expelled automatically "
                                "at the end of your following turn.</p>")
eff_fineprint = effect("rc-fineprint", "Blizzard of Fine Print", icon("rc-fineprint"), duration={"rounds": 1},
                       description="<p>Disadvantage on your next d20 roll before the end of your next turn.</p>")

red_items = [
    feat(K + "-writbound", "Writ-Bound Authority",
         P("The Red Clause's power in the High Court flows from three floating Infernal Writs. While a Writ stands, he "
           "keeps the power it grants; when a Writ is invalidated by evidence or destroyed, that power ends at once.",
           "<strong>Writ I — Presumption of Default:</strong> Default Notice; bailiffs remain under central command.<br>"
           "<strong>Writ II — Perpetuity of Service:</strong> Perpetual Service (regains 15 hit points).<br>"
           "<strong>Writ III — Doctrine of Abandoned Souls:</strong> Legendary Resistance (2/Encounter)."),
         img=icon("rc-writ"), activities=[]),
    feat(K + "-legres", "Legendary Resistance (2/Encounter, Writ III)",
         P("While Writ III stands, if the Red Clause fails a saving throw, he can choose to succeed instead. Any unused "
           "uses vanish the moment Writ III is invalidated or destroyed."),
         img=icon("rc-resist"), activities=[utility(K + "-legres", 0, act=SPECIAL, consumption=consume_legres())]),
    feat(K + "-perpetual", "Perpetual Service (Writ II)",
         P("While Writ II stands, the Red Clause regains 15 hit points at the start of his turn. This ends permanently "
           "when Writ II is invalidated or destroyed."),
         img=icon("rc-clock"), activities=[heal_act(K + "-perp", 0, formula_part=dmg_formula("15"),
                                                     act=activation("turnStart", None), tgt=target("", "self"))]),
    feat(K + "-avatar", "Seasonal Avatar",
         P("The Red Clause is an avatar constructed and empowered by Asmodeus. If reduced to 0 hit points he "
           "disintegrates into red paper, broken gears and burning ash, leaving his <strong>Infernal Signet</strong> "
           "behind. The master ledger keeps running; see <em>If the Players Kill the Red Clause</em>."),
         img=icon("rc-signet")),
    feat(K + "-arbitration", "Bound by Arbitration",
         P("The Red Clause must permit a properly demanded arbitration before the Brass Arbiter and cannot act to "
           "silence the Arbiter. He can, however, try to disrupt the people presenting the case."),
         img=icon("rc-gavel")),
    feat(K + "-multi", "Multiattack", P("The Red Clause makes two Clause Chain attacks."), img=icon("rc-multi"),
         activities=[utility(K + "-multi", 0)]),
    feat(K + "-chain", "Clause Chain",
         P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]. The chains are "
           "magical."),
         img=icon("rc-chain"),
         activities=[attack(K + "-chain", 0, to_hit=11, reach=15,
                            parts=[dmg(2, 8, 6, ["slashing"]), dmg(1, 8, "", ["psychic"])])]),
    feat(K + "-breach", "Breach Notice (Recharge 5–6)",
         P("The Red Clause projects an infernal legal pronouncement in a 30-foot cone. Each enemy in the area makes a "
           "[[/save]] saving throw, taking [[/damage extended]] and being unable to take reactions until the start of "
           "its next turn on a failed save, or half as much damage on a successful one."),
         img=icon("rc-breach"), uses_=uses(1, [recharge(5)]),
         effects=[eff_noreact],
         activities=[save(K + "-breach", 0, ability="wis", dc=18, parts=[dmg(5, 8, "", ["psychic"])],
                          tgt=target("", "enemy", "cone", 30), consumption=consume_item_uses(),
                          effects=[eff_noreact["_id"]])]),
    feat(K + "-sack", "Sack of Repossession (Recharge 6)",
         P("One Large or smaller creature within 30 feet must make a [[/save]] saving throw. On a failure it is pulled "
           "into an extradimensional compartment inside the sack, where it has no line of sight or effect to the "
           "outside and takes [[/damage extended]] at the start of each of its turns.",
           "A trapped creature can use an action to escape with a DC 17 Strength (Athletics) or Intelligence (Arcana) "
           "check, attack the inner seams (AC 15, 25 HP), or use teleportation magic. An ally outside can damage the "
           "external clasp the same way. The creature is expelled automatically at the end of its following turn. "
           "The sack holds one creature at a time."),
         img=icon("rc-sack"), uses_=uses(1, [recharge(6)]), effects=[eff_sacked],
         activities=[save(K + "-sack", 0, ability="str", dc=18, parts=[], on_save="none",
                          tgt=target(1, "creature"), rng_=rng(30), consumption=consume_item_uses(),
                          effects=[eff_sacked["_id"]]),
                     damage_act(K + "-sack-cold", 1, name="Cold of the Sack (start of turn)",
                                parts=[dmg(3, 6, "", ["cold"])], act=SPECIAL)]),
    feat(K + "-default", "Default Notice (Writ I)",
         P("<strong>Bonus Action, while Writ I stands.</strong> One creature the Red Clause can see within 60 feet "
           "must succeed on a [[/save]] saving throw or receive a hovering crimson citation. Until the end of that "
           "creature's next turn its speed is reduced by 10 feet, and the first time it attacks or casts a spell in "
           "that time it takes [[/damage extended]]. The creature can remove the citation as a Bonus Action."),
         img=icon("rc-citation"), effects=[eff_citation],
         activities=[save(K + "-default", 0, ability="wis", dc=18, on_save="none", act=BONUS(),
                          tgt=target(1, "creature"), rng_=rng(60), effects=[eff_citation["_id"]]),
                     damage_act(K + "-default-dmg", 1, name="Citation Penalty", parts=[dmg(2, 6, "", ["psychic"])],
                                act=SPECIAL)]),
    feat(K + "-legactions", "Legendary Actions",
         P("The Red Clause can take 2 legendary actions (3 against six heroes), choosing from the options below. "
           "Only one legendary action can be used at a time and only at the end of another creature's turn. He "
           "regains spent legendary actions at the start of his turn."),
         img=icon("rc-legendary")),
    feat(K + "-staple", "Staple of Judgment (Costs 1 Action)",
         P("Once per round. <em>Ranged Spell Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
         img=icon("rc-staple"),
         activities=[attack(K + "-staple", 0, to_hit=11, kind="ranged", classification="spell", range_=30,
                            parts=[dmg(2, 8, 4, ["force"])], act=LEG(1), consumption=consume_legact(1))]),
    feat(K + "-relocate", "Relocate Assets (Costs 1 Action)",
         P("The Red Clause moves up to half his speed without provoking opportunity attacks."), img=icon("rc-relocate"),
         activities=[utility(K + "-relocate", 0, act=LEG(1), consumption=consume_legact(1))]),
    feat(K + "-order", "Order Enforcement (Costs 1 Action)",
         P("Once per round. One allied Jingle Bailiff moves up to half its speed and makes one Binding Baton attack."),
         img=icon("rc-order"), activities=[utility(K + "-order", 0, act=LEG(1), consumption=consume_legact(1))]),
    feat(K + "-lair-furnace", "Lair Action: Furnace Discharge",
         P("A 40-foot-long, 10-foot-wide line of hellfire roars from the central furnace. Each creature in it makes a "
           "[[/save]] saving throw, taking [[/damage extended]] on a failure, or half as much on a success."),
         img=icon("rc-furnace"),
         activities=[save(K + "-furnace", 0, ability="dex", dc=18, parts=[dmg(3, 8, "", ["fire"])], act=LAIR,
                          tgt=target("", "creature", "line", 40, 10))]),
    feat(K + "-lair-ribbon", "Lair Action: Gift-Wrapped Restraints",
         P("A 20-foot square erupts with ribbons. Each creature in it must succeed on a [[/save]] saving throw or be "
           "&Reference[restrained] until the end of its next turn."),
         img=icon("rc-ribbon"), effects=[eff_wrapped],
         activities=[save(K + "-ribbon", 0, ability="dex", dc=17, on_save="none", act=LAIR,
                          tgt=target("", "creature", "square", 20), effects=[eff_wrapped["_id"]])]),
    feat(K + "-lair-fineprint", "Lair Action: Blizzard of Fine Print",
         P("Each creature in a 20-foot-radius area must succeed on a [[/save]] saving throw or have disadvantage on "
           "its next d20 roll before the end of its next turn."),
         img=icon("rc-fineprint"), effects=[eff_fineprint],
         activities=[save(K + "-fineprint", 0, ability="wis", dc=17, on_save="none", act=LAIR,
                          tgt=target("", "creature", "radius", 20), effects=[eff_fineprint["_id"]])]),
    feat(K + "-phase2", "The Smile Disappears (Phase II, once)",
         P("Triggered once, when two Writs have fallen or the Red Clause drops below half his hit points. His coat "
           "splits open on a furnace of black iron and white-hot chains. Each creature within 15 feet makes a "
           "[[/save]] saving throw, taking [[/damage extended]] on a failure, or half as much on a success. His "
           "statistics do not change; his manner becomes cold, legalistic and absolutely serious."),
         img=icon("rc-phase2"),
         activities=[save(K + "-phase2", 0, ability="wis", dc=18, parts=[dmg(4, 8, "", ["psychic"])], act=SPECIAL,
                          tgt=target("", "creature", "radius", 15))]),
]

RED_CLAUSE = npc(K, "Nicholas Red Clause", img=portrait("red-clause"), token=tok("red-clause"), size="huge",
                 ctype="fiend", subtype="devil", alignment="Lawful Evil", cr=15, ac=19, hp=250, hp_formula="20d12 + 120",
                 speed=40, abilities=(22, 12, 22, 18, 16, 22), saves=("str", "con", "int", "wis", "cha"),
                 skills={"dec": 2, "ins": 1, "prc": 1, "prf": 1}, dr=("cold", "fire", "necrotic"), di=("poison",),
                 ci=("charmed", "frightened", "poisoned"), senses={"truesight": 60}, langs=("common", "infernal"),
                 lang_custom="telepathy 120 ft.", legact=2, legres=2, lair=True, items=red_items,
                 bio=P("<em>Asmodeus's Seasonal Avatar. Executive Director of Seasonal Obligations.</em>",
                       "About nine feet tall, with curling black horns, an enormous white beard, polished spectacles, "
                       "a crimson coat and a sack larger than a carriage. His body creaks like clockwork. He smells "
                       "faintly of cinnamon and brimstone.",
                       "In Act I he should be genuinely funny. By Act IV he is terrifying precisely because he has "
                       "stopped being funny."),
                 gm_note="CR 15 is listed for XP only; this is an encounter-specific homebrew boss.")
note("Nicholas Red Clause: the plan gives no CR. Proficiency +5 in his saves implies CR 13–16, so the sheet lists CR 15 "
     "(13,000 XP) for the XP tracker only. HP 250 = 20d12 + 120.")

# ===========================================================================
#  ENFORCEMENT
# ===========================================================================
K = "jingle-bailiff"
eff_cite_b = effect("jb-citation", "Bailiff's Citation", icon("rc-citation"),
                    changes=[("system.attributes.movement.walk", 2, -10)], duration={"turns": 1},
                    description="<p>Speed reduced by 10 feet until the end of this turn.</p>")
eff_giftwrap = effect("jb-giftwrap", "Gift-Wrapped", icon("rc-ribbon"), statuses=["restrained"],
                      description="<p>Restrained by red ribbon (escape DC 15).</p>")
JINGLE_BAILIFF = npc(K, "Jingle Bailiff", img=portrait("jingle-bailiff"), token=tok("jingle-bailiff"), size="med",
                     ctype="construct", alignment="Lawful Neutral", cr=5, ac=16, ac_calc="natural", hp=48,
                     hp_formula="8d8 + 12", speed=30, abilities=(20, 12, 14, 8, 12, 6), skills={"prc": 1},
                     di=("poison", "psychic"), ci=("charmed", "exhaustion", "frightened", "poisoned"),
                     senses={"darkvision": 60}, langs=("common", "infernal"),
                     lang_custom="understands but speaks only in announcements",
                     bio=P("A brass-and-tin enforcement automaton shaped like a toy footman, with a bell for a head and "
                           "a fixed painted smile. It speaks only in capital letters."),
                     items=[
                         feat(K + "-command", "Central Command",
                              P("The bailiff obeys the Red Clause's commands. When Writ I — the Presumption of "
                                "Default — is broken, every bailiff is &Reference[stunned] until the end of its next "
                                "turn and thereafter acts on its own last instruction."), img=icon("rc-writ")),
                         feat(K + "-appeal", "Appeal Protocol",
                              P("A bailiff that is handed a properly filed appeal (any written or spoken appeal citing "
                                "Clause V of the Hearthlight certificate) must suspend the collection it is carrying "
                                "out. It may insist on a stamp, a signature or a particular form first; it may not "
                                "refuse outright. The system has merely been hiding the procedure."), img=icon("rc-gavel")),
                         feat(K + "-multi", "Multiattack", P("The bailiff makes two Binding Baton attacks."),
                              img=icon("rc-multi"), activities=[utility(K + "-multi", 0)]),
                         feat(K + "-baton", "Binding Baton",
                              P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                              img=icon("rc-baton"), activities=[attack(K + "-baton", 0, to_hit=8, parts=[dmg(2, 8, 4, ["force"])])]),
                         feat(K + "-wrap", "Gift-Wrap (Recharge 5–6)",
                              P("Red ribbon unwinds from the bailiff's chest. One creature within 10 feet must succeed "
                                "on a [[/save]] saving throw or be &Reference[restrained] (escape DC 15). PLEASE DO NOT "
                                "RESIST YOUR GIFT."),
                              img=icon("rc-ribbon"), uses_=uses(1, [recharge(5)]), effects=[eff_giftwrap],
                              activities=[save(K + "-wrap", 0, ability="dex", dc=15, on_save="none", rng_=rng(10),
                                               tgt=target(1, "creature"), consumption=consume_item_uses(),
                                               effects=[eff_giftwrap["_id"]])]),
                         feat(K + "-citation", "Citation",
                              P("<strong>Reaction</strong> when a creature within 10 feet moves away from the bailiff. "
                                "The creature makes a [[/save]] saving throw or its speed is reduced by 10 feet until "
                                "the end of its turn."),
                              img=icon("rc-citation"), effects=[eff_cite_b],
                              activities=[save(K + "-cite", 0, ability="wis", dc=16, on_save="none", act=REACT(),
                                               rng_=rng(10), tgt=target(1, "creature"), effects=[eff_cite_b["_id"]])]),
                     ])
note("Jingle Bailiff: +8 to hit implies +5 Strength and +3 proficiency, so it is CR 5 with Strength 20; Multiattack and "
     "Gift-Wrap were added so a CR 5 creature hits like one. Psychic immunity added: it has no mind to fine.")

K = "toy-soldier"
TOY_SOLDIER = npc(K, "Festive Toy Soldier", img=portrait("toy-soldier"), token=tok("toy-soldier"), size="sm",
                  ctype="construct", alignment="Unaligned", cr=2, ac=15, ac_calc="natural", hp=25,
                  hp_formula="10d6 - 10", speed=30, abilities=(10, 18, 8, 5, 10, 1),
                  di=("poison", "psychic"), ci=("charmed", "exhaustion", "frightened", "poisoned"),
                  senses={"darkvision": 60}, langs=(), lang_custom="understands Common, can't speak",
                  bio=P("A painted wooden soldier with a tin sabre and a wind-up key in its back. Most were handed out "
                        "as gifts; some were built as enforcement units."),
                  items=[
                      feat(K + "-sabre", "Toy Sabre",
                           P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                           img=icon("rc-sabre"), activities=[attack(K + "-sabre", 0, to_hit=6, parts=[dmg(1, 8, 4, ["slashing"])])]),
                      feat(K + "-package", "Packaged for Delivery",
                           P("As an action the soldier folds into a small gift box, or unfolds from one. While boxed "
                             "it is an object and can be carried in one hand."), img=icon("rc-gift"),
                           activities=[utility(K + "-pack", 0)]),
                      feat(K + "-directive", "Directive",
                           P("A soldier normally follows its assigned owner. The Red Clause can activate an "
                             "enforcement override on any foundation-owned soldier that is not protected by a "
                             "fulfilled gift agreement. A soldier given as one of the Nine Gifts never attacks its "
                             "recipient unless someone independently uses a command override."), img=icon("rc-key")),
                  ])
note("Festive Toy Soldier: CR 2 with Dexterity 18 gives the plan's +6 to hit; damage becomes 1d8 + 4 so it matches the "
     "Dexterity bonus. HP 25 = 10d6 − 10 (brittle painted wood, Constitution 8).")

K = "brass-supervisor"
eff_cheer = effect("bs-cheer", "Compulsory Cheer", icon("rc-collar"), statuses=["charmed"], duration={"rounds": 1},
                   description="<p>Charmed by the supervisor and smiling. You can't attack the supervisor or its "
                               "allies until the end of your next turn.</p>")
BRASS_SUPERVISOR = npc(K, "Brass Supervisor", img=portrait("brass-supervisor"), token=tok("brass-supervisor"),
                       size="lg", ctype="construct", alignment="Lawful Evil", cr=6, ac=17, hp=76, hp_formula="9d10 + 27",
                       speed=30, abilities=(19, 10, 16, 12, 14, 8), saves=("con", "wis"), skills={"inv": 4, "prc": 5},
                       di=("poison", "psychic"), ci=("charmed", "exhaustion", "frightened", "paralyzed", "poisoned"),
                       senses={"darkvision": 60}, langs=("common", "infernal"),
                       bio=P("A tall overseer of riveted brass with a clock face where its chest should be and a ring "
                             "of collar-keys at its belt. It is proud of its numbers."),
                       items=[
                           feat(K + "-quota", "Quota Logic",
                                P("The supervisor cannot ignore a procedural argument. A creature that cites a "
                                  "regulation, quota or clause at it can make a DC 15 Charisma (Persuasion or "
                                  "Deception) check as an action; on a success the supervisor spends its next turn "
                                  "verifying the claim and takes no actions."), img=icon("rc-ledger")),
                           feat(K + "-multi", "Multiattack",
                                P("The supervisor makes two Brass Rod attacks, or one Brass Rod attack and uses Turn "
                                  "the Wheel."), img=icon("rc-multi"), activities=[utility(K + "-multi", 0)]),
                           feat(K + "-rod", "Brass Rod",
                                P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                                img=icon("rc-baton"),
                                activities=[attack(K + "-rod", 0, to_hit=7, reach=10, parts=[dmg(2, 10, 4, ["bludgeoning"])])]),
                           feat(K + "-wheel", "Turn the Wheel",
                                P("The supervisor turns a collar-key at a creature within 10 feet. The target must "
                                  "succeed on a [[/save]] saving throw or be &Reference[charmed] until the end of its "
                                  "next turn, smiling the whole time. A creature wearing a Collar of Compulsory Cheer "
                                  "has disadvantage on the save."),
                                img=icon("rc-collar"), effects=[eff_cheer],
                                activities=[save(K + "-wheel", 0, ability="wis", dc=14, on_save="none", rng_=rng(10),
                                                 tgt=target(1, "creature"), effects=[eff_cheer["_id"]])]),
                           feat(K + "-directive", "Productivity Directive",
                                P("<strong>Bonus Action.</strong> One construct ally the supervisor can see moves up to "
                                  "half its speed."), img=icon("rc-order"), activities=[utility(K + "-dir", 0, act=BONUS())]),
                       ])

K = "yule-engine"
eff_net = effect("ye-net", "Netted", icon("rc-net"), statuses=["restrained"],
                 description="<p>Restrained by a weighted net (DC 15 Strength check or 10 slashing damage to the net, "
                             "AC 10, frees the creature).</p>")
YULE_ENGINE = npc(K, "Yule Enforcement Engine", img=portrait("yule-engine"), token=tok("yule-engine"), size="lg",
                  ctype="construct", alignment="Lawful Neutral", cr=7, ac=17, hp=95, hp_formula="10d10 + 40",
                  speed=20, fly=60, hover=True, abilities=(18, 14, 18, 6, 12, 1), skills={"prc": 4},
                  di=("poison", "psychic"), dr=("fire",), ci=("charmed", "exhaustion", "frightened", "poisoned"),
                  senses={"darkvision": 120}, langs=(), lang_custom="understands Infernal, can't speak",
                  bio=P("A flying enforcement unit: a brass sleigh-hull on spinning gear-wings, with a lantern eye and a "
                        "net cannon. It chases stolen sleighs across the rooftops."),
                  items=[
                      feat(K + "-multi", "Multiattack", P("The engine makes two Chain Lash attacks, or one Chain Lash and "
                                                          "one Net Cannon."), img=icon("rc-multi"),
                           activities=[utility(K + "-multi", 0)]),
                      feat(K + "-lash", "Chain Lash",
                           P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                           img=icon("rc-chain"),
                           activities=[attack(K + "-lash", 0, to_hit=7, reach=10,
                                              parts=[dmg(2, 8, 4, ["slashing"]), dmg(1, 6, "", ["fire"])])]),
                      feat(K + "-net", "Net Cannon (Recharge 5–6)",
                           P("The engine fires a weighted net at a point within 60 feet. Each creature within 5 feet "
                             "of that point must succeed on a [[/save]] saving throw or be &Reference[restrained]."),
                           img=icon("rc-net"), uses_=uses(1, [recharge(5)]), effects=[eff_net],
                           activities=[save(K + "-net", 0, ability="dex", dc=15, on_save="none", rng_=rng(60),
                                            tgt=target("", "creature", "radius", 5), consumption=consume_item_uses(),
                                            effects=[eff_net["_id"]])]),
                  ])

K = "hellforged-reindeer"
HELL_REINDEER = npc(K, "Hellforged Reindeer", img=portrait("hellforged-reindeer"), token=tok("hellforged-reindeer"),
                    size="lg", ctype="fiend", subtype="devil", alignment="Lawful Evil", cr=3, ac=13, hp=68,
                    hp_formula="8d10 + 24", speed=60, fly=90, abilities=(18, 15, 16, 6, 13, 9),
                    di=("fire",), senses={"darkvision": 60}, langs=(), lang_custom="understands Infernal",
                    bio=P("One of the nine nightmare reindeer that pull the Red Clause's sleigh. Ridiculous decorative "
                          "antlers hide flaming eyes."),
                    items=[
                        feat(K + "-illum", "Hellfire Eyes",
                             P("The reindeer sheds bright light in a 10-foot radius and dim light for an additional "
                               "10 feet. It can hide the glow behind its decorative antlers."), img=icon("rc-eye")),
                        feat(K + "-hooves", "Hooves",
                             P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                             img=icon("rc-hoof"),
                             activities=[attack(K + "-hooves", 0, to_hit=6, parts=[dmg(2, 8, 4, ["bludgeoning"]),
                                                                                   dmg(2, 6, "", ["fire"])])]),
                    ])

K = "dash-er"
eff_nog = effect("de-eggnog", "Doused in Eggnog", icon("rc-eggnog"), statuses=["prone"],
                 description="<p>Knocked prone in a wave of enchanted eggnog.</p>")
DASHER = npc(K, "DASH-ER 3000", img=portrait("dash-er"), token=tok("dash-er"), size="lg", ctype="construct",
             alignment="Unaligned", cr=4, ac=15, hp=85, hp_formula="10d10 + 30", speed=60,
             abilities=(19, 14, 16, 3, 10, 1), di=("fire", "poison", "psychic"),
             ci=("charmed", "exhaustion", "frightened", "poisoned"), senses={"darkvision": 60}, langs=(),
             lang_custom="shouts delivery announcements", disposition=0,
             bio=P("A clockwork delivery reindeer with eight legs, two flaming antlers and a malfunctioning navigation "
                   "system. Normally run as a skill challenge, not a fight."),
             items=[
                 feat(K + "-runaway", "Runaway",
                      P("Run DASH-ER as a skill challenge: three successes before two failures at DC 15 (Athletics, "
                        "Acrobatics, Animal Handling, Arcana or creative spellcasting). Success stops it intact; "
                        "failure ends in a harmless explosion of pastries and eggnog. Its manifest names Workshop "
                        "Nine, Nessus Distribution Network."), img=icon("rc-manifest")),
                 feat(K + "-gore", "Flaming Antlers",
                      P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                      img=icon("rc-antler"),
                      activities=[attack(K + "-gore", 0, to_hit=6, parts=[dmg(2, 8, 4, ["piercing"]), dmg(1, 6, "", ["fire"])])]),
                 feat(K + "-nog", "Delivery Attempt (Recharge 5–6)",
                      P("DASH-ER hurls a barrel of enchanted eggnog. Each creature in a 10-foot cube within 30 feet "
                        "must succeed on a [[/save]] saving throw or be knocked &Reference[prone]. "
                        "DELIVERY ATTEMPT FAILED! RECIPIENT NOT AT ADDRESS!"),
                      img=icon("rc-eggnog"), uses_=uses(1, [recharge(5)]), effects=[eff_nog],
                      activities=[save(K + "-nog", 0, ability="dex", dc=13, on_save="none", rng_=rng(30),
                                       tgt=target("", "creature", "cube", 10), consumption=consume_item_uses(),
                                       effects=[eff_nog["_id"]])]),
             ])


def imp(key, name, bio, extra_items, disposition=-1):
    return npc(key, name, img=portrait(key), token=tok(key), size="tiny", ctype="fiend", subtype="devil",
               alignment="Lawful Evil", cr=1, ac=13, ac_calc="natural", hp=10, hp_formula="3d4 + 3", speed=20, fly=40,
               abilities=(6, 17, 13, 11, 12, 14), skills={"dec": 1, "ins": 1, "prf": 1, "ste": 1},
               dr=("cold", "bludgeoning", "piercing", "slashing"), dr_custom="from nonmagical attacks that aren't silvered",
               di=("fire", "poison"), ci=("poisoned",), senses={"darkvision": 120}, langs=("common", "infernal"),
               disposition=disposition, bio=bio,
               items=[
                   feat(key + "-shape", "Shapechanger",
                        P("The imp can use its action to polymorph into a beast form that resembles a rat (speed 20 "
                          "ft.), a raven (20 ft., fly 60 ft.) or a spider (20 ft., climb 20 ft.), or back into its "
                          "true form. Its statistics are the same in each form except for the speed changes noted."),
                        img=icon("rc-mask"), activities=[utility(key + "-shape", 0)]),
                   feat(key + "-sight", "Devil's Sight", P("Magical darkness doesn't impede the imp's darkvision."),
                        img=icon("rc-eye")),
                   feat(key + "-mr", "Magic Resistance",
                        P("The imp has advantage on saving throws against spells and other magical effects."),
                        img=icon("rc-resist")),
                   feat(key + "-sting", "Sting",
                        P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]], and "
                          "the target must make a DC 11 Constitution saving throw, taking 10 (3d6) poison damage on a "
                          "failed save, or half as much on a successful one."),
                        img=icon("rc-sting"),
                        activities=[attack(key + "-sting", 0, to_hit=5, parts=[dmg(1, 4, 3, ["piercing"])]),
                                    save(key + "-poison", 1, ability="con", dc=11, parts=[dmg(3, 6, "", ["poison"])],
                                         name="Venom", rng_=rng(5), tgt=target(1, "creature"))]),
                   feat(key + "-invis", "Invisibility",
                        P("The imp magically turns &Reference[invisible] until it attacks or until its concentration "
                          "ends. Any equipment it wears or carries is invisible with it."),
                        img=icon("rc-invisible"), activities=[utility(key + "-invis", 0)]),
               ] + extra_items)


SPROCKET = imp("sprocket-jingles", "Sprocket Jingles",
               P("Supervisor of the Bureau of Festive Compliance. A bespectacled imp with a tiny brass clipboard.",
                 "<strong>Disposition:</strong> cheerfully officious, utterly terrified of his employer. "
                 "<strong>Voice:</strong> nasal, fast, constantly correcting himself.",
                 "<strong>Public secret:</strong> employees earn a commission for every citizen who accepts a gift. "
                 "<strong>Private secret:</strong> he has falsified his own employee happiness reports for three "
                 "centuries."),
               [feat("sprocket-jingles-fine", "Issue Citation",
                     P("Sprocket writes a fine from the [[/table Festive Compliance Fines]] and waves it about. The fine "
                       "is ridiculous and unenforceable; he cannot confiscate property for refusal. His clipboard bears "
                       "a faint infernal signature (DC 15 Intelligence (Arcana) or Intelligence (Religion))."),
                     img=icon("rc-clipboard"), activities=[utility("sprocket-fine", 0, roll=("1d6", "Fine"))])],
               disposition=0)
MIZZLE = imp("mizzle", "Mizzle",
             P("A frightened imp who manages the shipping manifests at the hidden Delivery Depot.",
               "He will talk if offered protection, a credible escape plan or immunity from ordinary prosecution. "
               "He explains that the workshop is a pocket dimension linked to Waterdeep through magical deliveries, "
               "built to stop workers ever reaching the end of their contractual night. He can provide a "
               "<strong>Service Access Token</strong> and a <strong>Maintenance Schematic</strong>."),
             [], disposition=0)

K = "festive-clerk"
FESTIVE_CLERK = npc(K, "Festive Clerk", img=portrait("festive-clerk"), token=tok("festive-clerk"), size="sm",
                    ctype="fiend", subtype="devil", alignment="Lawful Evil", cr=0.5, ac=13, hp=22, hp_formula="5d6 + 5",
                    speed=30, abilities=(8, 16, 12, 11, 10, 13), skills={"dec": 1, "ste": 1}, dr=("cold",),
                    di=("fire", "poison"), ci=("poisoned",), senses={"darkvision": 120}, langs=("common", "infernal"),
                    bio=P("A small green-clad clerk who looks like a traditional Christmas elf. It is a minor devil "
                          "working under a contractual disguise; the hat hides the horns."),
                    items=[
                        feat(K + "-disguise", "Contractual Disguise",
                             P("The clerk appears to be a cheerful elf. <em>See invisibility</em>, truesight or a "
                               "Hearthlight Candle reveals its true form."), img=icon("rc-mask")),
                        feat(K + "-stamp", "Rubber Stamp of Disapproval",
                             P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]], "
                               "and the target has disadvantage on its next ability check."),
                             img=icon("rc-stamp"),
                             activities=[attack(K + "-stamp", 0, to_hit=5, parts=[dmg(1, 6, 3, ["bludgeoning"]),
                                                                                 dmg(1, 4, "", ["fire"])])]),
                        feat(K + "-flee", "Clock Off", P("<strong>Bonus Action.</strong> The clerk takes the Dash or "
                                                         "Disengage action."), img=icon("rc-relocate"),
                             activities=[utility(K + "-flee", 0, act=BONUS())]),
                    ])

K = "carolling-snowman"
eff_dance = effect("cs-carol", "Carol of Compliance", icon("rc-bell"), duration={"turns": 1},
                   description="<p>You must spend half your movement dancing in place on your next turn.</p>")
SNOWMAN = npc(K, "Carolling Snowman", img=portrait("carolling-snowman"), token=tok("carolling-snowman"), size="med",
              ctype="construct", alignment="Unaligned", cr=1, ac=11, hp=30, hp_formula="5d8 + 8", speed=20,
              abilities=(14, 8, 15, 3, 10, 12), dv=("fire",), di=("cold", "poison", "psychic"),
              ci=("charmed", "exhaustion", "frightened", "poisoned"), senses={"darkvision": 60},
              lang_custom="sings in Common", disposition=0,
              bio=P("An animated snowman in a scarf and top hat, one of a choir that sings about generosity, kindness "
                    "and the timely settlement of outstanding accounts. When the bell sounds, the choir falls silent."),
              items=[
                  feat(K + "-snowball", "Snowball",
                       P("<em>Ranged Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                       img=icon("rc-snowball"),
                       activities=[attack(K + "-ball", 0, to_hit=4, kind="ranged", range_=30, parts=[dmg(1, 6, 2, ["cold"])])]),
                  feat(K + "-carol", "Carol of Compliance",
                       P("The snowman sings at one creature within 30 feet that can hear it. The target must succeed on "
                         "a [[/save]] saving throw or spend half its movement on its next turn dancing in place."),
                       img=icon("rc-bell"), effects=[eff_dance],
                       activities=[save(K + "-carol", 0, ability="wis", dc=12, on_save="none", rng_=rng(30),
                                        tgt=target(1, "creature"), effects=[eff_dance["_id"]])]),
              ])

# ===========================================================================
#  THE COURT: ARBITER, WRITS AND OBJECTS
# ===========================================================================
K = "brass-arbiter"
ARBITER = npc(K, "The Brass Arbiter of Hearthlight", img=portrait("brass-arbiter"), token=tok("brass-arbiter"),
              size="lg", ctype="construct", alignment="Lawful Neutral", cr=10, ac=22, hp=200, hp_formula="16d10 + 112",
              speed=0, abilities=(10, 10, 24, 20, 22, 18), saves=("con", "int", "wis", "cha"), skills={"ins": 2, "inv": 2},
              di=("fire", "cold", "necrotic", "poison", "psychic", "radiant"),
              ci=("blinded", "charmed", "deafened", "frightened", "paralyzed", "petrified", "poisoned", "stunned"),
              senses={"truesight": 120}, langs=("common", "infernal", "celestial"), disposition=0,
              bio=P("The independent arbiter named in Clause VI of every Hearthlight certificate: a brass scale-headed "
                    "judge fused into its lectern. Its ruling binds the foundation and all its appointed agents.",
                    "It is not on anyone's side. It hears evidence, records destruction and announces rulings in a "
                    "voice like a struck bell."),
              items=[
                  feat(K + "-neutral", "Inviolable Neutrality",
                       P("The Arbiter does not fight. A creature that attacks it or targets it with a harmful effect is "
                         "held in contempt (see below). It cannot be moved from its lectern."), img=icon("rc-gavel")),
                  feat(K + "-hear", "Hear Petition",
                       P("A character at the witness lectern can use an action to present an exhibit. Matching, "
                         "authenticated evidence invalidates the Writ it targets automatically. Incomplete evidence "
                         "needs a DC 18 Intelligence (Investigation), Intelligence (Arcana), Intelligence (Religion), "
                         "Wisdom (Insight) or Charisma (Persuasion) check backed by an actual argument; success "
                         "suspends that Writ for one round, and two separate successes invalidate it. Only one "
                         "petition receives a full ruling per round."), img=icon("rc-scales")),
                  feat(K + "-contempt", "Contempt of Court",
                       P("The Arbiter rings its bell at a creature in contempt within 60 feet. The creature must succeed "
                         "on a [[/save]] saving throw or be &Reference[incapacitated] until the end of its next turn."),
                       img=icon("rc-bell"),
                       activities=[save(K + "-contempt", 0, ability="cha", dc=20, on_save="none", rng_=rng(60),
                                        tgt=target(1, "creature"))]),
              ])

WRITS = []
for n, (title, counter, power, broken) in enumerate([
    ("Writ I — The Presumption of Default",
     "Exhibit A: the authenticated original verification records.",
     "The Red Clause can use Default Notice, and the Jingle Bailiffs remain under central command.",
     "Bailiffs are stunned until the end of their next turn, and the Red Clause loses Default Notice."),
    ("Writ II — The Perpetuity of Service",
     "Exhibit C: the clock maintenance schematic or calibration records proving Waterdeep's sunrise has been suppressed.",
     "The Red Clause regains 15 hit points at the start of his turn.",
     "The regeneration ends, and the next advancing bell is delayed by one round."),
    ("Writ III — The Doctrine of Abandoned Souls",
     "Exhibit B (falsified delivery addresses) or Exhibit D (no separate soul-transfer agreement exists).",
     "The Red Clause has two uses of Legendary Resistance.",
     "He loses any unused Legendary Resistance, and the Arbiter warns that the soul transfer lacks legal title."),
], start=1):
    K = f"writ-{n}"
    WRITS.append(npc(K, title, img=portrait(f"writ-{n}"), token=tok(f"writ-{n}"), size="med", ctype="construct",
                     subtype="object", alignment="Lawful Evil", cr=0, ac=17, hp=35, speed=0, hover=True,
                     abilities=(1, 1, 10, 1, 1, 1), di=("poison", "psychic"),
                     ci=("blinded", "charmed", "deafened", "exhaustion", "frightened", "paralyzed", "petrified",
                         "poisoned", "prone", "stunned", "unconscious"),
                     bio=P(f"A hovering infernal writ suspended in a golden frame. One stage of the unlawful collection "
                           f"process, made solid."),
                     items=[
                         feat(K + "-power", "While This Writ Stands", P(power), img=icon("rc-writ")),
                         feat(K + "-counter", "Legal Counter", P(counter + " Present it at the witness lectern."),
                              img=icon("rc-scales")),
                         feat(K + "-broken", "When Broken",
                              P(broken, "Destroying the Writ (0 hit points) suppresses its power, but the Arbiter "
                                        "notes that destruction does not establish the same binding precedent as "
                                        "winning the hearing."), img=icon("rc-broken")),
                     ]))

OBJECTS = []
for key, name, ac, hp, size, text in [
    ("master-ledger", "The Master Ledger", 17, 40, "lg",
     "An immense book chained above the central furnace. Destroying it, stamping an emergency cancellation with the "
     "Infernal Signet, or a final ruling from the Arbiter stops the harvest."),
    ("midnight-engine", "The Midnight Engine", 17, 45, "huge",
     "The great clock frozen at 11:59 p.m., with an artificial sun trapped in a glass sphere above it. Smash it, "
     "reverse the gears (DC 17 Arcana or tinker's tools), free the sun (magic or DC 18 Athletics), or use Mizzle's "
     "schematic for automatic success."),
    ("intake-lock", "Intake Department Lock", 17, 30, "med",
     "The locking mechanism on the restricted door beyond the Intake Department. Two DC 16 Arcana or Investigation "
     "successes override it; a failure sounds an alarm."),
    ("sack-seam", "Sack of Repossession (Seam)", 15, 25, "med",
     "The inner seam or external clasp of the Red Clause's sack. Breaking it frees a trapped creature."),
]:
    OBJECTS.append(npc(key, name, img=portrait(key), token=tok(key), size=size, ctype="construct", subtype="object",
                       alignment="Unaligned", cr=0, ac=ac, hp=hp, speed=0, abilities=(1, 1, 10, 1, 1, 1),
                       di=("poison", "psychic"),
                       ci=("blinded", "charmed", "deafened", "exhaustion", "frightened", "paralyzed", "petrified",
                           "poisoned", "prone", "stunned", "unconscious"), disposition=0, bio=P(text),
                       items=[feat(key + "-obj", "Object", P(text), img=icon("rc-gear"))]))

# ===========================================================================
#  PEOPLE OF WATERDEEP (friendly / neutral)
# ===========================================================================


def commoner(key, name, bio, *, size="med", ctype="humanoid", subtype="", alignment="Neutral Good", hp=4, ac=10,
             abilities=(10, 10, 10, 10, 10, 10), skills=None, extra=(), langs=("common",), disposition=1, cr=0,
             senses=None):
    return npc(key, name, img=portrait(key), token=tok(key), size=size, ctype=ctype, subtype=subtype,
               alignment=alignment, cr=cr, ac=ac, ac_calc="flat" if ac != 10 else "default", hp=hp, speed=30 if size != "sm" else 25,
               abilities=abilities, skills=skills, langs=langs, disposition=disposition, bio=bio, senses=senses,
               items=list(extra) or [feat(key + "-club", "Club",
                                          P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                                          img=icon("rc-baton"),
                                          activities=[attack(key + "-club", 0, to_hit=2, parts=[dmg(1, 4, "", ["bludgeoning"])])])])


EDDA = commoner("edda-hearth", "Edda Hearth",
                P("An elderly halfling baker who has spent Midwinter Day giving free bread to people struggling through "
                  "winter. Warm, generous and entirely unremarkable.",
                  "She accepted an Everwarm Scarf and gave a loaf to a grieving widow in front of witnesses. Her "
                  "kindness was recorded as FULFILLED, then overwritten to DEFAULT by a central audit because the "
                  "widow was still unhappy."),
                size="sm", subtype="halfling", abilities=(8, 12, 10, 11, 14, 13), skills={"ins": 1})
MARTA = npc("marta-quill", "Sergeant Marta Quill", img=portrait("marta-quill"), token=tok("marta-quill"), size="med",
            ctype="humanoid", subtype="human", alignment="Lawful Neutral", cr=3, ac=17, ac_calc="flat", hp=58,
            hp_formula="9d8 + 18", speed=30, abilities=(16, 13, 14, 10, 11, 10), skills={"ath": 1, "prc": 1, "itm": 1},
            langs=("common", "dwarvish"), disposition=1,
            bio=P("A veteran sergeant of the City Watch overseeing festival safety. Tired, efficient and deeply irritated "
                  "by magically binding bureaucracy.",
                  "\"First somebody turns the city's gutters into peppermint, and now we've got arrest warrants from "
                  "Hell. I should've taken that bloody promotion.\"",
                  "She can deputise the party to investigate on the Watch's behalf, giving them standing to challenge "
                  "the contracts even if none of them accepted a gift. Her request: <em>\"Find the people they've "
                  "taken. Bring them home.\"</em>"),
            items=[feat("marta-multi", "Multiattack", P("Marta makes two longsword attacks. If she has a shortsword "
                                                        "drawn, she can also make a shortsword attack."),
                        img=icon("rc-multi"), activities=[utility("marta-multi", 0)]),
                   feat("marta-longsword", "Longsword",
                        P("<em>Melee Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                        img=icon("rc-sabre"), activities=[attack("marta-ls", 0, to_hit=5, parts=[dmg(1, 8, 3, ["slashing"])])]),
                   feat("marta-crossbow", "Heavy Crossbow",
                        P("<em>Ranged Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                        img=icon("rc-crossbow"),
                        activities=[attack("marta-xb", 0, to_hit=3, kind="ranged", range_=100, parts=[dmg(1, 10, 1, ["piercing"])])]),
                   feat("marta-deputise", "Deputise",
                        P("Marta grants the party temporary authority to investigate on behalf of the City Watch. "
                          "This gives them standing before the Brass Arbiter."), img=icon("rc-badge"))])
TILDA = commoner("tilda-marr", "Tilda Marr",
                 P("An adult elven artisan on the Assembly Line of Eternal Gratitude. She accepted a gift to feed her "
                   "neighbours, genuinely failed to complete her kindness in time, and owed a single night of service.",
                   "That was ninety-three years ago, by her own experience. It is still Midwinter night in the "
                   "workshop.",
                   "\"One night. He said one night.\" \"Please. Do you know if the sun is still there?\""),
                 subtype="elf", abilities=(9, 14, 10, 13, 12, 11), skills={"inv": 1}, senses={"darkvision": 60},
                 langs=("common", "elvish"))
AGNA = commoner("agna-vell", "Agna Vell (Citizen 771)",
                P("The grieving widow who received Edda's bread. Her husband died the day before Midwinter. The "
                  "foundation's records list her only as <em>Bereaved Citizen 771</em>. She will testify that Edda's "
                  "kindness was real."), subtype="human", abilities=(9, 10, 10, 10, 12, 10))
PELL = commoner("ossian-pell", "Ossian Pell",
                P("A fussy clerk at the Font of Knowledge, Oghma's temple, who keeps a copy of the city's residence "
                  "rolls. He discovers that every seized recipient's address was changed to somewhere in Nessus "
                  "immediately before the notices went out."),
                subtype="human", abilities=(9, 10, 10, 15, 13, 11), skills={"his": 1, "inv": 1}, langs=("common", "elvish"))
HARL = commoner("harl-bramble", "Old Harl Bramble",
                P("An eggnog merchant whose pastry stall is flattened by DASH-ER 3000, which then tries to deliver "
                  "sixteen barrels of enchanted eggnog to him. He would like everyone to stop doing that."),
                subtype="human", abilities=(11, 9, 12, 10, 11, 12))
GHOST = npc("midwinter-ghost", "The Ghost of Midwinters Past", img=portrait("midwinter-ghost"),
            token=tok("midwinter-ghost"), size="med", ctype="undead", alignment="Neutral Good", cr=4, ac=11, hp=45,
            hp_formula="10d8", speed=0, fly=40, hover=True, abilities=(7, 13, 10, 10, 16, 17),
            dr=("acid", "fire", "lightning", "thunder", "bludgeoning", "piercing", "slashing"),
            dr_custom="from nonmagical attacks", di=("cold", "necrotic", "poison"),
            ci=("charmed", "exhaustion", "frightened", "grappled", "paralyzed", "petrified", "poisoned", "prone",
                "restrained"), senses={"darkvision": 60}, langs=("common",), disposition=1,
            bio=P("A callback to last year's Christmas Carol one-shot: a familiar spectral visitor in a candle-crowned "
                  "hood. It appears briefly during the investigation.",
                  "\"Last year, you showed a man what became of a life without generosity. This year, something has "
                  "learned to put a price upon it.\""),
            items=[feat("ghost-incorp", "Incorporeal Movement",
                        P("The ghost can move through other creatures and objects as if they were difficult terrain."),
                        img=icon("rc-ghost")),
                   feat("ghost-vision", "Glimpse of Midwinters Past",
                        P("The ghost shows one creature a vision of a Midwinter long gone. The creature regains "
                          "[[/heal 2d8 + 3]] hit points and learns one true fact about the foundation of the DM's "
                          "choice."), img=icon("rc-candle"),
                        activities=[heal_act("ghost-heal", 0, formula_part=dmg(2, 8, 3), rng_=rng(30),
                                             tgt=target(1, "creature"))])])
WATCH = npc("watch-constable", "City Watch Constable", img=portrait("watch-constable"), token=tok("watch-constable"),
            size="med", ctype="humanoid", subtype="human", alignment="Lawful Neutral", cr=0.125, ac=16, ac_calc="flat",
            hp=11, hp_formula="2d8 + 2", abilities=(13, 12, 12, 10, 11, 10), skills={"prc": 1}, langs=("common",),
            disposition=1, bio=P("A member of the Waterdeep City Watch in green-and-gold livery, freezing at a festival post."),
            items=[feat("watch-spear", "Spear",
                        P("<em>Melee or Ranged Weapon Attack:</em> [[/attack extended]]. <em>Hit:</em> [[/damage extended]]."),
                        img=icon("rc-spear"), activities=[attack("watch-spear", 0, to_hit=3, parts=[dmg(1, 6, 1, ["piercing"])])])])
CITIZEN = commoner("waterdeep-citizen", "Waterdhavian Gift Recipient",
                   P("An ordinary citizen of Waterdeep clutching an enchanted gift and a Certificate of Festive "
                     "Entitlement."), subtype="human", disposition=0)
WORKER = commoner("collared-worker", "Collared Worker",
                  P("A former gift recipient working the endless night of the Workshop of Good Intentions. An "
                    "enchanted collar keeps the smile in place. Removing or dispelling the collar (DC 13) lets the "
                    "worker speak freely."), subtype="any race", disposition=0)

FOLDERS = {
    "Nicholas Red Clause": [RED_CLAUSE],
    "Festive Enforcement": [JINGLE_BAILIFF, TOY_SOLDIER, BRASS_SUPERVISOR, YULE_ENGINE, FESTIVE_CLERK],
    "Sleigh & Workshop Beasts": [HELL_REINDEER, DASHER, SNOWMAN],
    "Imps of the Foundation": [SPROCKET, MIZZLE],
    "The High Court": [ARBITER] + WRITS,
    "Objects & Machinery": OBJECTS,
    "People of Waterdeep": [EDDA, MARTA, AGNA, PELL, HARL, WATCH, CITIZEN, GHOST],
    "Workshop Captives": [TILDA, WORKER],
}
