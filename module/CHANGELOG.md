# Changelog
## 2.1.9 — Castle Ravenloft (and Barovia) populated
- **Every Part I map is populated: 242 creatures in 23 maps,** on top of the 51 finale creatures, all hidden until you reveal them. They tell the finale's story: Strahd's frightened, divided household; the War of Broken Gods spilling inside; Finn's chapel left empty on purpose.
  - *Grounds:* Strahd's wolves, Beucephalus in the stable, gargoyles on the walls, a gate warden, Orcus's risen dead, the blood cult around the Blood Hearts.
  - *Main Floor and Court of the Count:* household guards (vampire spawn), frightened servants, animated armour and blades, a rug of smothering, shadows, a wight and skeletons in the bone room, bats. The unattended dinner stays unattended.
  - *Rooms of Weeping:* weeping spirits, a ghost, shadows.
  - *Rooftops and Spires 1–7:* gargoyles, bats, tower guards, a wraith, a wight.
  - *Larders (both versions):* ghouls and a ghast, Orcus's dead, rats, an ochre jelly, prisoners in the cells.
  - *Catacombs (both versions):* crypt guards (vampire spawn), wights, skeletons, specters, a ghost, ghouls, the dead in the lower cave. Phase III's hall and the tomb are kept clear.
  - *Vallaki streets (all three):* the watch and its hounds, frightened townsfolk, corpses standing and facing west, a priest and acolytes of St. Andral's.
  - *Van Richten's workshop:* refugees and a hound. *The Last Road:* wolves, Orcus's dead on the road, gate gargoyles, bats, a gate warden. *The Mistway:* mist-shadows, wolves, will-o'-wisps, the wandering dead, lost souls, refugees at the wagons.
