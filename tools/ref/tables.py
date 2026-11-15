"""Rollable tables."""
from lib5e import *

TABLES = []


def table(key, name, formula, rows, desc="", img=None):
    tid = fid("table:" + key)
    results = []
    lo = 1
    for i, r in enumerate(rows):
        weight = 1
        text = r
        if isinstance(r, tuple):
            text, weight = r
        rid = fid(f"tr:{key}:{i}")
        results.append({"_id": rid, "type": "text", "name": "", "description": text, "text": text, "img": icon("tb-dice"),
                        "weight": weight, "range": [lo, lo + weight - 1], "drawn": False,
                        "_key": f"!tables.results!{tid}.{rid}"})
        lo += weight
    TABLES.append({"_id": tid, "name": name, "img": img or icon("tb-dice"), "description": desc, "formula": formula,
                   "replacement": True, "displayRoll": True, "results": results, "folder": None, "sort": len(TABLES) * 100,
                   "flags": {MOD: {"key": key}}, "_key": f"!tables!{tid}", "_stats": STATS})


table("festive-fines", "Festive Compliance Fines", "1d6", [
    "<strong>Insufficiently festive expression.</strong> 5 gp.", "<strong>Unauthorised humbuggery.</strong> 10 gp.",
    "<strong>Failure to reciprocate a seasonal greeting.</strong> 15 gp.", "<strong>Excessive use of sarcasm.</strong> 20 gp.",
    "<strong>Premeditated carolling without a licence.</strong> 50 gp.",
    "<strong>Displaying an unregistered magical beard.</strong> 100 gp."],
      "Sprocket Jingles' schedule of fines. Unenforceable: he cannot confiscate property for refusal.", icon("mc-fine"))
table("nine-gifts", "The Nine Gifts of Midwinter", "1d9", [
    uuid_item("everwarm-scarf", "The Everwarm Scarf") + ": resistance to cold damage for 1 hour.",
    uuid_item("candy-cane-mercy", "The Candy Cane of Mercy") + ": restore 5d8 + 5 HP once.",
    uuid_item("bell-perfect-timing", "The Bell of Perfect Timing") + ": +1d8 to a failed check or save.",
    uuid_item("jolly-soldier", "The Jolly Soldier") + ": a toy soldier ally for 1 hour.",
    uuid_item("stocking-holding", "The Stocking of Holding") + ": holds 50 lb.",
    uuid_item("gingerbread-champion", "The Gingerbread Champion") + ": 15 temporary HP.",
    uuid_item("star-good-fortune", "The Star of Good Fortune") + ": reroll one d20.",
    uuid_item("mirror-merriment", "The Mirror of Merriment") + ": cast disguise self once.",
    uuid_item("hearthlight-candle", "The Hearthlight Candle") + ": see invisibility for 10 minutes."],
      "Every gift carries the same contract (Form H-25). No gift has a hidden drawback.", icon("mc-gift"))
table("market-moments", "Midwinter Market Moments", "1d10", [
    "A brass reindeer loops drunkenly overhead, trailing sparks and a jaunty tune, and briefly gets stuck in a chimney.",
    "A Festive Clerk presents a child with a gift and a nine-page certificate. The child signs it in crayon.",
    "The snowman choir hits a high note about 'the timely settlement of outstanding accounts'.",
    "A candy cane sprouts from the cobbles with a sound like a cork popping; a dwarf trips over it and is fined.",
    "A beggar who was healed this morning is dancing. He has not yet read his contract.",
    "Two Watch constables argue over whether peppermint gutters count as a public hazard.",
    "A citizen gives away her gift to a stranger and is visibly relieved; a clerk scribbles furiously.",
    "A lantern flickers and, for a heartbeat, its glow is the colour of hellfire.",
    "Someone shouts that the pastries at Bramble's are free today. They are not. They never were.",
    "A gift box at the foot of the Midwinter tree wriggles, sneezes and is still."], "Flavour for Act I.")
table("red-dialogue", "The Red Clause's Dialogue", "1d12", [
    "\"Oh, a cautious one! How terribly unprofitable!\"", "\"A devil? My dear, I'm an executive!\"",
    "\"We believe in transparency. That's why our terms are printed in such wonderfully translucent ink.\"",
    "\"Bribery? Please! We call those expedited relationship fees.\"", "\"We prefer the term mandatory volunteer experience.\"",
    "\"They were given a wonderful opportunity to contribute. Some have been contributing for generations.\"",
    "\"You'll find that generosity is a remarkably expensive principle.\"",
    "\"Objection acknowledged. How delightfully inconvenient.\"", "\"Enough. The festivities are over.\"",
    "\"Now THAT is the spirit of giving.\"", "\"No. No, that cannot be correct. Read it again.\"",
    "\"You have no idea what my employer is going to do to me.\""], "", icon("rc-phase2"))
table("lair-actions", "Lair Actions (Initiative 20)", "1d3", [
    "<strong>Furnace Discharge.</strong> 40-ft by 10-ft line of hellfire: [[/save dexterity 18]], [[/damage 3d8 fire]] (half on success).",
    "<strong>Gift-Wrapped Restraints.</strong> 20-ft square of ribbons: [[/save dexterity 17]] or restrained until the end of its next turn.",
    "<strong>Blizzard of Fine Print.</strong> 20-ft radius: [[/save wisdom 17]] or disadvantage on its next d20 roll."],
      "Advance the bell first, then use one. Rotate rather than repeating.", icon("rc-furnace"))
