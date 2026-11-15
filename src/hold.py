"""Kharad-Varr: the Hold — taverns, baths, a gaming house, a smith, an enchanter, an apothecary and the
rune smiths, each with a self-contained side quest rooted in the dwarven settlement and with side notes
into the main story. Plus a painted overview scene that pins every place (venue pages and district
pages; district pages link every map).

Module law still holds: side quests never replace an essential revelation, never hand out a track
change that a keyed scene already gives, and never make the Dark Powers the cause of the war.
Hold side quests can raise Defence by at most +2 and Accord by at most +2 across the whole arc.
"""
from lib5e import *
import bestiary as BE
from bestiary import B, creature, bio, BONUS, REACT, ACT, per_day
import items_spells as IS
import misc as MI

FOLDER = "The Hold of Kharad-Varr"
DW, OR = BE.DW, BE.OR
GOB = ("common", "goblin", "dwarvish")

# ============================================================================ the Hold's people
def _cast():
    creature(FOLDER, "grimma", "Grimma Tapwell, Keeper of the Low Lantern", cr=0.5, ac=11, hp=27, abilities=(14, 10, 14, 10, 13, 14),
             langs=DW, disposition=1, skills={"ins": 1, "prf": 1},
             b=B("grimma").attack("Bung Mallet", 4, "1d6+2", "bludgeoning", ic="ab-hammer")
             .feature("Last Orders", "Bonus Action. Grimma bangs the bar; every Lowhearth patron who can hear her stops fighting and listens for one round unless attacked.", ic="ab-kitchen", act=BONUS())
             .feature("Lowhearth Ears", "If it was said in Lowhearth last night, Grimma has heard a version of it. She shares freely with people she trusts and never with officers.", ic="ab-lantern"),
             bio=bio("Widowed tavern keeper of the Low Lantern, Lowhearth's only public house with a hearth big enough to sleep beside. Loud, generous, keeps the message slate behind the bar.",
                     "Her brother Hollin's name back in the register. Hollin was struck off as a deserter six months ago. She does not believe it and cannot prove otherwise.",
                     "If you're drinking, sit. If you're grieving, sit closer to the fire."))
    creature(FOLDER, "old-dagny", "Old Dagny Songkeeper", cr=0, ac=10, hp=9, abilities=(8, 10, 10, 12, 15, 14), langs=DW, disposition=1,
             skills={"prf": 2, "his": 1},
             b=B("old-dagny").feature("Song-Keeper", "Dagny knows every shift-song of Lowhearth, including the verses nobody sings any more. Singing with her grants advantage on Performance checks to move a Lowhearth crowd.", ic="ab-rally"),
             bio=bio("Lowhearth's song-keeper; once a pump-hand, now too stiff for the galleries. Leads Song Night at the Low Lantern.",
                     "To sing the whole of 'Down the Ninth' once more without anyone being arrested for it.",
                     "The song has seven verses. We've been singing six. Ask yourself who taught us to stop."))
    creature(FOLDER, "sorvald", "Sorvald Brightmantle, Host of the Gilded Nail", cr=0.25, ac=15, hp=22, abilities=(11, 12, 11, 12, 14, 16),
             langs=DW, disposition=0, skills={"per": 2, "ins": 1},
             b=B("sorvald").attack("Ceremonial Dagger", 3, "1d4+1", "piercing", ic="ab-blade")
             .feature("Rules of the House", "Sorvald can call a Hammer-Moot to order. Officers who break moot rules in his house lose face with every officer present.", ic="ab-command"),
             bio=bio("Retired quartermaster who runs the officers' tavern on the Crown Market. Status-proud, scrupulous about rules, quietly decent.",
                     "His house kept clean of politics. It hasn't been clean for months.",
                     "In this house rank buys the table, not the argument."))
    creature(FOLDER, "eirik", "Lieutenant Eirik Hammerline", cr=3, ac=18, hp=58, abilities=(17, 12, 15, 10, 11, 13),
             saves=("str", "con"), skills={"ath": 1, "itm": 1}, langs=DW, disposition=0,
             b=B("eirik").multi("Eirik makes two Warhammer attacks.")
             .attack("Warhammer", 5, "1d8+3", "bludgeoning", ic="ab-hammer")
             .feature("Moot Discipline", "In a Hammer-Moot, Eirik fights to the yield. He stops the instant his opponent yields or is bloodied, and expects the same.", ic="ab-shield")
             .feature("In Debt", "Eirik owes 340 gp in Turning Gear markers. Somebody has been buying them.", ic="ab-ledger"),
             bio=bio("A young Righteous Vanguard lieutenant, brave, sharp-tongued and badly overextended at the gaming tables.",
                     "To be seen as a real officer. Hadrik's office bought his markers and asked for a favour: shame the metal man before the Public Roll.",
                     "An Ironfist name is carried in blood. Show me yours."))
    creature(FOLDER, "fenn", "Fenn Coalsong, Bathmaster", cr=0.5, ac=12, hp=33, abilities=(13, 11, 15, 14, 12, 11), langs=DW, disposition=1,
             skills={"inv": 1, "med": 1},
             b=B("fenn").attack("Valve Wrench", 3, "1d6+1", "bludgeoning", ic="ab-tools")
             .feature("Heat Log", "Fenn has logged the Ember Basin's temperature at every change of shift for nineteen years.", ic="ab-gauge"),
             bio=bio("Old heat-engineer who keeps the Ember Baths on the Steamstair. Half deaf from forty years of pipes. Kind to everyone who is cold.",
                     "His water hot again, and somebody to admit why it went cold.",
                     "Heat doesn't vanish. It goes somewhere. Ask where."))
    creature(FOLDER, "pip", "Pip Ashwick (goblin child)", cr=0, ac=12, hp=3, abilities=(6, 15, 10, 10, 12, 9), ctype="humanoid", subtype="goblin",
             size="sm", speed=30, langs=("goblin",), disposition=1, skills={"ste": 2},
             b=B("pip").feature("Small and Quick", "Bonus Action. Pip takes the Disengage or Hide action.", ic="ab-slip", act=BONUS()),
             bio=bio("A Cinder-Tusk child of nine who came up the drains looking for warm water for her grandmother's well-sickness.",
                     "Her grandmother warm; to go home without being caught.",
                     "The pipes are warm. Ours went cold. I only took a little."))
    creature(FOLDER, "scald-mephit", "Scald Mephit", cr=0.5, ac=10, hp=21, abilities=(5, 11, 10, 11, 10, 12), ctype="elemental", subtype="",
             size="sm", speed=30, langs=("aquan", "ignan"), disposition=-1, di=("fire", "poison"), ci=("poisoned",),
             b=B("scald-mephit").attack("Claws", 2, "1d4", "slashing", extra=("1d4", "fire"), ic="ab-vent")
             .save("Steam Breath", "dex", 10, "Recharge 6. 15-foot cone. 1d8 fire damage on a failed DC 10 Dexterity save, half on a success; a creature that fails also has its speed reduced by 10 feet until the end of its next turn.",
                   dice="1d8", dtype="fire", ic="ab-burst", uses_=uses(1, [recharge(6)]), consumption=consume_item_uses(), tgt=target("", "creature", "cone", 15))
             .feature("Death Burst", "When it dies it bursts into scalding steam: each creature within 5 feet makes a DC 10 Dexterity save or takes 1d4 fire damage.", ic="ab-burst")
             .feature("Drawn by Backed-Up Heat", "These steam-imps gather where pressure backs up. They are a symptom of the diversion, not an enemy plan.", ic="ab-gauge"),
             bio=bio("Steam elementals nesting in the Ember Baths' pipe crawl.", "Heat, noise, and something to scald.", "—"))
    creature(FOLDER, "iskra", "Madame Iskra Goldvein", cr=2, ac=15, hp=45, abilities=(10, 16, 12, 15, 16, 17),
             saves=("dex", "wis"), skills={"ins": 2, "dec": 1, "slt": 1}, langs=DW + ("orc",), disposition=0,
             b=B("iskra").multi("Iskra makes two Cane-Blade attacks.")
             .attack("Cane-Blade", 5, "1d6+3", "piercing", ic="ab-blade")
             .feature("House Odds", "Iskra's passive Insight is 18 at her own tables. She can, as a reaction, reroll one die in any game she deals.", ic="ab-ledger", act=REACT())
             .feature("Cunning Action", "Bonus Action. Dash, Disengage or Hide.", ic="ab-slip", act=BONUS()),
             bio=bio("Owner of the Turning Gear, the Crown Market's gaming house. Pragmatic, charming, never cheats a guest who isn't cheating her.",
                     "Her house to survive the war. She knows her officers pay their markers in foundry requisition chits and that when the emergency powers come, houses like hers are the first requisitioned.",
                     "Everyone stakes something, darling. Most people simply don't read the marker."))
    creature(FOLDER, "brannoc", "Master Brannoc Anvilsong", cr=2, ac=16, hp=60, abilities=(18, 10, 16, 11, 12, 10),
             saves=("str", "con"), skills={"ath": 1}, langs=DW, disposition=1,
             b=B("brannoc").multi("Brannoc makes two Forge Hammer attacks.")
             .attack("Forge Hammer", 6, "1d10+4", "bludgeoning", ic="ab-hammer")
             .feature("Master Smith", "Advantage on checks with smith's tools. Repairs a damaged weapon or shield in an hour.", ic="ab-tools"),
             bio=bio("Third-generation master of Anvilsong Forge on Forge Row, now under military quota. Soot to the elbows; speaks in short sentences.",
                     "To finish the commission he actually believes in: a safety gate for Lowhearth's lifts, halted when the ironbone was reserved for 'Bastion works'.",
                     "Quotas make plates. Smiths make things that keep people alive."))
    creature(FOLDER, "sigrun", "Sigrun Lampwright, Enchanter of Glimmerhall", cr=3, ac=12, hp=40, abilities=(9, 14, 12, 17, 14, 12),
             saves=("int", "wis"), skills={"arc": 2, "inv": 1}, langs=DW + ("draconic",), disposition=1,
             b=B("sigrun").attack("Lamp-Bolt", 5, "2d8+3", "radiant", range_="60", kind="ranged", ic="ab-lantern")
             .feature("Ward Lantern", "Action. Sigrun unshutters a ward lantern: until the end of her next turn, creatures of her choice in its 20-foot light gain +2 AC.", ic="ab-shield", act=ACT(), uses_=per_day(2), consumption=consume_item_uses())
             .feature("Consent First", "Sigrun never examines a person's enchantments without asking, and stops the moment they say stop.", ic="ab-will"),
             bio=bio("Enchanter and ward-maker on the Crown Market; makes the testimony lamps used in Stone Council hearings.",
                     "Her lamp quiet and its secrets returned to the people they belong to.",
                     "Light remembers. That used to be a comfort."))
    creature(FOLDER, "bera", "Bera 'Mother Moss' Mossbeard", cr=0.5, ac=11, hp=30, abilities=(10, 10, 14, 14, 16, 13), langs=DW + ("goblin",),
             disposition=1, skills={"med": 2, "nat": 1},
             b=B("bera").attack("Walking Stick", 2, "1d6", "bludgeoning", ic="ab-medic")
             .feature("Mother Moss's Poultice", "Action. One creature she touches regains 2d4 + 2 hit points.", ic="ab-heal", act=ACT(), heal="2d4+2", uses_=per_day(3), consumption=consume_item_uses()),
             bio=bio("Lowhearth's apothecary for thirty years, partner of the goblin herbalist Tikka Fernspit. Doses everyone, dwarf or goblin, at the same price.",
                     "The bitter cough cured, and Tikka safe from the people who need a goblin to blame.",
                     "Medicine has no clan, dearie. Sit down and cough for me."))
    creature(FOLDER, "tikka", "Tikka Fernspit", cr=0.25, ac=13, hp=14, abilities=(8, 15, 11, 13, 14, 9), ctype="humanoid", subtype="goblin",
             size="sm", speed=30, langs=GOB, disposition=1, skills={"nat": 2, "ste": 1},
             b=B("tikka").attack("Fungus Knife", 4, "1d4+2", "slashing", ic="ab-blade")
             .feature("Spore Pouch", "Action, once per day. A 10-foot puff of sleep-spores: creatures in it make a DC 12 Constitution save or are poisoned until the end of their next turn.", ic="ab-vent", act=ACT(), uses_=per_day(1), consumption=consume_item_uses()),
             bio=bio("Cinder-Tusk exile who has grown fungus beds in Lowhearth for twenty years. Bera's partner in business and in argument.",
                     "To prove her beds didn't make anybody sick; to get home once to see whether her sister's beds survived.",
                     "Mushrooms don't lie. They just die where the water's wrong."))
    creature(FOLDER, "kharn", "Old Kharn the Deepscribe", cr=4, ac=14, hp=66, abilities=(10, 11, 14, 18, 17, 12),
             saves=("int", "wis"), skills={"arc": 2, "his": 2}, langs=DW + ("giant", "primordial"), disposition=1,
             b=B("kharn").attack("Rune Staff", 3, "1d6", "bludgeoning", ic="ab-scroll")
             .attack("Spoken Rune", 7, "3d8+4", "thunder", range_="60", kind="ranged", ic="ab-burst")
             .feature("Read the Hand", "Kharn can authenticate a dwarven runic seal or inscription in ten minutes. A forgery shows him the forger's hand.", ic="ab-scroll"),
             bio=bio("Master of the Hall of Deep Script, the rune smiths' guild. Older than two of the three generals combined.",
                     "His guild's work used for keeping people alive, not for the reversal plates Hadrik's engineers made his apprentices cut.",
                     "A rune is a promise in stone. Be careful who you let make promises for you."))
    creature(FOLDER, "rune-warden", "The Rune Warden of the Deep Script", cr=6, ac=18, hp=110, ctype="construct", subtype="", size="lg",
             speed=25, abilities=(20, 9, 18, 6, 12, 1), saves=("con", "wis"), langs=(), lang_custom="understands Dwarvish", disposition=0,
             di=("poison", "psychic"), ci=("charmed", "exhaustion", "frightened", "paralyzed", "petrified", "poisoned"), senses={"darkvision": 60},
             b=B("rune-warden").multi("The Warden makes two Slam attacks.")
             .attack("Slam", 8, "2d8+5", "bludgeoning", ic="ab-construct")
             .save("Rune Glare", "wis", 15, "Recharge 5–6. One creature it can see within 30 feet: DC 15 Wisdom save or it must speak aloud the true name of the thing it fears to lose, and is stunned until the end of its next turn.",
                   ic="ab-will", uses_=uses(1, [recharge(5)]), consumption=consume_item_uses(), tgt=target(1, "creature"))
             .feature("A Test, Not a Killing", "The Warden fights to the yield. When reduced to half its hit points, or when a candidate speaks the rune of the trial correctly, it kneels. It never strikes a creature that is unconscious or has yielded.", ic="ab-shield"),
             bio=bio("Guild guardian animated to test candidates in the Trial of the Three Rings.", "To test; to keep the roll honest.", "—"))
    new = [a for a in BE.FOLDERS[FOLDER]]
    BE.ACTORS.extend(new)


