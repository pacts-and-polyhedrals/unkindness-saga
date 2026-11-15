"""Evidence, story items, runic materials, rune templates, rewards and the twelve rune spells."""
import json, re, os
from lib5e import *
from cards_data import DECKS

LEG = os.path.join(os.path.dirname(__file__), "legacy")


def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


def box(inner, cls="il-item"):
    return f'<div class="{cls}">{inner}</div>'


ITEMS = {}


def add(folder, doc):
    ITEMS.setdefault(folder, []).append(doc)
    return doc


# ---------------------------------------------------------------- evidence
EVID = {c[0]: c for c in DECKS["evidence"]["cards"]}
HANDOUT_FOR = {"e3": "h2", "e4": "h3", "e5": "h4", "e6": "h5"}
WHERE = {
    "e1": "Tovik's dated gauge sheet (2.1); the sluice flow markers; Runa's diagrams; Urzha and Skrik's well records.",
    "e2": "Odran's provisioning office and Venn's archive (3.2).",
    "e3": "The military archive's locked cabinet (3.4); Dagnner's duplicate; Baldrik's own admission.",
    "e4": "The Cinder-Tusk copy, presented at the filter station (4.2), matched to the dwarven copy in the archive.",
    "e5": "The lower exchange during the pressure test or the controlled inspection (5.5); Dagnner's duplicate dispatch (6.3).",
    "e6": "Runa and Skrik compare drawings in front of witnesses (6.1). Either engineer's separate drawings, or a competent PC's work, establish the same conclusion.",
    "e7": "A clan scout's copied assault order (4.6); orders carried by a tunnel captain.",
}
for k, (ck, title, ic, tags, body, foot) in EVID.items():
    add("Evidence (E1–E7)", item("ev-" + k, title, "loot", box(
        P(f"<strong>Proves:</strong> {body}", f"<strong>Limits:</strong> {foot}", f"<strong>Issue tags:</strong> {tags}",
          f"<strong>Where it can be found:</strong> {WHERE[k]}",
          "Copies are valid evidence when authenticated. Truth magic helps verify testimony but cannot establish facts an honest witness never knew.")),
        img=icon(ic), subtype="", flags={MOD: {"evidenceId": k.upper(), "evidenceTags": [t.strip() for t in tags.split("·")], "key": "ev-" + k}}))

# ---------------------------------------------------------------- story items
STORY = [
    ("commission", "Honorary Ironfist Commission", "it-commission",
     "A ceremonial commission offering rank, salary and residence. The fine print obliges its holder to obey lawful military orders, disclose operational research undertaken with military resources, and speak only within an assigned remit. Hadrik wants to stretch those clauses to cover Thorgrinn's body; that interpretation is disputed, not a fact of the setting. It is not a magical contract. The correction of the death register is a separate proceeding."),
    ("register", "The Corrected Death Register", "it-register",
     "Thorgrinn Ironfist. Former auxiliary service: Neverwinter. Previous status: deceased, reported by Captain Baldrik Ironfist. Correction entered upon personal return and corroborating witnesses. Current service status: to be determined separately. No new commission is implied by this correction."),
    ("two-rivet-shield", "The Two-Rivet Shield", "it-shield",
     "The shield the brothers repaired when they were too poor to hire a smith — one bronze rivet, one iron. Baldrik still carries it. It is a family symbol first. It becomes a gift only with both brothers' consent; taking it apart for the Shieldmate's Rivet requires the same."),
    ("pressure-key", "Heartworks Release Key", "it-key",
     "A heavy three-toothed key held by the Vanguard Redoubt's duty officer. At a Heartworks regulator station it provides one automatic progress."),
    ("bastion-manual", "Last Bastion Operating Manual", "it-manual",
     "The original operating manual for the three-station network: the reservoir wheel feeds the circuit, the relief channel releases pressure safely, the reversal brake locks the arrangement. All three must be set together. Kept in the redoubt's reinforced desk (AC 17, 30 HP, or DC 16 tools); its case protects the contents."),
    ("deepwell-accord", "Deepwell Accord (Draft)", "it-compact",
     "A writable treaty framework: who controls each valve, how prisoners are exchanged, who witnesses compliance, and what happens when either side breaches it. Fill it in at the table during 4.6 and again at 8.4."),
    ("clay-filter", "Clay Filter and Ration Tally", "it-filter",
     "Carried by a captured raider at the Ninth Sluice: a homemade water filter and a family ration tally showing the wells failing after the diversion. Corroborates E1; cannot by itself prove Hadrik's intent."),
    ("sluice-roster", "The Missing Shift's Roster", "it-ration",
     "Tovik's list of the shift still below the Ninth Sluice: Hild, Borri, Masa, Grenn, Tuvi and Oskar. Read the names aloud. The rescue is about people."),
    ("kharad-varr-sketch", "Soldier's Sketch of Kharad-Varr", "it-map",
     "A vertical sketch of the hold from the Fifth Finger to the Heartworks. Not to scale. Add lower routes as the party learns them."),
]
for k, n, ic, d in STORY:
    add("Story Items", item("story-" + k, n, "loot", box(P(d)), img=icon(ic), flags={MOD: {"key": "story-" + k}}))

