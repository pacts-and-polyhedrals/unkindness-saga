"""Roll tables, macros, card decks and playlists."""
from lib5e import *
from cards_data import DECKS
from playlists_data import PLAYLISTS, TRACK_TITLES, SFX

# ============================================================================ roll tables
TABLES = []


def table(key, name, rows, desc="", img="tb-dice", folder="At the Table"):
    tid = fid("table:" + key)
    results = []
    lo = 1
    for i, r in enumerate(rows):
        text, weight = (r if isinstance(r, tuple) else (r, 1))
        rid = fid(f"tr:{key}:{i}")
        results.append({"_id": rid, "type": "text", "name": "", "description": text, "text": text, "img": icon(img),
                        "weight": weight, "range": [lo, lo + weight - 1], "drawn": False,
                        "_key": f"!tables.results!{tid}.{rid}"})
        lo += weight
    TABLES.append({"_id": tid, "name": name, "img": icon(img), "description": desc, "formula": f"1d{lo - 1}",
                   "replacement": True, "displayRoll": True, "results": results, "folder": folder, "sort": len(TABLES) * 100,
                   "flags": {MOD: {"key": key}}, "_key": f"!tables!{tid}", "_stats": STATS})


T1, T2, T3 = "Names & Faces", "Life in the Hold", "War & Machinery"
table("dwarf-names", "Ironfist Names", [
    "Hild Copperbrow", "Borri Nailfast", "Masa Ironwick", "Grenn Deepgauge", "Tuvi Coalbraid", "Oskar Slatehand", "Yeln Brassmantle (no relation, she insists)",
    "Daga Flintward (a cousin, lower tier)", "Torvald Rivetson", "Sigrun Ashgrip", "Kell Hammerline", "Ostra Lampwright", "Brannoc Stoneclerk",
    "Mirri Ninth-Shift", "Haldor Sluicewarden", "Eskil Two-Lifts"], "Lowhearth workers, soldiers and clerks. Rank-holders give clan names; labourers often give their shift.", "ab-fist", T1)
table("cinder-names", "Cinder-Tusk Names", [
    "Gashra (orc, well-keeper)", "Tiv (goblin, pump runner)", "Morg Ashtooth (orc, cook)", "Ezzi (goblin, mushroom farmer)", "Ulka Deepwell (orc, Urzha's niece)",
    "Snark (goblin, fuse-maker)", "Hura Brightjaw (orc, midwife)", "Pell (goblin, cartographer's apprentice)", "Drogga (orc, retired raider)",
    "Kizz (goblin, lamp-tender)", "Vorna (orc, caravan driver)", "Nib (goblin, child, very curious)"],
                   "Neither ancestry predicts loyalty, kindness or competence.", "ab-tusk", T1)
table("npc-habits", "One Job, One Habit", [
    "Counts everyone in the room twice.", "Taps a rivet on their collar when lying — and when nervous, which is worse.",
    "Quotes regulation numbers instead of opinions.", "Offers food before answering anything.", "Speaks only to Thorgrinn, never to his body.",
    "Asks “May I?” before touching anything, a habit learned from a medic.", "Keeps a soot-blackened tally of the dead on their sleeve.",
    "Hums the Hearthwatch tune without noticing.", "Refuses to sit below the salt.", "Calls every officer “sir,” including the goblins."],
      "For minor actors: give each one job and one memorable habit.", "ab-scroll", T1)
table("feast-toasts", "Hammerhall Feast: Toasts & Questions", [
    "A veteran asks how you fought a vampire lord in his own castle — tactics, not glory.", "A singer gets a detail of your deeds amusingly wrong and invites correction.",
    "A smith offers to repair a dented piece of armour by morning, free.", "Someone toasts “the dead who came back,” then goes pale and apologises.",
    "A child asks Thorgrinn if his hands are cold.", "A council clerk asks Damien for a written account “for the archive.”",
    "Lowhearth workers in the gallery cheer when Heddra sits at the high table.", "A Vanguard soldier asks Legna whether the Raven Queen keeps a ledger.",
    "Bunch is asked to play; the drummers fall in behind.", "An old priest asks Vesper what Barovia's gods were like."],
      "Make the celebration sincere (1.4).", "ab-rally", T2)