_cast()

# ============================================================================ items
def box(*ps): return IS.box(IS.P(*ps))


ITEMS = [
    # key, name, type, icon, price, rarity, desc paragraphs, extra
    ("hold-deepcap-stout", "Cask of Deepcap Stout", "consumable", "it-ration", 15, "",
     ["The Low Lantern's famous black stout, brewed from the Deepcap spring two galleries below Lowhearth. The spring has run thin since the diversion, so this may be the last cask.",
      "A cask serves a hall. Bring it to a gathering and every Lowhearth worker present will hear the party out (no roll to secure a hearing)."], {"subtype": "food"}),
    ("hold-missing-verse", "The Missing Verse", "loot", "it-register", 0, "",
     ["The seventh verse of the shift-song <em>Down the Ninth</em>, naming Hollin Tapwell, Ysolde Rookbarrow, Aldo Cinderhand and Feyra Brassnail: the Seventh Cut crew, struck from the register as deserters.",
      "Once, before a public hearing or the Public Roll (5.2), a character who sings or reads it to Lowhearth witnesses gains advantage on one check to persuade a frightened witness to speak in public.",
      "It is a song, not evidence. Paired with the register entries it becomes corroboration that the diversion works began before the first raid (R1)."], None),
    ("hold-eirik-oathmark", "Eirik's Oathmark", "loot", "it-badge", 0, "",
     ["A bronze moot-token stamped with Eirik Hammerline's mark. He owes the bearer one act of lawful service.",
      "During Chapter 7 his squad can hold one unassigned front as if Defence Readiness were 2 higher for that front only. It does not change the track. Or, at any hearing, he testifies that Hadrik's office bought officers' gaming debts."], None),
    ("hold-ember-token", "Ember Baths Token", "consumable", "it-gauge", 5, "",
     ["A brass bath-token from the Steamstair, good for one long soak in the Ember Basin (once the heat is back).",
      "An hour in the Basin grants the benefits of a short rest; once per day the soak also removes one level of exhaustion."], {"subtype": "trinket", "uses": 3}),
    ("hold-heat-log", "Fenn's Heat Log", "loot", "it-manual", 0, "",
     ["Nineteen years of Ember Basin temperatures, one line per shift. Six months ago the readings fall every day for a fortnight, and they have stayed down since.",
      "Corroboration for R1: the heat left the Steamstair on the same dates the gauge record (E1) shows the diversion opening. With Runa's diagrams it removes any claim that the cooling followed the raids."], None),
    ("hold-lucky-rivet", "Iskra's Lucky Rivet", "trinket", "it-rivet", 0, "uncommon",
     ["<em>Wondrous item, uncommon.</em> A gilded rivet that once held the Turning Gear's wheel together.",
      "Once per long rest, after you roll a d20 for an ability check, you can roll a d4 and add it to the result. If you carry a Blood-Debt of the First Thirst, the rivet does nothing for you: you already owe."], None),
    ("hold-marker-ledger", "Iskra's Marker Ledger (copy)", "loot", "it-orders", 0, "",
     ["A fair copy of the Turning Gear's book of officers' markers. Since the diversion, eleven officers have settled their debts in foundry requisition chits, redeemable at the military foundries at face value.",
      "Corroboration for E2. If the party does not yet hold E2, this ledger together with Anvilsong Forge's quota book authenticates as E2 (one of its three routes). Either alone is supporting evidence only. Iskra will swear to it only if her house is protected from requisition."], None),
    ("hold-ration-book", "The Rookbarrow Ration Book", "loot", "it-ration", 0, "",
     ["A Lowhearth household's ration book, pawned for a gambling debt by Edvin Rookbarrow, whose wife Ysolde was struck from the register as a 'deserter'. Without it a family of five draws no food. If Ysolde's name is restored (The Missing Verse), her widow's share is restored with it."], None),
    ("hold-anvilsong-gate", "The Anvilsong Lift Gate", "loot", "it-key", 0, "",
     ["An ironbone safety gate for Lowhearth's great lifts, forged at Anvilsong Forge.",
      "Installed before Session 10, it holds: the first time the <em>The Lift Jams</em> siege dispatch is drawn in Chapter 7, it is resolved without loss."], None),
    ("hold-quota-book", "Anvilsong Quota Book", "loot", "it-orders", 0, "",
     ["Brannoc's copy of Forge Row's military quotas. It lists ironbone pressure plates 'for regulator modification, Heartworks' alongside foundry payments rising through the shortages.",
      "Corroboration for E2 (with Iskra's Marker Ledger it authenticates as E2) and a pointer toward R3: the plates are the ones later found installed in the Heartworks."], None),
    ("hold-hush-lantern", "Hush-Ward Lantern", "wondrous", "it-lantern", 0, "uncommon",
     ["<em>Wondrous item, uncommon.</em> A shuttered lantern made from the quiet half of Sigrun's testimony lamp.",
      "Once per long rest, unshutter it for up to 10 minutes. Nothing said inside its 20-foot light can be heard from outside it, or perceived by divination or by the senses of any Dark Power. Ideal for protecting a witness."], None),
    ("hold-lamp-fragment", "The Lamp's Council Fragment", "loot", "it-lantern", 0, "",
     ["A few sentences the testimony lamp kept from a closed council session: a voice like Hadrik's calls Lowhearth 'an acceptable loss of position' and asks whether the plates are 'cut yet'.",
      "Not proof on its own. A lamp is an object, and its testimony must be authenticated (Sigrun's oath plus Kharn's reading of the lamp's runes). Authenticated and paired with Runa's bypass calculations, it supports R3."], None),
    ("hold-glowcap-tincture", "Glowcap Tincture", "consumable", "it-mushroom", 50, "uncommon",
     ["A green, faintly glowing tincture brewed by Bera and Tikka from Cinder-Tusk glowcap.",
      "Cures the bitter cough and any disease caused by spores or foul water, and the drinker regains 2d4 + 2 hit points."], {"subtype": "potion", "uses": 3}),
    ("hold-spore-sample", "Tikka's Spore Sample", "loot", "it-mushroom", 0, "",
     ["Dead spores from Lowhearth's drains, matched under Tikka's lens to the poisoned Cinder-Tusk beds downstream.",
      "Counts as the 'dead fungal samples' route to R1 if the sluice samples are lost or destroyed."], None),
    ("hold-maker-mark", "Maker's Mark of the Deep Script", "loot", "rune-mor", 0, "",
     ["An entry in the guild roll of the Hall of Deep Script: a maker's mark in the bearer's own hand.",
      "It means the guild counts its bearer as a maker, not a made thing. It confers guild rights (Cut-grade runes forged at the Hall at no material cost, once per chapter) and nothing else. Nobody can take it except the bearer."], None),
    ("hold-reversal-key", "Orla's Reversal Key", "loot", "it-key", 0, "",
     ["A wax rubbing of the reversal runes Kharn's apprentice was ordered to cut for the Heartworks plates, with her note of which stroke inverts which.",
      "At 8.3, the first regulator station worked by someone holding this key starts with 1 progress. Shared with Runa and Skrik before Session 11: +1 Defence (once; counts toward the Hold cap)."], None),
]
for key, name, itype, ic, price, rar, ps, extra in ITEMS:
    sub = (extra or {}).get("subtype", "")
    use = uses((extra or {}).get("uses"), []) if (extra or {}).get("uses") else None
    real_type = {"trinket": "equipment", "wondrous": "equipment"}.get(itype, itype)
    IS.add(FOLDER, item(key, name, real_type, box(*ps), img=icon(ic), price=price, rarity=rar,
                        subtype=sub or ("trinket" if itype in ("trinket", "wondrous") else ""), uses_=use, flags={MOD: {"key": key}}))

