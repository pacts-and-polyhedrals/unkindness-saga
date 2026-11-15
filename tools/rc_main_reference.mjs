/**
 * The Night of the Red Clause — runtime.
 * Pacts & Polyhedrals · Asmo and Ben Vale.
 *
 * Installs compendium content into labelled world folders, stages every scene (map, walls,
 * doors, lights, journal pins, tokens), and provides the GM tools used at the table:
 * the Midnight Docket bell tracker, the Writ / exhibit system, nightfall, handouts and more.
 */
const MOD = "night-of-the-red-clause";
const ROOT = "The Night of the Red Clause";
const PACKS = [
  ["actors", "Actor", `${ROOT} — Actors`],
  ["pregens", "Actor", `${ROOT} — Pregenerated Heroes`],
  ["items", "Item", `${ROOT} — Items`],
  ["spells", "Item", `${ROOT} — Spells`],
  ["options", "Item", `${ROOT} — Player Options`],
  ["journals", "JournalEntry", ROOT],
  ["tables", "RollTable", ROOT],
  ["macros", "Macro", ROOT]
];
const PLAYER_JOURNALS = ["handouts", "pregens"];
const WRITS = {
  1: { name: "Writ I — The Presumption of Default", exhibits: ["A"], power: "Default Notice; bailiffs under central command" },
  2: { name: "Writ II — The Perpetuity of Service", exhibits: ["C"], power: "Regains 15 HP at the start of his turn" },
  3: { name: "Writ III — The Doctrine of Abandoned Souls", exhibits: ["B", "D"], power: "Legendary Resistance (2)" }
};
const EXHIBITS = {
  A: "Exhibit A: Evidence of Falsified Defaults",
  B: "Exhibit B: Evidence of Falsified Service Addresses",
  C: "Exhibit C: The Endless-Night Mechanism",
  D: "Exhibit D: Testimony and Records of Unauthorised Soul Transfers"
};
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"];

const gen = () => game.release?.generation ?? 13;
const esc = s => foundry.utils.escapeHTML ? foundry.utils.escapeHTML(String(s)) : String(s);
const DialogV2 = () => foundry.applications.api.DialogV2;

/* ------------------------------------------------------------------------ */
/*  Settings                                                                */
/* ------------------------------------------------------------------------ */
Hooks.once("init", () => {
  game.settings.register(MOD, "installedVersion", { scope: "world", config: false, type: String, default: "" });
  game.settings.register(MOD, "promptDismissed", { scope: "world", config: false, type: Boolean, default: false });
  game.settings.register(MOD, "partySize", { scope: "world", config: false, type: Number, default: 5 });
  game.settings.register(MOD, "docket", {
    scope: "world", config: false, type: Object,
    default: { bell: 3, stays: 0, delays: 0, visible: false, transfer: false },
    onChange: () => Docket.refresh()
  });
  game.settings.register(MOD, "writs", {
    scope: "world", config: false, type: Object,
    default: { 1: { state: "active", provisional: 0 }, 2: { state: "active", provisional: 0 }, 3: { state: "active", provisional: 0 }, phase2: false },
    onChange: () => Docket.refresh()
  });
  game.settings.registerMenu(MOD, "manager", {
    name: "Red Clause Manager", label: "Open Manager", hint: "Set up, update, rebuild scenes, or remove the adventure.",
    icon: "fa-solid fa-scroll", type: Manager, restricted: true
  });
});

Hooks.once("ready", async () => {
  game.modules.get(MOD).api = API;
  Docket.refresh();
  if (!game.user.isGM) return;
  const ver = game.modules.get(MOD).version;
  const installed = game.settings.get(MOD, "installedVersion");
  if (!installed && !game.settings.get(MOD, "promptDismissed")) {
    const ok = await DialogV2().confirm({
      window: { title: "The Night of the Red Clause" },
      content: `<p>Set up <strong>The Night of the Red Clause</strong> now?</p><p>This installs the actors, items, spells, journals, tables and macros into labelled folders and builds all ten scenes with walls, lighting, pins and tokens. You can do it later from <em>Game Settings → Red Clause Manager</em>.</p>`,
      yes: { label: "Set Up Everything" }, no: { label: "Later" }
    });
    if (ok) await API.setupAll();
    else await game.settings.set(MOD, "promptDismissed", true);
  } else if (installed && installed !== ver) {
    ui.notifications.info(`The Night of the Red Clause updated to ${ver}. Open the Red Clause Manager and choose "Update Content" to refresh your world copies.`, { permanent: true });
  }
});

