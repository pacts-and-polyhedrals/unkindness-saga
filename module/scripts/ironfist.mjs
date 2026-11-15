/**
 * The Shield Between Us: Ironfist Legacy — runtime.
 * Asmo, Pacts & Polyhedrals (Ben Vale).
 *
 * Installs compendium content into labelled world folders; stages every scene (map, walls, doors,
 * lights, journal pins, tokens, music); creates the card hands; and provides the table tools:
 * the Stone Ledger (tracks, evidence, council, Baldrik), hearings, work challenges, countdowns,
 * rune forging, favours, siege dispatches and the Last Bastion pressure stages.
 */
const MOD = "unkindness-saga";
const ROOT = "Ironfist Legacy";
const PACKS = [
  ["actors", "Actor", `${ROOT} — Actors`],
  ["items", "Item", `${ROOT} — Items`],
  ["spells", "Item", `${ROOT} — Rune Spells`],
  ["journals", "JournalEntry", ROOT],
  ["tables", "RollTable", ROOT],
  ["macros", "Macro", ROOT],
  ["playlists", "Playlist", ROOT],
  ["cards", "Cards", ROOT]
];
const HANDS = [
  { key: "hand-dossier", name: "Party Dossier (Evidence)", type: "hand", observer: true },
  { key: "hand-favours", name: "Favours Earned", type: "hand", observer: true },
  { key: "pile-table", name: "On the Table (Dispatches & Pressure)", type: "pile", observer: true }
];
const BOSSES = { korga: 220, "bastion-engine": 250, hadrik: 180 };
const DEFAULT_LEDGER = {
  defence: 2, accord: 0, evidence: {}, council: { brynja: 0, odran: 0, hadrik: 0 },
  baldrik: { admitted: false, refused: false, submitted: false }, runes: [], hearings: {}, hold: {}
};

const gen = () => game.release?.generation ?? 13;
const esc = s => foundry.utils.escapeHTML ? foundry.utils.escapeHTML(String(s)) : String(s);
const DialogV2 = () => foundry.applications.api.DialogV2;
const managed = d => d.getFlag?.(MOD, "managed") === true && d.getFlag?.(MOD, "part") !== "ravenloft";
const byKey = (coll, key) => coll.find(d => d.getFlag?.(MOD, "key") === key);

/* ------------------------------------------------------------------------ */
Hooks.once("init", () => {
  game.settings.register(MOD, "installedVersion", { scope: "world", config: false, type: String, default: "" });
  game.settings.register(MOD, "promptDismissed", { scope: "world", config: false, type: Boolean, default: false });
  game.settings.register(MOD, "partySize", { scope: "world", config: false, type: Number, default: 5 });
  game.settings.register(MOD, "ledger", { scope: "world", config: false, type: Object, default: foundry.utils.deepClone(DEFAULT_LEDGER), onChange: () => Ledger.refresh() });
  game.settings.register(MOD, "migrated", { scope: "world", config: false, type: Boolean, default: false });
  game.settings.register(MOD, "inheritance", { scope: "world", config: false, type: Object, default: {}, onChange: () => Inheritance.refresh() });
  game.settings.register(MOD, "clock", { scope: "world", config: false, type: Object, default: { visible: false }, onChange: () => Clock.refresh() });
  game.settings.register(MOD, "autoMusic", {
    name: "Play scene music on activation", hint: "When the GM activates an Ironfist Legacy scene, start its assigned track.",
    scope: "world", config: true, type: Boolean, default: true
  });
  game.settings.register(MOD, "artBase", { scope: "world", config: false, type: String, default: `modules/${MOD}/` });
  game.settings.registerMenu(MOD, "manager", {
    name: "The Unkindness Saga Manager", label: "Open Manager", hint: "Set up Part I (Ravenloft finale) and Part II (Ironfist Legacy), update, rebuild scenes, scale for party size, or remove Part II.",
    icon: "fa-solid fa-shield-halved", type: Manager, restricted: true
  });
});

Hooks.once("ready", async () => {
  game.modules.get(MOD).api = API;
  Clock.refresh();
  // Part I's own Setup / Repair macro also gives its creatures their spells
  const C = game.catAndUnkindness;
  if (C?.setup && !C.setup.__spells) { const orig = C.setup; C.setup = async (...a) => { const r = await orig.apply(C, a); try { await grantSpells(); } catch (e) { console.error(MOD, e); } return r; }; C.setup.__spells = true; }
  if (!game.user.isGM) { artBase(); return; }
  for (const old of ["cat-and-unkindness", "ironfist-legacy"]) if (game.modules.get(old)?.active)
    ui.notifications.warn(`The Unkindness Saga replaces the separate "${old}" module. Disable it in Manage Modules to avoid duplicate content.`, { permanent: true });
  if (!game.settings.get(MOD, "migrated")) await migrateLegacy({ quiet: true });
  try { await fixTokenLevels(); } catch (e) { console.error(MOD, "token levels", e); }
  try { await fixPartOnePadding(); } catch (e) { console.error(MOD, "Part I alignment", e); }
  try { await repairArt({ quiet: true }); } catch (e) { console.error(MOD, "art repair", e); }
  const ver = game.modules.get(MOD).version;
  const installed = game.settings.get(MOD, "installedVersion");
  if (!installed && !game.settings.get(MOD, "promptDismissed")) {
    const ok = await DialogV2().confirm({
      window: { title: "The Unkindness Saga" },
      content: `<p>Set up <strong>The Unkindness Saga</strong> now?</p><p><strong>Part I</strong> (The Cat and the Unkindness) imports the Ravenloft finale: 23 walled and lit scenes, the brides, Strahd, the Dark Powers and the finale dashboard. <strong>Part II</strong> (The Shield Between Us) installs the actors, items, rune spells, journals, roll tables, macros, music and card decks into folders named <em>Ironfist Legacy</em>, and builds all fifteen scenes with walls, lighting, journal pins, tokens and music. Player character sheets are never touched. You can do it later from <em>Game Settings → The Unkindness Saga Manager</em>.</p>`,
      yes: { label: "Set Up Everything" }, no: { label: "Later" }
    });
    if (ok) await API.setupAll();
    else await game.settings.set(MOD, "promptDismissed", true);
  } else if (installed && installed !== ver) {
    ui.notifications.info(`The Unkindness Saga updated to ${ver}. Open the Manager, run "Set Up / Repair Part I", then "Update Content".`, { permanent: true });
  }
});

Hooks.on("updateScene", (scene, changes) => {
  if (!game.user.isGM || !changes.active || !managed(scene)) return;
  if (game.settings.get(MOD, "autoMusic")) playSceneMusic(scene);
});

/* ------------------------------------------------------------------------ */
/*  Content installation                                                    */
/* ------------------------------------------------------------------------ */
async function ensureFolder(name, type, parent = null, color = "#4a0c10") {
  const pid = parent?.id ?? null;
  let f = game.folders.find(x => x.type === type && x.name === name && (x.folder?.id ?? null) === pid);
  if (!f) f = await Folder.create({ name, type, folder: pid, color, sorting: "m", flags: { [MOD]: { managed: true } } });
  return f;
}
function folderDepth(f) { let d = 0; let p = f.folder; while (p) { d++; p = p.folder; } return d; }

async function importPack(packName, type, rootName, { update = false } = {}) {
  const pack = game.packs.get(`${MOD}.${packName}`);
  if (!pack) { console.warn(`${MOD} | missing pack ${packName}`); return 0; }
  const docs = await pack.getDocuments();
  const root = await ensureFolder(rootName, type);
  const fmap = new Map();
  const pfolders = [...(pack.folders ?? [])].sort((a, b) => folderDepth(a) - folderDepth(b));
  for (const f of pfolders) {
    const parent = f.folder ? fmap.get(f.folder.id) : root;
    fmap.set(f.id, await ensureFolder(f.name, type, parent, f.color ?? "#4a0c10"));
  }
  const coll = game.collections.get(type);
  const cls = getDocumentClass(type);
  const create = [];
  for (const d of docs) {
    const data = coll.fromCompendium(d, { keepId: true, clearFolder: true, clearOwnership: false });
    data.folder = fmap.get(d.folder?.id ?? d.folder)?.id ?? root.id;
    foundry.utils.setProperty(data, `flags.${MOD}.managed`, true);
    if (type === "JournalEntry" && d.getFlag(MOD, "player")) data.ownership = { default: CONST.DOCUMENT_OWNERSHIP_LEVELS.OBSERVER };
    const existing = coll.get(d.id);
    if (existing) {
      if (!update) continue;
      await existing.delete();
    }
    create.push(data);
  }
  for (let i = 0; i < create.length; i += 50) await cls.createDocuments(create.slice(i, i + 50), { keepId: true });
  return create.length;
}

async function ensureHands() {
  const folder = await ensureFolder(ROOT, "Cards");
  for (const h of HANDS) {
    if (byKey(game.cards, h.key)) continue;
    await Cards.create({
      name: h.name, type: h.type, folder: folder.id, img: `${artUrl()}assets/icons/mc-cards.webp`,
      ownership: { default: h.observer ? CONST.DOCUMENT_OWNERSHIP_LEVELS.OBSERVER : 0 },
      flags: { [MOD]: { managed: true, key: h.key } }
    });
  }
}

async function installContent({ update = false } = {}) {
  let n = 0;
  const note = ui.notifications.info(`${ROOT}: installing content…`, { permanent: true });
  for (const [pack, type, root] of PACKS) n += await importPack(pack, type, root, { update });
  await ensureHands();
  note?.remove?.();
  ui.notifications.info(`${ROOT}: ${update ? "updated" : "installed"} ${n} documents.`);
  return n;
}

/* ------------------------------------------------------------------------ */
/*  Scenes                                                                  */
/* ------------------------------------------------------------------------ */
let SCENES = null;
async function sceneData() {
  if (!SCENES) SCENES = await (await fetch(`modules/${MOD}/data/scenes.json`)).json();
  return SCENES;
}
async function sceneLevel(scene) {
  const levels = scene?.levels?.contents ?? [];
  return scene?.initialLevel ?? levels[0] ?? null;
}
async function setBackground(scene, src, name) {
  if (gen() >= 14) {
    const level = await sceneLevel(scene);
    if (level?.update) await level.update({ "background.src": src });
    else if (scene.createEmbeddedDocuments) await scene.createEmbeddedDocuments("Level", [{ name, background: { src } }]);
  } else await scene.update({ "background.src": src });
}

async function ensureScene(spec, folder) {
  let scene = game.scenes.get(spec.id);
  const base = {
    _id: spec.id, name: spec.title, folder: folder.id, navigation: true, navOrder: spec.order, sort: spec.order * 1000,
    width: spec.width, height: spec.height, padding: 0,
    grid: { size: spec.grid || 100, type: spec.grid ? 1 : 0, distance: 5, units: "ft", alpha: 0.1, color: "#000000" },
    tokenVision: !!spec.grid, fog: { exploration: true },
    environment: { darknessLevel: spec.env.darkness ?? 0, globalLight: { enabled: !!spec.env.globalLight, darkness: { max: 1, min: 0 } }, cycle: true },
    journal: spec.journal ?? null, journalEntryPage: spec.journalPage ?? null,
    playlist: game.playlists.get(spec.playlist) ? spec.playlist : null,
    playlistSound: game.playlists.get(spec.playlist)?.sounds.get(spec.sound) ? spec.sound : null,
    flags: { [MOD]: { managed: true, key: spec.key, playlist: spec.playlist, sound: spec.sound } }
  };
  if (gen() < 14) base.background = { src: spec.src };
  else base.levels = [{ name: spec.title, background: { src: spec.src } }];
  if (!scene) [scene] = await Scene.createDocuments([base], { keepId: true });
  else {
    const { _id, ...upd } = base;
    delete upd.levels; delete upd.background;
    await scene.update(upd);
  }
  await setBackground(scene, spec.src, spec.title);
  return scene;
}

async function stageScene(key) {
  const all = await sceneData();
  const spec = [all.landing, all.section, ...all.scenes].find(s => s.key === key);
  if (!spec) throw new Error(`Unknown scene ${key}`);
  const folder = await ensureFolder(ROOT, "Scene");
  const scene = await ensureScene(spec, folder);
  if (!spec.walls) return scene;
  const levelId = gen() >= 14 ? (await sceneLevel(scene))?.id : null;
  const lv = levelId ? { levels: [levelId] } : {};
  for (const [embedded, coll] of [["Wall", scene.walls], ["AmbientLight", scene.lights], ["Note", scene.notes], ["Token", scene.tokens]]) {
    const ids = coll.filter(managed).map(d => d.id);
    if (ids.length) await scene.deleteEmbeddedDocuments(embedded, ids);
  }
  const flag = { [MOD]: { managed: true } };
  const W = CONST.WALL_SENSE_TYPES, M = CONST.WALL_MOVEMENT_TYPES;
  const walls = spec.walls.map(w => {
    const d = { c: w.c, flags: flag, ...lv };
    if (w.kind === "door" || w.kind === "secret") { d.door = w.kind === "secret" ? 2 : 1; d.ds = w.locked ? 2 : 0; }
    if (w.kind === "window") { d.sight = W.PROXIMITY ?? 30; d.light = W.PROXIMITY ?? 30; d.threshold = { sight: 10, light: 10 }; }
    if (w.kind === "invisible") { d.sight = W.NONE; d.light = W.NONE; d.sound = W.NONE; }
    if (w.kind === "terrain") { d.sight = W.LIMITED; d.light = W.LIMITED; d.move = M.NORMAL; d.sound = W.LIMITED; }
    return d;
  });
  if (walls.length) await scene.createEmbeddedDocuments("Wall", walls);
  const lights = spec.lights.map(l => ({
    x: l.x, y: l.y, walls: l.walls !== false, flags: flag, ...lv,
    config: { dim: l.dim * 5, bright: l.bright * 5, color: l.color, alpha: l.alpha, luminosity: l.luminosity ?? 0.5, attenuation: 0.6, coloration: 1,
      animation: { type: l.anim ?? null, speed: l.speed ?? 3, intensity: l.intensity ?? 3, reverse: false }, darkness: { min: 0, max: 1 } }
  }));
  if (lights.length) await scene.createEmbeddedDocuments("AmbientLight", lights);
  const notes = spec.notes.filter(n => game.journal.get(n.entryId)).map(n => ({
    x: n.x, y: n.y, entryId: n.entryId, pageId: n.pageId, text: n.label, flags: flag, ...lv,
    texture: { src: `${artUrl()}assets/icons/note-pin.webp` }, iconSize: 48, fontSize: 22, textAnchor: 1, global: false
  }));
  if (notes.length) await scene.createEmbeddedDocuments("Note", notes);
  const tokens = [];
  for (const t of spec.tokens) {
    const actor = game.actors.get(t.actorId);
    if (!actor) { console.warn(`${MOD} | token actor missing`, t); continue; }
    const size = actor.prototypeToken.width * spec.grid;
    const td = await actor.getTokenDocument({ x: Math.round(t.x - size / 2), y: Math.round(t.y - size / 2), hidden: !!t.hidden });
    const data = td.toObject();
    if (t.name) data.name = t.name;
    foundry.utils.setProperty(data, `flags.${MOD}.managed`, true);
    delete data.levels;
    if (levelId) data.level = levelId; // tokens take a single level id in v14, not a levels set
    tokens.push(data);
  }
  if (tokens.length) await scene.createEmbeddedDocuments("Token", tokens);
  try { const thumb = await scene.createThumbnail({ img: spec.src }); if (thumb?.thumb) await scene.update({ thumb: thumb.thumb }); }
  catch (e) { console.warn(`${MOD} | thumbnail skipped`, e); }
  return scene;
}

async function buildScenes() {
  const all = await sceneData();
  const note = ui.notifications.info(`${ROOT}: building scenes (Part II, then Part I)…`, { permanent: true });
  const folder = await ensureFolder(ROOT, "Scene");
  await ensureScene(all.landing, folder);
  await ensureScene(all.section, folder);
  for (const s of all.scenes) await stageScene(s.key);
  let p1 = 0; try { p1 = await buildPartOneScenes(); } catch (e) { console.error(MOD, "Part I scenes", e); }
  note?.remove?.();
  await repairArt({ quiet: true });
  const chk = await checkScenes({ repair: true });
  ui.notifications[chk.incomplete.length ? "warn" : "info"](`${ROOT}: ${chk.total} scenes built${chk.incomplete.length ? `; ${chk.incomplete.length} still incomplete (see the Scene check card in chat)` : " and checked: every one complete"}.`);
}

async function setupAll() {
  await migrateLegacy();
  await installContent({ update: false });
  await buildScenes(); // also sets up Part I and places its creatures
  await applyPartySize(game.settings.get(MOD, "partySize"));
  await grantSpells();
  await repairArt({ quiet: true });
  await game.settings.set(MOD, "installedVersion", game.modules.get(MOD).version);
  ui.notifications.info(`The Unkindness Saga is ready. Part I starts in "00 — START HERE: THE LAST TWO SESSIONS"; Part II in "00 — Start Here: The Stone Ledger".`);
  byKey(game.journal, "start")?.sheet?.render(true);
}
async function updateContent() {
  await installContent({ update: true });
  await grantSpells();
  await applyPartySize(game.settings.get(MOD, "partySize"));
  await repairArt({ quiet: true });
  await game.settings.set(MOD, "installedVersion", game.modules.get(MOD).version);
}
async function removeAll() {
  const ok = await DialogV2().confirm({ window: { title: "Remove Ironfist Legacy" },
    content: "<p>Delete every world document and folder this module created (scenes, actors, items, journals, tables, macros, playlists, card decks and hands)? Anything you created yourself is kept, and player characters are never touched.</p>" });
  if (!ok) return;
  for (const coll of [game.scenes, game.actors, game.items, game.journal, game.tables, game.macros, game.playlists, game.cards]) {
    const ids = coll.filter(managed).map(d => d.id);
    if (ids.length) await coll.documentClass.deleteDocuments(ids);
  }
  const fids = game.folders.filter(managed).map(f => f.id);
  if (fids.length) await Folder.deleteDocuments(fids);
  await game.settings.set(MOD, "installedVersion", "");
  ui.notifications.info(`${ROOT} removed.`);
}

