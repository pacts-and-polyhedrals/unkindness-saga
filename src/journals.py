"""All journals: start-here, twelve session guides, eight chapters (from the adventure plan), gazetteer,
cast dossiers, politics, runes, encounter profiles, branches, handouts."""
import json, os, re, html as H
from lib5e import *
import schedule as SC
from cards_data import DECKS

LEG = os.path.join(os.path.dirname(__file__), "legacy")
SRC = open(f"{LEG}/The_Shield_Between_Us.md", encoding="utf-8").read()
JOURNALS = []  # (jkey, name, folder, pages[(pkey, title, html)], sort, player)


def journal(jkey, name, folder, pages, sort=0, player=False):
    JOURNALS.append((jkey, name, folder, pages, sort, player))


# ----------------------------------------------------------------------------- link helpers (world UUIDs)
def L_actor(k, label):
    return f"@UUID[Actor.{fid('actor:' + k)}]{{{label}}}"


def L_item(k, label):
    return f"@UUID[Item.{fid('item:' + k)}]{{{label}}}"


def L_spell(k, label):
    return f"@UUID[Item.{fid('spell:' + k)}]{{{label}}}"


def L_page(j, p, label):
    return f"@UUID[JournalEntry.{fid('journal:' + j)}.JournalEntryPage.{fid('page:' + j + ':' + p)}]{{{label}}}"


def L_scene(k, label):
    return f"@UUID[Scene.{fid('scene:' + k)}]{{{label}}}"


def L_macro(k, label):
    return f"@UUID[Macro.{fid('macro:' + k)}]{{{label}}}"


def L_table(k, label):
    return f"@UUID[RollTable.{fid('table:' + k)}]{{{label}}}"


def L_sound(k, label):
    pl = PLAYLIST_OF[k]
    return f"@UUID[Playlist.{fid('playlist:' + pl)}.PlaylistSound.{fid('sound:' + k)}]{{{label}}}"


def L_cards(k, label):
    return f"@UUID[Cards.{fid('cards:' + k)}]{{{label}}}"


from playlists_data import PLAYLISTS, TRACK_TITLES
PLAYLIST_OF = {t: pl for pl, ts in PLAYLISTS.items() for t in ts}