- Their stat blocks are imported once from your dnd5e monster compendium (both SRD spellings understood) into *07 — Castle Inhabitants*. Each group is spread over free squares in the room it belongs to, never across a wall or on top of another token.
- Build All Scenes and Set Up / Repair Part I place them; the Scene check counts them.
## 2.1.8 — Every scene built, checked and repaired
- **Part I's maps are now built by the same builder as Part II's.** Walls and lights are placed on the scene's level, in batches. If the server rejects a batch, it retries one entry at a time, so a single bad entry can't wipe out a whole floor's walls. Coordinates are kept inside the map.
- **Build All Scenes checks its own work.** After building, it compares every scene (47) with what the module ships: walls, lights, pins, tokens and whether the map picture loads. It rebuilds any that came out incomplete, then whispers you the result.
- **New: Check all scenes** (Control Board → Setup & Repair, and the Manager). It only reports and changes nothing.
- **Part I maps get pins and journal links like Part II.** 44 pins on 14 maps open the journal page that runs each scene (the Unattended Dinner, the Ballroom, the chapel scenes, the Laboratory of Night, the Heart, Phase III and the coffin, the War of Broken Gods fronts, the Vallaki pages, Van Richten's workshop and Strahd's letter, the Last Road, and Barovia's collapse). Each of those maps opens its main journal from the scene's notes button.
- Van Richten now stands in his workshop (the Arcane Outfitter map), hidden like the rest.
## 2.1.7 — One button for every scene; Part I creatures placed
- **Build All Scenes now rebuilds both parts.** Part II's 24 maps as before, then Part I's 23 (walls and lights redrawn from the module data), then every creature placed. *Set Up Everything* uses it too.
- **Part I's creatures are on their maps (50 tokens on 11 scenes), all hidden** until you reveal them:
  - *Court of the Count:* Anastrasya and Volenta in the great hall (Movement I); the Abbot at the chapel altar, Finn in the aisle, Tatyana on the dais and Strahd Phase I by the doors.
  - *Spires 2:* Ludmilla in the witches' workroom with her three Nightglass Pylons.
  - *Spires 3 (Heart of Sorrow):* Strahd Phase II on the landing, the Blood, Stone and Dominion Heart Chains around the Heart.
  - *Dungeons & Catacombs* (and the mist-lit version): Strahd Phase III in the crypt hall, the coffin in his tomb.
  - *Grounds* (both versions): Orcus and three Grave Horns in the west yard, Vampyr and three Blood Hearts in the east yard.
  - *Vallaki streets* (all three versions): three Blood Choir zealots and two Grave Apostles.
  - *The Last Road:* Arl on the castle approach.
- *Set Up / Repair Part I* re-places the creatures too. Re-running either replaces only the tokens this module placed; your own tokens are left alone.
## 2.1.6 — Creature audit
- **Spellcasters now have their spells.** 12 creatures get real spell lists (107 spells), pulled at setup from the dnd5e system's own compendiums so every spell rolls properly: Sigrun, Old Kharn and Runa (including this module's rune spells), Sister Yrsa, Ludmilla, Strahd (Phases I and II), the Abbot, Arl, Orcus, Vampyr and Saraphene. Prepared casters get slots; innate casters get their uses per day. Each has a Spellcasting feature that explains it.
- **Hit points:** every creature now has a hit-dice formula matching its size and Constitution (HP moved by at most a few points so the numbers agree).
- **Legendary actions** for the Orcus and Vampyr manifestations (3 each), which their CR assumed.
- **Challenge ratings corrected** where the stat block didn't support the listed CR (checked with the DMG method): the Pylon, Heart Chains, Coffin and Dark Power anchors (objects), van Richten, Arl, General Odran, Sergeant Dagnner, Tovik and Aunt Heddra.
- Missing saving-throw proficiencies added (Odran, Dagnner, Edda, Runa, Yrsa, Urzha, Skrik, Ketta); the Bastion Engine gets tremorsense.
## 2.1.5 — DM Control Board
- **One window for everything.** The new **★ DM Control Board** (macro, or the Manager's top button) gathers every tracker and tool for both parts on four tabs, each section with a line explaining what it does:
  - *Ravenloft Finale:* the party's stage (16 steps) and the status card; Vallaki prelude, Arl and ally deployment; each bride's and Finn's state and Finn's three chains; Strahd's phase, Legendary Resistances, Heart Chains, coffin distance, Tatyana and the offer of rest; Orcus pressure, Vampyr claim and Attention; interventions, reconstitution and final endings; the Wish; Madam Eva's prophecies; supplies.
  - *Stone Ledger:* Defence and Accord with what each level means, evidence E1–E7, the council, Baldrik, the Hold side-quest awards (applies the +1 and enforces the +2 cap), and Shadow Attention.
  - *Session Tools* and *Setup & Repair.*
- Lit buttons show what's true now; click to toggle. Part I's typed-in prompts are replaced by buttons.
- New journal **00 — DM Control Board: Manual** (a page per tab, what's automatic, FAQ). The board's Manual button opens the page for the tab you're on.
- The individual macros still work and are filed under *Individual tools (all on the DM Control Board)*.
## 2.1.4 — Full stat blocks, aligned Ravenloft maps
- **Part I NPCs now have full stat blocks.** All 23 Ravenloft-finale actors had their actions stored only as notes, so their sheets showed a single flavour feature. Every action, bonus action, reaction, legendary action and trait is now a real item with working activities: attack rolls and damage (split by type), saving throws with DCs and areas, healing, recharge 5–6, per-encounter uses and legendary-action costs. 184 items in total. Added saves, skills, senses, damage and condition immunities, resistances, languages, Legendary Resistance and legendary action pools, token sizes (Orcus and Vampyr are Huge, Arl is Large), and real rules text where there were only notes (vampire Regeneration, Spider Climb and weaknesses; Magic Resistance; object traits; concrete effects for the Heart Chains, pylons, anchors and coffin).
- **Part I maps realigned with their walls and lights.** The scenes used 5% padding, which shifted every map under walls placed in map coordinates. Existing scenes are fixed on load.
- **Part II:** the Fifth Finger gate now spans the passage (gate, portcullis and door line up), the Hammerhall side-chamber doors no longer overlap, and the Treaty Stair portcullis matches its door. Quieter NPCs got working abilities (Heddra, Tovik, Venn, Sorvald, Old Dagny, Fenn, Pip, Tikka, Bera, couriers).
## 2.1.3 — Token levels (Foundry v14)
- **Fixes "level must exist".** Tokens placed by Build All Scenes were given a `levels` set, which v14 ignores for tokens: a token takes a single `level` id. Without one, Foundry rejected any update that moved them, which also stopped 2.1.1's art repair on the first scene. New tokens get the scene's level, and on load every token the module placed is put on its scene's level.
- Includes 2.1.2: the art repair changes only image fields, repairs each document separately, shows progress and lists anything it couldn't fix.
## 2.1.2 — Art repair, sturdier
- The automatic art repair on load now shows a notice while it works ("pointing N documents at the art…") and another when it's done, instead of running silently. 2.1.1 could look finished while it was still going, or stop after the first scene.
- Each document is repaired on its own and only the image fields are changed, so one document Foundry refuses can no longer stop the rest; anything that fails is listed in the console.
- Thumbnails are rebuilt after the paths are fixed, not during.
## 2.1.1 — Art on The Forge
- **Blank maps on The Forge fixed.** The Forge installed the module's code and data but none of its images or audio, so every map, portrait, token, icon and track answered 404. On load the module now checks where its art actually loads from (the module folder, then your Forge assets library, then this module's public GitHub repository) and points every scene, actor, item, journal, table, macro, playlist and card deck it created at that copy. It runs automatically on load and after every setup, update or scene rebuild, and switches back by itself if the module folder ever starts serving the art.
- Manager: **Repair Art** button, and the header shows where the art is loading from. Console: `game.modules.get("unkindness-saga").api.art.report()` lists every location tried.
- Scene thumbnails are rebuilt after a repair.
## 2.1.0 — The Hold of Kharad-Varr
- **Linked overview map** (*H0 · Kharad-Varr: The Hold*): a painted, gridless cutaway of the whole mountain from the Fifth Finger to the Heartworks. 25 pins: venue pins open the venue page; district pins open a district page linking every map in it.
- **Eight new venue maps**, walled, darkly lit, pinned and populated, in the same painted style: the Low Lantern (Lowhearth tavern), the Gilded Nail (officers' tavern), the Ember Baths (Steamstair), the Turning Gear (gaming house), Anvilsong Forge (smith), Glimmerhall (enchanter), Mossbeard and Fernspit Remedies (apothecary) and the Hall of Deep Script (rune smiths).
- **Eight self-contained side quests**, each with a hook, the truth, beats, endings, rewards, services and prices, side notes into the evidence (E1, E2, E4, R1, R3, R5), the cast and the war, and Shadows Beyond Barovia notes. Hold quests can raise Defence by at most +2 and Accord by at most +2 across the arc.
- New journal *10 — Kharad-Varr: The Hold* (28 pages), 14 new actors with portraits and tokens, 16 items, 8 roll tables and 3 macros (*Open the Hold*, *Rivets and Runes*, *Hold Rumour*). Start Here links the new section.
- Gridless scenes now get a valid grid size.
## 2.0.0 — The Unkindness Saga
- Merged **The Cat and the Unkindness 0.6.1** (Part I) and **Ironfist Legacy 1.1.0** (Part II) into one module, `unkindness-saga`.
- One Manager sets up both parts; *Set Up Everything* runs Part I then Part II. Part I's world content now sits under *The Cat and the Unkindness* folders.
- Shadows Beyond Barovia reads Part I's finale state directly. Part I's last journal page links straight into Part II.
- Automatic migration from the two separate modules: world documents (and their walls, lights, pages and embedded items), the finale state, the Stone Ledger and the Inheritance carry over. A warning shows if either old module is still enabled.
- Part I and Part II documents are kept apart: *Remove Module Content* only removes Part II; Part I's edit protection only watches Part I documents.

## Ironfist Legacy 1.1.0 — Shadows Beyond Barovia
- **Continuity with The Cat and the Unkindness.** One-click import of the Ravenloft finale: Dark Power Attention, final banish / spare / bargain choices, brides, Finn, Tatyana, Strahd's courtesy, the Wish source and price, Arl, Vallaki mercy and Madam Eva's five prophecies. Black Road is set by hand.
- **The Inheritance of the Mists** window (Manager → Shadows Beyond Barovia): Attention per power with thresholds (Watching / Reaching / Claiming / Arriving), primary and combined arcs, the outcome rules that apply, reputation, marks and gifts taken.
- **Rules:** signature rules for Orcus (the Grave-Thief's Toll), Vampyr (Blood-Debt) and Vecna (the Redacted Line); what raises and lowers Attention; nine Dark Gifts that are shortcuts to routes the adventure already has, each with a stated price; three Marks; four combined arcs; outcome rules for every Ravenloft ending; Reputation from the Mists (Merciful / Balanced / Ruthless) that sets where the Stone Ledger tracks start; five Prophecy Fulfilled boons; the Keepsake Box.
- **38 Shadow beats** keyed to existing scenes across all twelve sessions, each with a hook into a branch the adventure already supports. Every session guide links its beats. Calling cards for 8.6.
- **4 journals, 14 items, 5 roll tables, 5 macros.** Dark Power art from the Ravenloft finale.
- **All 15 battlemaps repainted** in the textured top-down style of the Castle Ravenloft set: material textures, bevelled stone and rock walls with cast shadows, ambient occlusion, painted pines, boulders and fungus, blooms and mist. GM labels and zone marks removed from the player-facing art (journal pins carry them). Wall geometry, doors, pins and tokens are unchanged.
- **Walls added** to the Pump Bridge and Lower Bridge (low walls along every ledge, gaps at each ladder). Every light is now a dark shade at low alpha so the maps are not washed out.
- Scene and story data otherwise unchanged; existing worlds update with *Update Content* and *Build All Scenes*.

## Ironfist Legacy 1.0.0
- Rebuilt v0.1.0 as a full module: compendium packs, one-click setup and a Manager window.
- 15 staged vector battlemaps; title scene and player sketch of Kharad-Varr.
- Portraits and top-down tokens for the full cast; 108 icons; card faces.
- All actors rebuilt with native dnd5e activities (Appendix A numbers); damage types corrected.
- Eight chapters split into twelve weekly sessions (29 Nov – 14 Feb) with session guides; two new scenes.
- Original music (17 tracks, 8 SFX), 12 roll tables, 16 macros, 4 card decks with hands.
- Stone Ledger, hearings, work challenge and countdown clock, rune forge, favours, dispatches, pressure stages.
- "Damian" normalised to "Damien".

## The Cat and the Unkindness 0.6.1
- Complete artwork edition, plus the Last Road and the Barovia Unravelling maps. See docs/ravenloft/README.md.