/* ------------------------------------------------------------------------ */
/*  Party size (Appendix A: four heroes = bosses at ~85% HP; six = add support, not HP) */
/* ------------------------------------------------------------------------ */
async function applyPartySize(n) {
  n = Math.max(4, Math.min(6, Number(n) || 5));
  await game.settings.set(MOD, "partySize", n);
  for (const [key, hp] of Object.entries(BOSSES)) {
    const a = byKey(game.actors, key);
    const v = n === 4 ? Math.round(hp * 0.85) : hp;
    if (a) await a.update({ "system.attributes.hp.value": v, "system.attributes.hp.max": v });
  }
  return n;
}

/* ------------------------------------------------------------------------ */
/*  Music                                                                   */
/* ------------------------------------------------------------------------ */
async function playSceneMusic(scene = canvas.scene) {
  if (!scene) return;
  const pl = game.playlists.get(scene.getFlag(MOD, "playlist") ?? scene.playlist?.id);
  const snd = pl?.sounds.get(scene.getFlag(MOD, "sound") ?? scene.playlistSound?.id);
  if (!snd) return ui.notifications.warn("This scene has no Ironfist Legacy music assigned.");
  for (const p of game.playlists.filter(managed)) for (const s of p.sounds) if (s.playing && s.id !== snd.id && s.repeat) await p.stopSound(s);
  if (!snd.playing) await pl.playSound(snd);
}
async function playSfx(key) {
  const pl = game.playlists.find(p => managed(p) && p.sounds.some(s => s.getFlag(MOD, "key") === key));
  const s = pl?.sounds.find(x => x.getFlag(MOD, "key") === key);
  if (s) await pl.playSound(s);
}

/* ------------------------------------------------------------------------ */
/*  Chat helper                                                             */
/* ------------------------------------------------------------------------ */
function chat(content, alias = "The Stone Ledger", whisper = false) {
  const data = { content: `<div class="il-chat">${content}</div>`, speaker: { alias } };
  if (whisper) data.whisper = ChatMessage.getWhisperRecipients("GM").map(u => u.id);
  return ChatMessage.create(data);
}

/* ------------------------------------------------------------------------ */
/*  The Stone Ledger                                                        */
/* ------------------------------------------------------------------------ */
const EVIDENCE = {
  E1: ["Ninth Sluice Gauge Record", ["CAUSE"]], E2: ["Foundry Requisition Ledger", ["CAUSE", "SUPPLY"]],
  E3: ["Baldrik's Occupancy Classification", ["CIVILIANS", "COMMAND"]], E4: ["The Water-and-Stone Compact", ["CAUSE", "SETTLEMENT"]],
  E5: ["Hadrik's Last Bastion Order", ["CIVILIANS", "COMMAND"]], E6: ["The Engineers' Joint Finding", ["CIVILIANS", "SETTLEMENT"]],
  E7: ["Korga's Upper Reservoir Order", ["THREAT", "SETTLEMENT"]]
};
const ISSUES = { cause: ["CAUSE", "SUPPLY"], civilians: ["CIVILIANS"], command: ["COMMAND"], settlement: ["SETTLEMENT", "THREAT"] };
const ISSUE_LABEL = { cause: "Cause of the crisis", civilians: "Treatment of civilians", command: "Immediate command", settlement: "The settlement" };
const STANCE = { "-2": "Hostile", "-1": "Resistant", "0": "Uncommitted", "1": "Supportive", "2": "Committed" };

function ledgerState() {
  return foundry.utils.mergeObject(foundry.utils.deepClone(DEFAULT_LEDGER), game.settings.get(MOD, "ledger") ?? {}, { inplace: false });
}
async function setLedger(patch) {
  if (!game.user.isGM) return ui.notifications.warn("Only the GM can change the Stone Ledger.");
  const next = foundry.utils.mergeObject(ledgerState(), patch, { inplace: false });
  await game.settings.set(MOD, "ledger", next);
  return next;
}

class LedgerApp extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = {
    id: "il-ledger", tag: "div", classes: ["il-app"],
    window: { title: "The Stone Ledger", icon: "fa-solid fa-scale-balanced", resizable: true },
    position: { width: 520, height: "auto" },
    actions: {
      track: async function (ev, el) {
        const s = ledgerState(); const k = el.dataset.k, d = Number(el.dataset.d);
        const max = k === "defence" ? 6 : 4;
        await setLedger({ [k]: Math.max(0, Math.min(max, s[k] + d)) });
        chat(`<p><strong>${k === "defence" ? "Defence Readiness" : "Civilian Accord"}</strong> ${d > 0 ? "rises" : "falls"} to <strong>${Math.max(0, Math.min(max, s[k] + d))}</strong>.</p>`, "The Stone Ledger", true);
      },
      evidence: async function (ev, el) { await toggleEvidence(el.dataset.e); },
      council: async function (ev, el) {
        const s = ledgerState(); const who = el.dataset.w;
        const v = Math.max(-2, Math.min(2, (s.council[who] ?? 0) + Number(el.dataset.d)));
        await setLedger({ council: { [who]: v } });
      },
      baldrik: async function (ev, el) { await baldrikEvent(el.dataset.b); },
      post: async function () { postLedger(); }
    }
  };
  async _renderHTML() {
    const s = ledgerState(); const gm = game.user.isGM;
    const pips = (v, max, k) => `<div class="il-track"><b>${k === "defence" ? "Defence Readiness" : "Civilian Accord"}</b>
      ${gm ? `<button type="button" data-action="track" data-k="${k}" data-d="-1">−</button>` : ""}
      <span class="il-pips">${Array.from({ length: max + 1 }, (_, i) => `<i class="${i <= v ? "on" : ""}">${i}</i>`).join("")}</span>
      ${gm ? `<button type="button" data-action="track" data-k="${k}" data-d="1">+</button>` : ""}</div>`;
    const ev = Object.entries(EVIDENCE).map(([id, [n]]) => `<button type="button" class="il-ev ${s.evidence[id] ? "on" : ""}" data-action="evidence" data-e="${id}" title="${esc(n)}">${id}</button>`).join("");
    const council = ["brynja", "odran", "hadrik"].map(w => `<div class="il-council"><b>${w[0].toUpperCase() + w.slice(1)}</b>
      ${gm ? `<button type="button" data-action="council" data-w="${w}" data-d="-1">−</button>` : ""}<span>${STANCE[String(s.council[w] ?? 0)]}</span>
      ${gm ? `<button type="button" data-action="council" data-w="${w}" data-d="1">+</button>` : ""}</div>`).join("");
    const bal = [["admitted", "Admits the report"], ["refused", "Refuses an unlawful order"], ["submitted", "Submits to judgement"]]
      .map(([k, l]) => `<button type="button" class="il-ev ${s.baldrik[k] ? "on" : ""}" data-action="baldrik" data-b="${k}">${l}</button>`).join("");
    const eff = s.defence <= 1 ? "One unassigned front falls back." : s.defence <= 3 ? "Unassigned fronts hold, with damage." : "Unassigned fronts hold and grant one reinforcement.";
    const acc = s.accord <= 1 ? "No cross-clan assistance." : s.accord === 2 ? "Civilians share safe routes." : "A Cinder-Tusk engineering team helps both populations.";
    return `<div class="il-ledger"><img class="il-ledger-banner" src="${artUrl()}assets/art/banner.webp" alt="">
      ${pips(s.defence, 6, "defence")}<p class="hint">${eff}</p>${pips(s.accord, 4, "accord")}<p class="hint">${acc}</p>
      <h3>Evidence</h3><div class="il-row">${ev}</div>
      <h3>The Council</h3>${council}
      <h3>Baldrik</h3><div class="il-row">${bal}</div>
      ${gm ? `<div class="il-row"><button type="button" data-action="post"><i class="fa-solid fa-comment"></i> Post to GM chat</button></div>` : ""}</div>`;
  }
  _replaceHTML(result, content) { content.innerHTML = result; }
}
const Ledger = {
  app: null,
  open() { this.app ??= new LedgerApp(); return this.app.render(true); },
  refresh() { if (this.app?.rendered) this.app.render(); }
};
function postLedger() {
  const s = ledgerState();
  const ev = Object.keys(s.evidence).filter(k => s.evidence[k]).join(", ") || "none";
  chat(`<h3>The Stone Ledger</h3><p>Defence Readiness <strong>${s.defence}</strong>/6 · Civilian Accord <strong>${s.accord}</strong>/4</p>
    <p>Evidence: ${ev}</p><p>Council: Brynja ${STANCE[s.council.brynja]}, Odran ${STANCE[s.council.odran]}, Hadrik ${STANCE[s.council.hadrik]}</p>
    <p>Baldrik: ${s.baldrik.admitted ? "✓" : "—"} admitted · ${s.baldrik.refused ? "✓" : "—"} refused · ${s.baldrik.submitted ? "✓" : "—"} submitted</p>`, "The Stone Ledger", true);
}

async function toggleEvidence(id) {
  const s = ledgerState(); const on = !s.evidence[id];
  await setLedger({ evidence: { [id]: on } });
  if (on) {
    await passCard("evidence", id.toLowerCase(), "hand-dossier");
    playSfx("evidence-sting");
    chat(`<p><strong>${id} — ${esc(EVIDENCE[id][0])}</strong> is authenticated and added to the Party Dossier.</p><p class="hint">Issues: ${EVIDENCE[id][1].join(", ")}</p>`, "The Evidence Ledger");
  }
}
async function awardEvidence() {
  const s = ledgerState();
  const opts = Object.entries(EVIDENCE).map(([id, [n]]) => `<option value="${id}" ${s.evidence[id] ? "disabled" : ""}>${id} — ${esc(n)}${s.evidence[id] ? " (held)" : ""}</option>`).join("");
  const id = await DialogV2().prompt({ window: { title: "Award Evidence" }, content: `<div class="il-form"><select name="e">${opts}</select></div>`,
    ok: { label: "Authenticate", callback: (ev, b) => b.form.elements.e.value } });
  if (id) await toggleEvidence(id);
}
async function adjustTrack(which) {
  const k = which === "accord" ? "accord" : "defence";
  const d = await DialogV2().wait({ window: { title: k === "defence" ? "Defence Readiness" : "Civilian Accord" },
    content: `<p>Current: <strong>${ledgerState()[k]}</strong>. Award changes only once per concrete achievement.</p>`,
    buttons: [{ action: "-1", label: "−1" }, { action: "1", label: "+1" }] });
  if (!d) return;
  const s = ledgerState(); const max = k === "defence" ? 6 : 4;
  const v = Math.max(0, Math.min(max, s[k] + Number(d)));
  await setLedger({ [k]: v });
  chat(`<p><strong>${k === "defence" ? "Defence Readiness" : "Civilian Accord"}</strong> is now <strong>${v}</strong>.</p>`, "The Stone Ledger", true);
}
async function baldrikEvent(k) {
  if (!k) k = await DialogV2().wait({ window: { title: "Baldrik's Accountability" }, content: "<p>Record (or clear) an event. Each happens only through his own choices in play.</p>",
    buttons: [{ action: "admitted", label: "Admits the report" }, { action: "refused", label: "Refuses an unlawful order" }, { action: "submitted", label: "Submits to judgement" }] });
  if (!k) return;
  const s = ledgerState(); const on = !s.baldrik[k];
  await setLedger({ baldrik: { [k]: on } });
  if (on && k === "refused") await passCard("favours", "baldrik", "hand-favours");
  chat(`<p>Baldrik — <strong>${{ admitted: "admits the report", refused: "refuses an unlawful order in front of his soldiers", submitted: "submits evidence and himself to judgement" }[k]}</strong>${on ? "" : " (cleared)"}.</p>`, "The Stone Ledger", true);
}

/* ------------------------------------------------------------------------ */
/*  Hearings — the Weight of Stone                                          */
/* ------------------------------------------------------------------------ */
async function hearing() {
  const s = ledgerState();
  const actor = canvas.tokens?.controlled?.[0]?.actor ?? game.user.character;
  const skills = Object.entries(CONFIG.DND5E.skills).map(([k, v]) => `<option value="${k}" ${k === "per" ? "selected" : ""}>${esc(v.label)}</option>`).join("");
  const issues = Object.entries(ISSUE_LABEL).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
  const res = await DialogV2().prompt({ window: { title: "Stone Council Hearing" },
    content: `<div class="il-form"><label>Issue <select name="issue">${issues}</select></label>
      <label>Credible witnesses (0–2) <input type="number" name="w" value="1" min="0" max="2"></label>
      <label>Principal argument (${actor ? esc(actor.name) : "select the speaker's token"}) <select name="skill">${skills}</select></label>
      <p class="hint">Authenticated evidence relevant to the issue counts automatically (+2 each, max 4). Threshold 5. A failed hearing never erases evidence.</p></div>`,
    ok: { label: "Hear the Case", callback: (ev, b) => ({ issue: b.form.elements.issue.value, w: Number(b.form.elements.w.value) || 0, skill: b.form.elements.skill.value }) } });
  if (!res) return;
  const used = Object.entries(EVIDENCE).filter(([id, [, tags]]) => s.evidence[id] && tags.some(t => ISSUES[res.issue].includes(t))).map(([id]) => id);
  const docWeight = Math.min(4, used.length * 2);
  const witness = Math.max(0, Math.min(2, res.w));
  let total = 0, rollHtml = "";
  if (actor?.rollSkill) {
    const r = await actor.rollSkill({ skill: res.skill }, {}, { create: true });
    const roll = Array.isArray(r) ? r[0] : r;
    total = roll?.total ?? 0;
  } else {
    const roll = await new Roll("1d20").evaluate(); total = roll.total; rollHtml = " (no speaker selected: flat d20)";
  }
  const argW = total >= 20 ? 2 : total >= 15 ? 1 : 0;
  const weight = docWeight + witness + argW;
  const ok = weight >= 5;
  await setLedger({ hearings: { [res.issue]: { ok, weight, used, at: Date.now() } } });
  chat(`<h3>Stone Council — ${ISSUE_LABEL[res.issue]}</h3>
    <p>Evidence: ${used.join(", ") || "none"} (+${docWeight}) · Witnesses +${witness} · Argument ${total}${rollHtml} (+${argW})</p>
    <p class="il-ruling ${ok ? "good" : "bad"}">Weight ${weight}/5 — ${ok ? "ESTABLISHED" : "NOT YET ESTABLISHED"}</p>
    <p class="hint">${ok ? "The council accepts the finding." : "Nothing is erased: change the political cost, the conditions or public support, and keep playing."}</p>`, "The Stone Council");
}