# ---------------------------------------------------------------- materials, rune templates, rewards
legacy_items = json.load(open(f"{LEG}/items.json"))["items"]
MATS = {"deep-silver": 100, "emberglass": 150, "oathstone": 200, "sky-iron": 500, "hearthstone": 75, "ironbone": 250}
for x in legacy_items:
    sid = x["sourceId"]
    if sid.startswith("il.material."):
        k = sid.split(".")[-1]
        text = re.sub(r"<[^>]+>", " ", x["system"]["description"]["value"]).replace("◆ ◈ ◆", "").strip()
        text = text.split(x["name"], 2)[-1].strip(" —")
        add("Runic Materials", item("mat-" + k, x["name"], "loot", box(P(text, "Used in Bound and Crowned rune grades; see <em>The Deep Runes</em>.")),
                                    img=icon("mat-" + k), price=MATS[k], flags={MOD: {"runicMaterial": True, "key": "mat-" + k}}))

RUNES = json.load(open(f"{LEG}/runes.json"))["runes"]
for code, r in RUNES.items():
    k = code.lower()
    d = (P(f"<strong>{r['name']}</strong>") +
         f'<table class="il-table"><tr><th>Grade</th><th>Effect</th></tr>'
         f'<tr><td><strong>Cut</strong> (DC 13, 4 hours, 50 gp)</td><td>{r["cut"]}</td></tr>'
         f'<tr><td><strong>Bound</strong> (DC 16, 8 hours, 250 gp + special material)</td><td>{r["bound"]}</td></tr>'
         f'<tr><td><strong>Crowned</strong> (DC 19, 24 hours, 1,000 gp + rare material and a prepared forge)</td><td>{r["crowned"]}</td></tr></table>'
         + P("Use the <strong>Rune Forge</strong> macro with the crafter's token selected to cut this rune; on a success the grade's effect is added to that character as a feature."))
    add("Rune Templates", feat("rune-" + k, r["name"], box(d), img=icon("rune-" + k), ftype="", flags={MOD: {"runeCode": code, "key": "rune-" + k}}))

k = "reward-rivet"
add("Rewards", item(k, "Shieldmate's Rivet", "equipment", box(P(
    "<em>Wondrous item, rare (no attunement).</em> One worn rivet or badge — a single item for the party, not a free copy for everyone.",
    "Once per long rest, when a willing ally within 10 feet of you takes damage, you can use your reaction to reduce that damage by 1d10 + your proficiency bonus. It doesn't stack with another copy against the same instance.",
    "It can be made from a new piece of metal. Taking Baldrik's old shield apart for it requires his and Thorgrinn's consent. It represents protection offered, not obedience owed.")),
    img=icon("it-rivet"), rarity="rare", subtype="trinket",
    activities=[heal_act(k, 0, formula_part=dmg_formula("1d10 + @prof"), act=activation("reaction", 1, "A willing ally within 10 feet takes damage"),
                         tgt=target(1, "ally"), temp=True, consumption=consume_item_uses())],
    uses_=uses(1, ["lr"]), flags={MOD: {"key": k}}))
