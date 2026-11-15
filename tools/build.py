"""Build Part II of The Unkindness Saga (Ironfist Legacy) — pack sources, scenes.json, inheritance.json; compile with the Foundry CLI.
Part I (The Cat and the Unkindness) ships as static data in module/data/ravenloft and module/assets/ravenloft."""
import json, os, shutil, subprocess, sys, copy, re
ROOT = "/home/claude/saga/il"
sys.path.insert(0, f"{ROOT}/src")
from lib5e import *
import bestiary, items_spells, journals, misc, schedule as SC
import inheritance
import hold
import p1_actors
import spellbooks
import p1_tokens
import p1_inhabitants
print('Part I inhabitants (scenes, creatures):', p1_inhabitants.write(f'{ROOT}/module/data/ravenloft/inhabitants.json'))
print('Part I tokens (scenes, tokens):', p1_tokens.write(f'{ROOT}/module/data/ravenloft/tokens.json'))
CR2_FIX = {"odran": 4, "dagnner": 5, "tovik": 1, "heddra": 0.5}
SAVES2 = {"odran": ("wis", "cha"), "dagnner": ("str", "con"), "edda": ("str", "con"), "runa": ("int", "wis"), "yrsa": ("wis", "cha"),
          "urzha": ("con", "wis"), "skrik": ("dex", "int"), "ketta": ("dex", "int")}
for _a in bestiary.ACTORS:
    _k = _a["flags"][MOD]["key"]
    for _ab in SAVES2.get(_k, ()):
        _a["system"]["abilities"][_ab]["proficient"] = 1
    hp_formula(_a["system"])
    if _k == "bastion-engine":
        _a["system"]["attributes"]["senses"]["tremorsense"] = 60
    if _k in CR2_FIX:
        _a["system"]["details"]["cr"] = CR2_FIX[_k]
    if _k in spellbooks.SPELLBOOKS:
        _bk = spellbooks.SPELLBOOKS[_k]
        _a["system"]["attributes"]["spellcasting"] = _bk["ability"]
        _a["system"]["details"]["spellLevel"] = _bk["level"]
        _a["items"].append(feat(f"{_k}-spellcasting", "Spellcasting", f"<p>{_bk['note']} The spells are on the Spells tab (added at setup from the dnd5e compendiums and this module's rune spells).</p>", img=icon("ab-scroll"), sort=900000))
print('spellbooks (creatures, spells):', spellbooks.write(f'{ROOT}/module/data/spellbooks.json'))
print('Part I stat blocks (actors, items):', p1_actors.build())
from playlists_data import PLAYLISTS

MODDIR = f"{ROOT}/module"
SRC = f"{ROOT}/build/packs"
VERSION = "2.1.9"
REPO = "https://github.com/pacts-and-polyhedrals/unkindness-saga"

shutil.rmtree(SRC, ignore_errors=True)
os.makedirs(SRC)
PACKDOCS = {}


def folder(pack, name, ftype, parent=None, color="#4a0c10", sort=0):
    fidv = fid(f"folder:{pack}:{name}:{parent}")
    PACKDOCS.setdefault(pack, []).append({"_id": fidv, "name": name, "type": ftype, "folder": parent, "sorting": "m",
                                          "sort": sort, "color": color, "description": "", "flags": {},
                                          "_key": f"!folders!{fidv}", "_stats": STATS})
    return fidv


def add(pack, doc, fold=None):
    d = copy.deepcopy(doc)
    d["folder"] = fold
    PACKDOCS.setdefault(pack, []).append(d)


COLORS = ["#4a0c10", "#6a4a1a", "#3a5014", "#2c3a4a", "#3a2a50", "#5a3a14", "#26262e"]
for i, (fname, actors) in enumerate(bestiary.FOLDERS.items()):
    f = folder("actors", fname, "Actor", sort=i * 1000, color=COLORS[i % len(COLORS)])
    for j, a in enumerate(actors):
        a["sort"] = j * 100
        add("actors", key_items(a), f)
for i, (fname, docs) in enumerate(items_spells.ITEMS.items()):
    f = folder("items", fname, "Item", sort=i * 1000, color=COLORS[i % len(COLORS)])
    for j, d in enumerate(docs):
        d["sort"] = j * 100
        add("items", key_item(d), f)
LV = {0: "Cantrips", 1: "1st Level", 2: "2nd Level", 3: "3rd Level", 4: "4th Level", 5: "5th Level"}
lvf = {}
for s in items_spells.SPELLS:
    lv = s["system"]["level"]
    if lv not in lvf:
        lvf[lv] = folder("spells", LV[lv], "Item", sort=lv * 100, color="#2c3a4a")
    add("spells", key_item(s), lvf[lv])
jf = {}
for j in journals.build_docs():
    fn = j["folder"]
    if fn not in jf:
        jf[fn] = folder("journals", fn, "JournalEntry", sort=len(jf) * 1000, color=COLORS[len(jf) % len(COLORS)])
    add("journals", j, jf[fn])
tf = {}
for t in misc.TABLES:
    fn = t["folder"]
    if fn not in tf:
        tf[fn] = folder("tables", fn, "RollTable", sort=len(tf) * 1000)
    add("tables", t, tf[fn])