# ============================================================================ roll tables & macros
T = "The Hold of Kharad-Varr"
MI.table("hold-rumours", "Hold Rumours", [
    "'The Low Lantern stopped singing the seventh verse. Grimma's brother is in it.' (The Missing Verse)",
    "'The officers have a moot on at the Gilded Nail. Somebody wants to measure the metal Ironfist.' (A Name Above Its Station)",
    "'The Ember Baths are cold as a cellar and Fenn's cursing the pipes. Something hisses in the crawl.' (Cold Water)",
    "'Iskra at the Turning Gear takes ration books as stakes now. Nobody wins them back.' (The House Always Requisitions)",
    "'Brannoc's been told his forge makes plates now. Plates for what, nobody says.' (The Last Commission)",
    "'A lamp on the Crown Market whispers at night. My neighbour heard her own secret in it.' (The Lamp That Remembers)",
    "'The bitter cough's in every family on Lift Street. Some say Tikka's mushrooms did it.' (The Bitter Cough)",
    "'Old Kharn wants to meet the Ironfist made of metal. Wants to see his runes, he says. Asks first, mind.' (A Rune Nobody Taught)",
    "'Six months back the baths went cold, the stout went thin and the Seventh Cut crew deserted. All in the same fortnight.' (true; R1)",
    "'The orcs poisoned the wells first.' (false; the wells failed after the diversion, see E1)",
    "'There's a goblin child in the drains stealing hot water.' (true; Pip, Cold Water)",
    "'Hadrik's office pays officers' debts. Cheaper than paying their wages.' (true; Gilded Nail and Turning Gear)",
    "'The new plates for the Heartworks are thick as a door.' (true; R3 pointer)",
    "'The metal Ironfist can be switched off by a general's order.' (false; nobody can)",
    "'Brynja's standing orders let any household hold a vigil, rank or no rank.' (true; useful at Hearthwatch)",
    "'Mother Moss treats goblins at the same price as dwarves. Somebody painted her door.' (true)",
], "One rumour per visit to a venue, or roll when the party spends a watch in the Hold. Rumours marked true point to real leads; false ones are what Lowhearth fears.", "tb-dice", T)
MI.table("hold-low-lantern", "Who's at the Low Lantern Tonight", [
    "Old Dagny tuning a battered lap-harp; she nods at Thorgrinn as if she'd been expecting him.",
    "Tovik Deepgauge's crew, still in their sluice-mud, buying one round between nine.",
    "Two Vanguard troopers off duty, drinking quietly in the corner and pretending not to listen.",
    "A courier who has been told to wait for an answer and has been waiting since noon.",
    "Heddra, settling the kitchen's tab and telling Grimma about the family dinner.",
    "Lift-hands arguing about whether the Lift IX cable was cut or simply snapped.",
    "Yrsa collecting names for Hearthwatch on a slate.",
    "A Cinder-Tusk exile who has lived in Lowhearth for years, sitting alone because nobody sits with him now.",
], "Faces in the taproom. Use one or two per visit.", "ab-kitchen", T)
MI.table("hold-gilded-nail", "Gilded Nail Gossip (officers)", [
    "'Brynja's furious about the requisition quotas. Says they're starving the gate garrison of iron.'",
    "'Odran wants every wagon counted twice. Somebody's been counting them once and selling the second.'",
    "'Hadrik buys a round for the whole Vanguard table every night. Wonder who pays his tab.'",
    "'Baldrik hasn't been in since his brother came back. Used to sit in the corner with the old shield.'",
    "'There'll be a commission at the Public Roll. Honorary. Nothing honorary about the clauses.'",
    "'Hammerline's in deep at the Turning Gear. Deeper since someone took over his markers.'",
    "'The Treaty Stair? Old nonsense. The compact's obsolete. Says so in the briefing.' (Hadrik's line)",
    "'If the orcs come up the lower bridge we'll need every hand, rank or not.'",
], "What officers say when they think the wine is the only listener.", "ab-command", T)
MI.table("hold-ember-baths", "Overheard in the Steam", [
    "Two engineers comparing burns: both from the same jammed valve on the new foundry line.",
    "A Lowhearth mother bathing her children in the cool basin because the warm one isn't any more.",
    "A council clerk complaining that the Heartworks inspection was cancelled 'by order'.",
    "Fenn reading temperatures aloud to nobody, then writing them down.",
    "A Vanguard sergeant who swears he saw a goblin child in the pipes.",
    "Laundry-women gossiping that Iskra takes ration books as stakes.",
], "Steam carries voices further than people expect.", "it-gauge", T)
MI.table("hold-turning-gear", "Turning Gear Tells", [
    "The dealer touches her ear before every Rune: Iskra is watching this table.",
    "An officer pays in a blue-sealed foundry chit instead of coin.",
    "A Lowhearth father stakes a ration book; the room goes quiet for a heartbeat.",
    "Iskra laughs at a joke a fraction too late: she's counting someone else's stack.",
    "The Wheel's brake squeals on 9. It always lands near 9 when the house is losing.",
    "A Vanguard aide in plain clothes buys a lieutenant's marker at the cage.",
], "Use with Insight (DC 13). A tell is a clue, never a guaranteed win.", "tb-dice", T)
MI.table("hold-glimmerhall", "Glimmerhall Curios", [
    "A lamp that burns brighter when someone in its light lies. Unreliable; it hates poetry.",
    "A ward-nail that hums when a door it's driven into is opened.",
    "A lantern that only shows things that are cold.",
    "A brass moth that finds the nearest flame and sits on it.",
    "A glass bead holding one breath of mountain air from before the hold was dug.",
    "A testimony-lamp shutter, cracked, still whispering one word: 'yes'.",
], "Small wonders for sale (10–50 gp each). Mostly harmless.", "it-lantern", T)
MI.table("hold-remedies", "What's in Mother Moss's Jar?", [
    "Bitter-root syrup: soothes a cough, tastes of pennies.",
    "Smokeleaf breather: advantage on saves against inhaled spores or steam for an hour.",
    "Fire-salve: regain 1d4 hit points when applied to a burn; Fenn buys it by the pot.",
    "Dark-sleep tea: a long rest takes 6 hours tonight.",
    "Glowcap, dried and powerless; she keeps it to remind herself what's missing.",
    "Something Tikka labelled in goblin. Bera doesn't ask.",
], "Small remedies for 1–25 gp.", "it-mushroom", T)
MI.table("hold-deep-script", "A Lesson in the Deep Script", [
    "VARN, Ward: 'A ward is a promise to stand still where it matters.'",
    "DOR, Impact: 'Every blow returns to the arm. Cut accordingly.'",
    "KETH, Binding: 'Never bind what you cannot also release.'",
    "ORUN, Memory: 'Stone remembers better than clerks. That's why clerks hate it.'",
    "THAR, Oath: 'An oath carved for someone else is a chain.'",
    "MOR, Lineage: 'A name is carried by choice. Blood is only the ink.'",
    "RUUN, Voice: 'A rune spoken is a rune witnessed.'",
    "KHAL, Forge: 'What you make outlives what you meant.'",
], "Kharn's teaching for a visit. Each lesson also counts as preparation for that rune's Cut grade (advantage on the next Rune Forge check for it).", "rune-mor", T)
MI.macro("hold-map", "Kharad-Varr: Open the Hold", "api.hold.map();", "mc-session", T)
MI.macro("hold-rivets", "Rivets & Runes (Turning Gear)", "api.hold.rivets();", "mc-cards", T)
MI.macro("hold-rumour", "Hold Rumour", "api.hold.rumour();", "mc-handout", T)