add("Rewards", item("reward-chisel", "Stone-Script Chisel", "tool", box(P(
    "<em>Tool, uncommon.</em> A masterwork runecarver's chisel. Once per long rest, while using it for runic crafting, a proficient crafter may treat a failure by 1 or 2 as a success that gains a Crafting Complication.")),
    img=icon("it-chisel"), rarity="uncommon", price=500, flags={MOD: {"key": "reward-chisel"}}))
add("Rewards", item("reward-badge", "Badge of the Open Gate", "loot", box(P(
    "Struck after the settlement for those who held a gate open rather than shut. Grants reciprocal travel rights where negotiated, a safe base in Lowhearth and the trust of named craftspeople. Optional home for the Shieldmate's Rivet.")),
    img=icon("it-badge"), flags={MOD: {"key": "reward-badge"}}))

# ---------------------------------------------------------------- spells
SCHOOL = {"TRS": "trs", "ABJ": "abj", "DIV": "div", "EVO": "evo", "CON": "con"}
legacy_spells = json.load(open(f"{LEG}/spells.json"))["spells"]
SPELLS = []


def _dur(s):
    s = s.strip()
    conc = s.lower().startswith("concentration")
    if "Instantaneous" in s:
        return {"value": "", "units": "inst"}, conc
    m = re.search(r"(\d+)\s*(minute|hour|round)", s)
    if m:
        return {"value": m.group(1), "units": {"minute": "minute", "hour": "hour", "round": "round"}[m.group(2)]}, conc
    return {"value": "", "units": "spec", "special": s}, conc


def _range(s):
    s = s.strip()
    if s.startswith("Touch"):
        return rng("", "touch")
    if s.startswith("Self"):
        return rng("", "self", s)
    m = re.match(r"(\d+)", s)
    return rng(m.group(1) if m else "", "ft")


DAMAGE = {"hammerfall": ("dex", "4d8", "thunder"), "returning-hammer": None}
for x in legacy_spells:
    key = x["sourceId"].split(".")[-1]
    html = x["system"]["description"]["value"]
    text = re.sub(r"<[^>]+>", "|", html)
    body = html.split("</h2>", 1)[1].split("<p><strong>Level")[0]
    meta = dict(re.findall(r"<strong>(\w+):</strong>\s*([^&<]+)", html))
    lvl = x["system"]["level"]
    dur, conc = _dur(meta.get("Duration", ""))
    cast = meta.get("Casting", "action").strip()
    act = activation({"action": "action", "bonus": "bonus", "reaction": "reaction", "ritual": "minute"}[cast], 10 if cast == "ritual" else 1)
    acts_ = []
    if key == "hammerfall":
        acts_.append(save("sp-" + key, 0, ability="dex", parts=[dmg(4, 8, "", ["thunder"], "whole", 1)], spell=True,
                          tgt=target("", "creature", "sphere", 10)))
    elif key == "stoneward-script":
        acts_.append(heal_act("sp-" + key, 0, formula_part=dmg_formula("1d8 + @mod"), act=act, tgt=target(1, "creature")))
    elif key == "oath-rune":
        acts_.append(heal_act("sp-" + key, 0, formula_part=dmg_formula("3"), act=act, tgt=target(2, "ally"), temp=True))
    else:
        acts_.append(utility("sp-" + key, 0, act=act))
    SPELLS.append(spell("sp-" + key, x["name"], box(body + P(
        f"<em>{('Cantrip' if lvl == 0 else f'Level {lvl}')} · {meta.get('School', '').strip()} · Casting: {cast} · Duration: {meta.get('Duration', '').strip()} · Range: {meta.get('Range', '').strip()}</em>",
        "Rune magic of Kharad-Varr. Available to artificers, clerics, wizards and any character who learns it from an Ironfist runecarver (GM's call).")),
        img=icon("sp-" + key), level=lvl, school=SCHOOL[meta.get("School", "ABJ").strip()], activities=acts_,
        comps=("vocal", "somatic", "material") if lvl >= 3 else ("vocal", "somatic"), materials="chalk or a chisel" if lvl < 3 else "a chisel and powdered emberglass",
        act=act, duration=dur, rng_=_range(meta.get("Range", "")), ritual=(cast == "ritual"), concentration=conc))
