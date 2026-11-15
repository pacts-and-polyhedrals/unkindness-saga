// Stand-in Foundry harness: runs Set Up Everything, the ledger, cards and clock tools end to end.
import fs from "node:fs";
import path from "node:path";
const ROOT = "/home/claude/saga/il";
const MOD = "unkindness-saga";
const GEN = Number(process.argv[2] || 13);
const deep = o => JSON.parse(JSON.stringify(o));
let idc = 0; const rid = () => "x" + (idc++).toString(36).padStart(15, "0");
const log = []; const errors = [];

function getProp(o, p) { return p.split(".").reduce((a, k) => a?.[k], o); }
function setProp(o, p, v) { const ks = p.split("."); let c = o; for (const k of ks.slice(0, -1)) c = c[k] ??= {}; c[ks.at(-1)] = v; }
function merge(a, b) { const o = deep(a ?? {}); for (const [k, v] of Object.entries(b ?? {})) { if (k.includes(".")) { setProp(o, k, v); continue; } o[k] = (v && typeof v === "object" && !Array.isArray(v) && o[k] && typeof o[k] === "object") ? merge(o[k], v) : v; } return o; }

class Coll extends Map {
  constructor(type) { super(); this.type = type; }
  get contents() { return [...this.values()]; }
  find(f) { return this.contents.find(f); } filter(f) { return this.contents.filter(f); } some(f) { return this.contents.some(f); }
  map(f) { return this.contents.map(f); }
  get documentClass() { return DOC[this.type]; }
  fromCompendium(d) { const o = deep(d._source); delete o.folder; return o; }
}
class Doc {
  constructor(data, type, parent = null) {
    this._source = deep(data); Object.assign(this, deep(data)); this.id = data._id ?? rid(); this._id = this.id; this.documentName = type; this.parent = parent;
    this.flags ??= {};
    if (type === "Scene") { for (const k of ["walls", "lights", "notes", "tokens", "levels"]) this[k] = new Coll(k); for (const l of data.levels ?? []) { const d = new Doc(l, "Level", this); this.levels.set(d.id, d); } }
    if (type === "JournalEntry") { const ps = new Coll("JournalEntryPage"); for (const p of data.pages ?? []) ps.set(p._id, new Doc(p, "JournalEntryPage", this)); this.pages = ps; }
    if (type === "Playlist") { const ss = new Coll("PlaylistSound"); for (const p of data.sounds ?? []) ss.set(p._id, new Doc(p, "PlaylistSound", this)); this.sounds = ss; }
    if (type === "Cards") { const cs = new Coll("Card"); for (const p of data.cards ?? []) cs.set(p._id, new Doc(p, "Card", this)); this.cards = cs; }
    if (type === "Actor") { this.prototypeToken = data.prototypeToken ?? { width: 1 }; this.items = new Coll("Item"); for (const i of data.items ?? []) this.items.set(i._id ?? rid(), new Doc(i, "Item", this)); }
  }
  getFlag(s, k) { return this.flags?.[s]?.[k]; }
  async update(u) { for (const [k, v] of Object.entries(u)) setProp(this, k, v); log.push(`update ${this.documentName}`); return this; }
  async delete() { COLLS[this.documentName]?.delete(this.id); }
  async updateEmbeddedDocuments(type, ups) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Item: "items", JournalEntryPage: "pages" }; const c = this[map[type]]; for (const u of ups) { const d = c?.get(u._id); const { _id, ...rest } = u; await d?.update(rest); } }
  toObject() { return deep({ ...this, parent: undefined, _source: undefined }); }
  async createEmbeddedDocuments(t, arr) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Level: "levels", Item: "items", JournalEntryPage: "pages" }; const c = this[map[t]] ??= new Coll(t); for (const a of arr) { if (t === "Note" && !a.entryId) throw new Error("note without entry"); const d = new Doc(a, t, this); c.set(d.id, d); } return arr; }
  async deleteEmbeddedDocuments(t, ids) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens" }; for (const i of ids) this[map[t]].delete(i); }
  async getTokenDocument(o) { return { toObject: () => ({ ...deep(this.prototypeToken), ...o, actorId: this.id }) }; }
  async createThumbnail() { return { thumb: "data:" }; }
  get initialLevel() { return this.levels?.contents?.[0]; }
  async pass(to, ids) { for (const i of ids) { const c = this.cards.get(i); if (!c || c.drawn) throw new Error("pass bad card"); c.drawn = true; const n = new Doc({ ...c._source, _id: rid() }, "Card", to); to.cards.set(n.id, n); } }
  async playSound(s) { s.playing = true; } async stopSound(s) { s.playing = false; }
  get rendered() { return false; }
}
const COLLS = {}; const DOC = {};
for (const t of ["Actor", "Item", "JournalEntry", "RollTable", "Macro", "Playlist", "Cards", "Scene", "Folder"]) {
  COLLS[t] = new Coll(t);
  DOC[t] = class { static async create(d) { const x = new Doc(d, t); COLLS[t].set(x.id, x); return x; }
    static async createDocuments(arr, o) { return arr.map(d => { if (o?.keepId && !d._id) throw new Error("keepId without _id"); const x = new Doc(d, t); if (COLLS[t].has(x.id)) throw new Error(`duplicate ${t} ${x.id}`); COLLS[t].set(x.id, x); return x; }); }
    static async deleteDocuments(ids) { for (const i of ids) COLLS[t].delete(i); }
    static async updateDocuments(ups) { for (const u of ups) { const d = COLLS[t].get(u._id); const { _id, ...rest } = u; await d?.update(rest); } } };
}
// packs from build sources
const PACKS = new Map();
for (const dir of fs.readdirSync(`${ROOT}/build/packs`)) {
  const files = fs.readdirSync(`${ROOT}/build/packs/${dir}`).map(f => JSON.parse(fs.readFileSync(`${ROOT}/build/packs/${dir}/${f}`, "utf8")));
  const folders = files.filter(f => f._key.startsWith("!folders")).map(f => ({ ...f, id: f._id }));
  for (const f of folders) f.folder = folders.find(x => x.id === f.folder) ?? null;
  const type = { actors: "Actor", items: "Item", spells: "Item", journals: "JournalEntry", tables: "RollTable", macros: "Macro", playlists: "Playlist", cards: "Cards" }[dir];
  const docs = files.filter(f => !f._key.startsWith("!folders")).map(f => { const d = new Doc(f, type); d.folder = folders.find(x => x.id === f.folder) ?? null; return d; });
  PACKS.set(`${MOD}.${dir}`, { folders, getDocuments: async () => docs });
}
const settings = new Map(); const reg = new Map();
globalThis.game = {
  release: { generation: GEN }, version: `${GEN}.350`, ready: true,
  user: { isGM: true, character: null }, modules: new Map([[MOD, { version: "1.0.0" }]]),
  packs: PACKS, settings: { register: (m, k, o) => reg.set(k, o), registerMenu() {}, get: (m, k) => settings.has(k) ? settings.get(k) : deep(reg.get(k)?.default), set: async (m, k, v) => { settings.set(k, v); reg.get(k)?.onChange?.(v); } },
  collections: { get: t => COLLS[t] }, folders: COLLS.Folder, journal: COLLS.JournalEntry, actors: COLLS.Actor, items: COLLS.Item,
  scenes: COLLS.Scene, tables: COLLS.RollTable, macros: COLLS.Macro, playlists: COLLS.Playlist, cards: COLLS.Cards
};
globalThis.Folder = DOC.Folder; globalThis.Scene = DOC.Scene; globalThis.Cards = DOC.Cards;
globalThis.getDocumentClass = t => DOC[t];
globalThis.CONST = { DOCUMENT_OWNERSHIP_LEVELS: { NONE: 0, OBSERVER: 2 }, WALL_SENSE_TYPES: { NONE: 0, LIMITED: 10, NORMAL: 20, PROXIMITY: 30 }, WALL_MOVEMENT_TYPES: { NONE: 0, NORMAL: 20 } };
globalThis.CONFIG = { DND5E: { skills: { per: { label: "Persuasion" } }, abilities: { str: { label: "Strength" } } } };
globalThis.ui = { notifications: { info: (m) => { log.push(m); return { remove() {} }; }, warn: m => errors.push("warn: " + m), error: m => errors.push(m) } };
const hooks = {}; globalThis.Hooks = { once: (h, f) => (hooks[h] ??= []).push(f), on: (h, f) => (hooks[h] ??= []).push(f) };
globalThis.ChatMessage = { create: async d => { log.push("chat"); return d; }, getWhisperRecipients: () => [{ id: "gm" }] };
globalThis.Roll = class { constructor(f) { this.f = f; } async evaluate() { this.total = 17; return this; } async toMessage() {} };
globalThis.foundry = { utils: { deepClone: deep, mergeObject: (a, b) => merge(a, b), setProperty: setProp, escapeHTML: s => s },
  applications: { api: { ApplicationV2: class { render() { return this; } }, DialogV2: { confirm: async () => true, prompt: async o => null, wait: async () => null } } } };
