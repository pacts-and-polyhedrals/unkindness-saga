"""The DM Control Board manual: one page per tab, plus what's automatic and an FAQ."""


def build(J):
    P, BOX, UL, TABLE, BANNER = J.P, J.BOX, J.UL, J.TABLE, J.BANNER
    L_macro = J.L_macro
    open_line = BOX("Opening the board", UL(
        "Run the macro <strong>★ DM Control Board</strong> (Macros directory, top folder in both parts' macro folders), or drag it to your hotbar.",
        "Or: Game Settings → The Unkindness Saga Manager → <em>Open the DM Control Board</em>.",
        "Or in the console: <code>game.modules.get(\"unkindness-saga\").api.board.open()</code>."))
    pages = []
    pages.append(("overview", "How the Control Board Works", BANNER("DM Control Board", "One window for both parts")
        + P("Every tracker and tool in the module is on one board with four tabs. Each section explains itself in a line of grey text; every button has a tooltip. "
            "A <strong>lit (green) button</strong> means that thing is true right now: a chain broken, a piece of evidence held, a prophecy fulfilled. Click it again to switch it off. "
            "<strong>− / +</strong> buttons step a number up or down.")
        + open_line
        + TABLE(["Tab", "What it's for"], [
            ["Ravenloft Finale", "Part I. Where the party is, Vallaki, Arl, the brides and Finn, Strahd's phases and Heart Chains, the Dark Powers, the Wish, prophecies and supplies."],
            ["Stone Ledger", "Part II. Defence and Accord, evidence E1–E7, the council, Baldrik, the Hold side-quest awards, and Dark Power Attention."],
            ["Session Tools", "One-off tools you use at the table: hearings, work challenges, countdowns, group saves, dispatches, pressure, favours, the rune forge, music and the Hold."],
            ["Setup & Repair", "Install, update, rebuild scenes and repair art."]])
        + BOX("The status card", "<em>Post status card</em> (Ravenloft tab) whispers you a summary of the whole finale: stage, brides, Finn, Strahd, the Dark Powers, allies and prophecies. "
              "It reads exactly what the board shows, so tick things off on the board and post the card whenever you want a recap.")
        + BOX("The old macros", "They all still work, and they're filed under <em>Individual tools (all on the DM Control Board)</em> if you prefer hotbar buttons. You don't need them.")))
    pages.append(("p1", "Tab 1 — Ravenloft Finale", BANNER("DM Control Board", "Ravenloft Finale (Part I)")
        + TABLE(["Section", "What you click", "What happens"], [
            ["Where the party is", "The stage they've reached (16 steps, from the Wachter House cellar to the campaign's end).", "Saved silently; the status card and dashboard use it. <em>Post status card</em> whispers the summary. <em>Reset</em> puts the whole finale back to the Nov 8 handoff (asks first)."],
            ["Vallaki prelude", "Van Richten's warning; a cult surges; the party evacuates or leaves; Strahd's letter.", "Posts the scene card and records it. Van Richten's warning also hands over his diamonds and reagent once."],
            ["Arl", "Show terms → Sign → Free him. Breach if the contract breaks. Send Arl / Azrathox to a front.", "Posts the contract cards and records the state. Arl can only be deployed once freed."],
            ["Brides and Finn", "alive / mist / destroyed / saved for each; Finn's three chains.", "<em>Mist</em> = fled to reform. When all three of Finn's chains are lit he's marked saved automatically."],
            ["Strahd", "Phase, Legendary Resistances (shared, max 4), Heart Chains (lit = standing), coffin distance, Tatyana's agency, his offer of rest. Plus Mock, Lair action, Sunlight rule, NPC action.", "Entering Phase II or III gives back one Legendary Resistance automatically. <em>NPC action</em> needs a Part I token selected."],
            ["Dark Powers", "Orcus pressure, Vampyr claim, Attention for each power; an intervention; a manifestation reduced to 0; the final endings.", "Interventions and reconstitution post their cards. The final banish / spare / bargain only works once the Wish has made the Edict of Finality; before that it tells you so."],
            ["The Wish", "Crisis → Djinn or Vecna offers → Cast. Claim clock. Vecna offers a hero a bargain.", "Casting creates the Edict of Finality. Some steps ask a follow-up question (e.g. the Wish's wording)."],
            ["Prophecies", "Light a hero's when it's fulfilled.", "Imported into Part II as a boon."],
            ["Supplies", "Holy water, diamonds, reagent; silver shot and Legna's potion.", "Just counters; spend as used."]])))
    pages.append(("p2", "Tab 2 — Stone Ledger", BANNER("DM Control Board", "Stone Ledger (Part II)")
        + TABLE(["Section", "What you click", "What happens"], [
            ["The two tracks", "− / + on Defence Readiness (0–6) and Civilian Accord (0–4).", "Each change is whispered to you. The grey line under each track says what it means right now. Raise a track once per concrete achievement only."],
            ["Evidence E1–E7", "Light a piece when the party authenticates it.", "The evidence card is dealt into the Party Dossier hand, a sting plays and it's announced. Clicking again un-marks it."],
            ["The Stone Council", "− / + on each general's stance.", "Hostile → Resistant → Uncommitted → Supportive → Committed. The Hearing tool reads these."],
            ["Baldrik", "His three accountability events.", "Refusing an unlawful order also deals his Favour card."],
            ["Hold side quests", "Tick a quest when its rewarded ending happens.", "Raises its track by 1 until the Hold cap (+2 per track) is reached; after that it records the quest without moving the track. Unticking takes the point back."],
            ["Shadows Beyond Barovia", "− / + Attention; Import the Ravenloft ending; Inheritance window; Shadow beat; Dark Gift.", "Attention thresholds: 0 Watching, 3 Reaching, 6 Claiming, 9 Arriving. Crossing one is announced with what it means."]])))
    pages.append(("tools", "Tab 3 — Session Tools", BANNER("DM Control Board", "Session Tools")
        + TABLE(["Tool", "Use it when"], [
            ["Stone Council hearing", "A formal hearing (5.2, 5.4, 6.1): pick the issue and the evidence; it weighs them against the council and posts the finding."],
            ["Show a handout", "You want every player to see a handout page."],
            ["Work challenge", "A repair, forging or brewing task: puts up an on-screen clock (successes before setbacks)."],
            ["Countdown", "Something is about to give: a flood, a door, a fuse."],
            ["Request a group save", "Everyone on the scene makes the same save."],
            ["Draw a siege dispatch", "Chapter 7: something happens at a front nobody is holding."],
            ["Next pressure stage", "Chapter 8: the Last Bastion pressure rises."],
            ["Deal a favour", "The party earns a Shield-Wall Favour."],
            ["Rune Forge", "A character forges a rune."],
            ["Play this scene's music", "Start the track for the scene you're on (it also starts on scene activation)."],
            ["Hold map / Rivets and Runes / Hold rumour", "Downtime in Kharad-Varr."]])))
    pages.append(("setup", "Tab 4 — Setup & Repair", BANNER("DM Control Board", "Setup & Repair")
        + TABLE(["Button", "When"], [
            ["Set up everything", "First time in a world."],
            ["Set up / repair Part I", "After an update, or if Part I content went missing. Hand-edited documents are kept as recovery copies."],
            ["Update Part II content", "After an update."],
            ["Build all Part II scenes", "After an update that changed maps, or if a scene got messed up."],
            ["Repair art", "Maps, portraits or tokens show blank (common on The Forge)."],
            ["Open the Manager", "Party size, single-scene rebuilds, removing Part II."]])))
    pages.append(("faq", "What's Automatic, and FAQ", BANNER("DM Control Board", "What happens on its own")
        + UL("Breaking Finn's third chain marks him <em>saved</em>.",
             "Entering Strahd Phase II or III restores one Legendary Resistance (max 4).",
             "Authenticating evidence deals its card into the Party Dossier and plays the sting.",
             "Baldrik refusing an unlawful order deals his Favour card.",
             "Activating a Part II scene plays its music (setting: <em>Play scene music on activation</em>).",
             "On load the module realigns Part I maps, puts tokens on their level and repairs art paths if needed.")
        + "<h3>Everything else is manual</h3>" + P("The board doesn't read the battle. When a bride is destroyed, a chain breaks or a track should move, you click it. That keeps you in charge of what counts.")
        + "<h3>FAQ</h3>" + UL(
            "<strong>Can players see the board?</strong> No. It's GM-only; the cards it posts are whispered to you unless a card is meant for the table.",
            "<strong>I clicked something by mistake.</strong> Click it again (toggles) or use − (counters). Nothing on the board deletes documents.",
            "<strong>A button asked me a question.</strong> A few story tools (the Wish's wording, Vecna's price) need a short answer; the board fills in everything it can.",
            "<strong>Where's the status card?</strong> Ravenloft tab → <em>Post status card</em>.")))
    J.journal("board-manual", "00 — DM Control Board: Manual", "Reference", pages, sort=-100)
