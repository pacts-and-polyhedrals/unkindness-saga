# Install / Update

1. Remove or replace the previous `cat-and-unkindness` module directory.
2. Extract this package so Foundry sees `Data/modules/cat-and-unkindness/module.json`.
3. Enable **The Cat and the Unkindness — Ravenloft Finale** in the existing Strahd1 world.
4. As GM run `game.catAndUnkindness.setup()` or the **Ravenloft Finale — Setup / Repair** macro.
5. If upgrading from v0.4, run **Finale — Reset State to Nov 8 Handoff** once.
6. Open **00 — START HERE: THE LAST TWO SESSIONS** and run the **Ravenloft Finale — Dashboard** macro.
7. Begin with **00A — EXACT HANDOFF: WACHTER HOUSE**. The first live action is finishing/signing/releasing Arl.

Do not re-run the Vistani scenes; those already occurred.


## 0.6.1 — Last Road and Mistway maps

Install over 0.6.0 and run Setup / Repair once. It adds two scenes and leaves everything else as it is.

## Complete 0.6.0 artwork update

This is the **whole module**, not the v0.6 artwork overlay. Install by extracting
the ZIP into `Data/modules/`, resulting in
`Data/modules/cat-and-unkindness/module.json`. Do not nest two copies of
`cat-and-unkindness/`. The existing world and its campaign state remain intact.

1. Backup your Foundry world before replacing module files.
2. Replace the old `cat-and-unkindness` module folder using this ZIP.
3. Reload Foundry. As GM run `game.catAndUnkindness.setup()` to update source-backed
   portraits, objects, item icons and journal thumbnails.
4. Run the new `Ravenloft Art — Refresh Existing Scene Tokens` GM macro to update
   any previously placed Actor/Object tokens on scenes.
5. **Do not run `Reset State to Nov 8 Handoff`** if play has advanced since Nov 8.

The art is integrated directly into the source data; future Setup / Repair runs
will keep it. Maps and actor mechanics are unchanged.