# ----------------------------------------------------------------------------- html helpers
def P(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


def RA(*lines, title="Read Aloud"):
    return f'<blockquote class="il-readaloud"><h4>{title}</h4>{P(*lines)}</blockquote>'


def SECRET(title, *paras):
    return f'<section class="il-secret"><h4>{title}</h4>{P(*paras)}</section>'


def BOX(title, *paras, cls="il-box"):
    return f'<div class="{cls}"><h4>{title}</h4>{P(*paras)}</div>'


def UL(*items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def TABLE(head, rows):
    h = "".join(f"<th>{x}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="il-table"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def BANNER(kicker, title, sub=""):
    return (f'<header class="il-banner"><span class="il-kicker">{kicker}</span><h1>{title}</h1>'
            + (f'<span class="il-sub">{sub}</span>' if sub else "") + "</header>")


def IMG(src, cls="il-portrait"):
    return f'<img class="{cls}" src="{src}">'


# ----------------------------------------------------------------------------- source markdown
NUM = {"One": "One", "Two": "Two", "Three": "Three", "Four": "Four", "Five": "Five", "Six": "Six", "Seven": "Seven", "Eight": "Eight"}


def normalise(s):
    s = s.replace("Damian", "Damien")
    s = re.sub(r"\bSessions (\d)-(\d)", r"Chapters \1–\2", s)
    s = re.sub(r"\bSessions (\d) and (\d)", r"Chapters \1 and \2", s)
    s = re.sub(r"\bSessions (\d)", r"Chapters \1", s)
    s = re.sub(r"\bSession (\d)", r"Chapter \1", s)
    s = re.sub(r"\bSession (One|Two|Three|Four|Five|Six|Seven|Eight)\b", r"Chapter \1", s)
    s = s.replace("eight-session", "eight-chapter").replace("eight sessions", "eight chapters").replace("ninth session", "ninth chapter")
    s = s.replace("ninth-session", "ninth-chapter").replace("Eight-Session", "Eight-Chapter").replace("eight-Session", "eight-chapter")
    return s


def md(text):
    text = normalise(text)
    out = []
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        h = H.escape(para, quote=False)
        h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)
        h = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", h)
        if h.startswith("Read: "):
            q = h[6:].strip().strip('"').strip("“”")
            out.append(RA(q))
        else:
            out.append(f"<p>{h}</p>")
    return "".join(out)


def sections():
    tops = re.split(r"^# ", SRC, flags=re.M)[1:]
    res = []
    for t in tops:
        head, _, body = t.partition("\n")
        subs = re.split(r"^## ", body, flags=re.M)
        intro = subs[0]
        res.append((head.strip(), intro, [(s.partition("\n")[0].strip(), s.partition("\n")[2]) for s in subs[1:]]))
    return res


SECT = sections()
BY = {h: (i, s) for h, i, s in SECT}


def find(prefix):
    for h, i, s in SECT:
        if h.startswith(prefix):
            return h, i, s
    raise KeyError(prefix)


# auto-link names (first occurrence per page)
NAMES = [("Marshal-General Hadrik Varr", "hadrik"), ("Hadrik", "hadrik"), ("Baldrik", "baldrik"), ("Heddra", "heddra"), ("Runa", "runa"),
         ("Brynja", "brynja"), ("Odran", "odran"), ("Dagnner", "dagnner"), ("Edda", "edda"), ("Yrsa", "yrsa"), ("Tovik", "tovik"),
         ("Venn", "venn"), ("Korga", "korga"), ("Urzha", "urzha"), ("Skrik", "skrik"), ("Brakk", "brakk"), ("Ketta", "ketta"),
         ("Tunnel Captain", "brakk"), ("Shock Troopers", "shock-trooper"), ("Shock Trooper", "shock-trooper"),
         ("Goblin Sappers", "goblin-sapper"), ("Sappers", "goblin-sapper"), ("Shield Wardens", "shield-warden"),
         ("Troopers", "ironfist-trooper"), ("Bastion Engine", "bastion-engine")]
EVI = {f"E{i}": f"ev-e{i}" for i in range(1, 8)}


def autolink(h):
    parts = re.split(r"(<[^>]+>|@UUID\[[^\]]+\]\{[^}]*\})", h)
    done = set()

    def sub_text(t):
        for name, key in NAMES:
            if key in done:
                continue
            m = re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", t)
            if m:
                done.add(key)
                t = t[:m.start()] + L_actor(key, m.group(0)) + t[m.end():]
                return sub_text_after(t, m.start() + len(L_actor(key, m.group(0))))
        return t

    def sub_text_after(t, pos):
        return t[:pos] + sub_text(t[pos:])

    def sub_ev(t):
        for e, key in EVI.items():
            if e in done:
                continue
            m = re.search(r"(?<![\w])" + e + r"(?![\w])", t)
            if m:
                done.add(e)
                t = t[:m.start()] + L_item(key, e) + t[m.end():]
        return t

    for i, p in enumerate(parts):
        if not p or p.startswith("<") or p.startswith("@UUID"):
            continue
        parts[i] = sub_ev(sub_text(p))
    return "".join(parts)


# ----------------------------------------------------------------------------- chapter journals
def scene_strip(pk):
    mp, mu = SC.SCENE[pk]
    n = SC.SCENE_SESSION[pk]
    extra = ""
    if pk == "s73":
        extra = " · also " + L_scene("lower-bridge", "Lower Bridge") + " · " + L_scene("pump-galleries", "Pump Galleries")
    return (f'<div class="il-strip"><span><strong>Played:</strong> {L_page("sessions", f"n{n}", f"Session {n} · {SC.DATES[n-1]}")}</span>'
            f'<span><strong>Map:</strong> {L_scene(mp, SC.MAP_TITLES[mp])}{extra}</span>'
            f'<span><strong>Music:</strong> {L_sound(mu, TRACK_TITLES[mu])}</span></div>')


NEW_SCENES = {
    "s35b": ("3.5b — Hearthwatch Night (new) | 30 minutes",
             P("<strong>Place and actors:</strong> Lowhearth's lift street and the drain channel; Heddra, Runa, Yrsa, workers, Baldrik if invited.",
               "<em>New scene for the 27 December session.</em> Hearthwatch is the Ironfist midwinter vigil: every household lights a lantern for each of the year's dead and sets it on the drain channel, where the water carries the lights down toward the deep. Yrsa reads the names from the military register."),
             RA("Lantern after lantern drifts along the channel, and the whole street goes quiet for each name. Sister Yrsa reaches the bottom of the register, pauses, and reads it anyway: “Thorgrinn Ironfist. Neverwinter auxiliary.”")
             + P("Heddra kept a memorial token because she believed Baldrik's report. Let Jp decide what Thorgrinn does: strike his name from the list, light the lantern himself, ask someone else to, or leave it for Heddra. None is wrong. If Baldrik is present, the register says <em>reported by Captain Baldrik Ironfist</em> — every listener hears it.",
                 "Invite each player to name someone their character lost — in Barovia or before — and light a lantern for them. Keep it short and unforced; a player may pass. Vesper or Legna may lead the words; Bunch may play.",
                 "Lowhearth's dead this year include workers killed when the lift failed — the sabotage Skrik later owns — and two children who drank from a bad well. If anyone asks, Yrsa notes the well deaths predate the raids (supports E1).",
                 "<strong>The lantern from below.</strong> As the last lights drift away, one comes <em>up</em> the channel against the current: a clay lantern stamped with the old compact seal, pushed by a goblin swimmer who vanishes. Inside is the Cinder-Tusk invitation of 3.6.",
                 "<strong>Rewards:</strong> no track changes on their own. If the party joins Heddra in feeding the families who come to the vigil, that counts toward the 3.5 shelter award (A +1, once).")),
    "s67": ("6.7 — The Night Before the Horns (new) | 30 minutes",
            P("<strong>Place and actors:</strong> the redoubt's watch post and courtyard fires; any surviving allies.",
              "<em>New scene for the 31 January session.</em> This is the scheduled long rest before the siege (6.6). Give each player one short beat with a person of their choice. Ask, don't assign."),
            UL("<strong>Thorgrinn (Jp):</strong> Baldrik at the watch post with the two-rivet shield across his knees. He doesn't ask for anything. What does Thorgrinn say, if anything?",
               "<strong>Damien (S. Alice):</strong> Dagnner, counting her soldiers' wage packets. She asks what a promise from Damien is worth in coin.",
               "<strong>Vesper (Paige):</strong> Yrsa or Urzha, sitting with the wounded of both sides. Who does Vesper pray with?",
               "<strong>Bunch (John):</strong> Ketta, Skrik or the Lowhearth kids — someone wants a tune they've never heard. What does Bunch play?",
               "<strong>Legna (Ryan):</strong> Brynja asks what a Raven Queen's servant thinks of soldiers who die obeying the wrong order.")
            + P("End each beat on a line, not a resolution. Then ring the war horns at dawn.", "<strong>Rest:</strong> this is the long rest promised before Chapter 7. Say so plainly.")),
}


def build_chapters():
    chapter_heads = [h for h, _, _ in SECT if re.match(r"\d+\. Session", h)]
    for ci, head in enumerate(chapter_heads, 1):
        intro, subs = BY[head]
        title = normalise(head.split(" - ", 1)[1] if " - " in head else head)
        sessions = sorted({SC.SCENE_SESSION[f"s{ci}{i+1}"] for i in range(len(subs))})
        pages = []
        ov = BANNER(f"Chapter {ci}", title, "Played in " + ", ".join(L_page("sessions", f"n{n}", f"Session {n} ({SC.DATES[n-1].replace('Sunday ', '')})") for n in sessions))
        ov += autolink(md(intro))
        ov += BOX("Scenes in this chapter", UL(*[L_page(f"ch{ci}", f"s{ci}{i+1}", normalise(s[0])) for i, s in enumerate(subs)]
                                              + ([L_page("ch3", "s35b", "3.5b — Hearthwatch Night (new)")] if ci == 3 else [])
                                              + ([L_page("ch6", "s67", "6.7 — The Night Before the Horns (new)")] if ci == 6 else [])))
        pages.append(("overview", f"Chapter {ci}: {title}", ov))
        for i, (sh, body) in enumerate(subs, 1):
            pk = f"s{ci}{i}"
            name = normalise(sh).replace(" - ", " — ", 1)
            ttl, _, mins = name.partition(" | ")
            h = BANNER(f"Chapter {ci} · Scene {ci}.{i}" + (f" · {mins}" if mins else ""), ttl.split(" — ", 1)[-1])
            h += scene_strip(pk) + autolink(md(body))
            pages.append((pk, ttl, h))
            if pk == "s35":
                t2, *b2 = NEW_SCENES["s35b"]; b2 = "".join(b2)
                ttl2, _, mins2 = t2.partition(" | ")
                pages.append(("s35b", ttl2, BANNER("Chapter 3 · Scene 3.5b · " + mins2, "Hearthwatch Night") + scene_strip("s35b") + autolink(b2)))
            if pk == "s66":
                t2, *b2 = NEW_SCENES["s67"]; b2 = "".join(b2)
                ttl2, _, mins2 = t2.partition(" | ")
                pages.append(("s67", ttl2, BANNER("Chapter 6 · Scene 6.7 · " + mins2, "The Night Before the Horns") + scene_strip("s67") + autolink(b2)))
        journal(f"ch{ci}", f"Chapter {ci} — {title}", "The Adventure", pages, sort=ci * 100)


# ----------------------------------------------------------------------------- start here + sessions
def build_start():
    players = TABLE(["Character", "Player", "In this arc"], [[c, p, n] for c, p, n in SC.PLAYERS])
    cal = TABLE(["#", "Date", "Session", "Scenes", "Maps"],
                [[str(S["n"]), SC.DATES[S["n"] - 1].replace("Sunday ", ""), L_page("sessions", f"n{S['n']}", S["title"]),
                  ", ".join(L_page(f"ch{s[1]}", s, s[1] + "." + s[2:]) for s in S["scenes"]),
                  ", ".join(dict.fromkeys(SC.MAP_TITLES[SC.SCENE[s][0]].split(":")[0] for s in S["scenes"]))] for S in SC.SESSIONS])
    welcome = (BANNER("Ironfist Legacy", "The Shield Between Us", "A Curse of Strahd continuation for the Sunday group")
               + IMG(f"modules/{MOD}/assets/art/title.webp", "il-hero")
               + P("A dwarf returns from death in a body of metal. His homeland welcomes a hero, his brother welcomes a second chance, and his commanders welcome a weapon. Beneath the mountain, a real war is approaching. The question is not whether Thorgrinn can hold a shield wall. It is who he will allow to stand behind it.",
                   "This module holds the whole arc: eight chapters of keyed scenes played across <strong>twelve Sundays, 29 November to 14 February</strong>, with fifteen staged battlemaps, the full cast as working dnd5e actors, the evidence, the rune magic, original music, roll tables, four card decks and the GM tools to run the politics and the war.")
               + BOX("Quick start",
                     "1. Enable the module and reload as GM. Choose <strong>Set Up Everything</strong>, or later open <em>Game Settings → Ironfist Legacy Manager</em>.",
                     "2. Everything lands in folders named <em>Ironfist Legacy</em>: scenes (walled, lit, pinned and populated), actors, items, journals, roll tables, macros, playlists and card decks.",
                     "3. Drag the <em>At the Table</em> macros to your hotbar. Open " + L_page("sessions", "n1", "Session 1") + " on the night.",
                     "4. Nothing touches your players' character sheets. The arc does not begin until Strahd and the Dark Powers are dealt with — see " + L_page("start", "before", "Before the Arc Begins") + ".")
               + BOX("New in 2.1: the Hold of Kharad-Varr",
                     "Eight new places, each with a painted map, a keeper and a self-contained side quest (two taverns, the Ember Baths, a gaming house, a smith, an enchanter, an apothecary and the rune smiths), "
                     "plus a painted overview of the whole mountain that pins every place in Part II. Start at " + L_page("hold", "start", "The Hold — Start Here") + " or open " + L_scene("hold-map", "the overview map") + ".")
               + BOX("The table", players))
    before = (BANNER("Start Here", "Before the Arc Begins")
              + P("The Sunday group is 10th level and still has to finish Strahd and face the Dark Powers. This arc starts the moment the mists release them, so a few things need to be carried across honestly.")
              + BOX("Level dial",
                    "<strong>If they arrive at 10th level</strong> (the adventure plan's assumption): level 11 at the end of Session 4, level 12 at the end of Session 8, level 13 at the finale.",
                    "<strong>If the Dark Powers push them to 11th</strong> (likely): level 12 at the end of Session 6 (after Chapter 3), level 13 at the end of Session 10 (after Chapter 6), level 14 at the finale. The encounter profiles are tuned for 11–12; for a 13th-level war, use the six-PC adjustments in Appendix A rather than inflating hit points.",
                    "Party size scaling (4, 5 or 6 heroes) is one click in the Manager; it adjusts the three boss stat blocks per Appendix A.")
              + BOX("What to bring forward from Barovia",
                    UL("Who escaped with them, exactly. The module never decides retroactively who survived.",
                       "The red dragon ally, shield guardians, mounts, a dragon egg, treasure: Section 2 gives each a real effect (the dragon can hold the exterior roads; the galleries are too narrow for its body).",
                       "What Baldrik already knows. If he learned in the last Barovian sessions that Thorgrinn survived, remove his surprise at the first reunion and keep the relief, guilt and fear.",
                       "Thorgrinn stays in his soul-coin mechanical body. His sword compulsion stays lifted (the Raven Queen's shrine). Nothing here reverses either."))
              + __import__("inheritance").before_box(__import__("sys").modules[__name__])
              + BOX("Bridge scene (use at the end of the Dark Powers session)",
                    "As Barovia comes apart, the mist doesn't take them somewhere random. It thins over a mountain road that smells of pine and cold stone, and Thorgrinn hears hammers keeping a rhythm he learned before he could hold one. Fade there; open Session 1 on the road."))
    law = (BANNER("Start Here", "Module Law")
           + UL("Thorgrinn remains mechanical and soul-coin powered unless play itself changes that. No feature, clause or machine in this module can command, switch off or extract him.",
                "His sword compulsion remains resolved. His new struggle is what to do with freedom.",
                "The Ironfist homeland is a stratocracy ruled by generals, not a monarchy.",
                "The Cinder-Tusk grievance is real; Korga's expansionist choices are also real.",
                "Hadrik can be exposed, detained or killed early. The module does not resurrect his plot under a different villain.",
                "Evidence survives a bad social roll. Failure changes the political cost, not reality.",
                "Baldrik's development uses events, not a persuasion meter: (1) he admits his report, (2) he refuses an unlawful order in front of his soldiers, (3) he submits evidence and himself to judgement. None forces Thorgrinn to forgive him.",
                "Thorgrinn's answer belongs to Jp. Don't prescribe forgiveness, leadership, restoration or revolution as the correct ending."))
    tools = (BANNER("Start Here", "Running the Tools")
             + TABLE(["Tool", "What it does"], [
                 [L_macro("ledger", "The Stone Ledger"), "Opens the campaign dashboard: Defence Readiness (0–6), Civilian Accord (0–4), evidence E1–E7, council stances, Baldrik's three accountability events and learned runes. Click to change; it's saved in the world."],
                 [L_macro("evidence", "Award Evidence"), "Records an evidence card, deals it to the <em>Party Dossier</em> hand and plays the evidence sting."],
                 [L_macro("hearing", "Stone Council Hearing"), "Runs the Weight of Stone: authenticated documents (+2 each, max 4), witnesses (+1 each, max 2), one principal argument (DC 15 +1, DC 20 +2). Threshold 5. A failure never erases evidence."],
                 [L_macro("challenge", "Work Challenge"), "Three progress before two setbacks (or any target you set), posted as a live chat card."],
                 [L_macro("countdown", "Countdown"), "A round counter for the gate (5 rounds), the bridge (4 rounds) and Last Bastion (6 rounds + relief)."],
                 [L_macro("favour", "Deal a Favour"), "Deals a Shield Wall Favour card to the <em>Favours Earned</em> hand when the party earns it."],
                 [L_macro("dispatch", "Draw a Siege Dispatch"), "Draws a War Day dispatch for an unassigned front (Session 10)."],
                 [L_macro("pressure", "Next Pressure Stage"), "Flips the next Last Bastion stage card and shows it to everyone (Session 12)."],
                 [L_macro("forge", "Rune Forge"), "Crafting check for the selected token; on a success the rune's grade is added to that character."],
                 [L_macro("music", "Scene Music"), "Plays the music assigned to the current scene."],
                 [L_macro("handout", "Show Handout"), "Shows a handout to all players."],
                 [L_macro("manager", "Ironfist Legacy Manager"), "Set up, update content, rebuild one scene, scale for party size, or remove everything."],
             ])
             + BOX("Decks", UL(*[f"{L_cards(k, d['name'])} — {d['desc']}" for k, d in DECKS.items()])))
    cal_page = BANNER("Start Here", "The Twelve Sundays", "29 November – 14 February") + cal + P(
        "Sessions run about two and a half hours of play. Session 12 is the long one (the Heartworks plus the family ending): plan a longer night or split 8.5–8.6 into a short Session 13 if the group prefers.",
        "<strong>Holiday weeks.</strong> 27 December (Hearthwatch) and 3 January are the likeliest to lose players. Session 5 is written to survive a thin table; if you lose a week entirely, merge using each session's compression note and push the rest back one Sunday.")
    journal("start", "00 — Start Here: The Stone Ledger", "Start Here",
            [("welcome", "Welcome", welcome), ("calendar", "The Twelve Sundays", cal_page), ("before", "Before the Arc Begins", before),
             ("law", "Module Law", law), ("tools", "Running the Tools", tools)], sort=0)

    pages = []
    for S in SC.SESSIONS:
        n = S["n"]
        scenes = UL(*[f"{L_page('ch' + s[1], s, s[1] + '.' + s[2:] + ' ' + page_title(s))} — {L_scene(SC.SCENE[s][0], SC.MAP_TITLES[SC.SCENE[s][0]])}" for s in S["scenes"]])
        spot = TABLE(["Player", "Character", "Spotlight prompt"],
                     [[p, c, S["spot"][c]] for c, p, _ in SC.PLAYERS])
        music = UL(*dict.fromkeys(L_sound(SC.SCENE[s][1], TRACK_TITLES[SC.SCENE[s][1]]) for s in S["scenes"]))
        h = (BANNER(f"Session {n} · {SC.DATES[n-1]}", S["title"], f"About {S['minutes']} minutes of play" + (" · finale" if S.get("finale") else ""))
             + BOX("Recap prompt", S["open"][0]) + RA(S["open"][1], title="Cold open")
             + "<h3>Scenes</h3>" + scenes
             + "<h3>Before the game</h3>" + UL(*S["prep"])
             + "<h3>Spotlight</h3>" + spot
             + "<h3>Music</h3>" + music
             + BOX("Cards", S["cards"])
             + (BOX("Milestone", S["milestone"]) if S.get("milestone") else "")
             + BOX("End on", S["close"], cls="il-box il-close")
             + BOX("If time runs short", S["compress"])
             + __import__("inheritance").session_box(__import__("sys").modules[__name__], n))
        pages.append((f"n{n}", f"Session {n} — {S['title']}", h))
    journal("sessions", "01 — The Twelve Sundays (Session Guides)", "Start Here", pages, sort=100)


TITLES = {}


def page_title(pk):
    return TITLES.get(pk, "")


def index_titles():
    chapter_heads = [h for h, _, _ in SECT if re.match(r"\d+\. Session", h)]
    for ci, head in enumerate(chapter_heads, 1):
        for i, (sh, _) in enumerate(BY[head][1], 1):
            TITLES[f"s{ci}{i}"] = normalise(sh).split(" - ", 1)[-1].split(" | ")[0]
    TITLES["s35b"] = "Hearthwatch Night (new)"
    TITLES["s67"] = "The Night Before the Horns (new)"


# ----------------------------------------------------------------------------- reference journals
def build_reference():
    gz = []
    for pref, key in (("1. Continuity", "continuity"), ("2. Running", "running"), ("4. The mountain", "mountain")):
        h, intro, subs = find(pref)
        body = md(intro) + "".join(f"<h2>{H.escape(normalise(t))}</h2>" + autolink(md(b)) for t, b in subs)
        gz.append((key, normalise(h.split(". ", 1)[1]), BANNER("Kharad-Varr", normalise(h.split(". ", 1)[1])) + body))
    gz.insert(0, ("sketch", "The Hold at a Glance", BANNER("Kharad-Varr", "The Hold at a Glance") + IMG(f"modules/{MOD}/assets/art/kharad-varr-section.webp", "il-hero")
                  + TABLE(["Map", "Scene"], [[SC.MAP_TITLES[k], L_scene(k, "Open scene")] for k in SC.MAP_ORDER])))
    journal("gazetteer", "02 — Kharad-Varr: Gazetteer & Truth", "Reference", gz, sort=200)

    # cast dossiers
    h, intro, subs = find("3. Cast")
    text = {t: b for t, b in subs}
    cast_src = "\n\n".join(b for _, b in subs)
    paras = [p for p in cast_src.split("\n\n") if p.strip()]
    order = [("baldrik", "Baldrik"), ("heddra", "Heddra"), ("runa", "Runa"), ("hadrik", "Hadrik"), ("brynja", "Brynja"), ("odran", "Odran"),
             ("dagnner", "Dagnner"), ("yrsa", "Yrsa"), ("korga", "Korga"), ("urzha", "Urzha"), ("skrik", "Skrik"),
             ("edda", "Edda"), ("venn", "Venn"), ("tovik", "Tovik"), ("brakk", "Brakk"), ("ketta", "Ketta")]
    pages = [("intro", "The Cast", BANNER("Faces Carved in Stone", "The Cast") + autolink(md(text.get("Spotlight by player character", ""))) + autolink(md(text.get("The Cinder-Tusk clan", "").split("\n\n")[0])))]
    import bestiary
    byk = {a["flags"][MOD]["key"]: a for a in bestiary.ACTORS}
    for k, nm in order:
        src_p = [p for p in paras if p.startswith(f"**{nm}") or p.startswith(f"**{byk[k]['name']}") or (f"**{nm} " in p[:60])]
        body = md("\n\n".join(src_p)) if src_p else ""
        a = byk[k]
        pages.append((k, a["name"], BANNER("Faces Carved in Stone", a["name"]) + IMG(a["img"]) + a["system"]["details"]["biography"]["value"]
                      + body + P(L_actor(k, "Open the actor sheet"))))
    pages.append(("minor", "Minor Reusable Actors", BANNER("Faces Carved in Stone", "Minor Reusable Actors") + autolink(md([p for p in paras if p.startswith("**Minor")][0]))
                  + P(L_actor("lowhearth-worker", "Lowhearth Worker"), L_actor("cinder-civilian", "Cinder-Tusk Household Member"), L_actor("ironfist-courier", "Ironfist Courier"))))
    journal("cast", "03 — Faces Carved in Stone (Cast)", "Reference", pages, sort=300)

    # politics, evidence
    leg = {x["sourceId"]: x for x in json.load(open(f"{LEG}/journals.json"))["journals"]}

    def strip_legacy(html):
        html = re.sub(r'<div class="il-knot[^"]*">.*?</div>', "", html)
        return html

    pol = leg["il.journal.politics"]["pages"]
    ev_rows = [[L_item(f"ev-{c[0]}", c[1]), c[3], c[4], c[5]] for c in DECKS["evidence"]["cards"]]
    journal("council", "04 — The Stone Council & the War", "Reference", [
        ("mechanics", "Political Mechanics", BANNER("The Stone Council", "Political Mechanics") + strip_legacy(pol[0]["html"]).replace("The Command Console macro", "The Stone Ledger macro")),
        ("evidence", "The Evidence Ledger", BANNER("The Stone Council", "The Evidence Ledger") + TABLE(["Evidence", "Issues", "Proves", "Limits"], ev_rows)
         + P("Essential revelations have three access routes each (see the Gazetteer). No single destroyed ledger can erase a truth.")),
        ("tracks", "Tracks at the War Council", BANNER("The Stone Council", "Tracks at the War Council") + TABLE(["Track", "Value", "Effect at the war council (7.1)"], [
            ["Defence Readiness", "0–1", "One unassigned front falls back, losing stores and territory; civilian escape stays playable."],
            ["Defence Readiness", "2–3", "Unassigned fronts hold, with damage."],
            ["Defence Readiness", "4–6", "Unassigned fronts hold and grant one reinforcement: remove two ordinary enemies from the chosen encounter, recover one endangered objective, or two automatic work actions."],
            ["Civilian Accord", "0–1", "No cross-clan assistance."],
            ["Civilian Accord", "2", "Civilians share safe routes."],
            ["Civilian Accord", "3–4", "A Cinder-Tusk engineering team helps evacuate both populations (and starts one Heartworks station with one progress); Korga risks his authority if he refuses reasonable terms."]])
         + P("Award or deduct only the changes stated in keyed scenes, once per achievement. Disclose these effects plainly before the party assigns fronts.")),
    ], sort=400)

    # runes
    rp = leg["il.journal.runes"]["pages"]
    import items_spells
    spl = UL(*[L_spell(s["flags"].get(MOD, {}).get("key", "") or s["_id"], s["name"]) if False else f'@UUID[Item.{s["_id"]}]{{{s["name"]}}} — level {s["system"]["level"]}' for s in items_spells.SPELLS])
    journal("runes", "05 — The Deep Runes", "Reference", [
        ("lexicon", "Rune Lexicon & Forgecraft", BANNER("The Deep Runes", "Rune Lexicon & Forgecraft") + strip_legacy(rp[0]["html"])),
        ("effects", "Rune Effects by Grade", BANNER("The Deep Runes", "Rune Effects by Grade") + strip_legacy(rp[1]["html"])),
        ("spells", "Runes That Move (Spells)", BANNER("The Deep Runes", "Runes That Move") + P("Twelve original rune spells, playable by artificers, clerics, wizards and anyone taught by an Ironfist runecarver.") + spl),
    ], sort=500)

    # appendices
    for pref, key, name, sort in (("Appendix A", "profiles", "06 — Encounter Profiles & Procedures", 600),
                                  ("Appendix C", "branches", "07 — Branches, Endings & Continuity", 700),
                                  ("Appendix D", "sources", "08 — Source Ledger & Design Boundaries", 800)):
        h, intro, subs = find(pref)
        pages = [("intro", normalise(h.split(". ", 1)[1]), BANNER(h.split(".")[0], normalise(h.split(". ", 1)[1])) + autolink(md(intro)))]
        for i, (t, b) in enumerate(subs):
            pages.append((f"p{i}", normalise(t), BANNER(normalise(h.split(". ", 1)[1]), normalise(t)) + autolink(md(b))))
        journal(key, name, "Reference", pages, sort=sort)


def build_handouts():
    h, intro, subs = find("Appendix B")
    pages = [("sketch", "H0 — Soldier's Sketch of Kharad-Varr", IMG(f"modules/{MOD}/assets/art/kharad-varr-section.webp", "il-hero")
              + P("<em>Not to scale. Lower routes are added as you learn them.</em>"))]
    for i, (t, b) in enumerate(subs, 1):
        quote = re.search(r'^"(.+?)"\s*$', b.strip().split("\n\n")[0], re.S)
        text = quote.group(1) if quote else b.strip().split("\n\n")[0]
        ttl = normalise(t).replace("Handout ", "H").replace(" - ", " — ")
        pages.append((f"h{i}", ttl, f'<div class="il-parchment"><h2>{H.escape(ttl.split(" — ", 1)[-1])}</h2><p>{H.escape(normalise(text))}</p></div>'))
    pages.append(("commission", "H7 — The Honorary Commission", '<div class="il-parchment"><h2>Honorary Commission of the Ironfist Council</h2>'
                  + P("Granted to Thorgrinn Ironfist, returned from the dead, in recognition of service.",
                      "§1. The holder receives the honorary rank of Shield-Captain, a salary of the third tier, and residence in Gate Crown.",
                      "§2. The holder shall obey the lawful military orders of the Council and its designated commanders.",
                      "§3. Research and operational knowledge obtained with military resources shall be disclosed to the Council.",
                      "§4. The holder shall speak in the clan's name only within the remit assigned to him.",
                      "§5. This commission is distinct from the correction of the death register.",
                      "Sealed: Marshal-General Hadrik Varr, for the Council.") + "</div>"))
    pages.append(("terms", "H8 — Deepwell Accord (Blank Terms)", '<div class="il-parchment"><h2>Deepwell Accord — Terms</h2>'
                  + TABLE(["Clause", "Agreed terms", "Who enforces it", "Review date"], [[c, "", "", ""] for c in (
                      "Who controls each valve", "Water measured and witnessed by", "Prisoner exchange", "Civilian corridors",
                      "Breach by armed persons", "Military requisitions", "Engineering access")]) + "</div>"))
    journal("handouts", "09 — Player Handouts", "Handouts", pages, sort=900, player=True)


def build_docs():
    index_titles()
    build_start()
    build_chapters()
    build_reference()
    build_handouts()
    import sys as _s, inheritance as _inh
    _inh.build(_s.modules[__name__])
    import hold as _hold
    _hold.build(_s.modules[__name__])
    docs = []
    for jkey, name, folder, pages, sort, player in JOURNALS:
        jid = fid("journal:" + jkey)
        ps = []
        for i, (pkey, title, html) in enumerate(pages):
            pid = fid("page:" + jkey + ":" + pkey)
            ps.append({"_id": pid, "name": title, "type": "text", "sort": (i + 1) * 100000,
                       "title": {"show": False, "level": 1},
                       "text": {"format": 1, "content": f'<div class="il-journal">{html}</div>'},
                       "ownership": {"default": -1}, "flags": {MOD: {"key": pkey}},
                       "_key": f"!journal.pages!{jid}.{pid}", "_stats": STATS})
        docs.append({"_id": jid, "name": name, "pages": ps, "folder": folder, "sort": sort,
                     "ownership": {"default": 2 if player else 0}, "flags": {MOD: {"key": jkey, "player": player}},
                     "_key": f"!journal!{jid}", "_stats": STATS})
    return docs