table("workshop-horrors", "Workshop Horrors", "1d10", [
    "A worker hums the factory tune perfectly in her sleep, standing up, still sorting ribbons.",
    "A sign reads: <em>BREAKS ARE A PRIVILEGE. PRIVILEGES ARE A DEBT.</em>",
    "Every clock in the room shows 11:59, and every one of them is ticking.",
    "A collar-wheel squeaks somewhere behind you, and a sob stops mid-breath.",
    "A pile of children's mittens, each labelled with a name and a soul-coin value.",
    "A worker politely asks what year it is, then apologises for asking.",
    "The smell of cinnamon, and under it, something burning that is not wood.",
    "A conveyor carries a single wrapped box that whispers a lullaby in a grandmother's voice.",
    "A supervisor's ledger: <em>Employee 447 — gratitude quota exceeded. Reward: one additional night.</em>",
    "A worker's smile cracks for a second; you see the person underneath, and then they are gone again."],
      "Full-horror detail for Act III. Horror through coercion and indifference, not gore.", icon("rc-clock"))
table("confiscated-joys", "Confiscated Joys", "1d8", [
    "A toy that laughs in someone's late father's voice.", "A music box powered by a debtor's final happy thought.",
    "A scarf knitted from a wedding-day memory.", "A snow globe holding a first snowfall someone can no longer remember.",
    "A wooden horse that smells of a childhood kitchen.", "A candle that burns with the warmth of a first kiss.",
    "A pair of skates that remember a frozen lake and a held hand.",
    "A puppet that sings a lullaby in a voice its owner forgot existed."], "What the Assembly Line makes, and from what.")
table("clerk-names", "Festive Clerk Names", "1d20", [
    "Tinsel Grabwick", "Bauble Nethersnout", "Holly Vexgrin", "Jinglemoth", "Pinecrimp", "Sleetwhisker", "Mistle Gnashby",
    "Cinder Twinkletoe", "Ledgerbell", "Figgy Pudsworth", "Snapdragon Quill", "Ribbonrot", "Garland Spite", "Crumble",
    "Wassail Tick", "Nutcracker Grimes", "Yule Smallprint", "Frostnib", "Tally Sugarbane", "Wreathwick"])
table("fine-print", "Infernal Fine Print", "1d12", [
    "\"Kindness must be performed during business hours (11:00 to 11:01).\"",
    "\"Acts of kindness toward the foundation's own employees do not count.\"",
    "\"The foundation reserves the right to define 'genuine'.\"",
    "\"Snowfall constitutes acceptance.\"", "\"Smiling is considered a verbal agreement.\"",
    "\"Witnesses must themselves be in good standing with the foundation.\"",
    "\"Gratitude is non-refundable.\"", "\"All complaints shall be filed in triplicate, in Infernal, in person, in Nessus.\"",
    "\"This clause intentionally left blank.\"", "\"The recipient waives the right to read this clause.\"",
    "\"Merriment is mandatory; enthusiasm is assessed.\"",
    "<em>None of these appear on Form H-25. They are all on unauthorised supplemental notices, which is the point.</em>"],
      "Absurd 'supplemental' clauses the clerks wave about. None of them is in the actual contract.", icon("rc-fineprint"))
table("sleigh-complications", "Sleigh Chase Complications", "1d6", [
    "A chimney stack dead ahead: DC 16 Acrobatics or the sleigh clips it ([[/damage 3d10 bludgeoning]] to an exposed rider).",
    "A reindeer's harness snaps: DC 17 Athletics to hold the team, or lose speed (the pursuers close in).",
    "The Yule Enforcement Engine fires its net at the sleigh's runners.",
    "Washing lines full of festive bunting: DC 16 Dexterity save or a rider is tangled.",
    "The sleigh's infernal engine overheats: DC 17 Arcana or [[/damage 3d10 fire]] to the driver.",
    "A gap between rooftops that is wider than it looked: everyone makes a DC 16 Strength or Dexterity save."], "",
      icon("mc-challenge"))
table("satisfaction-survey", "Customer Satisfaction Survey", "1d6", [
    "How satisfied were you with the speed of your repossession?", "How would you rate the cheerfulness of your Jingle Bailiff?",
    "Was your soul handled with appropriate care?", "Would you recommend the Hearthlight Foundation to a friend, relative or enemy?",
    "How likely are you to accept a gift from us again?", "Please describe your eternal torment in five words or fewer."])
table("ledger-categories", "Ledger Categories", "1d8", [
    "UNASSIGNED MATERNAL AFFECTION — 14,000 soul-coins.", "UNCLAIMED PERSONAL ESSENCE — value pending arbitration.",
    "SURPLUS CHILDHOOD WONDER — bulk lot.", "DEPRECIATED HOPE (SLIGHTLY USED).", "RECOVERABLE GRATITUDE — 3 crates.",
    "LAPSED NEIGHBOURLINESS — written off.", "FIRST SNOWFALL MEMORIES — sorted by vintage.",
    "COURAGE (ONE SIZE FITS ALL) — out of stock."], "Entries in the Ledger of Abandoned Souls.", icon("rc-ledger"))