/* ------------------------------------------------------------------------ */
/*  The Stone Clock: work challenges and countdowns (visible to everyone)   */
/* ------------------------------------------------------------------------ */
const Clock = {
  el: null,
  get() { try { return foundry.utils.deepClone(game.settings.get(MOD, "clock")); } catch { return { visible: false }; } },
  async set(s) { if (game.user.isGM) await game.settings.set(MOD, "clock", s); },
  refresh() {
    const s = this.get();
    if (!s?.visible) { this.el?.remove(); this.el = null; return; }
    if (!this.el) {
      this.el = document.createElement("section"); this.el.id = "il-clock"; document.body.appendChild(this.el);
      this.el.addEventListener("click", ev => {
        const b = ev.target.closest("[data-act]"); if (!b || !game.user.isGM) return;
        this.act(b.dataset.act);
      });
    }
    const gm = game.user.isGM;
    let body = "";
    if (s.mode === "work") {
      const prog = Array.from({ length: s.need }, (_, i) => `<i class="${i < s.s ? "on" : ""}"></i>`).join("");
      const set = Array.from({ length: s.fail }, (_, i) => `<i class="bad ${i < s.f ? "on" : ""}"></i>`).join("");
      body = `<div class="il-clock-row"><span>Progress</span>${prog}</div><div class="il-clock-row"><span>Setbacks</span>${set}</div>
        ${s.s >= s.need ? `<p class="il-ruling good">DONE</p>` : (s.fail && s.f >= s.fail) ? `<p class="il-ruling bad">IT COSTS YOU</p>` : ""}
        ${gm ? `<div class="il-ctl"><button data-act="s">+ Progress</button><button data-act="f">+ Setback</button><button data-act="close">✕</button></div>` : ""}`;
    } else {
      const left = Math.max(0, s.max - s.cur);
      body = `<div class="il-clock-big">${left}</div><p>${left === 1 ? "round remains" : "rounds remain"}${s.bonus ? ` · +${s.bonus} from relief` : ""}</p>
        ${left === 0 ? `<p class="il-ruling bad">${esc(s.end || "TIME")}</p>` : ""}
        ${gm ? `<div class="il-ctl"><button data-act="tick">End Round</button><button data-act="back">Undo</button><button data-act="bonus">+1 Round</button><button data-act="close">✕</button></div>` : ""}`;
    }
    this.el.innerHTML = `<header>${esc(s.name || "The Stone Clock")}</header>${body}`;
  },
  async act(a) {
    const s = this.get();
    if (a === "close") s.visible = false;
    if (a === "s") s.s = Math.min(s.need, s.s + 1);
    if (a === "f") s.f = Math.min(s.fail, s.f + 1);
    if (a === "tick") { s.cur++; if (s.cur >= s.max) playSfx(s.sfx || "alarm-bell"); }
    if (a === "back") s.cur = Math.max(0, s.cur - 1);
    if (a === "bonus") { s.max++; s.bonus = (s.bonus ?? 0) + 1; }
    await this.set(s);
  }
};
const PRESET_WORK = {
  winch: ["The Broken Winch (1.2)", 3, 2], descent: ["The Broken Descent (2.3)", 3, 2], gate: ["The Sluice Gate (2.4) — DC 16 each", 3, 99],
  intake: ["Manual Intake (5.5)", 3, 2], evac: ["Evacuate the Workshop Bay (5.5)", 2, 2], pumps: ["Pump Galleries (7.3) — 4 progress", 4, 99],
  wheel: ["Reservoir Wheel (8.2)", 2, 99], relief: ["Relief Channel (8.2)", 2, 99], brake: ["Reversal Brake (8.2)", 2, 99]
};
async function workChallenge() {
  const buttons = Object.entries(PRESET_WORK).map(([k, [n]]) => ({ action: k, label: n }));
  buttons.push({ action: "custom", label: "Custom: 3 before 2" });
  const k = await DialogV2().wait({ window: { title: "Work Challenge" }, content: "<p>Three progress before two setbacks unless the scene says otherwise. Each character contributes once before anyone repeats.</p>", buttons, rejectClose: false });
  if (!k) return;
  const [name, need, fail] = PRESET_WORK[k] ?? ["Work Challenge", 3, 2];
  await Clock.set({ visible: true, mode: "work", name, need, fail: fail === 99 ? 0 : fail, s: 0, f: 0 });
}
const PRESET_COUNT = {
  gate: ["The Sluice Gate Opens (2.4)", 5, "THE GATE OPENS", "alarm-bell"], bridge: ["The Charges Blow (4.4)", 4, "THE SECTION RUPTURES", "pressure-rupture"],
  upper: ["Three Ram Impacts (7.3 Upper Gate)", 5, "THE GATE IS BREACHED", "great-door"], lower: ["Hold the Corridor (7.3 Lower Bridge)", 4, "THE CORRIDOR HELD", "war-horn"],
  galleries: ["Before the Flow Reverses (7.3 Pumps)", 5, "THE FLOW REVERSES", "steam-vent"], bastion: ["Last Bastion (8.3)", 6, "RUPTURE — TWO ROUNDS TO SAVE THE HOLD", "pressure-rupture"],
  evac: ["Evacuation (5.5)", 5, "THE VENTS OPEN", "steam-vent"]
};
async function countdown() {
  const buttons = Object.entries(PRESET_COUNT).map(([k, [n]]) => ({ action: k, label: n }));
  const k = await DialogV2().wait({ window: { title: "Countdown" }, content: "<p>The mechanism is visible and explained before initiative. Successful work is never secretly erased.</p>", buttons, rejectClose: false });
  if (!k) return;
  const [name, max, end, sfx] = PRESET_COUNT[k];
  await Clock.set({ visible: true, mode: "count", name, max, cur: 0, end, sfx, bonus: 0 });
  if (k === "bastion") playSfx("alarm-bell");
}

/* ------------------------------------------------------------------------ */
/*  Cards: evidence, favours, dispatches, pressure stages                   */
/* ------------------------------------------------------------------------ */
async function passCard(deckKey, cardKey, toKey) {
  const deck = byKey(game.cards, deckKey); const to = byKey(game.cards, toKey);
  if (!deck || !to) return null;
  const card = deck.cards.find(c => c.getFlag(MOD, "key") === cardKey && !c.drawn);
  if (!card) return null;
  try { await deck.pass(to, [card.id], { chatNotification: false }); } catch (e) { console.warn(MOD, e); }
  return card;
}
async function dealFavour() {
  const deck = byKey(game.cards, "favours");
  if (!deck) return ui.notifications.warn("Install the module content first.");
  const opts = deck.cards.contents.filter(c => !c.drawn).sort((a, b) => a.sort - b.sort).map(c => `<option value="${c.getFlag(MOD, "key")}">${esc(c.name)}</option>`).join("");
  if (!opts) return ui.notifications.info("Every Favour is already in play.");
  const k = await DialogV2().prompt({ window: { title: "Deal a Favour" }, content: `<div class="il-form"><select name="c">${opts}</select><p class="hint">Deal when the party earns it in play. Spent Favours return to the deck.</p></div>`,
    ok: { label: "Deal to Favours Earned", callback: (ev, b) => b.form.elements.c.value } });
  if (!k) return;
  const card = await passCard("favours", k, "hand-favours");
  if (card) chat(`<img class="il-card" src="${card.faces[0]?.img}"><p>The party earns <strong>${esc(card.name)}</strong>.</p>`, "Shield Wall Favours");
}
async function drawDispatch() {
  const deck = byKey(game.cards, "fronts"); const pile = byKey(game.cards, "pile-table");
  if (!deck || !pile) return ui.notifications.warn("Install the module content first.");
  const avail = deck.cards.contents.filter(c => !c.drawn);
  if (!avail.length) return ui.notifications.info("No dispatches left. Right-click the deck in the Cards directory and choose Reset.");
  const card = avail[Math.floor(Math.random() * avail.length)];
  await deck.pass(pile, [card.id], { chatNotification: false });
  playSfx("war-horn");
  chat(`<img class="il-card" src="${card.faces[0]?.img}"><p><strong>Dispatch:</strong> ${esc(card.name)}</p>`, "Siege Dispatch");
}
async function nextPressure() {
  const deck = byKey(game.cards, "pressure"); const pile = byKey(game.cards, "pile-table");
  if (!deck || !pile) return ui.notifications.warn("Install the module content first.");
  const avail = deck.cards.contents.filter(c => !c.drawn && c.getFlag(MOD, "key") !== "relief").sort((a, b) => a.sort - b.sort);
  const pick = await DialogV2().wait({ window: { title: "Last Bastion" }, content: "<p>Flip the next stage, or the relief card when the channel opens.</p>",
    buttons: [{ action: "next", label: "Next Stage" }, { action: "relief", label: "Relief Channel Opens" }], rejectClose: false });
  if (!pick) return;
  const card = pick === "relief" ? deck.cards.find(c => c.getFlag(MOD, "key") === "relief" && !c.drawn) : avail[0];
  if (!card) return ui.notifications.info("No stages left.");
  await deck.pass(pile, [card.id], { chatNotification: false });
  if (pick === "relief") { const s = Clock.get(); if (s.mode === "count") { s.max++; s.bonus = (s.bonus ?? 0) + 1; await Clock.set(s); } }
  else playSfx(card.getFlag(MOD, "key") === "rupture" ? "pressure-rupture" : "steam-vent");
  chat(`<img class="il-card" src="${card.faces[0]?.img}">`, "Last Bastion");
}

/* ------------------------------------------------------------------------ */
/*  Rune Forge                                                              */
/* ------------------------------------------------------------------------ */
const GRADES = { cut: [13, "Cut"], bound: [16, "Bound"], crowned: [19, "Crowned"] };
async function forgeRune() {
  const actor = canvas.tokens?.controlled?.[0]?.actor ?? game.user.character;
  if (!actor) return ui.notifications.warn("Select the crafter's token first.");
  const runes = game.items.filter(i => managed(i) && i.getFlag(MOD, "runeCode")).sort((a, b) => a.name.localeCompare(b.name));
  if (!runes.length) return ui.notifications.warn("Install the module content first.");
  const opts = runes.map(r => `<option value="${r.id}">${esc(r.name)}</option>`).join("");
  const res = await DialogV2().prompt({ window: { title: `Rune Forge — ${actor.name}` },
    content: `<div class="il-form"><label>Rune <select name="r">${opts}</select></label>
      <label>Grade <select name="g"><option value="cut">Cut — DC 13, 4 h, 50 gp</option><option value="bound">Bound — DC 16, 8 h, 250 gp + material</option><option value="crowned">Crowned — DC 19, 24 h, 1,000 gp + rare material + forge</option></select></label>
      <label>Ability <select name="a"><option value="int">Intelligence</option><option value="wis">Wisdom</option><option value="str">Strength</option><option value="dex">Dexterity</option></select></label>
      <label><input type="checkbox" name="p" checked> Proficient with suitable tools</label>
      <label><input type="checkbox" name="x"> Expertise</label>
      <label><input type="checkbox" name="h"> A proficient helper (+2)</label></div>`,
    ok: { label: "Forge", callback: (ev, b) => { const f = b.form.elements; return { r: f.r.value, g: f.g.value, a: f.a.value, p: f.p.checked, x: f.x.checked, h: f.h.checked }; } } });
  if (!res) return;
  const rune = game.items.get(res.r);
  const pb = actor.system?.attributes?.prof ?? 4;
  const mod = (actor.system?.abilities?.[res.a]?.mod ?? 0) + (res.p ? pb * (res.x ? 2 : 1) : 0) + (res.h ? 2 : 0);
  const roll = await new Roll(`1d20 + ${mod}`).evaluate();
  await roll.toMessage({ speaker: ChatMessage.getSpeaker({ actor }), flavor: `Rune Forge: ${rune.name} (${GRADES[res.g][1]})` });
  const dc = GRADES[res.g][0];
  const ok = roll.total >= dc, clear = roll.total >= dc + 5, major = roll.total <= dc - 5;
  if (ok) {
    const html = rune.system.description.value;
    await actor.createEmbeddedDocuments("Item", [{ name: `${rune.name} (${GRADES[res.g][1]})`, type: "feat", img: rune.img,
      system: { description: { value: `<p><strong>${GRADES[res.g][1]} rune</strong>, cut by ${esc(actor.name)} (${roll.total} vs DC ${dc}).</p>${html}` }, type: { value: "" } },
      flags: { [MOD]: { craftedRune: rune.getFlag(MOD, "runeCode"), grade: res.g } } }]);
  }
  playSfx("hammer-strike");
  chat(`<p><strong>${esc(actor.name)}</strong> — ${esc(rune.name)} (${GRADES[res.g][1]}): ${roll.total} vs DC ${dc}.</p>
    <p class="il-ruling ${ok ? "good" : "bad"}">${ok ? (clear ? "CLEAR CUT" : "THE RUNE BINDS") : major ? "MAJOR FAILURE" : "THE RUNE DOES NOT BIND"}</p>
    <p class="hint">${ok ? (clear ? "Recover 25% of the expendable material." : "Added to the character as a feature.") : major ? "Half the materials remain; roll on Rune Forge Complications." : "Half the expendable materials remain."}</p>`, "The Rune Forge");
}

/* ------------------------------------------------------------------------ */
/*  Small table tools                                                       */
/* ------------------------------------------------------------------------ */
async function showHandout() {
  const j = byKey(game.journal, "handouts");
  if (!j) return ui.notifications.warn("Install the module content first.");
  const opts = j.pages.contents.sort((a, b) => a.sort - b.sort).map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join("");
  const id = await DialogV2().prompt({ window: { title: "Show a Handout" }, content: `<div class="il-form"><select name="p">${opts}</select></div>`,
    ok: { label: "Show to Players", callback: (ev, b) => b.form.elements.p.value } });
  if (!id) return;
  const Journal = foundry.documents.collections?.Journal ?? globalThis.Journal;
  return Journal.show(j.pages.get(id), { force: true });
}
async function requestSave() {
  const abil = Object.entries(CONFIG.DND5E.abilities).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join("");
  const res = await DialogV2().prompt({ window: { title: "Request a Saving Throw" },
    content: `<div class="il-form"><label>Ability <select name="a">${abil}</select></label><label>DC <input type="number" name="dc" value="16"></label><label>Reason <input type="text" name="why" value=""></label></div>`,
    ok: { label: "Request", callback: (ev, b) => ({ a: b.form.elements.a.value, dc: b.form.elements.dc.value, why: b.form.elements.why.value }) } });
  if (!res) return;
  chat(`<p>${esc(res.why || "Make a saving throw.")}</p><p>[[/save ${res.a} ${Number(res.dc) || 10}]]</p>`, "Kharad-Varr");
}

/* ------------------------------------------------------------------------ */
/*  Manager                                                                 */
/* ------------------------------------------------------------------------ */
class Manager extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = {
    id: "il-manager", tag: "div", classes: ["il-app"],
    window: { title: "The Unkindness Saga — Manager", icon: "fa-solid fa-shield-halved", resizable: true },
    position: { width: 580, height: "auto" },
    actions: {
      setupAll: async function () { await API.setupAll(); this.render(); },
      board: async function () { Board.open(); },
      partOne: async function () { await rebuildPartOne({ scenes: false }); await repairArt({ quiet: true }); this.render(); },
      art: async function () { await repairArt({ force: true }); this.render(); },
      partOneDash: async function () { await game.catAndUnkindness?.dashboard?.(); },
      install: async function () { await installContent({ update: false }); await grantSpells(); await repairArt({ quiet: true }); this.render(); },
      update: async function () { await updateContent(); this.render(); },
      scenes: async function () { await buildScenes(); this.render(); },
      check: async function () { await checkScenes(); },
      scene: async function (ev, el) { await stageScene(el.dataset.key); await repairArt({ quiet: true }); ui.notifications.info(`Scene rebuilt: ${el.dataset.key}`); },
      remove: async function () { await removeAll(); this.render(); },
      party: async function (ev, el) { const n = await applyPartySize(Number(el.dataset.n)); ui.notifications.info(`Scaled for ${n} heroes.`); this.render(); },
      ledger: async function () { Ledger.open(); },
      inheritance: async function () { Inheritance.open(); },
      resetLedger: async function () {
        if (await DialogV2().confirm({ window: { title: "Reset the Stone Ledger" }, content: "<p>Reset tracks, evidence, council stances and Baldrik's events to the start of the arc?</p>" }))
          await game.settings.set(MOD, "ledger", foundry.utils.deepClone(DEFAULT_LEDGER));
      }
    }
  };
  async _renderHTML() {
    const all = await sceneData();
    const ver = game.modules.get(MOD).version;
    const inst = game.settings.get(MOD, "installedVersion");
    const ps = game.settings.get(MOD, "partySize");
    const rows = all.scenes.map(s => `<li><span>${esc(s.title)}</span><button type="button" data-action="scene" data-key="${s.key}"><i class="fa-solid fa-rotate"></i> Rebuild</button></li>`).join("");
    return `<div class="il-manager">
      <button type="button" class="il-big" data-action="board"><i class="fa-solid fa-gauge-high"></i> Open the DM Control Board</button>
      <header class="il-mhead"><img src="${artUrl()}assets/art/banner.webp" alt=""><p>Module ${ver} · World content ${inst || "not installed"} · Art: ${esc((ART_BASE ?? ART_PREFIX) === ART_PREFIX ? "module folder" : (ART_BASE ?? "").startsWith(GH_RAW) ? "GitHub repository (Forge fallback)" : "Forge assets library")}</p></header>
      <section><h3>Part I — The Cat and the Unkindness (Ravenloft finale)</h3>
        <div class="il-row"><button type="button" data-action="partOne"><i class="fa-solid fa-chess-rook"></i> Set Up / Repair Part I</button>
        <button type="button" data-action="partOneDash"><i class="fa-solid fa-gauge"></i> Finale Dashboard</button></div>
        <p class="hint">23 walled and lit Ravenloft, Vallaki and Barovia scenes, the brides, Strahd's phases, the Dark Powers and the finale state. Its world content lives under <em>The Cat and the Unkindness</em> folders.</p></section>
      <section><h3>Part II — The Shield Between Us (Ironfist Legacy)</h3>
        <button type="button" class="il-big" data-action="setupAll"><i class="fa-solid fa-wand-magic-sparkles"></i> Set Up Everything (Parts I and II)</button>
        <div class="il-row"><button type="button" data-action="install"><i class="fa-solid fa-download"></i> Install Content</button>
        <button type="button" data-action="update"><i class="fa-solid fa-arrows-rotate"></i> Update Content</button>
        <button type="button" data-action="art" title="Point every map, portrait, token, icon and track at a copy that loads (fixes blank maps on The Forge)"><i class="fa-solid fa-image"></i> Repair Art</button>
        <button type="button" data-action="scenes"><i class="fa-solid fa-map"></i> Build All Scenes</button>
        <button type="button" data-action="check" title="Compare every scene with what the module ships and whisper the result"><i class="fa-solid fa-list-check"></i> Check Scenes</button></div>
        <p class="hint">Build All Scenes rebuilds both parts' maps and places every creature (Part I's start hidden: reveal each encounter when it begins). Rebuilding a scene replaces only the walls, lights, pins and tokens this module placed. Update Content refreshes documents from the compendiums and keeps their IDs, so tokens and links keep working.</p></section>
      <section><h3>Party Size</h3><div class="il-row">${[4, 5, 6].map(n => `<button type="button" data-action="party" data-n="${n}" class="${n === ps ? "active" : ""}">${n} heroes</button>`).join("")}</div>
        <p class="hint">Four heroes: Korga, Hadrik and the Bastion Engine drop to about 85% hit points (Appendix A). Six heroes: hit points are unchanged — add one ordinary support enemy or an exposed objective instead.</p></section>
      <section><h3>The Stone Ledger</h3><div class="il-row"><button type="button" data-action="ledger"><i class="fa-solid fa-scale-balanced"></i> Open the Ledger</button><button type="button" data-action="resetLedger">Reset</button></div></section>
      <section><h3>Shadows Beyond Barovia</h3><div class="il-row"><button type="button" data-action="inheritance"><i class="fa-solid fa-eye"></i> The Inheritance of the Mists</button></div>
        <p class="hint">Carries the Ravenloft ending (Dark Power Attention, final choices, brides, Finn, the Wish, prophecies) into this arc. Import it once before Session 1.</p></section>
      <section><h3>Scenes</h3><ul class="il-scenes">${rows}</ul></section>
      <section class="il-danger"><button type="button" data-action="remove"><i class="fa-solid fa-trash"></i> Remove Module Content</button></section>
    </div>`;
  }
  _replaceHTML(result, content) { content.innerHTML = result; }
}