table("lowhearth-rumours", "Lowhearth Rumours", [
    "The lower wells taste of iron and rot since the spring. True.", "The Cinder-Tusk poisoned them. False — the diversion did.",
    "Runa got her sash because Baldrik paid for it. Half true: Baldrik's money repaired the house; Runa earned the sash.",
    "The Vanguard executed its own deserters on the Neverwinter road. True.", "Hadrik wants a hero's face on his war. True.",
    "There's a service stair nobody guards. True — it's how the workers move when the lifts stop.",
    "The generals eat fresh bread every day. True.", "Korga only wants water. False — he wants the upper gates.",
    "The Ninth Sluice was built over an old treaty stone. True.", "A metal dwarf came out of the mist and he's a weapon. Rumour; the module never makes it true."],
      "Hear these at the ration hall, the shrine or the lift queue.", "ab-kitchen", T2)
table("road-moments", "The Mountain Road (non-hostile)", [
    "A road crew offers water and directions; their foreman recognises the Ironfist emblem on Thorgrinn's plating.",
    "Pine needles, cold wind and no voice whispering your names. Someone laughs for no reason.",
    "A courier runs past, shouting “Fifth Finger! Returning kin!” — the story is already moving faster than you.",
    "A mile-post carved with a fist and a nail: KHARAD-VARR 12.", "Goats on a ledge. A goatherd who has never heard of Barovia.",
    "A shrine at a switchback with fresh bread left for travellers."], "No ambushes: the road is a welcome (1.1).", "ab-lantern", T2)
table("hearthwatch-names", "Hearthwatch Lanterns", [
    "Grenn's father, lost when the lift failed in summer.", "Two children of the Ninth Shift — the bad well.", "A Vanguard scout killed on the Barovian road.",
    "Old Ostra the lamp-tender, who died in her sleep at 340.", "A Cinder-Tusk prisoner who died in custody; someone lights a lantern anyway.",
    "Thorgrinn Ironfist — still on the list.", "A smith killed in the foundry explosion that nobody investigated.",
    "Every name the party gives from Barovia."], "Read by Yrsa on Hearthwatch Night (3.5b).", "it-lantern", T2)
table("work-setbacks", "Work Challenge Setbacks", [
    "A tool snaps; the next attempt needs a changed method.", "Noise carries; anyone listening knows you're here.", "Time lost: the next scene starts one round later.",
    "A minor injury: one character takes 2d6 damage of a fitting type.", "Supplies spent: one consumable or a piece of rope/chain is lost.",
    "Position lost: the work site shifts 10 feet toward danger."], "A setback costs time, position, supplies or readiness — never the essential clue.", "mc-challenge", T3)
table("crafting-complications", "Rune Forge Complications", [
    "The rune binds but hums audibly when active.", "The rune is keyed to the wrong hand; re-cutting takes an hour.", "Half the special material is consumed.",
    "The forge needs a day of repair.", "The rune works, but only on stone it can touch.", "A Runa-or-Skrik consultation is needed to stabilise it."],
      "On a major failure (5 or more below the DC).", "mc-forge", T3)
table("prisoner-concerns", "An Exchange with Names (6.3)", [
    "An untreated wound that needs Yrsa.", "A missing wage packet owed to their family.", "News for a household they haven't seen since spring.",
    "Fear of prosecution for something they didn't do.", "Fear of prosecution for something they did do.", "A letter to deliver to someone on the other side.",
    "A child in the other camp's custody.", "A tool they want back — it was their grandmother's."], "Give each named prisoner one concern.", "ab-chain", T3)
table("siege-sounds", "Sounds of the War Inside the Mountain", [
    "Horns answer horns from three directions.", "A lift chain screams and drops.", "The great pipes knock like a giant's heartbeat.",
    "Hammering on a gate that is not yours.", "A goblin voice counting down fuses.", "Heddra's ration bell, still ringing on schedule.",
    "Water where water should not be.", "A shield wall's chant, in two languages at once."], "Colour for Chapter 7.", "mc-fronts", T3)
table("korga-lines", "Korga's Arguments", [
    "“When they took our water it was policy. When we take their gates it is savagery.”", "“Peace is a word dwarves say after they win.”",
    "“My people want guarantees. Steel is the only guarantee anyone in this mountain has ever honoured.”",
    "“Your compact names captives. Name mine.”", "“I'll hear terms. I won't hear speeches.”", "“Urzha speaks for kitchens. I speak for the ones still alive to eat in them.”"],
      "For 7.5 — he admits the campaign now seeks the upper gates.", "ab-roar", T3)

# ============================================================================ macros
MACROS = []


def macro(key, name, call, img, folder):
    mid = fid("macro:" + key)
    cmd = (f'const api = game.modules.get("{MOD}")?.api;\n'
           f'if (!api) return ui.notifications.warn("Enable The Shield Between Us: Ironfist Legacy first.");\n{call}')
    MACROS.append({"_id": mid, "name": name, "type": "script", "scope": "global", "img": icon(img), "command": cmd,
                   "folder": folder, "sort": len(MACROS) * 100, "ownership": {"default": 0},
                   "flags": {MOD: {"key": key}}, "_key": f"!macros!{mid}", "_stats": STATS})