/* ------------------------------------------------------------------------ */
/*  Content installation                                                    */
/* ------------------------------------------------------------------------ */
async function ensureFolder(name, type, parent = null, color = "#5e0b18") {
  const pid = parent?.id ?? null;
  let f = game.folders.find(x => x.type === type && x.name === name && (x.folder?.id ?? null) === pid);
  if (!f) f = await Folder.create({ name, type, folder: pid, color, sorting: "a", flags: { [MOD]: { managed: true } } });
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
    fmap.set(f.id, await ensureFolder(f.name, type, parent, f.color ?? "#5e0b18"));
  }
  const coll = game.collections.get(type);
  const cls = getDocumentClass(type);
  const create = [];
  for (const d of docs) {
    const data = coll.fromCompendium(d, { keepId: true, clearFolder: true, clearOwnership: false });
    data.folder = fmap.get(d.folder?.id ?? d.folder)?.id ?? root.id;
    foundry.utils.setProperty(data, `flags.${MOD}.managed`, true);
    if (type === "JournalEntry" && PLAYER_JOURNALS.includes(d.getFlag(MOD, "key"))) {
      data.ownership = { default: CONST.DOCUMENT_OWNERSHIP_LEVELS.OBSERVER };
    }
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

async function installContent({ update = false } = {}) {
  let n = 0;
  const note = ui.notifications.info(`${ROOT}: installing content…`, { permanent: true });
  for (const [pack, type, root] of PACKS) n += await importPack(pack, type, root, { update });
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

function managed(d) { return d.getFlag?.(MOD, "managed") === true; }

async function sceneLevel(scene) {
  const levels = scene?.levels?.contents ?? [];
  return scene?.initialLevel ?? levels[0] ?? null;
}

async function setBackground(scene, src, name) {
  if (gen() >= 14) {
    const level = await sceneLevel(scene);
    if (level?.update) await level.update({ "background.src": src });
    else if (scene.createEmbeddedDocuments) await scene.createEmbeddedDocuments("Level", [{ name, background: { src } }]);
  } else {
    await scene.update({ "background.src": src });
  }
}

async function ensureScene(spec, folder) {
  let scene = game.scenes.get(spec.id);
  const base = {
    _id: spec.id, name: spec.title, folder: folder.id, navigation: true, navOrder: spec.order, sort: spec.order * 1000,
    width: spec.width, height: spec.height, padding: 0,
    grid: { size: spec.grid, type: 1, distance: 5, units: "ft", alpha: 0.12, color: "#000000" },
    tokenVision: true, fog: { exploration: true },
    environment: {
      darknessLevel: spec.env.darkness ?? 0,
      globalLight: { enabled: !!spec.env.globalLight, darkness: { max: 1, min: 0 } },
      cycle: true
    },
    journal: spec.journal ?? null, journalEntryPage: spec.journalPage ?? null,
    flags: { [MOD]: { managed: true, key: spec.key, night: spec.env.night ?? null, day: spec.env.darkness ?? 0 } }
  };
  if (gen() < 14) base.background = { src: spec.src };
  else base.levels = [{ name: spec.title, background: { src: spec.src } }];
  if (!scene) {
    [scene] = await Scene.createDocuments([base], { keepId: true });
  } else {
    const { _id, ...upd } = base;
    delete upd.levels;
    delete upd.background;
    await scene.update(upd);
  }
  await setBackground(scene, spec.src, spec.title);
  return scene;
}

async function stageScene(key) {
  const all = await sceneData();
  const spec = all.scenes.find(s => s.key === key);
  if (!spec) throw new Error(`Unknown scene ${key}`);
  const folder = await ensureFolder(ROOT, "Scene");
  const scene = await ensureScene(spec, folder);
  const levelId = gen() >= 14 ? (await sceneLevel(scene))?.id : null;
  const lv = levelId ? { levels: [levelId] } : {};
  // clear previous module placeables only
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
    if (w.sight === "none" && w.kind === "wall") { d.sight = W.NONE; d.light = W.NONE; }
    return d;
  });
  if (walls.length) await scene.createEmbeddedDocuments("Wall", walls);
  const lights = spec.lights.map(l => ({
    x: l.x, y: l.y, walls: l.walls !== false, flags: flag, ...lv,
    config: {
      dim: l.dim * 5, bright: l.bright * 5, color: l.color, alpha: l.alpha, luminosity: l.luminosity ?? 0.5,
      attenuation: 0.6, coloration: 1,
      animation: { type: l.anim ?? null, speed: l.speed ?? 3, intensity: l.intensity ?? 3, reverse: false },
      darkness: l.darkness ?? { min: 0, max: 1 }
    }
  }));
  if (lights.length) await scene.createEmbeddedDocuments("AmbientLight", lights);
  const notes = spec.notes.filter(n => game.journal.get(n.entryId)).map(n => ({
    x: n.x, y: n.y, entryId: n.entryId, pageId: n.pageId, text: n.label, flags: flag, ...lv,
    texture: { src: `modules/${MOD}/assets/icons/mc-handout.webp` }, iconSize: 48, fontSize: 22, textAnchor: 1,
    global: false
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
  try {
    const thumb = await scene.createThumbnail({ img: spec.src });
    if (thumb?.thumb) await scene.update({ thumb: thumb.thumb });
  } catch (e) { console.warn(`${MOD} | thumbnail skipped`, e); }
  return scene;
}

async function buildScenes() {
  const all = await sceneData();
  const note = ui.notifications.info(`${ROOT}: building scenes…`, { permanent: true });
  // landing scene
  const folder = await ensureFolder(ROOT, "Scene");
  await ensureScene(all.landing, folder);
  for (const s of all.scenes) await stageScene(s.key);
  note?.remove?.();
  ui.notifications.info(`${ROOT}: ${all.scenes.length} scenes built.`);
}

async function setupAll() {
  await installContent({ update: false });
  await buildScenes();
  await applyPartySize(game.settings.get(MOD, "partySize"));
  await game.settings.set(MOD, "installedVersion", game.modules.get(MOD).version);
  const landing = game.scenes.get((await sceneData()).landing.id);
  ui.notifications.info(`${ROOT} is ready. Open the Adventure Book to begin.`);
  const book = game.journal.find(j => j.getFlag(MOD, "key") === "adventure");
  book?.sheet.render(true);
  return landing;
}

async function updateContent() {
  await installContent({ update: true });
  await applyPartySize(game.settings.get(MOD, "partySize"));
  await game.settings.set(MOD, "installedVersion", game.modules.get(MOD).version);
}

async function removeAll() {
  const ok = await DialogV2().confirm({ window: { title: "Remove The Night of the Red Clause" },
    content: "<p>Delete every world document and folder this module created (scenes, actors, items, journals, tables, macros)? Anything you created yourself is kept.</p>" });
  if (!ok) return;
  for (const coll of [game.scenes, game.actors, game.items, game.journal, game.tables, game.macros]) {
    const ids = coll.filter(managed).map(d => d.id);
    if (ids.length) await coll.documentClass.deleteDocuments(ids);
  }
  const fids = game.folders.filter(managed).map(f => f.id);
  if (fids.length) await Folder.deleteDocuments(fids);
  await game.settings.set(MOD, "installedVersion", "");
  ui.notifications.info(`${ROOT} removed.`);
}

/* ------------------------------------------------------------------------ */
/*  Party size scaling                                                      */
/* ------------------------------------------------------------------------ */
async function applyPartySize(n) {
  n = Math.max(4, Math.min(6, Number(n) || 5));
  await game.settings.set(MOD, "partySize", n);
  const hp = { 4: 200, 5: 250, 6: 300 }[n], la = n >= 6 ? 3 : 2;
  const boss = game.actors.find(a => a.getFlag(MOD, "managed") && a.name === "Nicholas Red Clause");
  if (boss) await boss.update({ "system.attributes.hp.value": hp, "system.attributes.hp.max": hp,
    "system.resources.legact.max": la, "system.resources.legact.value": la });
  const court = game.scenes.find(s => s.getFlag(MOD, "key") === "court");
  if (court) {
    const bailiffs = court.tokens.filter(t => managed(t) && t.name === "Jingle Bailiff");
    const want = { 4: 1, 5: 2, 6: 3 }[n];
    const upd = bailiffs.map((t, i) => ({ _id: t.id, hidden: i >= want }));
    if (upd.length) await court.updateEmbeddedDocuments("Token", upd);
  }
  return n;
}

/* ------------------------------------------------------------------------ */
/*  The Midnight Docket                                                     */
/* ------------------------------------------------------------------------ */
const Docket = {
  el: null,
  state() { return foundry.utils.deepClone(game.settings.get(MOD, "docket")); },
  writs() { return foundry.utils.deepClone(game.settings.get(MOD, "writs")); },
  async set(s) { if (!game.user.isGM) return; await game.settings.set(MOD, "docket", s); },
  async open(visible = true) { const s = this.state(); s.visible = visible; await this.set(s); },
  async advance() {
    const s = this.state();
    if (s.delays > 0) { s.delays--; await this.set(s); return chat(`<p>The great clock shudders, and <strong>holds</strong>. The bell does not toll this round.</p>`, "The Midnight Docket"); }
    if (s.bell >= 9) {
      s.transfer = true; await this.set(s);
      return chat(`<p><strong>The transfer continues.</strong> About one-third of the remaining captive souls are drawn into Nessus.</p>`, "The Midnight Docket");
    }
    s.bell++;
    if (s.bell === 9) s.transfer = true;
    await this.set(s);
    chat(`<p class="nrc-toll">BELL ${ROMAN[s.bell]} OF IX</p>` + (s.bell === 9
      ? `<p><strong>The Ninth Bell.</strong> The soul transfer begins. At each initiative count 20, about one-third of the remaining captives are transferred.</p>`
      : `<p>${9 - s.bell} bell${9 - s.bell === 1 ? "" : "s"} remain before the transfer.</p>`), "The Midnight Docket");
  },
  async stay() {
    const s = this.state();
    if (s.stays >= 2) return ui.notifications.warn("Clever actions can delay the docket at most twice.");
    s.stays++; s.delays++; await this.set(s);
    chat(`<p><strong>Stay granted.</strong> The next toll is delayed by one round. (${s.stays}/2 clever stays used.)</p>`, "The Midnight Docket");
  },
  async delayWrit() { const s = this.state(); s.delays++; await this.set(s); },
  async reset() { await this.set({ bell: 3, stays: 0, delays: 0, visible: this.state().visible, transfer: false }); },
  async close() { const s = this.state(); s.visible = false; await this.set(s); },
  refresh() {
    if (!game.ready && !game.settings) return;
    let s, w;
    try { s = this.state(); w = this.writs(); } catch { return; }
    if (!s.visible) { this.el?.remove(); this.el = null; return; }
    if (!this.el) {
      this.el = document.createElement("section");
      this.el.id = "nrc-docket";
      document.body.appendChild(this.el);
      this.el.addEventListener("click", ev => {
        const b = ev.target.closest("[data-act]"); if (!b || !game.user.isGM) return;
        const a = b.dataset.act;
        if (a === "advance") this.advance(); else if (a === "stay") this.stay(); else if (a === "reset") this.reset();
        else if (a === "close") this.close(); else if (a === "exhibit") presentExhibit();
        else if (a.startsWith("writ")) breakWrit(Number(a.slice(4)));
      });
    }
    const bells = [1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => `<span class="nrc-bell ${i <= s.bell ? "rung" : ""} ${i === 9 ? "ninth" : ""}">${ROMAN[i]}</span>`).join("");
    const writs = [1, 2, 3].map(i => {
      const st = w[i]?.state ?? "active";
      return `<div class="nrc-writ ${st}" ${game.user.isGM ? `data-act="writ${i}"` : ""} title="${esc(WRITS[i].power)}"><b>${ROMAN[i]}</b><span>${st === "active" ? "Stands" : st === "suspended" ? "Suspended" : st === "invalidated" ? "Invalidated" : "Destroyed"}</span></div>`;
    }).join("");
    const gm = game.user.isGM ? `<div class="nrc-ctl"><button data-act="advance" title="Initiative count 20">Toll</button><button data-act="stay">Stay (${s.stays}/2)</button><button data-act="exhibit">Exhibit</button><button data-act="reset">Reset</button><button data-act="close">✕</button></div>` : "";
    this.el.innerHTML = `<header>The Midnight Docket</header><div class="nrc-bells">${bells}</div>
      <div class="nrc-status">${s.transfer ? "<strong>SOUL TRANSFER UNDER WAY</strong>" : `Bell ${ROMAN[s.bell]} of IX${s.delays ? ` · next toll delayed ${s.delays}` : ""}`}</div>
      <div class="nrc-writs">${writs}</div>${gm}`;
  }
};

/* ------------------------------------------------------------------------ */
/*  Writs and exhibits                                                      */
/* ------------------------------------------------------------------------ */
function chat(content, alias = "The Brass Arbiter") {
  return ChatMessage.create({ content: `<div class="nrc-chat">${content}</div>`, speaker: { alias } });
}

async function presentExhibit() {
  if (!game.user.isGM) return;
  const writOpts = [1, 2, 3].map(i => `<option value="${i}">${esc(WRITS[i].name)}</option>`).join("");
  const exOpts = Object.entries(EXHIBITS).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join("") +
    `<option value="none">Incomplete evidence / argument only</option>`;
  const res = await DialogV2().prompt({
    window: { title: "Present an Exhibit to the Brass Arbiter" },
    content: `<div class="nrc-form"><label>Writ challenged <select name="writ">${writOpts}</select></label>
      <label>Evidence presented <select name="ex">${exOpts}</select></label>
      <label><input type="checkbox" name="auth" checked> Evidence is authenticated (certified, sealed or sworn)</label>
      <p class="hint">Only one petition receives a full ruling per round.</p></div>`,
    ok: { label: "Present", callback: (ev, button) => ({ writ: Number(button.form.elements.writ.value), ex: button.form.elements.ex.value, auth: button.form.elements.auth.checked }) }
  });
  if (!res) return;
  const writs = Docket.writs();
  const w = writs[res.writ];
  if (["invalidated", "destroyed"].includes(w.state)) return ui.notifications.warn("That Writ has already fallen.");
  if (res.ex !== "none" && WRITS[res.writ].exhibits.includes(res.ex) && res.auth) {
    await chat(`<p>The Arbiter weighs <em>${esc(EXHIBITS[res.ex])}</em>.</p><p class="nrc-ruling">"EVIDENCE AUTHENTICATED. ${esc(WRITS[res.writ].name.toUpperCase())} IS INVALID."</p>`);
    return breakWrit(res.writ, "invalidated");
  }
  // provisional challenge
  await chat(`<p>The evidence does not decide the matter alone. The advocate must argue it.</p>
    <p>[[/check investigation arcana religion insight persuasion 18]]</p>
    <p class="hint">On a success, ${esc(WRITS[res.writ].name)} is <strong>suspended</strong> for one round. Two separate successes invalidate it. Use the Docket's Writ buttons to record the outcome.</p>`);
  const ok = await DialogV2().confirm({ window: { title: "Provisional Challenge" }, content: `<p>Did the advocate succeed on the DC 18 check?</p>`,
    yes: { label: "Success" }, no: { label: "Failure" } });
  if (!ok) return chat(`<p class="nrc-ruling">"PETITION NOT SUSTAINED."</p>`);
  w.provisional = (w.provisional ?? 0) + 1;
  if (w.provisional >= 2) { await game.settings.set(MOD, "writs", writs); return breakWrit(res.writ, "invalidated"); }
  w.state = "suspended";
  await game.settings.set(MOD, "writs", writs);
  chat(`<p class="nrc-ruling">"${esc(WRITS[res.writ].name.toUpperCase())} IS SUSPENDED PENDING FURTHER ARGUMENT."</p><p>Suspended for one round. One more successful challenge invalidates it.</p>`);
}

async function breakWrit(n, how = null) {
  if (!game.user.isGM) return;
  const writs = Docket.writs();
  const w = writs[n];
  if (!how) {
    const choice = await DialogV2().wait({
      window: { title: WRITS[n].name },
      content: `<p>Current state: <strong>${w.state}</strong>.</p>`,
      buttons: [{ action: "invalidated", label: "Invalidated by evidence" }, { action: "destroyed", label: "Destroyed (0 HP)" },
        { action: "active", label: "Restore (stands)" }]
    });
    if (!choice) return;
    how = choice;
  }
  const wasDown = ["invalidated", "destroyed"].includes(w.state);
  w.state = how;
  if (how === "active") w.provisional = 0;
  await game.settings.set(MOD, "writs", writs);
  if (how === "active" || wasDown) return;
  const scene = canvas.scene;
  const lines = [];
  if (n === 1) {
    lines.push("Every Jingle Bailiff is <strong>stunned</strong> until the end of its next turn. The Red Clause loses <strong>Default Notice</strong>.");
    for (const t of scene?.tokens ?? []) if (t.name === "Jingle Bailiff" && t.actor) await t.actor.toggleStatusEffect("stunned", { active: true });
  }
  if (n === 2) { lines.push("The Red Clause's regeneration ends. The next advancing bell is <strong>delayed by one round</strong>."); await Docket.delayWrit(); }
  if (n === 3) {
    lines.push("The Red Clause loses any unused <strong>Legendary Resistance</strong>. The Arbiter warns that the soul transfer lacks legal title.");
    for (const t of scene?.tokens ?? []) if (t.actor?.name === "Nicholas Red Clause") await t.actor.update({ "system.resources.legres.value": 0, "system.resources.legres.max": 0 });
  }
  const tok = scene?.tokens.find(t => t.actor?.name === WRITS[n].name);
  if (tok) await tok.update({ alpha: 0.35, "texture.tint": how === "destroyed" ? "#555555" : "#ffd27a" });
  await chat(`<p><strong>${esc(WRITS[n].name)}</strong> is ${how === "destroyed" ? "destroyed. The Arbiter records the destruction; it establishes no precedent." : "invalidated."}</p><p>${lines.join("</p><p>")}</p>`);
  const after = Docket.writs();
  const states = [1, 2, 3].map(i => after[i].state);
  if (states.every(s => s === "invalidated")) {
    await chat(`<p class="nrc-ruling">"ALL WRITS FOUND INVALID. THE HEARTHLIGHT COLLECTION PROGRAMME IS UNLAWFUL. THE LICENCE OF NICHOLAS RED CLAUSE IS TERMINATED. ALL ILLEGALLY HELD SOULS ARE RELEASED."</p><p>Ending A: The Unprecedented Verdict. The avatar is recalled to Nessus by his own chains.</p>`);
  } else if (states.every(s => ["invalidated", "destroyed"].includes(s))) {
    await chat(`<p>All three Writs have fallen. The collection machinery stops.${states.includes("destroyed") ? " The broader legal precedent remains unresolved." : ""}</p>`);
  }
  if (states.filter(s => s === "destroyed").length >= 2 && !after.phase2) {
    const go = await DialogV2().confirm({ window: { title: "Phase II" }, content: "<p>Two Writs are destroyed. Trigger <strong>The Smile Disappears</strong>?</p>" });
    if (go) await phase2();
  }
}

async function phase2() {
  if (!game.user.isGM) return;
  const writs = Docket.writs(); writs.phase2 = true; await game.settings.set(MOD, "writs", writs);
  await chat(`<p><em>The Red Clause stops moving. His smile remains for a moment, as though painted onto his face. Then it slowly folds inwards. You hear metal tearing. His crimson coat splits open on a furnace of black iron and white-hot chains; inside, thousands of names burn across the walls. The beard of silver bells unravels into barbed chain. His spectacles shatter.</em></p>
    <p class="nrc-ruling">"I have been exceedingly patient. You have exhausted the limits of my goodwill. Your account is now payable in full."</p>
    <p>Each creature within 15 feet: [[/save wisdom 18]] — [[/damage 4d8 psychic]] on a failure, half on a success.</p>`, "Nicholas Red Clause");
}

/* ------------------------------------------------------------------------ */
/*  Other table tools                                                       */
/* ------------------------------------------------------------------------ */
async function nightfall() {
  const scene = canvas.scene; if (!scene || !game.user.isGM) return;
  const night = scene.getFlag(MOD, "night") ?? 0.62;
  const day = scene.getFlag(MOD, "day") ?? 0;
  const cur = scene.environment?.darknessLevel ?? scene.darkness ?? 0;
  const target = cur < (night + day) / 2 ? night : day;
  await scene.update({ "environment.darknessLevel": target }, { animateDarkness: 6000 });
  if (target === night) chat(`<p><em>The sun sets over Waterdeep. One by one the lanterns light themselves… and a single deep bell begins to sound.</em></p>`, "Midwinter");
}

async function showHandout() {
  const j = game.journal.find(x => x.getFlag(MOD, "key") === "handouts");
  if (!j) return ui.notifications.warn("Install the module content first.");
  const opts = j.pages.contents.sort((a, b) => a.sort - b.sort).map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join("");
  const id = await DialogV2().prompt({ window: { title: "Show a Handout" }, content: `<div class="nrc-form"><select name="p">${opts}</select></div>`,
    ok: { label: "Show to Players", callback: (ev, b) => b.form.elements.p.value } });
  if (!id) return;
  const page = j.pages.get(id);
  const Journal = foundry.documents.collections?.Journal ?? globalThis.Journal;
  return Journal.show(page, { force: true });
}

async function issueFine() {
  const table = game.tables.find(t => t.getFlag(MOD, "key") === "festive-fines");
  if (!table) return ui.notifications.warn("Install the module content first.");
  const tok = canvas.tokens.controlled[0];
  const draw = await table.draw({ displayChat: false });
  const r = draw.results[0];
  const txt = r?.description ?? r?.text ?? r?.name ?? "";
  ChatMessage.create({ speaker: { alias: "Sprocket Jingles" },
    content: `<div class="nrc-chat nrc-citation"><p class="nrc-toll">CITATION</p><p>${tok ? `<strong>${esc(tok.name)}</strong> is hereby cited for:` : "You are hereby cited for:"}</p><p>${txt}</p><p class="hint">Unenforceable. Please pay promptly anyway.</p></div>` });
}

async function giveGift() {
  const pack = game.packs.get(`${MOD}.items`);
  const idx = await pack.getIndex({ fields: ["flags"] });
  const gifts = idx.filter(i => i.flags?.[MOD]?.gift);
  const actor = canvas.tokens.controlled[0]?.actor ?? game.user.character;
  if (!actor) return ui.notifications.warn("Select the recipient's token first.");
  const opts = gifts.map(g => `<option value="${g._id}">${esc(g.name)}</option>`).join("");
  const id = await DialogV2().prompt({ window: { title: `A Gift for ${actor.name}` }, content: `<div class="nrc-form"><select name="g">${opts}</select><p class="hint">The recipient signs Form H-25. Show them the certificate.</p></div>`,
    ok: { label: "Give the Gift", callback: (ev, b) => b.form.elements.g.value } });
  if (!id) return;
  const item = await pack.getDocument(id);
  await actor.createEmbeddedDocuments("Item", [game.items.fromCompendium(item)]);
  ChatMessage.create({ speaker: { alias: "A Festive Clerk" }, content: `<div class="nrc-chat"><p><strong>${esc(actor.name)}</strong> accepts <em>${esc(item.name)}</em>. "Sign here, here, and… here. Merry Midwinter!"</p></div>` });
  const j = game.journal.find(x => x.getFlag(MOD, "key") === "handouts");
  const page = j?.pages.find(p => p.getFlag(MOD, "key") === "certificate");
  const Journal = foundry.documents.collections?.Journal ?? globalThis.Journal;
  if (page) Journal.show(page, { force: true });
}

const Challenge = { s: 0, f: 0, need: 3, fail: 2, name: "" };
async function skillChallenge() {
  const preset = await DialogV2().wait({ window: { title: "Skill Challenge" }, content: "<p>Choose a challenge.</p>",
    buttons: [{ action: "dasher", label: "DASH-ER 3000 (3 before 2, DC 15)" }, { action: "sleigh", label: "Sleigh Chase (5 before 3, DC 16–18)" }, { action: "track", label: "Continue current" }] });
  if (!preset) return;
  if (preset === "dasher") Object.assign(Challenge, { s: 0, f: 0, need: 3, fail: 2, name: "The Runaway Reindeer" });
  if (preset === "sleigh") Object.assign(Challenge, { s: 0, f: 0, need: 5, fail: 3, name: "The Rooftop Sleigh Chase" });
  const r = await DialogV2().wait({ window: { title: Challenge.name || "Skill Challenge" },
    content: `<p><strong>${Challenge.s}</strong> / ${Challenge.need} successes · <strong>${Challenge.f}</strong> / ${Challenge.fail} failures</p>`,
    buttons: [{ action: "s", label: "+ Success" }, { action: "f", label: "+ Failure" }, { action: "x", label: "Close" }] });
  if (r === "s") Challenge.s++;
  if (r === "f") Challenge.f++;
  if (r === "s" || r === "f") {
    let msg = `<p><strong>${esc(Challenge.name)}:</strong> ${Challenge.s}/${Challenge.need} successes, ${Challenge.f}/${Challenge.fail} failures.</p>`;
    if (Challenge.s >= Challenge.need) msg += `<p class="nrc-ruling">SUCCESS!</p>`;
    else if (Challenge.f >= Challenge.fail) msg += `<p class="nrc-ruling">FAILURE — pastries and eggnog everywhere (or a rough landing).</p>`;
    chat(msg, "Skill Challenge");
    if (Challenge.s < Challenge.need && Challenge.f < Challenge.fail) return skillChallengeContinue();
  }
}
async function skillChallengeContinue() { return skillChallenge(); }

async function requestSave() {
  const abil = Object.entries(CONFIG.DND5E.abilities).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join("");
  const res = await DialogV2().prompt({ window: { title: "Request a Saving Throw" },
    content: `<div class="nrc-form"><label>Ability <select name="a">${abil}</select></label><label>DC <input type="number" name="dc" value="18"></label><label>Reason <input type="text" name="why" value=""></label></div>`,
    ok: { label: "Request", callback: (ev, b) => ({ a: b.form.elements.a.value, dc: b.form.elements.dc.value, why: b.form.elements.why.value }) } });
  if (!res) return;
  chat(`<p>${esc(res.why || "Make a saving throw.")}</p><p>[[/save ${res.a} ${Number(res.dc) || 10}]]</p>`, "The Night of the Red Clause");
}

/* ------------------------------------------------------------------------ */
/*  Manager window                                                          */
/* ------------------------------------------------------------------------ */
class Manager extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = {
    id: "nrc-manager", tag: "div", classes: ["nrc-app"],
    window: { title: "The Night of the Red Clause — Manager", icon: "fa-solid fa-scroll", resizable: true },
    position: { width: 560, height: "auto" },
    actions: {
      setupAll: async function () { await API.setupAll(); this.render(); },
      install: async function () { await installContent({ update: false }); this.render(); },
      update: async function () { await updateContent(); this.render(); },
      scenes: async function () { await buildScenes(); this.render(); },
      scene: async function (ev, el) { await stageScene(el.dataset.key); ui.notifications.info(`Scene rebuilt: ${el.dataset.key}`); },
      remove: async function () { await removeAll(); this.render(); },
      party: async function (ev, el) { const n = await applyPartySize(Number(el.dataset.n)); ui.notifications.info(`Scaled for ${n} heroes.`); this.render(); },
      docket: async function () { await Docket.open(true); }
    }
  };
  async _renderHTML() {
    const all = await sceneData();
    const ver = game.modules.get(MOD).version;
    const inst = game.settings.get(MOD, "installedVersion");
    const ps = game.settings.get(MOD, "partySize");
    const rows = all.scenes.map(s => `<li><span>${esc(s.title)}</span><button type="button" data-action="scene" data-key="${s.key}"><i class="fa-solid fa-rotate"></i> Rebuild</button></li>`).join("");
    return `<div class="nrc-manager">
      <header class="nrc-mhead"><img src="modules/${MOD}/assets/art/banner.webp" alt=""><p>Module ${ver} · World content ${inst || "not installed"}</p></header>
      <section><h3>Set Up</h3>
        <button type="button" class="nrc-big" data-action="setupAll"><i class="fa-solid fa-wand-magic-sparkles"></i> Set Up Everything</button>
        <div class="nrc-row"><button type="button" data-action="install"><i class="fa-solid fa-download"></i> Install Content</button>
        <button type="button" data-action="update"><i class="fa-solid fa-arrows-rotate"></i> Update Content</button>
        <button type="button" data-action="scenes"><i class="fa-solid fa-map"></i> Build All Scenes</button></div>
        <p class="hint">Rebuilding a scene replaces only the walls, lights, pins and tokens this module placed. Update Content refreshes actors, items, journals, tables and macros from the compendiums, keeping their IDs so scene tokens and links still work.</p></section>
      <section><h3>Party Size</h3><div class="nrc-row">${[4, 5, 6].map(n => `<button type="button" data-action="party" data-n="${n}" class="${n === ps ? "active" : ""}">${n} heroes</button>`).join("")}</div>
        <p class="hint">Sets the Red Clause's HP (200/250/300), legendary actions (2/2/3) and how many bailiffs are visible in the High Court.</p></section>
      <section><h3>Scenes</h3><ul class="nrc-scenes">${rows}</ul></section>
      <section><h3>At the Table</h3><div class="nrc-row"><button type="button" data-action="docket"><i class="fa-solid fa-bell"></i> Show the Midnight Docket</button></div></section>
      <section class="nrc-danger"><button type="button" data-action="remove"><i class="fa-solid fa-trash"></i> Remove Module Content</button></section>
    </div>`;
  }
  _replaceHTML(result, content) { content.innerHTML = result; }
}

/* ------------------------------------------------------------------------ */
const API = {
  setupAll, installContent, updateContent, buildScenes, stageScene, removeAll, applyPartySize,
  docket: Docket, presentExhibit, breakWrit, phase2, nightfall, showHandout, issueFine, giveGift, skillChallenge,
  requestSave, openManager: () => new Manager().render(true)
};
