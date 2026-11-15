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
  baldrik: { admitted: false, refused: false, submitted: false }, runes: [], hearings: {}
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
  game.settings.registerMenu(MOD, "manager", {
    name: "The Unkindness Saga Manager", label: "Open Manager", hint: "Set up Part I (Ravenloft finale) and Part II (Ironfist Legacy), update, rebuild scenes, scale for party size, or remove Part II.",
    icon: "fa-solid fa-shield-halved", type: Manager, restricted: true
  });
});

Hooks.once("ready", async () => {
  game.modules.get(MOD).api = API;
  Clock.refresh();
  if (!game.user.isGM) return;
  for (const old of ["cat-and-unkindness", "ironfist-legacy"]) if (game.modules.get(old)?.active)
    ui.notifications.warn(`The Unkindness Saga replaces the separate "${old}" module. Disable it in Manage Modules to avoid duplicate content.`, { permanent: true });
  if (!game.settings.get(MOD, "migrated")) await migrateLegacy({ quiet: true });
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
      name: h.name, type: h.type, folder: folder.id, img: `modules/${MOD}/assets/icons/mc-cards.webp`,
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
    texture: { src: `modules/${MOD}/assets/icons/note-pin.webp` }, iconSize: 48, fontSize: 22, textAnchor: 1, global: false
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
    Object.assign(data, lv);
    tokens.push(data);
  }
  if (tokens.length) await scene.createEmbeddedDocuments("Token", tokens);
  try { const thumb = await scene.createThumbnail({ img: spec.src }); if (thumb?.thumb) await scene.update({ thumb: thumb.thumb }); }
  catch (e) { console.warn(`${MOD} | thumbnail skipped`, e); }
  return scene;
}

async function buildScenes() {
  const all = await sceneData();
  const note = ui.notifications.info(`${ROOT}: building scenes…`, { permanent: true });
  const folder = await ensureFolder(ROOT, "Scene");
  await ensureScene(all.landing, folder);
  await ensureScene(all.section, folder);
  for (const s of all.scenes) await stageScene(s.key);
  note?.remove?.();
  ui.notifications.info(`${ROOT}: ${all.scenes.length} scenes built.`);
}

async function setupAll() {
  await migrateLegacy();
  try { if (game.catAndUnkindness?.setup) await game.catAndUnkindness.setup(); } catch (e) { console.error(MOD, "Part I setup", e); }
  await installContent({ update: false });
  await buildScenes();
  await applyPartySize(game.settings.get(MOD, "partySize"));
  await game.settings.set(MOD, "installedVersion", game.modules.get(MOD).version);
  ui.notifications.info(`The Unkindness Saga is ready. Part I starts in "00 — START HERE: THE LAST TWO SESSIONS"; Part II in "00 — Start Here: The Stone Ledger".`);
  byKey(game.journal, "start")?.sheet?.render(true);
}
async function updateContent() {
  await installContent({ update: true });
  await applyPartySize(game.settings.get(MOD, "partySize"));
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
    return `<div class="il-ledger"><img class="il-ledger-banner" src="modules/${MOD}/assets/art/banner.webp" alt="">
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
      partOne: async function () { await migrateLegacy(); await game.catAndUnkindness?.setup?.(); this.render(); },
      partOneDash: async function () { await game.catAndUnkindness?.dashboard?.(); },
      install: async function () { await installContent({ update: false }); this.render(); },
      update: async function () { await updateContent(); this.render(); },
      scenes: async function () { await buildScenes(); this.render(); },
      scene: async function (ev, el) { await stageScene(el.dataset.key); ui.notifications.info(`Scene rebuilt: ${el.dataset.key}`); },
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
      <header class="il-mhead"><img src="modules/${MOD}/assets/art/banner.webp" alt=""><p>Module ${ver} · World content ${inst || "not installed"}</p></header>
      <section><h3>Part I — The Cat and the Unkindness (Ravenloft finale)</h3>
        <div class="il-row"><button type="button" data-action="partOne"><i class="fa-solid fa-chess-rook"></i> Set Up / Repair Part I</button>
        <button type="button" data-action="partOneDash"><i class="fa-solid fa-gauge"></i> Finale Dashboard</button></div>
        <p class="hint">23 walled and lit Ravenloft, Vallaki and Barovia scenes, the brides, Strahd's phases, the Dark Powers and the finale state. Its world content lives under <em>The Cat and the Unkindness</em> folders.</p></section>
      <section><h3>Part II — The Shield Between Us (Ironfist Legacy)</h3>
        <button type="button" class="il-big" data-action="setupAll"><i class="fa-solid fa-wand-magic-sparkles"></i> Set Up Everything (Parts I and II)</button>
        <div class="il-row"><button type="button" data-action="install"><i class="fa-solid fa-download"></i> Install Content</button>
        <button type="button" data-action="update"><i class="fa-solid fa-arrows-rotate"></i> Update Content</button>
        <button type="button" data-action="scenes"><i class="fa-solid fa-map"></i> Build All Scenes</button></div>
        <p class="hint">Rebuilding a scene replaces only the walls, lights, pins and tokens this module placed. Update Content refreshes documents from the compendiums and keeps their IDs, so tokens and links keep working.</p></section>
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
      return `<div class="il-power" style="border-left:6px solid ${data.powers[k].color}"><img src="modules/${MOD}/assets/icons/${data.powers[k].icon}.webp" alt="">
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

// ---------------------------------------------------------------- the Hold (Kharad-Varr side quests)
const HoldAPI = {
  /** Stage (if needed) and view the painted overview of the Hold. */
  async map() {
    let scene = game.scenes.find(s => s.getFlag(MOD, "key") === "hold-map");
    if (!scene) scene = await stageScene("hold-map");
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

const API = {
  setupAll, installContent, updateContent, buildScenes, stageScene, removeAll, applyPartySize,
  ledger: Ledger, awardEvidence, toggleEvidence, adjustTrack, baldrikEvent, hearing, postLedger,
  workChallenge, countdown, clock: Clock, dealFavour, drawDispatch, nextPressure, passCard,
  forgeRune, showHandout, requestSave, playSceneMusic, playSfx, inheritance: Inheritance, migrateLegacy, hold: HoldAPI,
  openManager: () => new Manager().render(true)
};
