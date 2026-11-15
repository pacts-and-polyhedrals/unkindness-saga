# Live-World QA — v0.5.1

Static validation is run before packaging. In Foundry verify:

- [ ] Setup / Repair completes without errors.
- [ ] Dashboard says stage `wachter-cellar`.
- [ ] Arl begins not-free; Strahd letter begins sealed; Van Richten begins unvisited.
- [ ] Resources show 9 holy waters, silver shot, fire-giant potion, 0 diamonds before Van Richten.
- [ ] **Arl — Contract / Release** can sign then free him and advances the stage.
- [ ] **Strahd — Open / Read Letter** keeps the letter hidden until opened.
- [ ] Vallaki warning marks Van Richten visited and grants the finale cache (3x300 gp diamonds, 1x500 gp, 2 reagents).
- [ ] Ally Deployment refuses to deploy Arl before he is freed.
- [ ] Azrathox can be assigned after the Vallaki exit.
- [ ] Orcus/Vampyr reconstitution is locked until the Wish Edict is active.
- [ ] Djinn and Vecna Wish routes still work.
- [ ] Five prophecy toggles still work.
- [ ] Baldrik display references the keepsake box, not a funerary plaque.
- [ ] Volenta imports as the male Oathbreaker paladin; no OPTIONAL Oathbreaker Consort actor remains.
- [ ] All journals/actors/items/macros import with no duplicate source IDs.
- [ ] Re-running setup does not duplicate unchanged managed content.
- [ ] Editing a managed document then upgrading creates a recovery copy before refresh.


## Complete artwork integration — static checks

- Original user-supplied **0.6.0** manifest and `scripts/main.mjs` retained.
- **21** Castle Ravenloft/Vallaki scenes retained, map data byte-identical.
- **23 Actors**, **24 Items**, **35 Journals**, **28 Macros** (one new token refresh macro).
- **15** previously unillustrated Actor/Object docs given new portraits and circular token textures.
- **24** of 24 Item docs given new artwork; **22** Journal thumbnails illustrated.
- **39** source artworks represented in the actual Foundry records; **15** token crops.
- Corrected Finn art: ginger-haired **halfling vampire**.
- All art and token paths exist inside ZIP; image bytes decoded/verified.
- `sourceHash` updated for modified source-backed documents so manual Setup / Repair
  imports the art without deleting unrelated manual world actors or scenes.
- Remaining requirement: run inside Foundry VTT v14 / dnd5e v6 for live verification.


## 0.6.1 — maps added
- [ ] Setup / Repair creates **23** scenes; the 21 earlier scenes are unchanged (same source hashes, so no re-import).
- [ ] The Last Road: tokens can pass the open gates; the portcullis is locked; the drawbridge can be walked onto from both rims.
- [ ] Mistway: the road crosses both cracks with no wall in the way; the void edges block movement but not sight.
