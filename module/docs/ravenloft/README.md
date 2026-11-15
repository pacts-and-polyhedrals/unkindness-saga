# The Cat and the Unkindness — Ravenloft Finale

Version 0.6.1 — Complete Artwork Edition with the Last Road and Mistway maps. Foundry VTT v14 / dnd5e v6.

This is now the complete end-of-campaign overlay for Strahd1, rewritten from the Nov 8, 2026 session transcript. It starts at the exact cliffhanger beneath Wachter House before Arl is released, then carries the table through Van Richten, Vallaki's Orcus/Vampyr cult war, Strahd's still-sealed invitation, final supplies, the Azrathox rendezvous, the War of Broken Gods, the brides/Finn/Tatyana, the three-phase Strahd encounter, Wish/Vecna crisis, coffin chase, Barovia's collapse and the Ironfist handoff.

The module imports its own walled and lit map scenes but does not duplicate player-character actors. It is designed to overlay the existing Strahd1 world.

Run `game.catAndUnkindness.setup()` as GM after enabling/updating. If this world already had v0.4 finale state loaded, run **Finale — Reset State to Nov 8 Handoff** once before play. Managed documents use stable source IDs; edited managed copies are recovery-copied before refresh.

## v0.5 corrections
- Start state is Wachter House cellar, not the Vistani camp or Ravenloft approach.
- Arl contract is agreed but unsigned/unreleased at start.
- Strahd's letter is still sealed.
- Van Richten has not yet been visited.
- Azrathox is outside Vallaki.
- Baldrik's canonical object is the unopened family-crested keepsake box with star-shaped lock; the old funerary-plaque/rune hook is retired.
- Current party prep and Nov 8 discoveries are in the state dashboard.
- Bride continuity resolved: Volenta is the male Oathbreaker paladin from Madam Eva’s reading. No extra consort exists.

## 0.6.0 — Maps, walls, lighting and art

Run **Setup / Repair** once after updating. It now also imports 21 scenes into
`06 — Maps / Castle Ravenloft` and `06 — Maps / Vallaki`.

- Every Ravenloft floor is walled: grounds and curtain wall (roofed and open), main floor,
  Court of the Count, Rooms of Weeping, rooftops, spires 1–7, Larders of Ill Omen, Dungeons &
  Catacombs, plus the mist-lit larders and catacombs variants. Vallaki streets ×3 and the arcane outfitter.
- Doors sit on every doorway. Secret doors are on the canon positions. Strahd's tomb and the
  larder vault are locked. Dungeon cells are locked barred doors you can see and hear through.
- Battlements, balconies, stair wells and the rotunda gallery are **low walls**: they block
  movement but not sight or light.
- Lights use dark shades only (blood, ember, cold blue, moonlight, violet, grave green, teal mist),
  with low alpha and mostly dim radius, placed one per room so they don't stack. Darkness is set
  per scene (0.3–0.65); global illumination is off and token vision is on.
- Re-running Setup replaces only the walls and lights this module created. Anything you add by hand stays.

### Portraits and tokens originally added
Anastrasya, Volenta (male, subsequently replaced with masked Oathbreaker art), Ludmilla, Ireena/Tatyana,
Strahd phases I–III (dinner-suit Count / caped vampire / lightning devil), Van Richten, Saraphene.

### Portraits, object tokens and item art — COMPLETE

This is the **full 0.6.0 artwork-integrated module**. The 39 original placeholder roles
now have real gothic-fantasy art embedded directly into managed source documents:

- 15 Actor portraits/object illustrations, with 15 companion circular token textures:
  Finn (correctly portrayed as a **ginger-haired halfling vampire**), the Abbot, Arl,
  Orcus, Vampyr, both cultists, male Oathbreaker Volenta, Nightglass Pylon,
  all three Heart Chains, Strahd's Coffin, Grave Horn and Blood Heart.
- All **24 Items**, including the five Tarokka fate cards, the unopened Strahd letter,
  Arl's contract, Finn's three Chains of Claim, and all six rules/boon icons.
- 22 thematically linked journal thumbnails.
- All previously included Strahd phases, Tatyana, Anastrasya, Ludmilla, Saraphene
  and Van Richten portraits and tokens are retained from the supplied 0.6.0 module.

The 21 originally supplied scenes, maps, wall geometry, lights, macros, game
mechanics and November 8 starting state are preserved.

**Updating an existing world:** install the entire module ZIP, enable it, and
run `game.catAndUnkindness.setup()` as GM. Then run **Ravenloft Art — Refresh
Existing Scene Tokens** once to update already-placed tokens. Do not reset the
finale story state simply to update art.

Asset index: `assets/art/art-map.json` and `assets/art/asset-ledger.csv`.

### 0.6.1 — Two new maps

Two original maps, painted for this module in the same dark top-down style as the castle set,
100 px per square, 50 × 30 squares, walled and lit:

- **The Last Road — Gates of Ravenloft & the Drawbridge** (`06 — Maps / Castle Ravenloft`).
  The Svalich Road climbs out of the forest to the twin gate towers with their headless guardian
  statues and braziers. The rusted iron gates stand open. A cobbled ledge runs above the gorge to the
  rotting drawbridge and the portcullis of the castle gatehouse. Cliff rims and the bridge edges are
  low walls (they block movement but not sight). The gates are an open door; the portcullis is a locked door.
- **Barovia Unravelling — The Mistway Out** (`06 — Maps / Barovia`). The land is splitting into
  islands over a starless void lit red from below, with debris drifting in it. The road crosses two
  narrow cracks (jumpable, left open in the walls) to the Vistani caravan and the Ironfist muster
  fire and banner. A wall of mist swallows the east edge, with daylight from the world beyond
  showing faintly through it. Void edges are low walls; the wagons block sight and movement.

Still not mapped: the Wachter House cellar (the Nov 8 handoff).

### Third-party content
Character art: Moonberry Maple. Maps: Eledryll (mist-lit catacombs and larders), DM_Andy (Vallaki
streets), plus the 8k Castle Ravenloft map set and the arcane outfitter map. These are bundled for
private home-game use only. Get the creators' permission before publishing a public release.
