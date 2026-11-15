# Changelog
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