mf = {}
TOOLS = folder("macros", "Individual tools (all on the DM Control Board)", "Macro", sort=5000)
for m in misc.MACROS:
    fn = m["folder"]
    if fn not in mf:
        mf[fn] = folder("macros", fn, "Macro", parent=None if fn.startswith("★") else TOOLS, sort=len(mf) * 1000)
    add("macros", m, mf[fn])
for p in misc.PLAYLIST_DOCS:
    add("playlists", p, None)
for c in misc.CARDS:
    add("cards", c, None)

for pack, docs in PACKDOCS.items():
    os.makedirs(f"{SRC}/{pack}", exist_ok=True)
    for d in docs:
        name = re.sub(r"[^A-Za-z0-9]+", "_", d["name"])[:50] + "_" + d["_id"]
        json.dump(d, open(f"{SRC}/{pack}/{name}.json", "w"), ensure_ascii=False)

# ---------------------------------------------------------------- scenes.json
raw = json.load(open(f"{ROOT}/src/scenes.json"))
actor_ids = {a["flags"][MOD]["key"]: a["_id"] for a in bestiary.ACTORS}
page_ids = {}
for j in journals.build_docs():
    for p in j["pages"]:
        page_ids[(j["flags"][MOD]["key"], p["flags"][MOD]["key"])] = (j["_id"], p["_id"])
PLAYLIST_OF = {t: pl for pl, ts in PLAYLISTS.items() for t in ts}
start = fid("journal:start")
out = {"landing": {"key": "title", "id": fid("scene:title"), "title": "The Shield Between Us", "order": 0,
                   "src": f"modules/{MOD}/assets/art/title.webp", "width": 1920, "height": 1080, "grid": 0,
                   "env": {"darkness": 0, "globalLight": True}, "journal": start, "journalPage": fid("page:start:welcome"),
                   "playlist": fid("playlist:" + PLAYLIST_OF["the-shield-between-us"]), "sound": fid("sound:the-shield-between-us")},
       "section": {"key": "section", "id": fid("scene:section"), "title": "Kharad-Varr (Player Sketch)", "order": 1,
                   "src": f"modules/{MOD}/assets/art/kharad-varr-section.webp", "width": 1920, "height": 1080, "grid": 0,
                   "env": {"darkness": 0, "globalLight": True}, "journal": fid("journal:handouts"), "journalPage": fid("page:handouts:sketch"),
                   "playlist": fid("playlist:" + PLAYLIST_OF["beyond-the-last-mist"]), "sound": fid("sound:beyond-the-last-mist")},
       "scenes": []}
for i, k in enumerate(SC.MAP_ORDER, 2):
    s = raw[k]
    notes = []
    for n in s["notes"]:
        jk, pk = n["page"].split(":")
        assert (jk, pk) in page_ids, (k, n["page"])
        jid, pid = page_ids[(jk, pk)]
        notes.append({"x": n["x"], "y": n["y"], "label": n["label"], "entryId": jid, "pageId": pid})
    toks = []
    for t in s["tokens"]:
        assert t["actor"] in actor_ids, t["actor"]
        toks.append({"actorId": actor_ids[t["actor"]], "x": t["x"], "y": t["y"], "hidden": t["hidden"], "name": t["name"]})
    mus = SC.SCENE_MAP_DEFAULT_MUSIC[k]
    out["scenes"].append({"key": k, "id": fid("scene:" + k), "title": f"{i - 1:02d} · {SC.MAP_TITLES[k]}", "order": i,
                          "src": f"modules/{MOD}/assets/maps/{k}.webp", "width": s["width"], "height": s["height"],
                          "grid": s["grid"], "walls": s["walls"], "lights": s["lights"], "notes": notes, "tokens": toks,
                          "env": s["env"], "journal": notes[0]["entryId"] if notes else None, "journalPage": notes[0]["pageId"] if notes else None,
                          "playlist": fid("playlist:" + PLAYLIST_OF[mus]), "sound": fid("sound:" + mus)})
# the Hold: overview + eight venues (after the story maps; ids by key, so numbering is stable)
for i, k in enumerate(hold.HOLD_ORDER):
    s = raw[k]
    notes = []
    for n in s["notes"]:
        jk, pk = n["page"].split(":")
        assert (jk, pk) in page_ids, (k, n["page"])
        jid, pid = page_ids[(jk, pk)]
        notes.append({"x": n["x"], "y": n["y"], "label": n["label"], "entryId": jid, "pageId": pid})
    toks = []
    for t in s["tokens"]:
        assert t["actor"] in actor_ids, t["actor"]
        toks.append({"actorId": actor_ids[t["actor"]], "x": t["x"], "y": t["y"], "hidden": t["hidden"], "name": t["name"]})
    mus = hold.HOLD_MUSIC[k]
    jid, pid = page_ids[("hold", "start" if k == "hold-map" else k)]
    out["scenes"].append({"key": k, "id": fid("scene:" + k), "title": f"H{i} · {hold.HOLD_MAP_TITLES[k]}", "order": 100 + i,
                          "src": f"modules/{MOD}/assets/maps/{k}.webp", "width": s["width"], "height": s["height"],
                          "grid": s["grid"], "walls": s["walls"], "lights": s["lights"], "notes": notes, "tokens": toks,
                          "env": s["env"], "journal": jid, "journalPage": pid,
                          "playlist": fid("playlist:" + PLAYLIST_OF[mus]), "sound": fid("sound:" + mus)})