/* ------------------------------------------------------------------------ Shadows Beyond Barovia: the Inheritance of the Mists */
const INH_DEFAULT = {
  imported: false, source: "", session: 1, reputationApplied: false,
  attention: { orcus: 0, vampyr: 0, vecna: 0 },
  disposition: { orcus: "unset", vampyr: "unset", vecna: "distant" },
  status: { orcus: "unknown", vampyr: "unknown", vecna: "departed" },
  facts: { strahd: "unknown", restAccepted: null, tatyanaAgencyHonoured: null, finnFreed: null, bridesSaved: 0, bridesDestroyed: 0,
    wishSource: null, vecnaPrice: "", arlFreed: null, blackRoad: "unknown", mercyBeforeVictory: null,
    prophecies: { damien: false, vesper: false, bunch: false, legna: false, thorgrinn: false } },
  marks: [], log: []
};
const POWER_KEYS = ["orcus", "vampyr", "vecna"];
let INH_DATA = null;
async function inhData() {
  if (INH_DATA) return INH_DATA;
  const r = await fetch(`modules/${MOD}/data/inheritance.json`);
  INH_DATA = await r.json(); return INH_DATA;
}
function inhState() { return foundry.utils.mergeObject(foundry.utils.deepClone(INH_DEFAULT), game.settings.get(MOD, "inheritance") ?? {}, { inplace: false }); }
async function setInh(patch, { replace = false } = {}) {
  if (!game.user.isGM) return ui.notifications.warn("Only the GM can change the Inheritance.");
  const next = replace ? patch : foundry.utils.mergeObject(inhState(), patch, { inplace: false });
  await game.settings.set(MOD, "inheritance", next); return next;
}
function stageOf(v, th) { let s = th[0]; for (const t of th) if (v >= t[0]) s = t; return s; }
function presentPowers(s) {
  const pres = POWER_KEYS.filter(k => (s.attention[k] ?? 0) >= 3);
  const top = Math.max(0, ...pres.map(k => s.attention[k]));
  return { present: pres, primary: pres.filter(k => s.attention[k] >= top - 1) };
}
function matchedOutcomes(s, data) {
  const f = s.facts;
  return data.outcomes.filter(o => { try { return !!(new Function("s", `return (${o.cond});`))(f); } catch (e) { return false; } });
}
function mercyCount(s) {
  const f = s.facts;
  return ["orcus", "vampyr"].filter(k => s.status[k] === "withdrawn").length + (f.bridesSaved ?? 0) + (f.finnFreed ? 1 : 0)
    + (f.tatyanaAgencyHonoured ? 1 : 0) + (f.mercyBeforeVictory ? 1 : 0) + (f.prophecies?.damien ? 1 : 0);
}
function reputationOf(s) {
  const m = mercyCount(s); const harsh = (s.facts.bridesDestroyed ?? 0) + ["orcus", "vampyr"].filter(k => s.status[k] === "banished").length;
  return m >= 4 ? "Merciful" : (m <= 1 && harsh >= 2) ? "Ruthless" : "Balanced";
}
async function readFinale() {
  try { const api = game.catAndUnkindness; if (api?.getState) return await api.getState(); } catch (e) { }
  try { return game.settings.get(MOD, "finaleState"); } catch (e) { }
  const store = game.settings.storage?.get?.("world");
  const doc = store?.getSetting?.("cat-and-unkindness.finaleState") ?? store?.find?.(d => d.key === "cat-and-unkindness.finaleState");
  let v = doc?.value ?? doc?._source?.value;
  if (typeof v === "string") { try { v = JSON.parse(v); } catch (e) { v = null; } }
  return v ?? null;
}
async function importFinale() {
  const f = await readFinale();
  if (!f) return ui.notifications.warn("No Part I finale state was found in this world. Run Part I, or enter the ending by hand in the Inheritance window.");
  const dp = f.darkPowers ?? {}; const att = f.arcAttention ?? {}; const wish = f.wish ?? {};
  const brides = f.brides ?? {}; const bk = ["anastrasya", "volenta", "ludmilla"];
  const chains = f.finnChains ?? {};
  const vecDisp = (wish.source === "vecna" || wish.vecnaDeal?.accepted) ? "claimant" : (Number(att.vecna ?? 0) > 0 ? "curious" : "distant");
  const s = inhState();
  s.imported = true; s.source = `The Cat and the Unkindness (stage: ${f.stage ?? "?"})`;
  s.attention = { orcus: Number(att.orcus ?? 0), vampyr: Number(att.vampyr ?? 0), vecna: Number(att.vecna ?? 0) };
  s.disposition = { orcus: dp.orcus?.disposition ?? "unset", vampyr: dp.vampyr?.disposition ?? "unset", vecna: vecDisp };
  s.status = { orcus: dp.orcus?.status ?? "unknown", vampyr: dp.vampyr?.status ?? "unknown", vecna: dp.vecna?.status ?? "departed" };
  s.facts = {
    strahd: ["barovia-collapse", "campaign-ended"].includes(f.stage) ? "dead" : "unknown",
    restAccepted: f.restAccepted ?? null, tatyanaAgencyHonoured: f.tatyanaAgencyHonoured ?? null,
    finnFreed: brides.finn === "saved" || (chains.sanguine && chains.self && chains.gift) ? true : (brides.finn === "destroyed" || brides.finn === "mist") ? false : null,
    bridesSaved: bk.filter(b => brides[b] === "saved").length, bridesDestroyed: bk.filter(b => brides[b] === "destroyed").length,
    wishSource: wish.cast ? wish.source : null, vecnaPrice: wish.vecnaDeal?.accepted ? `${wish.vecnaDeal.target}: ${wish.vecnaDeal.price}` : "",
    arlFreed: !!(f.vallaki?.arlFreed || (f.allies?.pitFiend && f.allies.pitFiend !== "not-free")),
    blackRoad: "unknown", mercyBeforeVictory: f.vallaki?.mercyBeforeVictory ?? null,
    prophecies: { ...INH_DEFAULT.facts.prophecies, ...(f.prophecies ?? {}) }
  };
  s.log = [...(s.log ?? []), `Imported from the finale (${new Date().toLocaleDateString()})`];
  await setInh(s, { replace: true });
  const data = await inhData(); const p = presentPowers(s);
  chat(`<h3>The Inheritance of the Mists</h3><p>Imported the Ravenloft ending.</p>
    <p>${POWER_KEYS.map(k => `${data.powers[k].name} <strong>${s.attention[k]}</strong> (${stageOf(s.attention[k], data.thresholds)[1]}, ${esc(s.disposition[k])})`).join(" · ")}</p>
    <p>Present: <strong>${p.present.map(k => data.powers[k].name).join(", ") || "none"}</strong>${p.primary.length > 1 ? " — combined arc" : ""}.</p>
    <p>Reputation: <strong>${reputationOf(s)}</strong>. ${matchedOutcomes(s, data).length} outcome rules apply.</p>
    <p class="hint">Set Thorgrinn's Black Road choice by hand: the finale does not record it.</p>`, "Shadows Beyond Barovia", true);
  Inheritance.refresh(); return s;
}
async function adjustAttention(power, delta, reason = "") {
  if (!power) {
    const data = await inhData();
    const r = await DialogV2().prompt({
      window: { title: "Adjust Shadow Attention" },
      content: `<div class="form-group"><label>Power</label><select name="p">${POWER_KEYS.map(k => `<option value="${k}">${data.powers[k].name}</option>`).join("")}</select></div>
        <div class="form-group"><label>Change</label><input name="d" type="number" value="1"></div><div class="form-group"><label>Why</label><input name="r" type="text"></div>`,
      ok: { callback: (ev, btn) => ({ p: btn.form.elements.p.value, d: Number(btn.form.elements.d.value), r: btn.form.elements.r.value }) }
    }).catch(() => null);
    if (!r) return; power = r.p; delta = r.d; reason = r.r;
  }
  const s = inhState(); const data = await inhData();
  const before = s.attention[power] ?? 0; const after = Math.max(0, before + delta);
  const sb = stageOf(before, data.thresholds), sa = stageOf(after, data.thresholds);
  await setInh({ attention: { [power]: after }, log: [...s.log, `${data.powers[power].name} ${delta >= 0 ? "+" : ""}${delta}${reason ? ": " + reason : ""}`] });
  chat(`<p><strong>${data.powers[power].name}</strong> Attention ${before} → <strong>${after}</strong>${reason ? ` <em>(${esc(reason)})</em>` : ""}.</p>${sa[1] !== sb[1] ? `<p>Now <strong>${sa[1]}</strong>: ${sa[2]}</p>` : ""}`, "Shadows Beyond Barovia", true);
}
async function postBeats(n) {
  const s = inhState(); const data = await inhData();
  if (!n) {
    n = await DialogV2().prompt({ window: { title: "Shadow Beat" }, content: `<div class="form-group"><label>Session</label><input name="n" type="number" min="1" max="12" value="${s.session}"></div>`,
      ok: { callback: (ev, btn) => Number(btn.form.elements.n.value) } }).catch(() => null);
    if (!n) return;
  }
  await setInh({ session: n });
  const b = data.beats[String(n)] ?? {}; const pres = presentPowers(s).present;
  const rows = Object.entries(b).filter(([k]) => k === "all" ? pres.length : pres.includes(k));
  if (!rows.length) return chat(`<p>Session ${n}: no Dark Power is present (Attention 3+). Use an omen if you want atmosphere.</p>`, "Shadows Beyond Barovia", true);
  chat(`<h3>Shadow beats — Session ${n}</h3>` + rows.map(([k, v]) => `<p><strong>${k === "all" ? "All present powers" : data.powers[k].name}</strong> (${v.scene.slice(1, 2)}.${v.scene.slice(2)}): ${v.beat}</p><p class="hint"><em>Hook:</em> ${v.hook}</p>`).join(""), "Shadows Beyond Barovia", true);
}
async function offerGift() {
  const s = inhState(); const data = await inhData();
  const opts = POWER_KEYS.flatMap(k => data.gifts[k].map(g => `<option value="${k}:${g.key}" ${s.attention[k] < 3 ? "disabled" : ""}>${data.powers[k].name} — ${g.name}${s.attention[k] < 3 ? " (not present)" : ""}</option>`)).join("");
  const pick = await DialogV2().prompt({ window: { title: "Offer a Dark Gift" }, content: `<div class="form-group"><label>Gift</label><select name="g">${opts}</select></div><p class="hint">State the price before the player decides.</p>`,
    ok: { callback: (ev, btn) => btn.form.elements.g.value } }).catch(() => null);
  if (!pick) return;
  const [k, gk] = pick.split(":"); const g = data.gifts[k].find(x => x.key === gk);
  const card = `<h3>${data.powers[k].name} offers: ${g.name}</h3><p><em>${g.offer}</em></p><p><strong>Gives:</strong> ${g.effect}</p><p><strong>Price:</strong> ${g.price}</p>`;
  chat(card, "Shadows Beyond Barovia", true);
  const res = await DialogV2().wait({ window: { title: g.name }, content: card + "<p>Did they accept?</p>",
    buttons: [{ action: "accept", label: "Accepted" }, { action: "refuse", label: "Refused at real cost (−1)" }, { action: "none", label: "Not yet" }] }).catch(() => "none");
  if (res === "accept") { const add = Number((g.price.match(/\+(\d)/) ?? [0, 1])[1]); await adjustAttention(k, add, `accepted ${g.name}`); await setInh({ marks: [...s.marks, `${data.powers[k].name}: ${g.name}`] }); }
  if (res === "refuse") await adjustAttention(k, -1, `refused ${g.name}`);
}
async function applyReputation() {
  const s = inhState(); if (s.reputationApplied) return ui.notifications.info("Reputation was already applied.");
  const rep = reputationOf(s); const L = ledgerState();
  if (rep === "Merciful") await setLedger({ accord: Math.max(L.accord, 1) });
  if (rep === "Ruthless") await setLedger({ defence: Math.max(L.defence, 3), council: { hadrik: Math.max(L.council.hadrik ?? 0, 1) } });
  await setInh({ reputationApplied: true });
  chat(`<p>Reputation from the Mists: <strong>${rep}</strong>. ${rep === "Merciful" ? "Civilian Accord starts at 1." : rep === "Ruthless" ? "Defence Readiness starts at 3; Hadrik starts Supportive. Accord cannot rise above 3 until a public act of mercy." : "No change."}</p>`, "Shadows Beyond Barovia", true);
}
class InheritanceApp extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = {
    id: "il-inheritance", tag: "div", classes: ["il-app"],
    window: { title: "Shadows Beyond Barovia — The Inheritance of the Mists", icon: "fa-solid fa-eye", resizable: true },
    position: { width: 620, height: "auto" },
    actions: {
      att: async function (ev, el) { await adjustAttention(el.dataset.p, Number(el.dataset.d)); },
      disp: async function (ev, el) { const v = window.prompt("Disposition", inhState().disposition[el.dataset.p]); if (v != null) await setInh({ disposition: { [el.dataset.p]: v } }); },
      fact: async function (ev, el) {
        const k = el.dataset.f; const s = inhState(); const cur = s.facts[k];
        const opts = { strahd: ["dead", "escaped", "unknown"], wishSource: ["djinn", "vecna", "other", null], blackRoad: ["accepted", "refused", "unknown"] }[k];
        let next;
        if (opts) next = opts[(opts.indexOf(cur) + 1) % opts.length];
        else if (typeof cur === "number") next = (cur + 1) % 4;
        else next = cur === true ? false : cur === false ? null : true;
        await setInh({ facts: { [k]: next } });
      },
      proph: async function (ev, el) { const s = inhState(); await setInh({ facts: { prophecies: { [el.dataset.k]: !s.facts.prophecies[el.dataset.k] } } }); },
      importF: async function () { await importFinale(); },
      beat: async function () { await postBeats(); },
      gift: async function () { await offerGift(); },
      rep: async function () { await applyReputation(); },
      clearMarks: async function () { await setInh({ marks: [] }); },
      reset: async function () { if (await DialogV2().confirm({ window: { title: "Reset the Inheritance" }, content: "<p>Clear the imported ending, Attention and marks?</p>" })) await setInh(foundry.utils.deepClone(INH_DEFAULT), { replace: true }); }
    }
  };
  async _renderHTML() {
    const s = inhState(); const data = await inhData(); const gm = game.user.isGM; const p = presentPowers(s);
    const rows = POWER_KEYS.map(k => {
      const st = stageOf(s.attention[k], data.thresholds); const tag = p.primary.includes(k) ? (p.primary.length > 1 ? "co-primary" : "primary") : p.present.includes(k) ? "present" : "watching";
      return `<div class="il-power" style="border-left:6px solid ${data.powers[k].color}"><img src="${artUrl()}assets/icons/${data.powers[k].icon}.webp" alt="">
        <div><b>${data.powers[k].name}</b> <span class="hint">${data.powers[k].title}</span><br>
        ${gm ? `<button type="button" data-action="att" data-p="${k}" data-d="-1">−</button>` : ""}<strong class="il-att">${s.attention[k]}</strong>${gm ? `<button type="button" data-action="att" data-p="${k}" data-d="1">+</button>` : ""}
        <em>${st[1]}</em> · <span class="il-tag">${tag}</span> · <a data-action="disp" data-p="${k}">${esc(s.disposition[k])}</a> · ${esc(s.status[k])}</div></div>`;
    }).join("");
    const F = s.facts; const yn = v => v === true ? "yes" : v === false ? "no" : v ?? "—";
    const fact = (k, l) => `<button type="button" class="il-ev ${F[k] ? "on" : ""}" data-action="fact" data-f="${k}">${l}: ${esc(String(yn(F[k])))}</button>`;
    const proph = Object.keys(F.prophecies).map(k => `<button type="button" class="il-ev ${F.prophecies[k] ? "on" : ""}" data-action="proph" data-k="${k}">${k}</button>`).join("");
    const outs = matchedOutcomes(s, data).map(o => `<li><strong>${o.label}.</strong> ${o.effect}</li>`).join("") || "<li class='hint'>None yet — import or set the facts above.</li>";
    const comb = p.primary.length > 1 ? data.combined.find(c => c.key === (p.primary.length === 3 ? "all" : p.primary.slice().sort().join("+"))) : null;
    return `<div class="il-inheritance">
      <p class="hint">${s.imported ? esc(s.source) : "Not imported yet."} · Session ${s.session} · Reputation <strong>${reputationOf(s)}</strong>${s.reputationApplied ? " (applied)" : ""}</p>
      ${rows}
      ${comb ? `<div class="il-box"><h4>Combined arc: ${comb.name}</h4><p>${comb.rule}</p></div>` : ""}
      <h3>How Ravenloft ended</h3><div class="il-row">${fact("strahd", "Strahd")}${fact("restAccepted", "Courtesy accepted")}${fact("tatyanaAgencyHonoured", "Tatyana honoured")}${fact("finnFreed", "Finn freed")}
        ${fact("bridesSaved", "Brides saved")}${fact("bridesDestroyed", "Brides destroyed")}${fact("wishSource", "Wish")}${fact("arlFreed", "Arl fought")}${fact("blackRoad", "Black Road")}${fact("mercyBeforeVictory", "Vallaki mercy")}</div>
      <h3>Prophecies fulfilled</h3><div class="il-row">${proph}</div>
      <h3>Rules in force</h3><ul class="il-outcomes">${outs}</ul>
      <h3>Marks & Gifts taken</h3><p>${s.marks.map(esc).join(" · ") || "<span class='hint'>none</span>"}</p>
      ${gm ? `<div class="il-row"><button type="button" data-action="importF"><i class="fa-solid fa-file-import"></i> Import finale</button><button type="button" data-action="beat"><i class="fa-solid fa-ghost"></i> Shadow beat</button>
        <button type="button" data-action="gift"><i class="fa-solid fa-hand-holding"></i> Offer a Gift</button><button type="button" data-action="rep"><i class="fa-solid fa-scale-balanced"></i> Apply reputation</button>
        <button type="button" data-action="clearMarks">Clear marks</button><button type="button" data-action="reset">Reset</button></div>` : ""}
    </div>`;
  }
  _replaceHTML(result, content) { content.innerHTML = result; }
}
const Inheritance = {
  app: null,
  open() { this.app ??= new InheritanceApp(); return this.app.render(true); },
  refresh() { if (this.app?.rendered) this.app.render(); },
  beat: postBeats, gift: offerGift, adjust: adjustAttention, importFinale, applyReputation, state: inhState
};