globalThis.fetch = async u => ({ ok: true, json: async () => JSON.parse(fs.readFileSync(path.join(ROOT, "module", u.replace(`modules/${MOD}/`, "")), "utf8")) });
globalThis.document = { createElement: () => ({ addEventListener() {}, remove() {}, set innerHTML(v) {} }), body: { appendChild() {} } };
globalThis.canvas = { scene: null, tokens: { controlled: [] } };

for (const [t_, c_] of Object.entries(DOC)) globalThis[t_] ??= c_; globalThis.CONFIG ??= {};
globalThis.CONST ??= {}; CONST.JOURNAL_ENTRY_PAGE_FORMATS ??= { HTML: 1 }; CONST.GRID_TYPES ??= { SQUARE: 1 }; CONST.DOCUMENT_OWNERSHIP_LEVELS ??= { NONE: 0, OBSERVER: 2, OWNER: 3 };
game.system ??= { id: "dnd5e", version: "6.0.6", model: {} }; game.version ??= "14.360";
await import(`${ROOT}/module/scripts/ravenloft.mjs`);
await import(`${ROOT}/module/scripts/ironfist.mjs`);
for (const f of hooks.init) f();
settings.set("promptDismissed", true);
for (const f of hooks.ready) await f();
const api = game.modules.get(MOD).api;
await api.setupAll();
{ // the Hold
  const hm = game.scenes.find(s => s.getFlag(MOD, "key") === "hold-map");
  console.log("hold: overview staged", !!hm, "notes", hm?.notes?.size, "grid", JSON.stringify(hm?.grid ?? hm?._source?.grid ?? null));
  const DV = foundry.applications.api.DialogV2; const op = DV.prompt;
  DV.prompt = async () => ({ who: "Vesper", stake: "10", house: "iskra", cheat: true });
  const before = log.length; await api.hold.rivets(); DV.prompt = op;
  console.log("hold: rivets posted chat", log.slice(before).includes("chat"));
  const venues = ["low-lantern","gilded-nail","ember-baths","turning-gear","anvilsong-forge","glimmerhall","mossbeard-remedies","deep-script"].map(k => game.scenes.find(s => s.getFlag(MOD, "key") === k));
  console.log("hold: venues", venues.filter(Boolean).length, "walls", venues.reduce((n, s) => n + (s?.walls.size ?? 0), 0), "tokens", venues.reduce((n, s) => n + (s?.tokens.size ?? 0), 0));
}
const count = t => COLLS[t].size;
const p1 = t => COLLS[t].filter(d => d.getFlag(MOD, "part") === "ravenloft").length;
console.log(`Part I: actors ${p1("Actor")}, items ${p1("Item")}, journals ${p1("JournalEntry")}, macros ${p1("Macro")}, scenes ${p1("Scene")}; walls ${COLLS.Scene.filter(d => d.getFlag(MOD, "part") === "ravenloft").reduce((n, s) => n + s.walls.size, 0)}`);
console.log(`v${GEN}: actors ${count("Actor")}, items ${count("Item")}, journals ${count("JournalEntry")}, tables ${count("RollTable")}, macros ${count("Macro")}, playlists ${count("Playlist")}, cards ${count("Cards")}, scenes ${count("Scene")}`);
let walls = 0, toks = 0, notes = 0, lights = 0; for (const s of COLLS.Scene.contents) { walls += s.walls.size; toks += s.tokens.size; notes += s.notes.size; lights += s.lights.size; }
console.log(`placeables: walls ${walls}, lights ${lights}, notes ${notes}, tokens ${toks}; scenes with music ${COLLS.Scene.filter(s => s.playlistSound).length}`);
// table tools
await api.toggleEvidence("E3");
await api.baldrikEvent("refused");
await api.passCard("favours", "heddra", "hand-favours");
await api.drawDispatch();
const dossier = COLLS.Cards.find(c => c.getFlag(MOD, "key") === "hand-dossier"), fav = COLLS.Cards.find(c => c.getFlag(MOD, "key") === "hand-favours");
console.log(`dossier ${dossier.cards.size} card(s), favours ${fav.cards.size}; ledger`, JSON.stringify(game.settings.get(MOD, "ledger").evidence), JSON.stringify(game.settings.get(MOD, "ledger").baldrik));
await api.applyPartySize(4);
console.log("korga hp", COLLS.Actor.find(a => a.getFlag(MOD, "key") === "korga").system.attributes.hp.max);
await api.updateContent();
await api.playSceneMusic(COLLS.Scene.find(s => s.getFlag(MOD, "key") === "hammerhall"));
console.log("playing", COLLS.Playlist.contents.flatMap(p => p.sounds.filter(s => s.playing).map(s => s.name)));
console.log("errors", errors);