os.makedirs(f"{MODDIR}/data", exist_ok=True)
json.dump(out, open(f"{MODDIR}/data/scenes.json", "w"))

# ---------------------------------------------------------------- module.json
GMO = {"PLAYER": "NONE", "ASSISTANT": "OWNER"}
PLO = {"PLAYER": "OBSERVER", "ASSISTANT": "OWNER"}
packs = [
    ("journals", "JournalEntry", "Adventure Book & Journals", GMO),
    ("actors", "Actor", "Actors: Cast & Encounter Profiles", GMO),
    ("items", "Item", "Evidence, Story Items, Runes & Rewards", PLO),
    ("spells", "Item", "Rune Spells", PLO),
    ("tables", "RollTable", "Roll Tables", GMO),
    ("macros", "Macro", "Macros", GMO),
    ("playlists", "Playlist", "Music & Sound Effects", GMO),
    ("cards", "Cards", "Card Decks", GMO),
]
module = {
    "id": MOD, "title": "The Shield Between Us: Ironfist Legacy",
    "description": "<p>A Curse of Strahd continuation for D&amp;D 5e (levels 11–13): Thorgrinn Ironfist comes home in a body of metal to "
                   "Kharad-Varr, a dwarven stratocracy on the edge of an orc-and-goblin war. Eight chapters played across twelve weekly "
                   "sessions; fifteen staged vector battlemaps with walls, lights, pins, tokens and music; the full cast as working dnd5e "
                   "actors; evidence politics, rune magic and forgecraft; original music; roll tables; four card decks; and GM tools "
                   "for hearings, work challenges, countdowns and the Last Bastion. One-click setup.</p>",
    "version": VERSION,
    "authors": [{"name": "Asmo, Pacts & Polyhedrals (Ben Vale)", "url": "https://www.patreon.com/pactsandpolyhedrals"}],
    "compatibility": {"minimum": "13", "verified": "14"},
    "relationships": {"systems": [{"id": "dnd5e", "type": "system", "compatibility": {"minimum": "5.0.0", "verified": "5.3.3"}}]},
    "esmodules": ["scripts/main.mjs"], "styles": ["styles/ironfist-legacy.css"],
    "languages": [{"lang": "en", "name": "English", "path": "lang/en.json"}],
    "packs": [{"name": n, "label": l, "path": f"packs/{n}", "type": t, **({"system": "dnd5e"} if t in ("Actor", "Item") else {}), "ownership": o, "flags": {}}
              for n, t, l, o in packs],
    "packFolders": [{"name": "The Shield Between Us: Ironfist Legacy", "sorting": "m", "color": "#4a0c10",
                     "packs": [p[0] for p in packs], "folders": []}],
    "media": [{"type": "cover", "url": f"modules/{MOD}/assets/art/title.webp"},
              {"type": "icon", "url": f"modules/{MOD}/assets/icons/il-title.webp"}],
    "url": REPO, "manifest": f"{REPO}/releases/latest/download/module.json",
    "download": f"{REPO}/releases/download/v{VERSION}/{MOD}.zip",
    "readme": f"{REPO}/blob/main/README.md", "changelog": f"{REPO}/blob/main/CHANGELOG.md",
    "bugs": f"{REPO}/issues", "license": "LICENSE", "flags": {}
}
# The combined module (Part I + Part II) owns module.json; only keep its version in step.
_mj = json.load(open(f"{MODDIR}/module.json"))
_mj["version"] = VERSION
_mj["download"] = f"{REPO}/releases/download/v{VERSION}/{MOD}.zip"
json.dump(_mj, open(f"{MODDIR}/module.json", "w"), indent=2, ensure_ascii=False)
os.makedirs(f"{MODDIR}/lang", exist_ok=True)
json.dump({"IFL.Title": "The Shield Between Us: Ironfist Legacy", "IFL.Manager": "Ironfist Legacy Manager"}, open(f"{MODDIR}/lang/en.json", "w"), indent=2)

shutil.rmtree(f"{MODDIR}/packs", ignore_errors=True)
js = f"""
import {{ compilePack }} from '@foundryvtt/foundryvtt-cli';
const packs = {json.dumps([p[0] for p in packs])};
for (const p of packs) await compilePack('{SRC}/' + p, '{MODDIR}/packs/' + p, {{ log: false }});
console.log('compiled', packs.length);
"""
open(f"{ROOT}/tools/compile.mjs", "w").write(js)
r = subprocess.run(["node", f"{ROOT}/tools/compile.mjs"], cwd=ROOT, capture_output=True, text=True)
print(r.stdout, r.stderr[-2000:])
print({k: len(v) for k, v in PACKDOCS.items()})
