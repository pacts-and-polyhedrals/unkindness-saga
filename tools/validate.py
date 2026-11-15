"""Validate the built module: files, links, ids, dnd5e keys, macro API calls."""
import json, glob, os, re, sys
ROOT = "/home/claude/saga/il"
M = f"{ROOT}/module"
MOD = "unkindness-saga"
problems = []
docs = {}
for f in glob.glob(f"{ROOT}/build/packs/*/*.json"):
    d = json.load(open(f))
    docs.setdefault(f.split("/")[-2], []).append(d)

ids = {"Actor": set(), "Item": set(), "JournalEntry": set(), "JournalEntryPage": set(), "RollTable": set(), "Macro": set(),
       "Playlist": set(), "PlaylistSound": set(), "Cards": set(), "Scene": set()}
TYPE = {"actors": "Actor", "items": "Item", "spells": "Item", "journals": "JournalEntry", "tables": "RollTable", "macros": "Macro",
        "playlists": "Playlist", "cards": "Cards"}
for pack, ds in docs.items():
    for d in ds:
        if d.get("_key", "").startswith("!folders"):
            continue
        ids[TYPE[pack]].add(d["_id"])
        for p in d.get("pages", []):
            ids["JournalEntryPage"].add(p["_id"])
        for s in d.get("sounds", []):
            ids["PlaylistSound"].add(s["_id"])
sc = json.load(open(f"{M}/data/scenes.json"))
for s in [sc["landing"], sc["section"]] + sc["scenes"]:
    ids["Scene"].add(s["id"])


def walk(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)
    elif isinstance(o, str):
        yield o


def check_path(p, where):
    if p.startswith(f"modules/{MOD}/"):
        if not os.path.exists(f"{M}/{p[len(MOD) + 9:]}"):
            problems.append(f"missing file {p} ({where})")


DMG = {"acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", "piercing", "poison", "psychic", "radiant", "slashing", "thunder", "healing", "temphp"}
for pack, ds in docs.items():
    for d in ds:
        nm = d.get("name")
        for s in walk(d):
            for p in re.findall(r"modules/unkindness-saga/[\w\-/\.]+\.(?:webp|ogg|png|svg)", s):
                check_path(p, f"{pack}:{nm}")
            for m in re.finditer(r"@UUID\[([^\]]+)\]", s):
                parts = m.group(1).split(".")
                if parts[0] == "Compendium":
                    continue
                for t, i in zip(parts[0::2], parts[1::2]):
                    if i not in ids.get(t, set()):
                        problems.append(f"broken link {m.group(1)} in {pack}:{nm}")
        for s in walk(d):
            pass
        # damage types
        def dmgcheck(o):
            if isinstance(o, dict):
                if "types" in o and isinstance(o["types"], list) and ("denomination" in o or "custom" in o):
                    for t in o["types"]:
                        if t not in DMG:
                            problems.append(f"bad damage type {t} in {nm}")
                for v in o.values():
                    dmgcheck(v)
            elif isinstance(o, list):
                for v in o:
                    dmgcheck(v)
        dmgcheck(d)

for s in [sc["landing"], sc["section"]] + sc["scenes"]:
    check_path(s["src"], s["key"])
    if s["playlist"] not in ids["Playlist"] or s["sound"] not in ids["PlaylistSound"]:
        problems.append(f"scene music missing {s['key']}")
    for t in s.get("tokens", []):
        if t["actorId"] not in ids["Actor"]:
            problems.append(f"scene token actor missing {s['key']}")
    for n in s.get("notes", []):
        if n["entryId"] not in ids["JournalEntry"] or n["pageId"] not in ids["JournalEntryPage"]:
            problems.append(f"scene note broken {s['key']}")

js = open(f"{M}/scripts/ironfist.mjs").read()
api = re.search(r"const API = \{(.*?)\};", js, re.S).group(1)
names = set(re.findall(r"(\w+)(?=[,:\s])", api))
for d in [x for x in docs["macros"] if "command" in x]:
    for call in re.findall(r"api\.(\w+)", d["command"]):
        if call not in names:
            problems.append(f"macro {d['name']} calls missing api.{call}")
mj = json.load(open(f"{M}/module.json"))
for p in mj["packs"]:
    if not os.path.isdir(f"{M}/{p['path']}"):
        problems.append(f"pack dir missing {p['path']}")
for f in mj["esmodules"] + mj["styles"]:
    if not os.path.exists(f"{M}/{f}"):
        problems.append(f"missing {f}")
for url in re.findall(r'url\("\.\./([^"]+)"\)', open(f"{M}/styles/ironfist.css").read()):
    if not os.path.exists(f"{M}/{url}"):
        problems.append(f"css url missing {url}")
print("\n".join(problems[:60]))
print(f"{len(problems)} problems; docs: " + ", ".join(f"{k} {len(v)}" for k, v in docs.items()))
sys.exit(1 if problems else 0)