# ============================================================================ venues
# Each venue: map, keeper, district, opens (session), quest window, services, side notes, shadows, quest dict.
VENUES = [
    dict(key="low-lantern", name="The Low Lantern", district="d-lowhearth", keeper="grimma", opens=1, window="Sessions 2–5 (ends at Hearthwatch)",
         blurb="Lowhearth's public house: low beams, a hearth big enough to sleep beside, the message slate behind the bar, and Song Night whenever a shift comes up alive.",
         read=["Warm air, wet wool and burnt mutton. Somebody is singing badly and the whole room is forgiving them. Behind the bar a broad red-haired dwarf bangs a mallet on a cask and roars, “Sit, or get out of the light!”"],
         services=[["Slatewater small beer", "1 cp", "Deepcap Stout is 'off'. Ask why."], ["Mushroom-and-mutton pie", "3 cp", "Heddra supplies the pastry."],
                   ["Cask of Deepcap Stout (last ones)", "15 gp", "Secures a hearing at any Lowhearth gathering."], ["A cot by the hearth", "5 sp", "Long rest; Grimma hears everything."],
                   ["The message slate", "free", "Leave word for anyone in Lowhearth. Couriers check it."], ["Song Night", "free", "Most nights. Old Dagny leads."]],
         notes=["<strong>R1 (corroboration).</strong> The Deepcap spring that brews the stout ran thin the same fortnight the diversion opened.",
                "<strong>Heddra and Tovik.</strong> Heddra knew Hollin Tapwell; Tovik's crew drink here and will add their voices to the verse after 2.4 if their missing shift came home.",
                "<strong>Hearthwatch (3.5b).</strong> The natural ending: Yrsa reads the names from the register at the vigil. The Missing Verse adds four names that the register leaves out."],
         shadows=["<strong>Orcus.</strong> At Attention 3+, the seventh verse has a fifth name nobody wrote: the name of a party member, sung in the past tense. It is a sign, not a prophecy. Orcus wants the dead kept unsung."],
         quest=dict(key="q-low-lantern", title="The Missing Verse", hook="Song Night stops one verse early. Old Dagny puts down her harp and walks out into the drain-street. Grimma, wiping a dry tankard far too hard, asks the party to find out why nobody will sing the seventh verse of <em>Down the Ninth</em>, because her brother Hollin is in it.",
                    truth="Six months ago the four-strong Seventh Cut crew were reassigned to open the new diversion cut. A pressure-blow scalded Hollin Tapwell, Ysolde Rookbarrow, Aldo Cinderhand and Feyra Brassnail. Entering four deaths in the register would date the works before the first raid, so a clerk in Hadrik's office struck them as 'deserted'. Dagny wrote the verse that week. A Vanguard sergeant told her singing deserters' names was 'slander of command'.",
                    beats=["<strong>Dagny.</strong> She will sing it to the party privately if they promise to take the risk off her (no roll if they plainly offer protection; DC 13 Persuasion if they only ask). The verse names the four and 'the new cut that ate them'.",
                           "<strong>The register.</strong> All four are struck 'deserted' on the same day, the day before the first entry on the Ninth Sluice gauge record (E1). Access through Venn Stoneclerk, Dagnner, or the Military Archive during Chapter 3.",
                           "<strong>The cellar.</strong> Grimma's cellar hatch opens on the old drain. Silt washed down from the sluice holds a scorched brass work-tag stamped 'VII CUT · TAPWELL' (DC 13 Investigation; automatic if Grimma shows them).",
                           "<strong>Complication.</strong> A Vanguard sergeant warns Grimma that singing 'deserters' is sedition. The party can argue lawfully: Brynja's garrison standing orders protect household vigils regardless of rank."],
                    ends=["<strong>Sung at Hearthwatch.</strong> If the verse is sung at the vigil (3.5b) and at least one officer (Brynja, Dagnner, Baldrik or Eirik) stands for it in public: <strong>+1 Accord</strong> (once; counts toward the Hold cap). Hollin's name is read with the dead.",
                          "<strong>Sung at the Lantern.</strong> No track change, but the Low Lantern becomes the party's safe house: in Chapter 5 Grimma hides one frightened witness without a roll.",
                          "<strong>Left unsung.</strong> Nothing is lost from the main story. Grimma still serves them, but she stops asking them for anything."],
                    rewards=["The Missing Verse (item).", "The last Cask of Deepcap Stout, free, if the verse is sung anywhere.", "Free bed and board at the Low Lantern for the rest of the arc."],
                    items=["hold-missing-verse", "hold-deepcap-stout"])),
    dict(key="gilded-nail", name="The Gilded Nail", district="d-market", keeper="sorvald", opens=2, window="Sessions 3–6 (before the Public Roll, 5.2)",
         blurb="The officers' tavern on the Crown Market: marble floor, a red carpet worn pink by boots, trophy racks, a private card room, and the Moot Anvil in the middle of the room where disputes between officers are settled to the yield.",
         read=["Everything here is polished, from the brass rail to the officers' laughter. Conversation dims for exactly one breath when the party enters, then rises again a little louder than before."],
         services=[["Emberglass brandy", "5 gp", "Officers drink it to be seen drinking it."], ["The Generals' Cut (roast)", "2 gp", "Excellent, and very large."],
                   ["The card room", "10 gp / night", "Private. Turning Gear markers change hands here."], ["A Hammer-Moot", "by challenge", "Three bouts to the yield; Sorvald presides."]],
         notes=["<strong>Access.</strong> Officers and sponsored guests only. After 1.4 (<em>A table above their station</em>) Thorgrinn's name gets the party in, and that is exactly the problem.",
                "<strong>Council stances.</strong> Officers here repeat their generals' lines; use the gossip table to show the party where Brynja, Odran and Hadrik stand before 5.4.",
                "<strong>Baldrik.</strong> His corner table and empty chair. If the brothers meet here, it's in public: the whole room listens."],
         shadows=["<strong>Vampyr.</strong> Debt is the Gilded Nail's real currency. A character carrying the Blood-Debt feels the pull of every marker in the card room; Vampyr's attention rises by 1 if they buy one."],
         quest=dict(key="q-gilded-nail", title="A Name Above Its Station", hook="Lieutenant Eirik Hammerline stands on the Moot Anvil and asks the room whether a man of rivets can carry an Ironfist name, let alone a rank. He formally challenges Thorgrinn to a Hammer-Moot to 'prove the name'.",
                    truth="Hadrik's office bought Eirik's 340 gp of Turning Gear markers and asked one favour: embarrass Thorgrinn before the Public Roll. Eirik half-believes what he's saying, and hates that he was bought.",
                    beats=["<strong>The challenge.</strong> Thorgrinn may refuse. Sorvald rules a stated refusal honourable ('A name is not a debt to be collected'), and Eirik then looks petty. Thorgrinn may also name a champion from the party.",
                           "<strong>The moot.</strong> Best two of three bouts, to the yield: <em>Strength</em> (arm-wrestle across the anvil, contested Athletics), <em>Lore</em> (recite the Ironfist roll of oaths, contested History; Heddra or Runa can coach beforehand for advantage), <em>Word</em> (each says why they serve, contested Persuasion; the room decides).",
                           "<strong>The markers.</strong> Insight DC 13 during the moot shows Eirik glancing at a plain-clothes Vanguard aide. The card room and the Turning Gear lead to the rest.",
                           "<strong>Complication.</strong> If anyone strikes to wound outside the rules, Sorvald ends the moot and the offender's side loses face with the officers."],
                    ends=["<strong>Win with grace.</strong> Eirik yields, accepts the name before the room, and privately admits who holds his markers. The party gains Eirik's Oathmark.",
                          "<strong>Refuse.</strong> No loss. The officers respect the refusal more than they expected to. Eirik can still be turned later if the party clears his markers (see the Turning Gear).",
                          "<strong>Lose.</strong> Thorgrinn's name and personhood are untouched: nobody here can rule on them, and the module never lets them. Hadrik jokes about it at 5.2. Eirik, shamed by how it was arranged, comes looking for the party afterwards."],
                    rewards=["Eirik's Oathmark (item).", "A sponsored seat at the Gilded Nail for every party member."],
                    items=["hold-eirik-oathmark"])),
    dict(key="ember-baths", name="The Ember Baths", district="d-steamstair", keeper="fenn", opens=2, window="Sessions 3–6 (ideally before 4.1, the Treaty Stair)",
         blurb="Geothermal baths on the Steamstair between Lowhearth and the deep: cool, warm and Ember basins, changing rooms, and a pipe crawl full of valves. They are cooling, and the whole Steamstair is beginning to notice.",
         read=["The steam is thinner than it should be. In the Ember Basin an old dwarf in a soaked apron is holding a thermometer up to a lamp and swearing at it softly, like a friend who has let him down."],
         services=[["Common soak", "1 sp", "Lowhearth price."], ["Private basin", "1 gp", "Officers' price."],
                   ["Ember Basin soak (when hot)", "5 gp", "Short rest benefits; once a day, remove one level of exhaustion."], ["Laundry", "2 cp", "Gossip included."]],
         notes=["<strong>R1 (corroboration).</strong> Fenn's heat log dates the cooling to the diversion fortnight.",
                "<strong>Urzha and the Treaty Stair (4.1).</strong> Bringing Pip home first gives advantage on the first social check with Urzha, and the clan hears about it before the official passage.",
                "<strong>Accord.</strong> Accord measures practical cooperation. Pip's escort counts only if a dwarf of the Steamstair (Fenn) walks with her."],
         shadows=["<strong>Orcus.</strong> At Attention 3+, the steam in the crawl takes faces: the Seventh Cut crew (see the Low Lantern). They point down."],
         quest=dict(key="q-ember-baths", title="Cold Water", hook="Fenn asks the party to clear his pipe crawl: something hisses in there, the heat valve keeps jamming, and one of his assistants came out scalded. The Ember Basin is ten degrees down and the families of the Steamstair are bathing their children in cold water.",
                    truth="The diversion pulls geothermal heat to the foundries. The pressure backs up in the Steamstair crawl, and scald mephits gather where heat pools. Hiding at the very end of the crawl is Pip, a Cinder-Tusk child who climbed up the drains to steal warm water for her grandmother, whose well went foul.",
                    beats=["<strong>The log.</strong> Fenn's heat log shows the drop: Investigation DC 13, or simply ask him. It matches E1's dates.",
                           "<strong>The crawl.</strong> Three scald mephits (hidden tokens). Narrow, hot, poor light. The valve wheel at the north end can be closed (Athletics DC 13) to vent the crawl and halve the steam damage.",
                           "<strong>Pip.</strong> Found at the southern hatch, burned hands and a stolen kettle. She bolts if threatened (Small and Quick).",
                           "<strong>The choice.</strong> Hand her to the Vanguard (she is detained as a 'raider spy'), hide her (Bera or Grimma will), or take her home down the drains to the Treaty Stair, a dangerous two-hour route without Skrik's maps."],
                    ends=["<strong>Home safe, with Fenn.</strong> Pip reaches her family and a dwarf of the Steamstair walked her there: <strong>+1 Accord</strong> (once; counts toward the Hold cap). Urzha remembers it.",
                          "<strong>Hidden.</strong> No track change. Pip becomes a messenger who can carry one note to Urzha before 4.1.",
                          "<strong>Handed over.</strong> The Vanguard detain her. The party can still free her lawfully at 4.3 (prisoner exchange), and the Cinder-Tusk will ask about her by name."],
                    rewards=["Ember Baths Token (3 soaks).", "Fenn's Heat Log (item).", "Once the valve is reset, the Ember Basin is hot again for the rest of the arc."],
                    items=["hold-ember-token", "hold-heat-log"])),
    dict(key="turning-gear", name="The Turning Gear", district="d-market", keeper="iskra", opens=3, window="Sessions 3–8",
         blurb="The Crown Market's gaming house: a great brass Wheel of Gears, dice pits for Rivets and Runes, card tables for Anvil-Stakes, a cashier's cage, and Madame Iskra's office over a vault full of other people's promises.",
         read=["The Wheel turns with a sound like a slow clock. Every few seconds someone cheers and someone else does sums under their breath. At the cage a clerk weighs a stack of blue-sealed papers as if they were coin."],
         services=[["Rivets and Runes (dice)", "1–100 gp", "Use the Rivets and Runes macro. Triples pay 3 to 1."], ["Anvil-Stakes (cards)", "5–200 gp", "Three hands of contested Insight against Deception; best two of three."],
                   ["The Wheel of Gears", "1–50 gp", "d12: a single number pays 10 to 1; odd or even pays even money."], ["House limit", "200 gp", "Iskra raises it for people she finds interesting."]],
         notes=["<strong>E2 (one route).</strong> Officers settle markers with foundry requisition chits. The Marker Ledger plus Brannoc's quota book authenticates as E2.",
                "<strong>Eirik.</strong> His markers are in the vault, bought by a Vanguard aide. Clearing or recovering them turns him (see the Gilded Nail).",
                "<strong>Last Bastion's emergency powers</strong> would requisition houses like Iskra's. She knows, which gives the party leverage that doesn't need a threat."],
         shadows=["<strong>Vampyr.</strong> A character marked with the Blood-Debt has disadvantage on every game here. They already owe. If they win anyway, Vampyr's Attention +1."],
         quest=dict(key="q-turning-gear", title="The House Always Requisitions", hook="Grimma (or Heddra) asks for help: Edvin Rookbarrow, a Lowhearth father, pawned his family's ration book to cover a gambling debt. Without it five people draw no food. His wife Ysolde is one of the Seventh Cut crew struck off as 'deserters', so the household lost her share six months ago (see The Missing Verse). Iskra keeps it in her vault.",
                    truth="Iskra is a pragmatist, not a villain. Her officers have paid their markers in foundry requisition chits for six months; she cashes them at the foundries at face value, and the foundries pay. The ledger is a map of who profited from the shortages. A Vanguard aide has been buying junior officers' markers for Hadrik's office.",
                    beats=["<strong>Win it back.</strong> Iskra will stake the ration book against 100 gp in a best-of-three of Rivets and Runes (she deals herself). Cheating is possible; she notices on anything below 18.",
                           "<strong>Bargain.</strong> She trades the book, a copy of the Marker Ledger and her testimony for protection from requisition when the emergency powers come. That can be Odran's written guarantee, Brynja's order, or the party's open word.",
                           "<strong>Burgle.</strong> The office door to the vault is locked iron (DC 18 thieves' tools); the vault ledger is plain. Iskra will know who did it by morning and won't testify.",
                           "<strong>Complication.</strong> The Vanguard aide arrives to buy Eirik's last marker while the party is there."],
                    ends=["<strong>Bargain.</strong> The ration book comes home; Iskra swears to the ledger copy before a hearing.",
                          "<strong>Winnings.</strong> The ration book comes home. Iskra respects them and offers the ledger copy for a favour later (her house protected).",
                          "<strong>Burglary.</strong> The ration book and the ledger copy, but Iskra refuses to authenticate it, so it stays corroboration only."],
                    rewards=["The Rookbarrow Ration Book (item).", "Iskra's Marker Ledger, copy (item).", "Iskra's Lucky Rivet (item): her gift if the bargain is kept."],
                    items=["hold-ration-book", "hold-marker-ledger", "hold-lucky-rivet"])),
    dict(key="anvilsong-forge", name="Anvilsong Forge", district="d-forge", keeper="brannoc", opens=2, window="Sessions 2–9 (gate installed before Session 10)",
         blurb="Three forges, three anvils, a quench trough and a half-built lift gate on trestles. Forge Row's oldest smithy, now working to military quota.",
         read=["Three forges, and only one is working on anything Brannoc wants to make. On the trestles lies a gate of black ironbone bars, unfinished, with a sheet of quota paper nailed to it."],
         services=[["Repairs", "half price for Lowhearth", "A damaged weapon or shield in an hour."], ["Weapons and armour", "standard price", "Masterwork on request."],
                   ["A +1 weapon or armour commission", "1,000 gp + oathstone or ironbone", "Ready by Chapter 7."], ["Rune socket fitting", "100 gp", "With the Hall of Deep Script."]],
         notes=["<strong>E2 and R3 pointers.</strong> The quota book lists ironbone pressure plates 'for regulator modification, Heartworks', and foundry payments rising through the shortages.",
                "<strong>The two-rivet shield.</strong> Last month Baldrik ordered matched rivets for his old shield, then cancelled before Brannoc started. 'Said the mismatch was the point.' Use it at 1.5 or 8.5; don't force it.",
                "<strong>Siege dispatches.</strong> The gate answers <em>The Lift Jams</em> once."],
         shadows=["<strong>Vecna.</strong> At Attention 3+, the quota book has a column added in a hand nobody at the forge recognises, listing what each party member would trade for a shortcut. It's a sign. Burn it or keep it, but Vecna notices either way."],
         quest=dict(key="q-anvilsong-forge", title="The Last Commission", hook="Brannoc asks the party to help him finish the safety gate for Lowhearth's lifts. After a cage dropped two floors last winter, the Lowhearth households paid for it themselves. The ironbone he needs has been reserved for 'Bastion works'.",
                    truth="The ironbone went into the pressure plates installed in the Heartworks. Brannoc cut some of those plates himself without knowing what they were for. He's starting to guess.",
                    beats=["<strong>Find ironbone.</strong> Three routes: reclaim the forge's own stock from the Forge Row quota warehouse (lawful with Odran's or Brynja's signature; otherwise a stealth problem); salvage the wrecked pump housing at the Ninth Sluice after 2.4; or trade with Ketta or Skrik, who hold salvaged ironbone pipe (needs the Treaty Stair, and is a small act of cooperation).",
                           "<strong>Forge it.</strong> A work challenge: three progress before two setbacks. Smith's tools, Athletics at the bellows, Arcana or a Rune Forge check to temper the bars. A setback costs a day, not the gate.",
                           "<strong>Install it.</strong> The lift-hands of Lowhearth turn out to help. If it's installed before Session 10 it is ready for the war.",
                           "<strong>The quota book.</strong> Brannoc will hand over his copy once he understands what the plates are for (reveal R3 elsewhere, or show him Runa's figures)."],
                    ends=["<strong>Installed before Session 10.</strong> <strong>+1 Defence</strong> (once; counts toward the Hold cap) and the gate answers <em>The Lift Jams</em> in Chapter 7.",
                          "<strong>Installed later.</strong> No track change; it still answers <em>The Lift Jams</em> once.",
                          "<strong>Unfinished.</strong> Brannoc finishes it after the war; it's there in 8.6."],
                    rewards=["The Anvilsong Lift Gate (story item).", "Anvilsong Quota Book (item).", "One commission at cost (materials only)."],
                    items=["hold-anvilsong-gate", "hold-quota-book"])),
    dict(key="glimmerhall", name="Glimmerhall, Enchantments and Wards", district="d-market", keeper="sigrun", opens=4, window="Sessions 4–8",
         blurb="A shop of shuttered lamps and ward-nails on the Crown Market, with a workshop behind and a warded vault above. Sigrun makes the testimony lamps used in Stone Council hearings.",
         read=["Every lamp in the shop is shuttered but one. In the workshop circle a tall brass lamp burns violet, and every few breaths it speaks a sentence in a voice that isn't anyone's."],
         services=[["Identify an item", "20 gp", "Free for anyone who helps with the lamp."], ["Alarm ward-nail", "50 gp", "Hums when the warded door opens."],
                   ["Glimmerhall curio", "10–50 gp", "Roll on the curios table."], ["Hush-Ward Lantern", "not for sale", "The reward of the side quest."]],
         notes=["<strong>R3 (support).</strong> Authenticated, the lamp's council fragment supports Runa's bypass calculations. It never replaces them.",
                "<strong>Truth magic.</strong> Truth magic verifies Sigrun's testimony about the lamp. The lamp itself is an object, so authenticate it like a document (Kharn).",
                "<strong>Witness protection.</strong> The Hush-Ward Lantern is ideal for protecting Venn, Dagnner or Iskra."],
         shadows=["<strong>Vecna.</strong> At Attention 3+, the lamp begins whispering the party's secrets as well. Vecna is reading through it. Cleansing the lamp (see the quest) closes that window, and refusing Vecna's offer to 'keep the lamp's memory' lowers his Attention by 1."],
         quest=dict(key="q-glimmerhall", title="The Lamp That Remembers", hook="Sigrun asks for help with her testimony lamp, lent to the Stone Council chamber and returned 'cleaned'. It isn't. At night it whispers people's secrets into the Crown Market: a council session, a clerk's affair, a child's hiding place.",
                    truth="Somebody tried to scrub a closed council session from the lamp and only broke its seals. It now leaks everything it ever heard. Among the fragments is Hadrik's voice calling Lowhearth an 'acceptable loss of position'. Hadrik's people have noticed.",
                    beats=["<strong>Calm the lamp.</strong> A ritual work challenge in the circle: Arcana, Religion, Performance (sing to it), or a dispel used gently. Each setback, the lamp blurts out a secret belonging to someone in the room.",
                           "<strong>Sort the whispers.</strong> Separate the council fragment from the private secrets of townsfolk. Returning those secrets quietly to the people they belong to is the decent thing, and it's noticed.",
                           "<strong>The sweepers.</strong> That night two Vanguard officers and four troopers arrive with a warrant to 'seize seditious apparatus'. The warrant was signed by an aide, not a general; Brynja's or Odran's countersignature is required for property on the Crown Market. They can be stopped lawfully.",
                           "<strong>Consent.</strong> Sigrun asks to examine Thorgrinn's soul-coin runework, because similar bindings might help seal the lamp. He can refuse; she accepts it at once and finds another way (one more progress needed)."],
                    ends=["<strong>Sealed and sorted.</strong> The council fragment is preserved and authenticated (with Kharn); the private secrets are returned. Sigrun makes the Hush-Ward Lantern from the lamp's quiet half.",
                          "<strong>Seized.</strong> If the sweepers take the lamp, it's 'lost in the archive'. The party can recover it from the Military Archive in Chapter 3–5 as part of that scene.",
                          "<strong>Smashed.</strong> The secrets die with it, the council fragment included."],
                    rewards=["Hush-Ward Lantern (item).", "The Lamp's Council Fragment (item).", "Free identification for the rest of the arc."],
                    items=["hold-hush-lantern", "hold-lamp-fragment"])),
    dict(key="mossbeard-remedies", name="Mossbeard and Fernspit Remedies", district="d-lowhearth", keeper="bera", opens=2, window="Sessions 2–8 (the cure needs the warrens, Session 6+)",
         blurb="Lowhearth's apothecary: a counter of jars, a brewing room, a sick room with four cots, and Tikka's fungus beds glowing along the east wall.",
         read=["Bitter steam, green light, coughing. A white-haired dwarf woman holds a child's chin and listens to his chest while a goblin behind her crushes something in a mortar and argues with her about the dose."],
         services=[["Potion of healing", "50 gp", "Greater: 150 gp (two in stock)."], ["Antitoxin", "50 gp", ""],
                   ["Mother Moss's poultice", "5 sp", "Regain 2d4 + 2 hit points; one a day."], ["Small remedies", "1–25 gp", "Roll on the jar table."]],
         notes=["<strong>R1 (one route).</strong> Tikka's spore sample counts as the 'dead fungal samples' route if the sluice samples are lost.",
                "<strong>Yrsa's Infirmary.</strong> Bera and Yrsa share patients. A cure brewed here supplies the infirmary in Chapter 7.",
                "<strong>Accord.</strong> A cure shared with the warrens is cooperation both peoples can see."],
         shadows=["<strong>Orcus.</strong> At Reaching or higher, Orcus offers to 'take the cough'. It stops at midnight in every house at once, and the ravens come to Lowhearth's roofs. Bera knows what that means and refuses on everyone's behalf; the party may not."],
         quest=dict(key="q-mossbeard-remedies", title="The Bitter Cough", hook="Half of Lift Street has the bitter cough and the children have it worst. Bera needs help, and a Vanguard sergeant has just told a crowd outside that Tikka's mushrooms poisoned the drains.",
                    truth="The diversion poisoned the Cinder-Tusk fungal beds downstream. Their rotting spores ride the foul water back up the drains into Lowhearth. The cure needs fresh glowcap, which grows only in the warrens' upper beds, and those survived because Urzha's people rerouted a trickle of clean water to them.",
                    beats=["<strong>Diagnose.</strong> Medicine DC 13 or Nature DC 13 identifies spore-sickness; Tikka's lens matches the spores to the dead downstream beds.",
                           "<strong>The crowd.</strong> Defuse the accusation: the spore match plus the timing (E1 or the heat log) is enough for most of the crowd. Intimidation works and costs goodwill.",
                           "<strong>Glowcap.</strong> Ask Urzha for it at the Treaty Stair (Session 6+). She'll trade for clean-water filters, dwarven medicine, or the promise that the cure goes to the warrens too.",
                           "<strong>Brew.</strong> A work challenge with Bera and Tikka: Herbalism kit, Medicine, Nature. Each setback costs one dose."],
                    ends=["<strong>Shared cure.</strong> The tincture goes to Lowhearth and the warrens alike: <strong>+1 Accord</strong> (once; counts toward the Hold cap). Tikka's sister's beds are saved.",
                          "<strong>Lowhearth only.</strong> The cough clears in Lowhearth; no track change. Urzha remembers the bargain was broken.",
                          "<strong>No glowcap.</strong> Bera's bitter-root eases the cough; nobody dies of it. The children are weaker for weeks."],
                    rewards=["Glowcap Tincture (3 doses).", "Tikka's Spore Sample (item).", "Bera and Tikka supply the party at cost."],
                    items=["hold-glowcap-tincture", "hold-spore-sample"])),
    dict(key="deep-script", name="The Hall of Deep Script", district="d-forge", keeper="kharn", opens=3, window="Sessions 3–10 (key shared before Session 11)",
         blurb="The rune smiths' guild hall on Forge Row: a pillared nave of carving benches, archives behind shelf walls, and the Trial of the Three Rings in its centre with the Rune Warden standing in it.",
         read=["The only sound is chisels. Then an old voice from behind the shelves: “You can come in. Everyone with runes on them is welcome here. Even the ones who didn't choose them.”"],
         services=[["A rune lesson", "a watch", "Roll on the lesson table; advantage on the next Rune Forge check for that rune."], ["Inscription", "100 gp + materials", "Kharn's hand; Cut grade at the Hall."],
                   ["Authenticate a seal", "free to the honest", "Kharn can authenticate the dwarven copy of the Water-and-Stone Compact (E4)."], ["The Trial of the Three Rings", "by invitation", "See the quest."]],
         notes=["<strong>E4.</strong> Kharn's reading of the dwarven copy's runic seal is a sound way to authenticate it alongside the Cinder-Tusk copy.",
                "<strong>R3 and R5.</strong> The reversal key his apprentice cut points at the plates (R3) and helps the coordinated regulator work in 8.3 (R5). It is not the operating manual.",
                "<strong>Module law.</strong> Kharn's interest in Thorgrinn's runes has nothing to do with Last Bastion. Nobody can command, extract or 'switch off' Thorgrinn, and Kharn would be appalled at the idea."],
         shadows=["<strong>Vecna.</strong> If the Borrowed Ending took 'the inscriptions of his soul coin' as its price, this is where Thorgrinn can recover them: Kharn helps him re-carve them from memory, witnesses and choice (see the quest). That recovers the price, and Vecna's Attention −1."],
         quest=dict(key="q-deep-script", title="A Rune Nobody Taught", hook="Kharn invites Thorgrinn, and asks first, to take the Trial of the Three Rings and enter a maker's mark in the guild roll, as a being who carries runes and can make them, not as a thing that was made. Separately, his apprentice Orla Keenchisel has stopped eating.",
                    truth="Orla was ordered, under military requisition, to cut 'reversal runes' for pressure plates bound for the Heartworks. She kept a wax rubbing of the key because she was afraid of what it did.",
                    beats=["<strong>The invitation.</strong> Entirely Thorgrinn's choice. Kharn will not examine his runes without consent and stops when asked.",
                           "<strong>The Trial.</strong> Three rings. Outer: speak a rune's meaning in your own words (any rune from the lesson table; Arcana or History DC 13). Middle: carve it while the Warden's glare asks what you fear to lose (Wisdom save DC 15; failure costs a progress, not the trial). Inner: the Rune Warden tests your hand. It fights to the yield and kneels at half hit points or when the trial rune is spoken correctly. Party members may take the trial too.",
                           "<strong>Orla.</strong> Insight DC 13, or Kharn's word, brings her confession. She will give the rubbing to someone who will use it to make the Heartworks safe, not to someone who wants to fire it.",
                           "<strong>The inscriptions (only if Vecna took them).</strong> Kharn helps Thorgrinn re-carve what was taken: each party member contributes one memory of who Thorgrinn is (no roll). The inscriptions are his again."],
                    ends=["<strong>The roll.</strong> If Thorgrinn takes the trial and chooses to sign, his Maker's Mark enters the guild roll.",
                          "<strong>The key.</strong> Orla's Reversal Key, shared with Runa and Skrik before Session 11: <strong>+1 Defence</strong> (once; counts toward the Hold cap) and a head start at 8.3.",
                          "<strong>Declined.</strong> Kharn bows, means it, and teaches him anyway."],
                    rewards=["Maker's Mark of the Deep Script (item).", "Orla's Reversal Key (item).", "Rune lessons for free."],
                    items=["hold-maker-mark", "hold-reversal-key"])),
]