/* ------------------------------------------------------------------------ migration from the separate modules */
const LEGACY_SCOPES = { "cat-and-unkindness": "ravenloft", "ironfist-legacy": "ironfist" };
const LEGACY_SETTINGS = { "cat-and-unkindness": ["finaleState"], "ironfist-legacy": ["ledger", "clock", "inheritance", "partySize", "autoMusic", "promptDismissed"] };
async function migrateLegacy({ quiet = false } = {}) {
  if (!game.user.isGM) return;
  let docs = 0, emb = 0, sets = 0;
  const store = game.settings.storage?.get?.("world");
  for (const [scope, keys] of Object.entries(LEGACY_SETTINGS)) for (const k of keys) {
    const doc = store?.getSetting?.(`${scope}.${k}`) ?? store?.find?.(d => d.key === `${scope}.${k}`);
    if (!doc) continue;
    let v = doc.value ?? doc._source?.value; if (typeof v === "string") { try { v = JSON.parse(v); } catch (e) { } }
    const already = store?.getSetting?.(`${MOD}.${k}`) ?? store?.find?.(d => d.key === `${MOD}.${k}`);
    if (already || v == null) continue;
    try { await game.settings.set(MOD, k, v); sets++; } catch (e) { console.warn(MOD, "setting migration", k, e); }
  }
  const EMB_TYPE = { walls: "Wall", lights: "AmbientLight", notes: "Note", tokens: "Token", tiles: "Tile", sounds: "AmbientSound", drawings: "Drawing", regions: "Region", items: "Item", effects: "ActiveEffect", pages: "JournalEntryPage" };
  const EMB = { Scene: ["walls", "lights", "notes", "tokens", "tiles", "sounds", "drawings", "regions"], Actor: ["items", "effects"], JournalEntry: ["pages"], Item: ["effects"] };
  const patch = (d, scope) => { const f = d.flags?.[scope]; if (!f || d.flags?.[MOD]) return null; return { _id: d.id, [`flags.${MOD}`]: { ...foundry.utils.deepClone(f), ...(LEGACY_SCOPES[scope] === "ravenloft" ? { part: "ravenloft" } : {}) } }; };
  for (const coll of [game.folders, game.scenes, game.actors, game.items, game.journal, game.tables, game.macros, game.playlists, game.cards]) {
    if (!coll?.map) continue;
    for (const scope of Object.keys(LEGACY_SCOPES)) {
      const ups = coll.map(d => patch(d, scope)).filter(Boolean);
      if (ups.length) { await coll.documentClass.updateDocuments(ups, { cuInternal: true }); docs += ups.length; }
    }
    for (const d of (coll.contents ?? [...coll.values()])) for (const field of (EMB[d.documentName] ?? [])) {
      const c = d[field]; if (!c?.size || !c.map) continue;
      for (const scope of Object.keys(LEGACY_SCOPES)) {
        const ups = c.map(e => patch(e, scope)).filter(Boolean);
        if (ups.length) { await d.updateEmbeddedDocuments(EMB_TYPE[field], ups, { cuInternal: true }); emb += ups.length; }
      }
    }
  }
  if (!quiet || docs || emb || sets) ui.notifications.info(`The Unkindness Saga: migrated ${docs} documents, ${emb} embedded records and ${sets} settings from the separate modules.`);
  await game.settings.set(MOD, "migrated", true);
}