// --- combined-module checks
const before = Object.fromEntries(["Actor", "Item", "JournalEntry", "Macro", "Scene"].map(t => [t, COLLS[t].size]));
await game.catAndUnkindness.setup();
const after = Object.fromEntries(["Actor", "Item", "JournalEntry", "Macro", "Scene"].map(t => [t, COLLS[t].size]));
console.log("Part I re-run duplicates:", JSON.stringify(before) === JSON.stringify(after) ? "none" : JSON.stringify({ before, after }));
await api.removeAll();
const left = t => COLLS[t].filter(d => d.getFlag(MOD, "part") === "ravenloft").length;
const leftII = t => COLLS[t].filter(d => d.getFlag(MOD, "managed") && d.getFlag(MOD, "part") !== "ravenloft").length;
console.log(`after Remove Module Content: Part I scenes ${left("Scene")}, journals ${left("JournalEntry")}; Part II scenes ${leftII("Scene")}, journals ${leftII("JournalEntry")}`);

const pagesUnique = () => COLLS.JournalEntry.filter(d => d.getFlag(MOD, "part") === "ravenloft").every(j => new Set(j.pages.map(p => p.getFlag(MOD, "sourcePageId"))).size === j.pages.size);
const sampleJ = () => { const j = COLLS.JournalEntry.find(d => d.getFlag(MOD, "part") === "ravenloft"); return j ? `${j.name}: ${j.pages.size} pages, ids ${j.pages.map(p => p.getFlag(MOD, "sourcePageId") ?? JSON.stringify(p.flags)).join("|")}` : "none"; };
console.log("pages unique before upgrade:", pagesUnique(), sampleJ());
// --- upgrade path: Part I documents still flagged by the old separate module
const OLD = "cat-and-unkindness";
const toOld = d => { if (d.flags?.[MOD]?.part === "ravenloft" || d.flags?.[MOD]?.sourcePageId || (d.flags?.[MOD]?.managed && d.parent)) { const f = { ...d.flags[MOD] }; delete f.part; if (f.lastSourceHash) f.lastSourceHash = "old-0.6.1"; if (d.img) d.img = String(d.img).replace("modules/unkindness-saga/assets/ravenloft/", "modules/cat-and-unkindness/assets/"); d.flags[OLD] = f; delete d.flags[MOD]; } };
for (const t of ["Actor", "Item", "JournalEntry", "Macro", "Scene"]) for (const d of COLLS[t].values()) {
  if (d.flags?.[MOD]?.part !== "ravenloft") continue;
  for (const f of ["walls", "lights", "pages", "items"]) for (const e of (d[f]?.values?.() ?? [])) toOld(e);
  toOld(d);
}
const preCount = Object.fromEntries(["Actor", "Item", "JournalEntry", "Macro", "Scene"].map(t => [t, COLLS[t].size]));
const preWalls = COLLS.Scene.contents.reduce((n, s) => n + s.walls.size, 0);
await api.migrateLegacy();
await game.catAndUnkindness.setup();
const postCount = Object.fromEntries(["Actor", "Item", "JournalEntry", "Macro", "Scene"].map(t => [t, COLLS[t].size]));
const postWalls = COLLS.Scene.contents.reduce((n, s) => n + s.walls.size, 0);
const pagesOk = COLLS.JournalEntry.filter(d => d.getFlag(MOD, "part") === "ravenloft").every(j => new Set(j.pages.map(p => p.getFlag(MOD, "sourcePageId"))).size === j.pages.size);
const recov = COLLS.JournalEntry.filter(d => /RECOVERY/.test(d.name)).length + COLLS.Actor.filter(d => /RECOVERY/.test(d.name)).length;
console.log(`upgrade: docs ${JSON.stringify(preCount) === JSON.stringify(postCount) ? "no duplicates" : JSON.stringify({ preCount, postCount })}; walls ${preWalls} -> ${postWalls}; pages unique ${pagesOk}; recovery copies ${recov}`);

const oldPaths = ["Actor", "Item", "JournalEntry", "Scene"].reduce((n, t) => n + COLLS[t].filter(d => String(d.img ?? "").includes("cat-and-unkindness")).length, 0);
const inFolder = COLLS.Scene.filter(d => d.getFlag(MOD, "part") === "ravenloft").every(s => { let f = COLLS.Folder.get(s.folder?.id ?? s.folder); while (f?.folder) f = COLLS.Folder.get(f.folder?.id ?? f.folder) ?? f.folder; return f?.name === "The Cat and the Unkindness"; });
console.log(`forced re-import: images still on old paths ${oldPaths}; Part I scenes under 'The Cat and the Unkindness' folder: ${inFolder}`);