DISTRICTS = [
    ("d-road", "The Mountain Road and the Fifth Finger", "The road out of the mists: nine miles of military road from the Fifth Finger to Gate Crown.", ["fifth-finger"], []),
    ("d-gate", "Gate Crown and Hammerhall", "The upper entry, the council chambers, military offices and the great celebration hall. Broad bridges for parades; sponsors required for administrative access, never for emergency shelter.", ["hammerhall", "records-annex", "upper-gate"], []),
    ("d-market", "The Crown Market", "The rank tier below Hammerhall: officers' houses, the officers' tavern, the gaming house and the enchanter, along one long street of stalls between the great lifts.", [], ["gilded-nail", "turning-gear", "glimmerhall"]),
    ("d-forge", "Forge Row", "The foundry street, now working to military quota. Chimneys to the surface; the rune smiths' guild at the far end.", [], ["anvilsong-forge", "deep-script"]),
    ("d-lowhearth", "Lowhearth", "The damp labour district two lifts below Hammerhall: Heddra's kitchen, the shrine, the communal workshops, the Low Lantern and the apothecary. A service stair if the lifts fail.", ["lowhearth"], ["low-lantern", "mossbeard-remedies"]),
    ("d-steamstair", "The Steamstair and Lift Shaft IX", "Below Lowhearth: the stair down to the Ember Baths, and the broken Lift Shaft IX toward the Ninth Sluice.", ["broken-descent"], ["ember-baths"]),
    ("d-deep", "The Deep Works", "Half a day below Lowhearth: the Ninth Sluice and its three galleries, the river, the pump bridge, the Treaty Stair and the lower galleries where the war is fought.", ["ninth-sluice", "pump-bridge", "treaty-stair", "lower-bridge", "pump-galleries"], []),
    ("d-warrens", "The Cinder Warrens", "Below the Treaty Stair: Cinder-Tusk dwellings, wells and fungal gardens, and Korga's command bridge.", ["cinder-warrens", "command-bridge"], []),
    ("d-redoubt", "The Vanguard Redoubt and the Heartworks", "The final military approach and, one hour beyond it, the regulators, relief outlets and the Bastion Engine.", ["vanguard-redoubt", "heartworks"], []),
]
VKEY = {v["key"]: v for v in VENUES}
HOLD_MAP_TITLES = {"hold-map": "Kharad-Varr: The Hold (linked overview)"} | {v["key"]: v["name"] for v in VENUES}
HOLD_MUSIC = {"hold-map": "the-shield-between-us", "low-lantern": "lowhearth-hearth", "gilded-nail": "hammerhall-feast", "ember-baths": "sluice-works",
              "turning-gear": "hammerhall-feast", "anvilsong-forge": "two-mismatched-rivets", "glimmerhall": "the-stone-council",
              "mossbeard-remedies": "lowhearth-hearth", "deep-script": "two-mismatched-rivets"}