GM, TB, WAR = "GM Setup", "At the Table", "Politics & War"
macro("manager", "Ironfist Legacy Manager", "api.openManager();", "mc-setup", GM)
macro("ledger", "The Stone Ledger", "api.ledger.open();", "mc-ledger", TB)
macro("music", "Scene Music", "api.playSceneMusic();", "mc-music", TB)
macro("handout", "Show Handout", "api.showHandout();", "mc-handout", TB)
macro("challenge", "Work Challenge", "api.workChallenge();", "mc-challenge", TB)
macro("countdown", "Countdown", "api.countdown();", "mc-countdown", TB)
macro("save", "Request Group Save", "api.requestSave();", "mc-save", TB)
macro("forge", "Rune Forge", "api.forgeRune();", "mc-forge", TB)
macro("evidence", "Award Evidence", "api.awardEvidence();", "mc-evidence", WAR)
macro("hearing", "Stone Council Hearing", "api.hearing();", "mc-hearing", WAR)
macro("defence", "Adjust Defence Readiness", "api.adjustTrack('defence');", "mc-defence", WAR)
macro("accord", "Adjust Civilian Accord", "api.adjustTrack('accord');", "mc-accord", WAR)
macro("baldrik", "Baldrik Accountability", "api.baldrikEvent();", "mc-baldrik", WAR)
macro("favour", "Deal a Favour", "api.dealFavour();", "mc-cards", WAR)
macro("dispatch", "Draw a Siege Dispatch", "api.drawDispatch();", "mc-fronts", WAR)
macro("pressure", "Next Pressure Stage", "api.nextPressure();", "mc-pressure", WAR)

# ============================================================================ cards
CARDS = []
for dk, d in DECKS.items():
    cid = fid("cards:" + dk)
    cards = []
    for i, (ck, title, ic, tag, body, foot) in enumerate(d["cards"]):
        kid = fid(f"card:{dk}:{ck}")
        cards.append({"_id": kid, "name": title, "type": "base", "description": f"<p><strong>{tag}</strong></p><p>{body}</p><p><em>{foot}</em></p>",
                      "suit": d["name"].split(" (")[0], "value": i + 1, "back": {"name": d["name"], "text": "", "img": f"{ASSET}/cards/{dk}-back.webp"},
                      "faces": [{"name": title, "text": "", "img": f"{ASSET}/cards/{dk}-{ck}.webp"}], "face": 0, "drawn": False,
                      "origin": None, "width": 3, "height": 4, "rotation": 0, "sort": i * 100, "system": {},
                      "flags": {MOD: {"key": ck}}, "_key": f"!cards.cards!{cid}.{kid}", "_stats": STATS})
    CARDS.append({"_id": cid, "name": d["name"], "type": "deck", "description": f"<p>{d['desc']}</p>", "img": f"{ASSET}/cards/{dk}-back.webp",
                  "displayCount": True, "width": 3, "height": 4, "rotation": 0, "cards": cards, "sort": len(CARDS) * 100, "system": {},
                  "ownership": {"default": 0}, "folder": None, "flags": {MOD: {"key": dk}}, "_key": f"!cards!{cid}", "_stats": STATS})

# ============================================================================ playlists
PLAYLIST_DOCS = []
for i, (pl, keys) in enumerate(PLAYLISTS.items()):
    pid = fid("playlist:" + pl)
    sounds = []
    for j, k in enumerate(keys):
        sid = fid("sound:" + k)
        sub = "sfx" if k in SFX else "music"
        sounds.append({"_id": sid, "name": TRACK_TITLES[k], "path": f"{ASSET}/audio/{sub}/{k}.ogg", "repeat": k not in SFX,
                       "volume": 0.5 if k not in SFX else 0.7, "playing": False, "pausedTime": None, "fade": 1500 if k not in SFX else 0,
                       "sort": j * 100, "description": "Original music for Ironfist Legacy (procedurally composed).",
                       "flags": {MOD: {"key": k}}, "_key": f"!playlists.sounds!{pid}.{sid}"})
    PLAYLIST_DOCS.append({"_id": pid, "name": pl, "description": "Original, royalty-free music made for this module.",
                          "mode": -1, "channel": "music" if "Sound Effects" not in pl else "environment",
                          "playing": False, "fade": 1500, "sorting": "m", "seed": None, "sounds": sounds, "sort": i * 100,
                          "folder": None, "ownership": {"default": 0}, "flags": {MOD: {"key": pl}}, "_key": f"!playlists!{pid}", "_stats": STATS})