// ---------------------------------------------------------------- art hosting
// The Forge sometimes installs a custom module's code and data but none of its images or audio, so every
// modules/unkindness-saga/assets/... request answers 404. When that happens the module finds another copy
// that does load (the Forge assets library, then this module's GitHub repository, which serves the same
// files with cross-site access) and rewrites the art paths in every world document it created.
const ART_PREFIX = `modules/${MOD}/`;
const ART_PROBE = "assets/art/banner.webp";
const GH_RAW = "https://raw.githubusercontent.com/pacts-and-polyhedrals/unkindness-saga";
const ART_RX = () => new RegExp(String.raw`(?:https://raw\.githubusercontent\.com/pacts-and-polyhedrals/unkindness-saga/[^/"'\s()]+/module/|https://assets\.forge-vtt\.com/[^"'\s()]*?/modules/unkindness-saga/|modules/unkindness-saga/)(?=assets/)`, "g");
let ART_BASE = null, ART_REPORT = [];
function probeImage(url, ms = 10000) {
  if (typeof Image === "undefined") return Promise.resolve(url.startsWith(ART_PREFIX));
  return new Promise(res => {
    const img = new Image(); if (/^https?:/.test(url)) img.crossOrigin = "anonymous";
    const t = setTimeout(() => { img.src = ""; res(false); }, ms);
    img.onload = () => { clearTimeout(t); res(true); }; img.onerror = () => { clearTimeout(t); res(false); };
    img.src = url;
  });
}
async function artBase(force = false) {
  if (ART_BASE !== null && !force) return ART_BASE;
  const ver = game.modules.get(MOD)?.version ?? "main";
  const cands = [ART_PREFIX];
  try {
    const P = globalThis.ForgeVTT?.ASSETS_LIBRARY_URL_PREFIX, uid = await globalThis.ForgeAPI?.getUserId?.();
    if (P && uid) cands.push(`${P}${uid}/${ART_PREFIX}`);
  } catch (e) { /* not on The Forge */ }
  cands.push(`${GH_RAW}/v${ver}/module/`, `${GH_RAW}/main/module/`);
  ART_REPORT = [];
  for (const b of cands) {
    const ok = await probeImage(b + ART_PROBE);
    ART_REPORT.push(`${ok ? "OK " : "404"} ${b}${ART_PROBE}`);
    if (ok) return (ART_BASE = b);
  }
  return (ART_BASE = ART_PREFIX);
}
const artUrl = (p = "") => (ART_BASE ?? ART_PREFIX) + p;
function fixArt(v, base) {
  if (typeof v === "string") return v.includes("assets/") ? v.replace(ART_RX(), base) : v;
  if (Array.isArray(v)) return v.map(x => fixArt(x, base));
  if (v && typeof v === "object") { const o = {}; for (const [k, x] of Object.entries(v)) o[k] = fixArt(x, base); return o; }
  return v;
}
function flatArt(o, pre = "", out = {}) {
  for (const [k, v] of Object.entries(o ?? {})) {
    const key = pre ? `${pre}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) flatArt(v, key, out); else out[key] = v;
  }
  return out;
}
/** Only the fields whose art path changes, as a flat update ({"texture.src": …}). */
function artChanges(obj, base, skip = new Set()) {
  const out = {};
  for (const [k, v] of Object.entries(flatArt(obj))) {
    if (skip.has(k.split(".")[0]) || k === "_id" || k.startsWith("_stats")) continue;
    if (typeof v === "string") { const nv = fixArt(v, base); if (nv !== v) out[k] = nv; }
    else if (Array.isArray(v)) { const nv = fixArt(v, base); if (JSON.stringify(nv) !== JSON.stringify(v)) out[k] = nv; }
  }
  return out;
}
/** v14: tokens this module placed before 2.1.3 were given no level, which Foundry rejects when they move. */
async function fixTokenLevels() {
  if (!game.user?.isGM || gen() < 14) return 0;
  let n = 0;
  for (const sc of game.scenes?.contents ?? []) {
    if (!sc.flags?.[MOD] || !sc.tokens?.size) continue;
    const lvl = sc.initialLevel ?? sc.levels?.contents?.[0];
    if (!lvl) continue;
    const ids = new Set(sc.levels.map(l => l.id));
    const ups = sc.tokens.filter(t => !ids.has(t._source?.level ?? t.level)).map(t => ({ _id: t.id, level: lvl.id }));
    if (!ups.length) continue;
    try { await sc.updateEmbeddedDocuments("Token", ups, { cuInternal: true }); n += ups.length; }
    catch (e) { for (const u of ups) { try { await sc.updateEmbeddedDocuments("Token", [u], { cuInternal: true }); n++; } catch (e2) { console.warn(MOD, "token level", sc.name, u._id, e2.message); } } }
  }
  if (n) console.log(`${MOD} | placed ${n} tokens on their scene's level`);
  return n;
}
/** Part I's walls and lights are in map-image coordinates; scene padding shifted the map under them. */
async function fixPartOnePadding() {
  if (!game.user?.isGM) return 0;
  let n = 0;
  for (const sc of game.scenes?.contents ?? []) {
    if (sc.flags?.[MOD]?.part !== "ravenloft" || !sc.padding) continue;
    try { await sc.update({ padding: 0 }, { cuInternal: true }); n++; } catch (e) { console.warn(MOD, "padding", sc.name, e.message); }
  }
  if (n) ui.notifications.info(`The Unkindness Saga: realigned ${n} Part I maps with their walls and lights.`);
  return n;
}
let ART_RUNNING = null;
/** Point every art path in the world documents at the copy that loads. Safe to repeat. */
function repairArt(opts = {}) { return (ART_RUNNING ??= runRepairArt(opts).finally(() => { ART_RUNNING = null; })); }
async function runRepairArt({ quiet = false, force = false } = {}) {
  if (!game.user?.isGM) return 0;
  try { await fixTokenLevels(); } catch (e) { console.error(MOD, "token levels", e); }
  const base = await artBase(force);
  const last = game.settings.get(MOD, "artBase");
  if (base === ART_PREFIX && last === ART_PREFIX && !force) return 0;
  // find what needs changing first, so the GM sees how much work there is
  const todo = [];
  for (const coll of [game.scenes, game.actors, game.items, game.journal, game.tables, game.macros, game.playlists, game.cards])
    for (const doc of (coll?.contents ?? [])) {
      const raw = JSON.stringify(doc.toObject());
      if (raw.includes("unkindness-saga/") && raw.replace(ART_RX(), base) !== raw) todo.push(doc);
    }
  if (!todo.length) {
    await game.settings.set(MOD, "artBase", base);
    if (!quiet) ui.notifications.info(`The Unkindness Saga: art already loads from ${artWhere(base)}.`);
    return 0;
  }
  const note = ui.notifications.info(`The Unkindness Saga: pointing ${todo.length} documents at the art in ${artWhere(base)}. Leave this world open until it says it's done…`, { permanent: true });
  let docs = 0, emb = 0; const errors = []; const scenes = new Set();
  for (const doc of todo) {
    try {
      const src = doc.toObject();
      const embedded = doc.constructor?.metadata?.embedded ?? doc._embeddedMap ?? {};
      const upd = artChanges(src, base, new Set(Object.values(embedded)));
      if (Object.keys(upd).length) { await doc.update(upd, { cuInternal: true }); docs++; }
      for (const [cls, key] of Object.entries(embedded)) {
        const ups = [];
        for (const e of (src[key] ?? [])) { const c = artChanges(e, base); if (Object.keys(c).length) ups.push({ _id: e._id, ...c }); }
        if (!ups.length) continue;
        try { await doc.updateEmbeddedDocuments(cls, ups, { cuInternal: true }); emb += ups.length; if (doc.documentName === "Scene") scenes.add(doc); }
        catch (e) {
          for (const u of ups) { try { await doc.updateEmbeddedDocuments(cls, [u], { cuInternal: true }); emb++; if (doc.documentName === "Scene") scenes.add(doc); } catch (e2) { errors.push(`${doc.name} › ${cls} ${u._id}: ${e2.message}`); } }
        }
      }
    } catch (e) { errors.push(`${doc.documentName} ${doc.name}: ${e.message}`); }
  }
  await game.settings.set(MOD, "artBase", base);
  note?.remove?.();
  const msg = `The Unkindness Saga: art now loads from ${artWhere(base)} (${docs} documents, ${emb} embedded records updated${errors.length ? `, ${errors.length} could not be updated — see the console` : ""}).`;
  if (errors.length) { console.error(MOD, "art repair problems", errors); ui.notifications.warn(msg, { permanent: true }); } else ui.notifications.info(msg);
  // thumbnails last: they download every map once
  for (const sc of scenes) { try { const t = await sc.createThumbnail(); if (t?.thumb) await sc.update({ thumb: t.thumb }, { cuInternal: true }); } catch (e) { console.warn(MOD, "thumbnail", sc.name, e); } }
  return docs + emb;
}
const artWhere = b => b === ART_PREFIX ? "the module folder" : b.startsWith(GH_RAW) ? "the module's GitHub repository" : "your Forge assets library";
const ArtAPI = { inhabitants: placePartOneTokens, base: artBase, repair: repairArt, tokens: fixTokenLevels, padding: fixPartOnePadding, spells: grantSpells, p1tokens: placePartOneTokens, p1rebuild: rebuildPartOne, p1scene: stagePartOneScene, check: checkScenes, report: async () => { await artBase(true); console.log(ART_REPORT.join("\n")); return ART_REPORT; } };

// ---------------------------------------------------------------- Part I creature placement
// data/ravenloft/tokens.json lists where each Part I creature stands (token centres). Every placed token starts hidden.
// ---------------------------------------------------------------- the castle's other inhabitants
// data/ravenloft/inhabitants.json: groups of SRD monsters per Part I map (anchor in map fractions). The stat blocks
// are imported once from the dnd5e system's monster compendium into "07 — Castle Inhabitants".
let MONSTER_INDEX = null;
async function monsterIndex() {
  if (MONSTER_INDEX) return MONSTER_INDEX;
  MONSTER_INDEX = new Map();
  const packs = (game.packs?.contents ?? [...(game.packs?.values?.() ?? [])]).filter(p => p.documentName === "Actor" && (p.metadata?.packageName === "dnd5e" || String(p.metadata?.id ?? p.collection).startsWith("dnd5e.")));
  packs.sort((a, b) => /legacy/i.test(a.collection) - /legacy/i.test(b.collection));
  for (const pack of packs) {
    let idx; try { idx = await pack.getIndex(); } catch (e) { continue; }
    for (const e of (idx.contents ?? [...idx.values?.() ?? idx])) {
      const k = String(e.name).toLowerCase().replace(/[’']/g, "'").trim();
      if (!MONSTER_INDEX.has(k)) MONSTER_INDEX.set(k, { pack, id: e._id });
    }
  }
  return MONSTER_INDEX;
}
async function inhabitantActor(key, names, missing) {
  const have = game.actors.find(a => a.flags?.[MOD]?.inhabitant === key);
  if (have) return have;
  const idx = await monsterIndex();
  const hit = names.map(n => idx.get(n.toLowerCase().replace(/[’']/g, "'"))).find(Boolean);
  if (!hit) { missing.add(names[0]); return null; }
  const src = await hit.pack.getDocument(hit.id); if (!src) { missing.add(names[0]); return null; }
  const folder = await folderPath("Actor", "The Cat and the Unkindness/07 — Castle Inhabitants");
  const d = src.toObject(); delete d._id; delete d._stats;
  d.folder = folder?.id ?? null;
  d.flags = { ...(d.flags ?? {}), [MOD]: { inhabitant: key } };
  return Actor.create(d, { cuInternal: true });
}
// Free squares near an anchor, in the same room: never across a wall, not hugging one, not on another token.
function spreadSquares(scene, ax, ay, size, count, occ) {
  const g = scene.grid?.size ?? 100, W = scene.width, H = scene.height;
  const walls = scene.walls.filter(w => (w.move ?? 1) !== 0).map(w => w.c);
  const cross = (p1, p2, a, b) => { const o = (u, v, w) => (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0]);
    return ((o(a, b, p1) > 0) !== (o(a, b, p2) > 0)) && ((o(p1, p2, a) > 0) !== (o(p1, p2, b) > 0)); };
  const dist = (px, py, c) => { const dx = c[2] - c[0], dy = c[3] - c[1], L = dx * dx + dy * dy; const t = L ? Math.max(0, Math.min(1, ((px - c[0]) * dx + (py - c[1]) * dy) / L)) : 0; return Math.hypot(px - (c[0] + t * dx), py - (c[1] + t * dy)); };
  const cx = Math.floor(ax / g), cy = Math.floor(ay / g), R = 10, out = [];
  const cands = []; for (let dx = -R; dx <= R; dx++) for (let dy = -R; dy <= R; dy++) cands.push([dx, dy]);
  cands.sort((a, b) => (a[0] ** 2 + a[1] ** 2) - (b[0] ** 2 + b[1] ** 2));
  for (const [dx, dy] of cands) {
    if (out.length >= count) break;
    const x0 = cx + dx, y0 = cy + dy, cells = [];
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) cells.push([x0 + i, y0 + j]);
    const ok = cells.every(([qx, qy]) => { const px = (qx + 0.5) * g, py = (qy + 0.5) * g;
      return !occ.has(`${qx},${qy}`) && px > 0 && py > 0 && px < W && py < H && !walls.some(c => cross([ax, ay], [px, py], [c[0], c[1]], [c[2], c[3]]) || dist(px, py, c) < 0.45 * g); });
    if (!ok) continue;
    cells.forEach(([qx, qy]) => occ.add(`${qx},${qy}`)); out.push({ x: x0 * g, y: y0 * g });
  }
  return out;
}
function occupied(scene) {
  const g = scene.grid?.size ?? 100, occ = new Set();
  for (const t of scene.tokens) { const x0 = Math.round(t.x / g), y0 = Math.round(t.y / g); for (let i = 0; i < (t.width ?? 1); i++) for (let j = 0; j < (t.height ?? 1); j++) occ.add(`${x0 + i},${y0 + j}`); }
  return occ;
}
async function placePartOneTokens(only = null) {
  if (!game.user?.isGM) return 0;
  let plan, inh; try { [plan, inh] = await Promise.all([p1json("tokens.json"), p1json("inhabitants.json")]); } catch (e) { console.warn(MOD, "Part I tokens", e); return 0; }
  const actorFor = sid => game.actors.find(a => a.getFlag?.(MOD, "sourceId") === sid || a.flags?.[MOD]?.sourceId === sid);
  let n = 0; const missing = new Set(), missingMon = new Set();
  for (const sid of new Set([...Object.keys(plan), ...Object.keys(inh.scenes)])) {
    if (only && !only.includes(sid)) continue;
    const scene = game.scenes.find(sc => sc.getFlag?.(MOD, "sourceId") === sid || sc.flags?.[MOD]?.sourceId === sid);
    if (!scene) continue;
    try {
      const old = scene.tokens.filter(t => t.flags?.[MOD]?.p1token).map(t => t.id);
      if (old.length) await scene.deleteEmbeddedDocuments("Token", old);
      const levelId = gen() >= 14 ? (await sceneLevel(scene))?.id : null;
      const grid = scene.grid?.size ?? 100;
      const finish = data => { foundry.utils.setProperty(data, `flags.${MOD}.p1token`, true); delete data.levels; if (levelId) data.level = levelId; return data; };
      const docs = [];
      for (const t of plan[sid] ?? []) {
        const actor = actorFor(t.actor);
        if (!actor) { missing.add(t.actor); continue; }
        const w = actor.prototypeToken?.width ?? 1, h = actor.prototypeToken?.height ?? w;
        const data = (await actor.getTokenDocument({ x: Math.round(t.x - (w * grid) / 2), y: Math.round(t.y - (h * grid) / 2), hidden: true })).toObject();
        data.name = t.name || data.name || actor.name;
        docs.push(finish(data));
      }
      if (docs.length) { await scene.createEmbeddedDocuments("Token", docs); n += docs.length; }
      // the other inhabitants, spread over free squares around each group's anchor
      const occ = occupied(scene), more = [];
      for (const grp of inh.scenes[sid] ?? []) {
        const actor = await inhabitantActor(grp.m, inh.monsters[grp.m] ?? [grp.m], missingMon);
        if (!actor) continue;
        const size = Math.max(1, Math.round(actor.prototypeToken?.width ?? 1));
        for (const sq of spreadSquares(scene, grp.x * scene.width, grp.y * scene.height, size, grp.n, occ)) {
          const data = (await actor.getTokenDocument({ x: sq.x, y: sq.y, hidden: true })).toObject();
          if (grp.label) data.name = grp.label;
          foundry.utils.setProperty(data, `flags.${MOD}.inhabitant`, grp.m);
          more.push(finish(data));
        }
      }
      if (more.length) { await scene.createEmbeddedDocuments("Token", more); n += more.length; }
    } catch (e) { console.error(MOD, "Part I tokens on", scene.name, e); }
  }
  if (missing.size) console.warn(`${MOD} | Part I creatures not in this world (run Set Up / Repair Part I):`, [...missing]);
  if (missingMon.size) ui.notifications.warn(`The Unkindness Saga: ${missingMon.size} castle inhabitants weren't found in your dnd5e monster compendium and were left off the maps: ${[...missingMon].join(", ")}.`);
  return n;
}
// ---------------------------------------------------------------- Part I scenes, built by this module
// Part I's own setup still imports its journals, actors and macros; its maps are built here the same way as
// Part II's (walls and lights on the scene's level, in batches that survive a bad entry), then checked.
const p1data = {};
async function p1json(f) { return (p1data[f] ??= await (await fetch(`modules/${MOD}/data/ravenloft/${f}`)).json()); }
async function folderPath(type, path) {
  let parent = null;
  for (const name of String(path ?? "").split("/").map(x => x.trim()).filter(Boolean)) {
    let f = game.folders.find(x => x.type === type && x.name === name && (x.folder?.id ?? x.folder ?? null) === (parent?.id ?? null));
    if (!f) f = await Folder.create({ name, type, folder: parent?.id ?? null, sorting: "a" }, { cuInternal: true });
    parent = f;
  }
  return parent;
}
const bySource = (coll, sid) => coll.find(d => d.flags?.[MOD]?.sourceId === sid);
async function createSafely(scene, type, docs) {
  let ok = 0, bad = 0;
  for (let i = 0; i < docs.length; i += 100) {
    const chunk = docs.slice(i, i + 100);
    try { const r = await scene.createEmbeddedDocuments(type, chunk, { cuInternal: true }); ok += r?.length ?? chunk.length; }
    catch (e) {
      for (const d of chunk) { try { await scene.createEmbeddedDocuments(type, [d], { cuInternal: true }); ok++; } catch (e2) { bad++; console.warn(`${MOD} | ${scene.name}: skipped a ${type}`, e2.message, d); } }
    }
  }
  return { ok, bad };
}
async function stagePartOneScene(src) {
  const [plan, pins] = await Promise.all([p1json("tokens.json"), p1json("pins.json")]);
  const base = await artBase();
  const img = fixArt(src.img, base);
  const folder = await folderPath("Scene", src.folder);
  const W = src.width, H = src.height;
  const flags = { [MOD]: { sourceId: src.sourceId, managed: true, part: "ravenloft", lastSourceHash: src.sourceHash, dirty: false } };
  const data = { name: src.name, folder: folder?.id ?? null, width: W, height: H, padding: 0, backgroundColor: "#050306",
    grid: { type: 1, size: src.gridSize, distance: src.gridDistance ?? 5, units: "ft" }, tokenVision: true,
    environment: { darknessLevel: src.darkness ?? 0.6, globalLight: { enabled: false } }, flags };
  let scene = bySource(game.scenes, src.sourceId);
  if (!scene) {
    const create = { ...data, sort: src.sort ?? 0, navigation: false };
    if (gen() >= 14) create.levels = [{ name: "Ground", background: { src: img } }]; else create.background = { src: img };
    scene = await Scene.create(create, { cuInternal: true });
  } else await scene.update(data, { cuInternal: true });
  await setBackground(scene, img, "Ground");
  const level = gen() >= 14 ? (await sceneLevel(scene))?.id : null;
  const lv = level ? { levels: [level] } : {};
  const mine = d => d.flags?.["unkindness-saga"]?.managed || d.flags?.[MOD]?.p1token || d.flags?.[MOD]?.p1pin;
  for (const [type, coll] of [["Wall", scene.walls], ["AmbientLight", scene.lights], ["Note", scene.notes], ["Token", scene.tokens]]) {
    const ids = coll.filter(mine).map(d => d.id);
    if (ids.length) await scene.deleteEmbeddedDocuments(type, ids, { cuInternal: true });
  }
  const tag = { [MOD]: { managed: true, part: "ravenloft" } };
  const cl = (v, m) => Math.max(0, Math.min(m, Math.round(v)));
  const walls = (src.walls ?? []).map(w => ({ c: [cl(w.c[0], W), cl(w.c[1], H), cl(w.c[2], W), cl(w.c[3], H)], move: w.move, sight: w.sight, light: w.light, sound: w.sound,
    door: w.door ?? 0, ds: w.ds ?? 0, dir: w.dir ?? 0, flags: tag, ...lv })).filter(w => w.c[0] !== w.c[2] || w.c[1] !== w.c[3]);
  const lights = (src.lights ?? []).map(l => ({ ...l, x: cl(l.x, W), y: cl(l.y, H), flags: tag, ...lv }));
  const rw = await createSafely(scene, "Wall", walls);
  const rl = await createSafely(scene, "AmbientLight", lights);
  // map pins to the journal pages that run each scene
  const notes = []; let journal = null;
  for (const p of pins[src.sourceId] ?? []) {
    const j = bySource(game.journal, p.journal); if (!j) continue;
    const page = j.pages.find(pg => pg.flags?.[MOD]?.sourcePageId === p.page);
    journal ??= { j: j.id, p: page?.id ?? null };
    notes.push({ x: cl(p.x, W), y: cl(p.y, H), entryId: j.id, pageId: page?.id ?? null, text: p.label, global: false,
      texture: { src: `${artUrl()}assets/icons/note-pin.webp` }, iconSize: Math.max(48, Math.round(src.gridSize * 0.6)), fontSize: Math.max(22, Math.round(src.gridSize * 0.22)), textAnchor: 1,
      flags: { [MOD]: { p1pin: true } }, ...lv });
  }
  const rn = await createSafely(scene, "Note", notes);
  if (journal) await scene.update({ journal: journal.j, journalEntryPage: journal.p }, { cuInternal: true });
  const rt = await placePartOneTokens([src.sourceId]);
  try { const th = await scene.createThumbnail({ img }); if (th?.thumb) await scene.update({ thumb: th.thumb }, { cuInternal: true }); } catch (e) { /* thumbnails are optional */ }
  return { scene, walls: rw, lights: rl, notes: rn, tokens: rt };
}
async function buildPartOneScenes() {
  const C = game.catAndUnkindness;
  await migrateLegacy();
  if (C?.setup) { try { await C.setup(); } catch (e) { console.error(MOD, "Part I setup", e); } }
  const { scenes } = await p1json("scenes.json");
  let tokens = 0;
  for (const src of scenes) {
    try { const r = await stagePartOneScene(src); tokens += r.tokens; }
    catch (e) { console.error(`${MOD} | Part I scene ${src.name}`, e); }
  }
  return tokens;
}
async function rebuildPartOne({ scenes = true } = {}) {
  if (scenes) return buildPartOneScenes();
  const C = game.catAndUnkindness;
  await migrateLegacy(); if (C?.setup) await C.setup(); await fixPartOnePadding();
  return placePartOneTokens();
}
// ---------------------------------------------------------------- scene check
async function checkScenes({ repair = false, post = true } = {}) {
  const base = await artBase();
  const [{ scenes: p1 }, plan, pins, all, inh] = await Promise.all([p1json("scenes.json"), p1json("tokens.json"), p1json("pins.json"), sceneData(), p1json("inhabitants.json")]);
  const bgOf = sc => sc ? ((gen() >= 14 ? (sc.initialLevel ?? sc.levels?.contents?.[0])?.background?.src : null) ?? sc.background?.src ?? "") : "";
  const rows = [];
  const look = async (part, name, sc, want, fix) => {
    const got = sc ? { walls: sc.walls.size, lights: sc.lights.size, notes: sc.notes.size, tokens: sc.tokens.size } : null;
    const bg = bgOf(sc); const map = bg ? await probeImage(fixArt(bg, base), 15000) : false;
    const short = !sc || !map || got.walls < want.walls || got.lights < want.lights || got.notes < want.notes || got.tokens < want.tokens;
    rows.push({ part, name, sc, got, want, map, short, fix });
  };
  for (const s of p1) {
    const sc = bySource(game.scenes, s.sourceId);
    await look("I", s.name, sc, { walls: s.walls.length, lights: s.lights.length, notes: (pins[s.sourceId] ?? []).length, tokens: (plan[s.sourceId] ?? []).length + (inh.scenes[s.sourceId] ?? []).reduce((k, g) => k + g.n, 0) }, () => stagePartOneScene(s));
  }
  for (const s of all.scenes) {
    const sc = game.scenes.get(s.id);
    await look("II", s.title, sc, { walls: s.walls?.length ?? 0, lights: s.lights?.length ?? 0, notes: (s.notes ?? []).filter(n => game.journal.get(n.entryId)).length, tokens: (s.tokens ?? []).filter(t => game.actors.get(t.actorId)).length }, () => stageScene(s.key));
  }
  let fixed = 0;
  if (repair) for (const r of rows.filter(r => r.short)) {
    try { await r.fix(); fixed++; } catch (e) { console.error(MOD, "repair", r.name, e); }
  }
  if (repair && fixed) return checkScenes({ repair: false, post });
  const short = rows.filter(r => r.short);
  const cell = (g, w) => `${g ?? 0}/${w}`;
  const line = r => `<tr${r.short ? ' style="color:#e88"' : ""}><td>${r.part}</td><td>${r.name}</td><td>${r.got ? cell(r.got.walls, r.want.walls) : "—"}</td><td>${r.got ? cell(r.got.lights, r.want.lights) : "—"}</td><td>${r.got ? cell(r.got.notes, r.want.notes) : "—"}</td><td>${r.got ? cell(r.got.tokens, r.want.tokens) : "—"}</td><td>${!r.sc ? "missing" : r.map ? "ok" : "won't load"}</td></tr>`;
  console.table(rows.map(r => ({ part: r.part, scene: r.name, exists: !!r.sc, map: r.map, ...Object.fromEntries(Object.keys(r.want).map(k => [k, `${r.got?.[k] ?? 0}/${r.want[k]}`])) })));
  if (post) await ChatMessage.create({ whisper: ChatMessage.getWhisperRecipients("GM").map(u => u.id), speaker: { alias: "The Unkindness Saga" },
    content: `<div class="il-card"><h3>Scene check: ${short.length ? `${short.length} of ${rows.length} scenes incomplete` : `all ${rows.length} scenes complete`}</h3>
      <p style="font-size:11px">Each column is <em>in this world / what the module ships</em>. Red rows are incomplete${short.length ? ": <strong>Build all scenes</strong> on the DM Control Board's Setup tab rebuilds them" : ""}.</p>
      <table style="font-size:10px"><tr><th></th><th>Scene</th><th>Walls</th><th>Lights</th><th>Pins</th><th>Tokens</th><th>Map</th></tr>${rows.map(line).join("")}</table></div>` });
  return { total: rows.length, incomplete: short.map(r => r.name) };
}

// ---------------------------------------------------------------- creature spellcasting
// Spells come from the dnd5e system's own compendiums (and this module's rune spells) at install time,
// so every spell arrives with the system's full activities. data/spellbooks.json says who knows what.
let SPELL_INDEX = null;
async function spellIndex() {
  if (SPELL_INDEX) return SPELL_INDEX;
  SPELL_INDEX = new Map();
  const packs = (game.packs?.contents ?? [...(game.packs?.values?.() ?? [])]).filter(p => p.documentName === "Item" && (p.metadata?.packageName === MOD || p.metadata?.packageName === "dnd5e" || p.metadata?.id?.startsWith?.("dnd5e.")));
  // this module first, then the system's (newest SRD first, legacy last)
  packs.sort((a, b) => (a.metadata?.packageName === MOD ? -1 : b.metadata?.packageName === MOD ? 1 : /legacy/i.test(a.collection) - /legacy/i.test(b.collection)));
  for (const pack of packs) {
    let idx; try { idx = await pack.getIndex({ fields: ["type"] }); } catch (e) { continue; }
    for (const e of (idx.contents ?? [...idx.values?.() ?? idx])) {
      if (e.type !== "spell") continue;
      const k = e.name.toLowerCase().trim();
      if (!SPELL_INDEX.has(k)) SPELL_INDEX.set(k, { pack, id: e._id });
    }
  }
  return SPELL_INDEX;
}
async function grantSpells({ quiet = true } = {}) {
  if (!game.user?.isGM) return 0;
  let books; try { books = await (await fetch(`modules/${MOD}/data/spellbooks.json`)).json(); } catch (e) { console.warn(MOD, "spellbooks", e); return 0; }
  const idx = await spellIndex(); const missing = new Set(); let n = 0;
  for (const actor of game.actors?.contents ?? []) {
    const f = actor.flags?.[MOD] ?? {};
    const book = books[f.key] ?? books[f.sourceId];
    if (!book || (!f.managed && !f.sourceId)) continue;
    const old = actor.items.filter(i => i.getFlag(MOD, "grantedSpell"));
    const docs = [];
    for (const sp of book.spells) {
      const hit = idx.get(sp.name.toLowerCase());
      if (!hit) { missing.add(sp.name); continue; }
      const src = await hit.pack.getDocument(hit.id); if (!src) { missing.add(sp.name); continue; }
      const d = src.toObject(); delete d._id; delete d.folder; delete d._stats;
      d.system.method = sp.method === "atwill" ? "atwill" : sp.method === "innate" ? "innate" : "spell";
      d.system.prepared = sp.method === "spell" ? 1 : 0;
      d.system.preparation = { mode: sp.method === "atwill" ? "atwill" : sp.method === "innate" ? "innate" : "prepared", prepared: sp.method === "spell" };
      if (sp.method === "innate" && sp.uses) d.system.uses = { max: String(sp.uses), spent: 0, recovery: [{ period: "day", type: "recoverAll" }] };
      d.flags = { ...(d.flags ?? {}), [MOD]: { grantedSpell: true } };
      docs.push(d);
    }
    const sys = { "system.attributes.spellcasting": book.ability, "system.details.spellLevel": book.level, "system.attributes.spell.level": book.level };
    try {
      if (old.length) await actor.deleteEmbeddedDocuments("Item", old.map(i => i.id), { cuInternal: true });
      if (docs.length) await actor.createEmbeddedDocuments("Item", docs, { cuInternal: true });
      await actor.update(sys, { cuInternal: true });
      n++;
    } catch (e) { console.warn(MOD, "spells", actor.name, e); }
  }
  if (missing.size) console.warn(`${MOD} | spells not found in any dnd5e compendium:`, [...missing]);
  if (!quiet || missing.size) ui.notifications[missing.size ? "warn" : "info"](`The Unkindness Saga: spells given to ${n} creatures${missing.size ? ` (${missing.size} spells not found in your dnd5e compendiums: see the console)` : ""}.`);
  return n;
}

// ---------------------------------------------------------------- the Hold (Kharad-Varr side quests)
const HoldAPI = {
  /** Stage (if needed) and view the painted overview of the Hold. */
  async map() {
    let scene = game.scenes.find(s => s.getFlag(MOD, "key") === "hold-map");
    if (!scene) { scene = await stageScene("hold-map"); await repairArt({ quiet: true }); }
    return scene?.view();
  },
  /** Draw from one of the Hold's roll tables by key (default: rumours). */
  async rumour(key = "hold-rumours") {
    const t = game.tables.find(x => x.getFlag(MOD, "key") === key);
    if (!t) return ui.notifications.warn("Install the module content first (the Hold tables are missing).");
    return t.draw({ rollMode: CONST.DICE_ROLL_MODES.PRIVATE });
  },
  /** Rivets & Runes, the Turning Gear's dice game. Player 3d6 against the house 3d6. */
  async rivets() {
    const res = await DialogV2().prompt({
      window: { title: "Rivets & Runes — The Turning Gear" },
      content: `<div class="il-form"><div class="form-group"><label>Player</label><input name="who" type="text" value="${game.user.character?.name ?? "A player"}"></div>
        <div class="form-group"><label>Stake (gp)</label><input name="stake" type="number" min="1" value="10"></div>
        <div class="form-group"><label>House</label><select name="house"><option value="table">A dealer (honest dice)</option><option value="iskra">Iskra herself (she rerolls one Rivet)</option></select></div>
        <div class="form-group"><label><input name="cheat" type="checkbox"> Player palms a die (Sleight of Hand DC 15; Iskra's passive Insight 18)</label></div>
        <p class="hint">Highest total wins even money. Any triple beats any total and pays 3 to 1. A Rivet Run (1-2-3) loses outright. Ties: the house keeps half.</p></div>`,
      ok: { label: "Roll", callback: (ev, b) => { const e = b.form.elements; return { who: esc(e.who.value), stake: e.stake.value, house: e.house.value, cheat: e.cheat.checked }; } },
      rejectClose: false
    });
    if (!res) return;
    const stake = Math.max(1, Number(res.stake) || 1);
    const roll3 = async () => { const d = []; for (let i = 0; i < 3; i++) d.push((await new Roll("1d6").evaluate()).total); return { d }; };
    const p = await roll3(); let h = await roll3();
    let note = "";
    if (res.house === "iskra" && h.d.includes(1)) {
      const i = h.d.indexOf(1); const nr = await new Roll("1d6").evaluate(); h.d[i] = nr.total; note += `<p><em>Iskra flicks a Rivet back into the cup: it lands ${nr.total}.</em></p>`;
    }
    if (res.cheat) {
      const sl = await new Roll("1d20").evaluate();
      note += `<p><em>${res.who} palms a die (Sleight of Hand: roll ${sl.total} + modifier against DC 15; Iskra notices on a total below 18).</em></p>`;
    }
    const kind = d => { const s = [...d].sort(); if (s[0] === s[2]) return 3; if (s.join() === "1,2,3") return -1; return 0; };
    const tot = d => d.reduce((a, b) => a + b, 0);
    const pk = kind(p.d), hk = kind(h.d);
    let out;
    if (pk === -1 && hk !== -1) out = ["loses (Rivet Run)", -stake];
    else if (hk === -1 && pk !== -1) out = ["wins (the house throws a Rivet Run)", stake];
    else if (pk === 3 && hk !== 3) out = ["wins with a triple", stake * 3];
    else if (hk === 3 && pk !== 3) out = ["loses to the house's triple", -stake];
    else if (tot(p.d) > tot(h.d)) out = ["wins", stake];
    else if (tot(p.d) < tot(h.d)) out = ["loses", -stake];
    else out = ["ties (the house keeps half)", -Math.ceil(stake / 2)];
    const face = d => d.map(x => x === 1 ? "⚙" : x === 6 ? "ᚱ" : x).join(" · ");
    await ChatMessage.create({
      whisper: ChatMessage.getWhisperRecipients("GM").map(u => u.id).concat(game.user.id),
      content: `<div class="il-chat"><h3>Rivets &amp; Runes</h3><p><strong>${res.who}:</strong> ${face(p.d)} (${tot(p.d)})<br><strong>House:</strong> ${face(h.d)} (${tot(h.d)})</p>${note}
        <p><strong>${res.who} ${out[0]}:</strong> ${out[1] >= 0 ? "+" : ""}${out[1]} gp.</p></div>`
    });
  }
};

/* ------------------------------------------------------------------------ */
/*  DM Control Board — every tracker and tool for both parts, in one window */
/* ------------------------------------------------------------------------ */
const STAGE_LABEL = {
  "wachter-cellar": "Wachter House cellar (Nov 8 handoff)", "arl-released": "Arl released", "van-richten-route": "On the way to Van Richten",
  "van-richten-briefing": "Van Richten's briefing", "vallaki-exit": "Leaving Vallaki", "azrathox-rendezvous": "Azrathox rendezvous",
  "war-of-broken-gods": "The War of Broken Gods", "bride-gauntlet": "The bride gauntlet", "finn-tatyana": "Finn and Tatyana",
  "strahd-phase-1": "Strahd, Phase I", "strahd-phase-2": "Strahd, Phase II", "wish-crisis": "The Wish crisis", "strahd-phase-3": "Strahd, Phase III",
  "coffin-chase": "The coffin chase", "barovia-collapse": "Barovia collapses", "campaign-ended": "Campaign ended"
};
const HOLD_AWARDS = { "low-lantern": ["The Missing Verse", "accord"], "ember-baths": ["Cold Water", "accord"], "mossbeard-remedies": ["The Bitter Cough", "accord"],
  "anvilsong-forge": ["The Last Commission", "defence"], "deep-script": ["A Rune Nobody Taught", "defence"] };
const C1 = () => game.catAndUnkindness;
/** Run one of Part I's prompt-driven tools with its answers filled in (any further question is still asked). */
async function withAnswers(answers, fn) {
  const orig = window.prompt; const q = [...answers];
  window.prompt = (msg, def) => (q.length ? String(q.shift()) : orig.call(window, msg, def));
  try { return await fn(); } finally { window.prompt = orig; }
}
async function p1patch(patch) { if (!C1()) return ui.notifications.warn("Part I isn't loaded."); await C1().patchState(patch); Board.refresh(); }
async function holdAward(key) {
  const L = ledgerState(); const hold = { ...(L.hold ?? {}) }; const [title, track] = HOLD_AWARDS[key]; const max = track === "defence" ? 6 : 4;
  const used = Object.entries(hold).filter(([k, v]) => v === "applied" && HOLD_AWARDS[k]?.[1] === track).length;
  const patch = {};
  if (hold[key]) {
    if (hold[key] === "applied") patch[track] = Math.max(0, L[track] - 1);
    hold[key] = null;
    chat(`<p>Hold award cleared: <strong>${esc(title)}</strong>${patch[track] !== undefined ? ` (${track === "defence" ? "Defence" : "Accord"} back to ${patch[track]})` : ""}.</p>`, "The Stone Ledger", true);
  } else if (used >= 2) {
    hold[key] = "capped";
    chat(`<p><strong>${esc(title)}</strong> complete. The Hold cap for ${track === "defence" ? "Defence" : "Accord"} (+2) is already reached, so the track doesn't move; the quest's ending and items still apply.</p>`, "The Stone Ledger", true);
  } else {
    hold[key] = "applied"; patch[track] = Math.min(max, L[track] + 1);
    chat(`<p><strong>${esc(title)}</strong> complete: ${track === "defence" ? "Defence Readiness" : "Civilian Accord"} rises to <strong>${patch[track]}</strong> (Hold award ${used + 1}/2).</p>`, "The Stone Ledger", true);
  }
  await game.settings.set(MOD, "ledger", foundry.utils.mergeObject(L, { ...patch, hold }, { inplace: false, performDeletions: true }));
}

class BoardApp extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = {
    id: "il-board", tag: "div", classes: ["il-app", "il-board-app"],
    window: { title: "DM Control Board — The Unkindness Saga", icon: "fa-solid fa-gauge-high", resizable: true },
    position: { width: 900, height: 760 },
    actions: {
      tab: function (ev, el) { this.tab = el.dataset.tab; this.render(); },
      run: async function (ev, el) {
        const name = el.dataset.run, arg = el.dataset.arg;
        try {
          if (name.includes(":")) { const [pre, key] = name.split(":"); await BOARD_RUN[pre]?.(key, arg); }
          else await BOARD_RUN[name]?.(arg, el);
        } catch (e) { console.error(MOD, "board action", name, e); ui.notifications.error(`Control Board: ${e.message}`); }
        this.render();
      },
      manual: function () { const j = byKey(game.journal, "board-manual"); if (j) j.sheet.render(true, { pageId: j.pages.find(p => p.getFlag(MOD, "key") === (this.tab ?? "p1"))?.id }); else ui.notifications.warn("Install Part II content to get the manual."); }
    }
  };
  tab = "p1";
  async _renderHTML() {
    const tabs = [["p1", "fa-chess-rook", "Ravenloft Finale"], ["p2", "fa-scale-balanced", "Stone Ledger"], ["tools", "fa-toolbox", "Session Tools"], ["setup", "fa-gear", "Setup & Repair"]];
    const nav = `<nav class="il-board-tabs">${tabs.map(([k, i, l]) => `<button type="button" data-action="tab" data-tab="${k}" class="${this.tab === k ? "on" : ""}"><i class="fa-solid ${i}"></i> ${l}</button>`).join("")}
      <button type="button" data-action="manual" class="il-board-help" title="Open the manual page for this tab"><i class="fa-solid fa-book-open"></i> Manual</button></nav>`;
    let body = "";
    try { body = this.tab === "p1" ? await boardP1() : this.tab === "p2" ? boardP2() : this.tab === "tools" ? boardTools() : boardSetup(); }
    catch (e) { console.error(MOD, "board", e); body = `<p class="hint">Couldn't draw this tab: ${esc(e.message)}</p>`; }
    return `<div class="il-board">${nav}<div class="il-board-body">${body}</div></div>`;
  }
  _replaceHTML(result, content) { const top = content.querySelector(".il-board-body")?.scrollTop ?? 0; content.innerHTML = result; const b = content.querySelector(".il-board-body"); if (b) b.scrollTop = top; }
}
const Board = { app: null, open(tab) { this.app ??= new BoardApp(); if (tab) this.app.tab = tab; return this.app.render(true); }, refresh() { if (this.app?.rendered) this.app.render(); } };
Hooks.on("updateSetting", st => { if (String(st.key ?? "").startsWith(`${MOD}.`)) Board.refresh(); });

const btn = (run, label, { arg = "", on = false, title = "", icon = "", cls = "" } = {}) =>
  `<button type="button" class="il-b ${on ? "on" : ""} ${cls}" data-action="run" data-run="${run}" data-arg="${esc(String(arg))}" title="${esc(title)}">${icon ? `<i class="fa-solid ${icon}"></i> ` : ""}${label}</button>`;
const card = (title, help, inner, wide = false) => `<section class="il-card ${wide ? "wide" : ""}"><h3>${title}</h3><p class="il-help">${help}</p>${inner}</section>`;
const stepper = (run, label, value, max, help = "") => `<div class="il-step"><span class="il-step-l">${label}</span>${btn(run, "−", { arg: -1, title: "Lower" })}<b>${value}${max !== null ? `<small>/${max}</small>` : ""}</b>${btn(run, "+", { arg: 1, title: "Raise" })}${help ? `<small class="il-step-h">${help}</small>` : ""}</div>`;

async function boardP1() {
  if (!C1()) return `<p class="hint">Part I (The Cat and the Unkindness) isn't loaded.</p>`;
  const s = await C1().getState();
  const stage = Object.entries(STAGE_LABEL).map(([k, l], i) => btn("stage", `${i + 1}. ${l}`, { arg: k, on: s.stage === k })).join("");
  const B = ["alive", "mist", "destroyed", "saved"];
  const brides = ["anastrasya", "volenta", "ludmilla", "finn"].map(w => `<div class="il-line"><span class="il-step-l">${w[0].toUpperCase() + w.slice(1)}</span>${B.map(st => btn("bride", st, { arg: `${w}:${st}`, on: s.brides?.[w] === st })).join("")}</div>`).join("");
  const chains = [["sanguine", "Sanguine Moon"], ["self", "Rejected Self"], ["gift", "Master's Gift"]].map(([k, l]) => btn("finn", (s.finnChains?.[k] ? "✓ " : "") + l, { arg: k, on: s.finnChains?.[k], title: "Broken = lit" })).join("");
  const phase = [0, 1, 2, 3].map(n => btn("phase", n ? `Phase ${n}` : "Not started", { arg: n, on: (s.strahdPhase ?? 0) === n })).join("");
  const hearts = [["blood", "Blood"], ["stone", "Stone"], ["dominion", "Dominion"]].map(([k, l]) => btn("heart", (s.heartChains?.[k] ? "" : "✗ ") + l, { arg: k, on: s.heartChains?.[k], title: "Lit = still standing; click to destroy / restore" })).join("");
  const dp = s.darkPowers ?? {};
  const pro = ["damien", "vesper", "bunch", "legna", "thorgrinn"].map(w => btn("prophecy", (s.prophecies?.[w] ? "✓ " : "") + w[0].toUpperCase() + w.slice(1), { arg: w, on: s.prophecies?.[w] })).join("");
  const r = s.resources ?? {};
  const w = s.wish ?? {};
  const v = s.vallaki ?? {};
  return `<div class="il-grid">
    ${card("Where the party is", "Click the stage the party has reached. The status card in chat and the dashboard read this. <em>Post status card</em> whispers the full finale summary (stage, brides, Strahd, powers, prophecies) to you.",
      `<div class="il-stages">${stage}</div><div class="il-line">${btn("dash", "Post status card", { icon: "fa-comment", cls: "big" })}${btn("reset", "Reset to the Nov 8 handoff", { icon: "fa-rotate-left", title: "Puts the whole finale state back to the start. Asks first." })}</div>`, true)}
    ${card("Vallaki prelude", "Each button posts the scene card and records the outcome. Van Richten's warning also grants his diamonds and reagent if they haven't been given yet.",
      `<div class="il-line">${btn("vallaki", "Van Richten's warning", { arg: "warning" })}${btn("vallaki", "Vampyr cult surges", { arg: "vampyr" })}${btn("vallaki", "Orcus cult surges", { arg: "orcus" })}</div>
       <div class="il-line">${btn("vallaki", "Party evacuates", { arg: "evacuate" })}${btn("vallaki", "Both cults at once", { arg: "both" })}${btn("vallaki", "Party leaves Vallaki", { arg: "leave" })}</div>
       <div class="il-line"><span class="il-step-l">Strahd's letter</span>${btn("letter", v.strahdLetterOpened ? "✓ Opened" : "Open it", { arg: "open", on: v.strahdLetterOpened })}${btn("letter", "Show again", { arg: "show" })}</div>`)}
    ${card("Arl, the contracted pit fiend", "Show the agreed terms, then sign, then free him. Breach if either side breaks mutual non-harm. Deploying him needs him freed.",
      `<div class="il-line">${btn("arl", "Show terms", { arg: "terms" })}${btn("arl", v.arlContract === "signed" ? "✓ Signed" : "Sign", { arg: "sign", on: v.arlContract === "signed" })}${btn("arl", v.arlFreed ? "✓ Freed" : "Free him", { arg: "free", on: v.arlFreed })}${btn("arl", "Breach", { arg: "breach" })}</div>
       <div class="il-line"><span class="il-step-l">Send Arl to</span>${["orcus", "vampyr", "ravenloft", "unassigned"].map(t => btn("ally", t, { arg: `pitfiend:${t}`, on: s.allies?.pitFiend === t })).join("")}</div>
       <div class="il-line"><span class="il-step-l">Send Azrathox to</span>${["orcus", "vampyr", "ravenloft", "unassigned"].map(t => btn("ally", t, { arg: `azrathox:${t}`, on: s.allies?.azrathox === t })).join("")}</div>`)}
    ${card("The brides and Finn", "Set each one's state as it happens: <em>mist</em> = fled to reform, <em>destroyed</em>, or <em>saved</em> (talked down, freed). Finn's chains: light each one as the party breaks it; when all three are lit Finn is saved automatically.",
      `${brides}<div class="il-line"><span class="il-step-l">Finn's chains</span>${chains}</div>`)}
    ${card("Strahd", "Phase buttons move the fight on (entering Phase II or III gives back one Legendary Resistance, up to 4). Heart Chains: lit = standing; click when one is destroyed. Coffin distance counts down the chase.",
      `<div class="il-line">${phase}</div>${stepper("legres", "Legendary Resistances", s.legendaryResistances ?? 4, 4, "shared across all three phases")}
       <div class="il-line"><span class="il-step-l">Heart Chains</span>${hearts}</div>${stepper("coffin", "Coffin distance", s.coffinDistance ?? 5, null, "0 = they reach it")}
       <div class="il-line">${btn("flag", (s.tatyanaAgencyHonoured ? "✓ " : "") + "Tatyana treated as a person", { arg: "tatyana", on: s.tatyanaAgencyHonoured, title: "If lit, she uses 'No' in Phase III" })}
         <span class="il-step-l">Strahd's offer of rest</span>${["yes", "no", "unset"].map(x => btn("rest", x, { arg: x, on: (s.restAccepted === true ? "yes" : s.restAccepted === false ? "no" : "unset") === x })).join("")}</div>
       <div class="il-line">${btn("mock", "Strahd mocks someone", { icon: "fa-masks-theater", title: "Posts a taunt aimed at a hero you choose" })}${btn("lair", "Lair action", { icon: "fa-dungeon", title: "Rolls and posts a Ravenloft lair action" })}${btn("sun", "Artifact sunlight rule", { icon: "fa-sun", title: "Posts the sunlight rules card" })}${btn("npc", "NPC action (selected token)", { icon: "fa-hand-fist", title: "Select a Part I token first" })}</div>`)}
    ${card("The Dark Powers", "Pressure (Orcus) and Claim (Vampyr) rise as they gain ground. Attention is how much each power is watching the party (it carries into Part II). Intervention rolls a power's move; Reconstitution is for when a manifestation hits 0 HP before the Wish.",
      `${stepper("pressure", "Orcus pressure", dp.orcus?.pressure ?? 2, 6, dp.orcus?.status ?? "")}${stepper("claim", "Vampyr claim", dp.vampyr?.claim ?? 2, 6, dp.vampyr?.status ?? "")}
       ${["orcus", "vampyr", "vecna"].map(p => stepper(`arc:${p}`, `${p[0].toUpperCase() + p.slice(1)} attention`, s.arcAttention?.[p] ?? 0, null)).join("")}
       <div class="il-line">${["orcus", "vampyr", "vecna"].map(p => btn("intervene", `${p} intervenes`, { arg: p })).join("")}</div>
       <div class="il-line">${btn("recon", "Orcus reduced to 0", { arg: "orcus" })}${btn("recon", "Vampyr reduced to 0", { arg: "vampyr" })}</div>
       <div class="il-line"><span class="il-step-l">Final ending (needs the Edict)</span>${["banish", "spare", "bargain"].map(e => btn("ending", `Orcus: ${e}`, { arg: `orcus:${e}` })).join("")}${["banish", "spare", "bargain"].map(e => btn("ending", `Vampyr: ${e}`, { arg: `vampyr:${e}` })).join("")}</div>`, true)}
    ${card("The Wish", "Run these in order as the finale demands: <em>Crisis</em> when damage stops being the answer, then the source (Damien's djinn or Vecna's bargain), then <em>Cast</em>. Casting creates the Edict of Finality, which lets the Dark Powers' endings stick.",
      `<div class="il-line">${btn("wish", (w.impossibleProven ? "✓ " : "") + "Crisis", { arg: "crisis", on: w.impossibleProven })}${btn("wish", "Djinn offers", { arg: "djinn" })}${btn("wish", "Vecna offers", { arg: "vecna" })}${btn("wish", (w.cast ? "✓ " : "") + "Cast the Wish", { arg: "cast", on: w.cast })}${btn("wish", "Claim clock", { arg: "claim" })}</div>
       <div class="il-line">${btn("vecnadeal", "Vecna offers a hero a bargain", { icon: "fa-eye" })}<span class="hint">Edict of Finality: <b>${w.edictActive ? "active" : "not yet"}</b>${w.source ? ` · source: ${esc(w.source)}` : ""}</span></div>`)}
    ${card("Madam Eva's prophecies", "Light a hero's prophecy when it is fulfilled. Each fulfilled prophecy gives a boon in Part II (Shadows Beyond Barovia imports them).", `<div class="il-line">${pro}</div>`)}
    ${card("Supplies", "What the party is carrying into the castle. Spend them here as they're used.",
      `${stepper("res:holyWater", "Holy water", r.holyWater ?? 0, null)}${stepper("res:diamonds300", "300 gp diamonds", r.diamonds300 ?? 0, null)}${stepper("res:diamonds500", "500 gp diamonds", r.diamonds500 ?? 0, null)}${stepper("res:antiUndeadReagent", "Anti-undead reagent", r.antiUndeadReagent ?? 0, null)}
       <div class="il-line">${btn("restog", (r.silverShot ? "✓ " : "") + "Silver shot", { arg: "silverShot", on: r.silverShot })}${btn("restog", (r.fireGiantPotionLegna ? "✓ " : "") + "Legna's fire giant potion", { arg: "fireGiantPotionLegna", on: r.fireGiantPotionLegna })}</div>`)}
  </div>`;
}

function boardP2() {
  const L = ledgerState();
  const eff = L.defence <= 1 ? "One unassigned front falls back." : L.defence <= 3 ? "Unassigned fronts hold, with damage." : "Unassigned fronts hold and grant one reinforcement.";
  const acc = L.accord <= 1 ? "No cross-clan assistance." : L.accord === 2 ? "Civilians share safe routes." : "A Cinder-Tusk engineering team helps both populations.";
  const ev = Object.entries(EVIDENCE).map(([id, [n]]) => btn("evidence", `${L.evidence[id] ? "✓ " : ""}${id} · ${esc(n)}`, { arg: id, on: L.evidence[id], title: "Authenticating deals the card to the Party Dossier and posts it" })).join("");
  const council = ["brynja", "odran", "hadrik"].map(w => stepper(`council:${w}`, w[0].toUpperCase() + w.slice(1), STANCE[String(L.council[w] ?? 0)], null)).join("");
  const bal = [["admitted", "Admits the report"], ["refused", "Refuses an unlawful order"], ["submitted", "Submits to judgement"]].map(([k, l]) => btn("baldrik", (L.baldrik[k] ? "✓ " : "") + l, { arg: k, on: L.baldrik[k] })).join("");
  const hold = L.hold ?? {};
  const used = t => Object.entries(hold).filter(([k, v]) => v === "applied" && HOLD_AWARDS[k]?.[1] === t).length;
  const ha = Object.entries(HOLD_AWARDS).map(([k, [t, tr]]) => btn("hold", `${hold[k] ? "✓ " : ""}${t} <small>(+1 ${tr === "defence" ? "D" : "A"}${hold[k] === "capped" ? ", capped" : ""})</small>`, { arg: k, on: !!hold[k] })).join("");
  const I = inhState();
  return `<div class="il-grid">
    ${card("The two tracks", "Raise a track once per concrete achievement the adventure names (never twice for the same thing). The line under each track is what it means right now.",
      `${stepper("track:defence", "Defence Readiness", L.defence, 6)}<p class="il-help">${eff}</p>${stepper("track:accord", "Civilian Accord", L.accord, 4)}<p class="il-help">${acc}</p>${btn("postledger", "Post the Stone Ledger to chat", { icon: "fa-comment" })}`)}
    ${card("Evidence E1–E7", "Light a piece of evidence when the party authenticates it. It is dealt into the Party Dossier card hand and announced. Click again to un-mark it (the card stays).", `<div class="il-col">${ev}</div>`)}
    ${card("The Stone Council", "Each general's stance, from Hostile to Committed. Move them as hearings and scenes change their minds; the Hearing tool reads these.", council)}
    ${card("Baldrik's accountability", "Each happens only through his own choices in play. Refusing an unlawful order also deals his Favour card.", `<div class="il-col">${bal}</div>`)}
    ${card("Hold side quests (Kharad-Varr)", `Tick a quest when its rewarded ending happens. It raises its track by 1, up to the Hold cap of +2 per track (Defence ${used("defence")}/2 · Accord ${used("accord")}/2). Unticking takes the point back.`, `<div class="il-col">${ha}</div>`)}
    ${card("Shadows Beyond Barovia", "Dark Power Attention carried over from Part I. Thresholds: 0 Watching, 3 Reaching, 6 Claiming, 9 Arriving. Import pulls everything from the Ravenloft finale state.",
      `${["orcus", "vampyr", "vecna"].map(p => stepper(`inh:${p}`, `${p[0].toUpperCase() + p.slice(1)}`, I.attention?.[p] ?? 0, null)).join("")}
       <div class="il-line">${btn("inhimport", "Import the Ravenloft ending", { icon: "fa-file-import" })}${btn("inhopen", "Inheritance window", { icon: "fa-eye" })}${btn("inhbeat", "Shadow beat for this session", { icon: "fa-moon" })}${btn("inhgift", "Offer a Dark Gift", { icon: "fa-gift" })}</div>`)}
  </div>`;
}

function boardTools() {
  const T = (run, label, icon, help) => `<div class="il-tool">${btn(run, label, { icon, cls: "big" })}<p class="il-help">${help}</p></div>`;
  return `<div class="il-grid">
    ${card("Politics", "", T("hearing", "Stone Council hearing", "fa-gavel", "Pick the issue and the evidence presented; it weighs evidence against the generals' stances and posts the council's finding.") + T("handout", "Show a handout", "fa-scroll", "Shows a handout journal page to every player."))}
    ${card("Challenges", "", T("work", "Work challenge", "fa-screwdriver-wrench", "Puts an on-screen progress clock up (e.g. 3 successes before 2 setbacks) for repairs, forging, brewing.") + T("countdown", "Countdown", "fa-hourglass-half", "A visible countdown for pressure that's building: flooding, a door giving way.") + T("save", "Request a group save", "fa-dice-d20", "Asks every player token on the scene for the same saving throw."))}
    ${card("War (Chapter 7)", "", T("dispatch", "Draw a siege dispatch", "fa-envelope", "Draws the next siege dispatch card onto the table and posts what happens at an unassigned front.") + T("pressure2", "Next pressure stage", "fa-gauge-simple-high", "Advances the Last Bastion pressure stage at the Heartworks.") + T("favour", "Deal a favour", "fa-handshake", "Deals an earned Shield-Wall Favour card to the party."))}
    ${card("Magic and music", "", T("rune", "Rune Forge", "fa-hammer", "Walks a character through forging a rune: materials, check, result.") + T("music", "Play this scene's music", "fa-music", "Starts the track assigned to the scene you're viewing."))}
    ${card("Kharad-Varr: the Hold", "", T("holdmap", "Open the Hold map", "fa-map", "The painted overview of the whole mountain; every pin opens its place.") + T("rivets", "Rivets and Runes", "fa-dice", "The Turning Gear's dice game, rolled and settled in chat.") + T("rumour", "Draw a Hold rumour", "fa-comments", "A private rumour for you; true rumours point at real leads."))}
  </div>`;
}

function boardSetup() {
  const T = (run, label, icon, help) => `<div class="il-tool">${btn(run, label, { icon, cls: "big" })}<p class="il-help">${help}</p></div>`;
  return `<div class="il-grid">
    ${card("Install and update", "Use these after installing or updating the module. None of them touch player characters.",
      T("setupall", "Set up everything", "fa-wand-magic-sparkles", "First-time setup for both parts: content, scenes, music, cards.") +
      T("p1setup", "Set up / repair Part I", "fa-chess-rook", "Re-imports the Ravenloft finale content. Anything you edited by hand is kept as a recovery copy.") +
      T("update", "Update Part II content", "fa-arrows-rotate", "Refreshes Part II actors, items, journals, tables and macros from the module.") +
      T("scenes", "Build all scenes", "fa-map-location-dot", "Rebuilds every map in both parts: walls, lights, pins, music, and the creatures (Part I's start hidden). Then checks every scene, rebuilds any that came out incomplete, and whispers you the result."), true)}
    ${card("Repair", "", T("check", "Check all scenes", "fa-list-check", "Changes nothing: compares every scene with what the module ships (walls, lights, pins, tokens, whether the map loads) and whispers you a table. Red rows need Build all scenes.") + T("art", "Repair art", "fa-image", "Points every map, portrait, token and track at a copy that loads. Fixes blank maps on The Forge.") + T("manager", "Open the Manager", "fa-shield-halved", "The full Manager window: party size, single-scene rebuilds, removal."))}
  </div>`;
}

const p1st = async () => C1().getState();
const BOARD_RUN = {
  // Part I
  stage: async k => p1patch({ stage: k }),
  dash: async () => C1()?.dashboard(),
  reset: async () => C1()?.resetToHandoff(),
  vallaki: async op => withAnswers([op], () => C1().promptVallaki()),
  letter: async op => withAnswers([op], () => C1().promptLetter()),
  arl: async op => withAnswers([op], () => C1().promptArl()),
  ally: async a => { const [who, to] = a.split(":"); return withAnswers([who, to], () => C1().promptAlly()); },
  bride: async a => { const [who, st] = a.split(":"); const s = await p1st(); return p1patch({ brides: { ...s.brides, [who]: st } }); },
  finn: async k => { const s = await p1st(); const fc = { ...s.finnChains, [k]: !s.finnChains?.[k] }; const patch = { finnChains: fc }; if (Object.values(fc).every(Boolean)) patch.brides = { ...s.brides, finn: "saved" }; return p1patch(patch); },
  phase: async n => { const s = await p1st(); n = Number(n); let lr = s.legendaryResistances ?? 4; if (n > (s.strahdPhase ?? 0) && n > 1) lr = Math.min(4, lr + 1); return p1patch({ strahdPhase: n, stage: n ? `strahd-phase-${n}` : s.stage, legendaryResistances: lr }); },
  legres: async d => { const s = await p1st(); return p1patch({ legendaryResistances: Math.max(0, Math.min(4, (s.legendaryResistances ?? 4) + Number(d))) }); },
  heart: async k => { const s = await p1st(); return p1patch({ heartChains: { ...s.heartChains, [k]: !s.heartChains?.[k] } }); },
  coffin: async d => { const s = await p1st(); return p1patch({ coffinDistance: Math.max(0, (s.coffinDistance ?? 5) + Number(d)) }); },
  flag: async () => { const s = await p1st(); return p1patch({ tatyanaAgencyHonoured: !s.tatyanaAgencyHonoured }); },
  rest: async x => p1patch({ restAccepted: x === "yes" ? true : x === "no" ? false : null }),
  mock: async () => C1()?.promptMockery(),
  lair: async () => C1()?.promptLair(),
  sun: async () => C1()?.promptSunlight(),
  npc: async () => C1()?.npcAction(),
  pressure: async d => { const s = await p1st(); const dp = foundry.utils.deepClone(s.darkPowers); dp.orcus.pressure = Math.max(0, Math.min(6, (dp.orcus.pressure ?? 2) + Number(d))); return p1patch({ darkPowers: dp }); },
  claim: async d => { const s = await p1st(); const dp = foundry.utils.deepClone(s.darkPowers); dp.vampyr.claim = Math.max(0, Math.min(6, (dp.vampyr.claim ?? 2) + Number(d))); return p1patch({ darkPowers: dp }); },
  intervene: async p => withAnswers([p], () => C1().promptIntervention()),
  recon: async p => withAnswers([p], () => C1().promptReconstitution()),
  ending: async a => { const [p, e] = a.split(":"); return withAnswers([p, e], () => C1().promptPowerEnding()); },
  wish: async op => withAnswers([op], () => C1().promptWish()),
  vecnadeal: async () => C1()?.promptVecnaDeal(),
  prophecy: async w => { const s = await p1st(); return p1patch({ prophecies: { ...s.prophecies, [w]: !s.prophecies?.[w] } }); },
  restog: async k => { const s = await p1st(); return p1patch({ resources: { ...s.resources, [k]: !s.resources?.[k] } }); },
  // Part II
  postledger: async () => postLedger(),
  evidence: async id => toggleEvidence(id),
  baldrik: async k => baldrikEvent(k),
  hold: async k => holdAward(k),
  inhimport: async () => Inheritance.importFinale(), inhopen: async () => Inheritance.open(), inhbeat: async () => Inheritance.beat(), inhgift: async () => Inheritance.gift(),
  // tools
  hearing: async () => hearing(), handout: async () => showHandout(), work: async () => workChallenge(), countdown: async () => countdown(), save: async () => requestSave(),
  dispatch: async () => drawDispatch(), pressure2: async () => nextPressure(), favour: async () => dealFavour(), rune: async () => forgeRune(), music: async () => playSceneMusic(),
  holdmap: async () => HoldAPI.map(), rivets: async () => HoldAPI.rivets(), rumour: async () => HoldAPI.rumour(),
  // setup
  setupall: async () => API.setupAll(), p1setup: async () => { await rebuildPartOne({ scenes: false }); await repairArt({ quiet: true }); },
  update: async () => updateContent(), scenes: async () => buildScenes(), check: async () => checkScenes(), art: async () => repairArt({ force: true }), manager: async () => new Manager().render(true)
};
// steppers with a key after the colon
for (const [pre, fn] of Object.entries({
  "arc": async (p, d) => { const s = await p1st(); return p1patch({ arcAttention: { ...s.arcAttention, [p]: Math.max(0, (s.arcAttention?.[p] ?? 0) + Number(d)) } }); },
  "res": async (k, d) => { const s = await p1st(); return p1patch({ resources: { ...s.resources, [k]: Math.max(0, (s.resources?.[k] ?? 0) + Number(d)) } }); },
  "track": async (k, d) => { const s = ledgerState(); const max = k === "defence" ? 6 : 4; const v = Math.max(0, Math.min(max, s[k] + Number(d))); await setLedger({ [k]: v }); chat(`<p><strong>${k === "defence" ? "Defence Readiness" : "Civilian Accord"}</strong> is now <strong>${v}</strong>.</p>`, "The Stone Ledger", true); },
  "council": async (w, d) => { const s = ledgerState(); await setLedger({ council: { [w]: Math.max(-2, Math.min(2, (s.council[w] ?? 0) + Number(d))) } }); },
  "inh": async (p, d) => adjustAttention(p, Number(d), "Control Board")
})) BOARD_RUN[pre] = fn;

const API = {
  setupAll, installContent, updateContent, buildScenes, stageScene, removeAll, applyPartySize,
  ledger: Ledger, awardEvidence, toggleEvidence, adjustTrack, baldrikEvent, hearing, postLedger,
  workChallenge, countdown, clock: Clock, dealFavour, drawDispatch, nextPressure, passCard,
  forgeRune, showHandout, requestSave, playSceneMusic, playSfx, inheritance: Inheritance, migrateLegacy, hold: HoldAPI, art: ArtAPI, board: Board,
  openManager: () => new Manager().render(true)
};