HOLD_ORDER = list(HOLD_MAP_TITLES)
CAP = "Hold side quests can raise <strong>Defence</strong> by at most +2 and <strong>Civilian Accord</strong> by at most +2 across the whole arc. Each award happens once."


# ============================================================================ journals
def build(J):
    P, RA, BOX, UL, TABLE, BANNER, SECRET, IMG = J.P, J.RA, J.BOX, J.UL, J.TABLE, J.BANNER, J.SECRET, J.IMG
    L_page, L_scene, L_actor, L_item, L_table, L_macro = J.L_page, J.L_scene, J.L_actor, J.L_item, J.L_table, J.L_macro
    import schedule as SC
    title = lambda s: J.TITLES.get(s, s)
    sc = lambda s: L_page("ch" + s[1], s, f"{s[1]}.{s[2:]} {title(s)}")
    vlink = lambda k: L_page("hold", k, VKEY[k]["name"])
    qlink = lambda k: L_page("hold", VKEY[k]["quest"]["key"], VKEY[k]["quest"]["title"])
    mapname = lambda k: SC.MAP_TITLES.get(k) or HOLD_MAP_TITLES[k]
    pages = []
    start = (BANNER("Kharad-Varr", "The Hold", "Taverns, baths, smiths and side quests")
             + IMG(f"modules/{MOD}/assets/maps/hold-map.webp", "il-hero")
             + P("Between the scenes of the war the party lives somewhere: in a mountain of eleven thousand dwarves, two lifts and a hundred grudges. "
                 "This section opens that mountain. There are eight new places, each with its own map, keeper and <strong>self-contained side quest</strong> rooted in the hold's daily life, and each quest has <strong>side notes</strong> that connect it back to the evidence, the cast and the war.")
             + BOX("The overview map",
                   "Open " + L_scene("hold-map", "Kharad-Varr: The Hold") + " (or the " + L_macro("hold-map", "Open the Hold") + " macro). It is a gridless painted cutaway of the whole mountain. "
                   "<strong>Venue pins</strong> open the venue's page; <strong>district pins</strong> open a district page that links every map in that district, so every place in Part II is two clicks from the overview.")
             + BOX("Module law still holds", UL(
                   "Side quests <strong>corroborate</strong>; they never replace an essential revelation. Where a quest offers an evidence route, the page says exactly what it counts as.",
                   CAP,
                   "No quest changes Thorgrinn's body, consent or nature, and none brings the Dark Powers in as the cause of anything. Shadows notes are signs and offers only.",
                   "Nothing here is required. Skip any of it and the main arc runs unchanged."))
             + "<h3>The eight venues</h3>"
             + TABLE(["Venue", "District", "Keeper", "Side quest", "Open from", "Best played"],
                     [[vlink(v["key"]), L_page("hold", v["district"], dict((d[0], d[1]) for d in DISTRICTS)[v["district"]]), L_actor(v["keeper"], J_actor_name(v["keeper"])), qlink(v["key"]),
                       f"Session {v['opens']}", v["window"]] for v in VENUES])
             + "<h3>Tools</h3>" + UL(L_table("hold-rumours", "Hold Rumours") + " — one per visit; true rumours point to real leads.",
                                     L_macro("hold-rivets", "Rivets and Runes") + " — the Turning Gear's dice game, rolled and settled in chat.",
                                     L_macro("hold-rumour", "Hold Rumour") + " — draws a rumour privately for the GM."))
    pages.append(("start", "The Hold — Start Here", start))
    downtime = (BANNER("Kharad-Varr", "Downtime in the Hold")
                + P("The calendar is adjustable, and enemy plans advance when the party takes significant downtime (Section 2). Side quests use the same honest clock:")
                + TABLE(["Activity", "Time", "Notes"], [
                    ["Visit a venue, eat, gossip, shop", "an hour", "One rumour; one roll on the venue's table."],
                    ["A side-quest beat (one bullet on a quest page)", "a watch (about 4 hours)", "Two or three beats fit an evening between keyed scenes."],
                    ["A work challenge (forge a gate, brew a cure, calm a lamp)", "a watch to a day", "A setback costs time, never the whole quest."],
                    ["Travel between districts", "minutes by lift; half a day to the deep", "Lifts fail during the siege; the service stair still works."]])
                + BOX("When the war arrives",
                      "From Session 10 (the night before the horns) the side quests pause. Unfinished quests get a line in 8.6, <em>The next morning</em>: Brannoc finishes the gate, Dagny sings the verse anyway, the cure goes down the stair. Never use a side quest to punish the party for fighting the war.")
                + BOX("Rewards and the tracks", CAP, "Record each award with " + L_macro("defence", "Adjust Defence Readiness") + " or " + L_macro("accord", "Adjust Civilian Accord") + ", and tick it here so it isn't awarded twice:",
                      UL("☐ Low Lantern (+1 A)", "☐ Ember Baths (+1 A)", "☐ Mossbeard and Fernspit (+1 A)", "☐ Anvilsong Forge (+1 D)", "☐ Deep Script (+1 D)"),
                      "There are three Accord awards available for a cap of +2: once the cap is reached, the third still earns its story ending and its items.")
                + BOX("Spending money", "Prices follow the 5e standard. Lowhearth prices are lower than Crown Market prices; officers pay for being seen. Funded food, compensation or repairs can still earn a keyed track increase once (Section 2), never a second time through a venue."))
    pages.append(("downtime", "Downtime, Rewards and the Cap", downtime))
    # district pages
    for dk, dname, ddesc, maps, venues in DISTRICTS:
        h = (BANNER("Kharad-Varr · District", dname) + P(ddesc))
        if maps:
            h += "<h3>Maps in this district</h3>" + UL(*[L_scene(m, mapname(m)) for m in maps])
        if venues:
            h += "<h3>Venues</h3>" + UL(*[f"{vlink(v)} — {L_scene(v, VKEY[v]['name'])} · {qlink(v)}" for v in venues])
        if dk == "d-lowhearth":
            h += BOX("Also here", "Heddra's kitchen (1.3, 3.5), Yrsa's shrine and infirmary (2.1), and the Hearthwatch vigil (3.5b).")
        if dk == "d-gate":
            h += BOX("Also here", "The welcome feast (1.4), the Public Roll (5.2), the war council (6.1) and the Upper Gate front (7.3).")
        h += P(L_scene("hold-map", "← Back to the overview map"))
        pages.append((dk, dname, h))
    # venue + quest pages
    for v in VENUES:
        q = v["quest"]
        vh = (BANNER("Kharad-Varr · " + dict((d[0], d[1]) for d in DISTRICTS)[v["district"]], v["name"], v["blurb"])
              + strip(J, v["key"], HOLD_MUSIC[v["key"]], v["name"])
              + RA(*v["read"])
              + BOX("Keeper", L_actor(v["keeper"], J_actor_name(v["keeper"])) + ". Open from Session " + str(v["opens"]) + ". Side quest: " + qlink(v["key"]) + " (" + v["window"] + ").")
              + "<h3>Services and prices</h3>" + TABLE(["Service", "Price", "Notes"], v["services"])
              + "<h3>Side notes to the main story</h3>" + UL(*v["notes"])
              + BOX("Shadows Beyond Barovia", *v["shadows"], cls="il-box il-shadows")
              + P("Tables: " + ", ".join(L_table(t, n) for t, n in VENUE_TABLES.get(v["key"], [])) + (" · " if VENUE_TABLES.get(v["key"]) else "") + L_table("hold-rumours", "Hold Rumours"))
              + P(L_page("hold", v["district"], "← District") + " · " + L_scene("hold-map", "Overview map")))
        pages.append((v["key"], v["name"], vh))
        qh = (BANNER("Side Quest · " + v["name"], q["title"], v["window"])
              + BOX("The hook", q["hook"])
              + SECRET("What is really going on", q["truth"])
              + "<h3>Beats</h3>" + UL(*q["beats"])
              + "<h3>Endings</h3>" + UL(*q["ends"])
              + "<h3>Rewards</h3>" + UL(*q["rewards"])
              + P("Items: " + ", ".join(L_item(i, dict((x[0], x[1]) for x in ITEMS)[i]) for i in q["items"]))
              + BOX("Cap reminder", CAP)
              + P(vlink(v["key"]) + " · " + L_scene(v["key"], "Map") + " · " + L_scene("hold-map", "Overview map")))
        pages.append((q["key"], "Side Quest: " + q["title"], qh))
    # session placement
    rows = []
    for S in SC.SESSIONS:
        n = S["n"]
        open_ = [vlink(v["key"]) for v in VENUES if v["opens"] <= n and n < 10]
        rows.append([f"{n}. {S['title']}", ", ".join(open_) if open_ else "— (the war; side quests pause)", SESSION_NUDGE.get(n, "")])
    pages.append(("sessions", "Side Quests by Session",
                  BANNER("Kharad-Varr", "Side Quests by Session") + P("What's open when, and a suggested nudge. Nudges are optional, so offer one, never more than two, per session.")
                  + TABLE(["Session", "Open venues", "Suggested nudge"], rows)))
    J.journal("hold", "10 — Kharad-Varr: The Hold (Side Quests)", "Reference", pages, sort=1000)


SESSION_NUDGE = {
    1: "End the night at the Low Lantern. Song Night stops a verse early (The Missing Verse).",
    2: "The cold baths, and Mother Moss's cough. Brannoc asks for ironbone after the sluice.",
    3: "Eirik's challenge at the Gilded Nail. Iskra's ration-book problem reaches Heddra.",
    4: "The Missing Verse's register entries sit beside E1 in the archive (3.2–3.4).",
    5: "Hearthwatch: the verse can be sung. Glimmerhall's lamp starts whispering.",
    6: "The Treaty Stair opens: take Pip home, ask Urzha for glowcap, trade for ironbone.",
    7: "Before the Public Roll: the Missing Verse, Eirik and Iskra's ledger all pay off here.",
    8: "After 'What Last Bastion means': Brannoc and Kharn understand what the plates were for.",
    9: "Last window: install the gate, share Orla's key, deliver the cure.",
    10: "The war arrives. Side quests pause; Eirik's Oathmark and the gate matter now.",
    11: "Fronts: the Anvilsong gate answers 'The Lift Jams'. Eirik holds a front.",
    12: "8.3: Orla's key gives a head start. 8.6: give every unfinished quest its line.",
}
VENUE_TABLES = {"low-lantern": [("hold-low-lantern", "Who's at the Low Lantern")], "gilded-nail": [("hold-gilded-nail", "Gilded Nail Gossip")],
                "ember-baths": [("hold-ember-baths", "Overheard in the Steam")], "turning-gear": [("hold-turning-gear", "Turning Gear Tells")],
                "glimmerhall": [("hold-glimmerhall", "Glimmerhall Curios")], "mossbeard-remedies": [("hold-remedies", "What's in Mother Moss's Jar?")],
                "deep-script": [("hold-deep-script", "A Lesson in the Deep Script")]}


def strip(J, mp, mu, name):
    return (f'<div class="il-strip"><span><strong>Map:</strong> {J.L_scene(mp, name)}</span>'
            f'<span><strong>Music:</strong> {J.L_sound(mu, J.TRACK_TITLES[mu])}</span></div>')


def J_actor_name(k):
    for a in BE.ACTORS:
        if a["flags"][MOD]["key"] == k:
            return a["name"]
    return k
