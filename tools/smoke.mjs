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
    Object.defineProperty(this, "_embeddedMap", { enumerable: false, value: { Scene: { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Level: "levels" }, JournalEntry: { JournalEntryPage: "pages" }, Playlist: { PlaylistSound: "sounds" }, Cards: { Card: "cards" }, Actor: { Item: "items" } }[type] ?? {} });
    if (type === "Scene") { for (const k of ["walls", "lights", "notes", "tokens", "levels"]) this[k] = new Coll(k); for (const l of data.levels ?? []) { const d = new Doc(l, "Level", this); this.levels.set(d.id, d); } }
    if (type === "JournalEntry") { const ps = new Coll("JournalEntryPage"); for (const p of data.pages ?? []) ps.set(p._id, new Doc(p, "JournalEntryPage", this)); this.pages = ps; }
    if (type === "Playlist") { const ss = new Coll("PlaylistSound"); for (const p of data.sounds ?? []) ss.set(p._id, new Doc(p, "PlaylistSound", this)); this.sounds = ss; }
    if (type === "Cards") { const cs = new Coll("Card"); for (const p of data.cards ?? []) cs.set(p._id, new Doc(p, "Card", this)); this.cards = cs; }
    if (type === "Actor") { this.prototypeToken = data.prototypeToken ?? { width: 1 }; this.items = new Coll("Item"); for (const i of data.items ?? []) this.items.set(i._id ?? rid(), new Doc(i, "Item", this)); }
  }
  getFlag(s, k) { return this.flags?.[s]?.[k]; }
  async update(u) { for (const [k, v] of Object.entries(u)) setProp(this, k, v); log.push(`update ${this.documentName}`); return this; }
  async delete() { COLLS[this.documentName]?.delete(this.id); }
  async updateEmbeddedDocuments(type, ups) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Item: "items", JournalEntryPage: "pages", Level: "levels", PlaylistSound: "sounds", Card: "cards" }; const c = this[map[type]]; for (const u of ups) { const d = c?.get(u._id); const { _id, ...rest } = u; await d?.update(rest); } }
  toObject() { const o = {}; for (const [k, v] of Object.entries(this)) { if (k === "parent" || k === "_source") continue; o[k] = v instanceof Coll ? v.contents.map(c => c.toObject()) : v; } return deep(o); }
  async createEmbeddedDocuments(t, arr) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Level: "levels", Item: "items", JournalEntryPage: "pages" }; const c = this[map[t]] ??= new Coll(t); for (const a of arr) { if (t === "Note" && !a.entryId) throw new Error("note without entry"); const d = new Doc(a, t, this); c.set(d.id, d); } return arr; }
  async deleteEmbeddedDocuments(t, ids) { const map = { Wall: "walls", AmbientLight: "lights", Note: "notes", Token: "tokens", Item: "items" }; for (const i of ids) this[map[t]].delete(i); }
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
  const meta = { packageName: MOD, id: `${MOD}.${dir}` };
  PACKS.set(`${MOD}.${dir}`, { folders, getDocuments: async () => docs, documentName: type, metadata: meta, collection: meta.id,
    getIndex: async () => docs.map(d => ({ _id: d._id ?? d.id, name: d.name, type: d.type })), getDocument: async id => docs.find(d => (d._id ?? d.id) === id) });
}
{ // a stand-in for the dnd5e system's SRD monster compendium (2024 spellings where they differ)
  const inh = JSON.parse(fs.readFileSync(`${ROOT}/module/data/ravenloft/inhabitants.json`, "utf8"));
  const big = { "dire-wolf": 2, nightmare: 2, "ochre-jelly": 2 };
  const docs = Object.entries(inh.monsters).map(([k, names], i) => new Doc({ _id: `mon${i}`, name: names.at(-1), type: "npc", system: { attributes: { hp: { value: 10, max: 10 } } }, prototypeToken: { name: names.at(-1), width: big[k] ?? 1, height: big[k] ?? 1 } }, "Actor"));
  const meta = { packageName: "dnd5e", id: "dnd5e.monsters" };
  PACKS.set("dnd5e.monsters", { documentName: "Actor", metadata: meta, collection: "dnd5e.monsters", getDocuments: async () => docs,
    getIndex: async () => docs.map(d => ({ _id: d._id ?? d.id, name: d.name, type: "npc" })), getDocument: async id => docs.find(d => (d._id ?? d.id) === id) });
}
{ // a stand-in for the dnd5e system's SRD spell compendium: every spell name the spellbooks ask for
  const books = JSON.parse(fs.readFileSync(`${ROOT}/module/data/spellbooks.json`, "utf8"));
  const names = [...new Set(Object.values(books).flatMap(b => b.spells.map(s => s.name)))];
  const docs = names.map((n, i) => new Doc({ _id: `srd${i}`, name: n, type: "spell", system: { level: 1, method: "spell", prepared: 0, activities: {} } }, "Item"));
  const meta = { packageName: "dnd5e", id: "dnd5e.spells" };
  PACKS.set("dnd5e.spells", { documentName: "Item", metadata: meta, collection: "dnd5e.spells", getDocuments: async () => docs,
    getIndex: async () => docs.map(d => ({ _id: d._id ?? d.id, name: d.name, type: "spell" })), getDocument: async id => docs.find(d => (d._id ?? d.id) === id) });
}
const settings = new Map(); const reg = new Map();
globalThis.game = {
  release: { generation: GEN }, version: `${GEN}.350`, ready: true,
  user: { isGM: true, character: null }, modules: new Map([[MOD, { version: "1.0.0" }]]),
  packs: Object.assign(PACKS, { get contents() { return [...PACKS.values()]; } }), settings: { register: (m, k, o) => reg.set(k, o), registerMenu() {}, get: (m, k) => settings.has(k) ? settings.get(k) : deep(reg.get(k)?.default), set: async (m, k, v) => { settings.set(k, v); reg.get(k)?.onChange?.(v); } },
  collections: { get: t => COLLS[t] }, folders: COLLS.Folder, journal: COLLS.JournalEntry, actors: COLLS.Actor, items: COLLS.Item,
  scenes: COLLS.Scene, tables: COLLS.RollTable, macros: COLLS.Macro, playlists: COLLS.Playlist, cards: COLLS.Cards
};
globalThis.Folder = DOC.Folder; globalThis.Scene = DOC.Scene; globalThis.Cards = DOC.Cards;
globalThis.getDocumentClass = t => DOC[t];
globalThis.CONST = { DOCUMENT_OWNERSHIP_LEVELS: { NONE: 0, OBSERVER: 2 }, WALL_SENSE_TYPES: { NONE: 0, LIMITED: 10, NORMAL: 20, PROXIMITY: 30 }, WALL_MOVEMENT_TYPES: { NONE: 0, NORMAL: 20 } };
globalThis.CONFIG = { DND5E: { skills: { per: { label: "Persuasion" } }, abilities: { str: { label: "Strength" } } } };
globalThis.ui = { notifications: { info: (m) => { log.push(m); return { remove() {} }; }, warn: m => errors.push("warn: " + m), error: m => errors.push(m) } };
const hooks = {}; globalThis.Hooks = { once: (h, f) => (hooks[h] ??= []).push(f), on: (h, f) => (hooks[h] ??= []).push(f) };
globalThis.ChatMessage = { create: async d => { log.push("chat"); return d; }, getWhisperRecipients: () => [{ id: "gm" }], getSpeaker: () => ({}) };
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
{ const who = ["Sigrun Lampwright", "Old Kharn", "Sister Yrsa", "Runa Ironfist", "Ludmilla", "Strahd — Phase I", "Orcus —", "Arl —"].map(n => game.actors.find(a => a.name.startsWith(n)));
  console.log("spells:", who.map(a => a ? `${a.name.split(/[ ,—]/)[0]} ${a.items.filter(i => i.type === "spell").length} (${a.system?.attributes?.spellcasting})` : "MISSING").join(" | "));
  const ka = game.actors.find(a => a.name.startsWith("Old Kharn")); console.log("spells: Kharn rune spells", ka.items.filter(i => i.type === "spell" && /Rune|Seal|Hammerfall|Chisel|Echoes|Stoneward/.test(i.name)).length, "| innate uses on Ludmilla's Blight", JSON.stringify(game.actors.find(a => a.name.startsWith("Ludmilla")).items.find(i => i.name === "Blight")?.system?.uses));
  const orc = game.actors.find(a => a.name.startsWith("Orcus —")); console.log("stats: Orcus hp", JSON.stringify(orc.system.attributes.hp), "legact", JSON.stringify(orc.system.resources?.legact), "legendary items", orc.items.filter(i => /Legendary\)/.test(i.name)).length, "| Arl CR", game.actors.find(a => a.name.startsWith("Arl —")).system.details.cr, "| Brynja hp", JSON.stringify(game.actors.find(a => a.name.startsWith("General Brynja")).system.attributes.hp));
  await api.art.spells(); console.log("spells: re-run keeps counts", game.actors.find(a => a.name.startsWith("Sister Yrsa")).items.filter(i => i.type === "spell").length); }
{ const p1 = () => game.scenes.filter(s => String(s.flags?.[MOD]?.sourceId ?? "").startsWith("cu.scene.")).map(s => [s, s.tokens.filter(x => x.flags?.[MOD]?.p1token)]);
  const before = p1(); const court = before.find(([s]) => /Court of the Count/.test(s.name));
  console.log("p1tokens: scenes with creatures", before.filter(([, t]) => t.length).length, "| total", before.reduce((n, [, t]) => n + t.length, 0),
    "| court", court?.[1].map(x => x.name).join(", "), "| all hidden", before.every(([, t]) => t.every(x => x.hidden)), "| level set", before.every(([, t]) => t.every(x => !!x.level || GEN < 14)));
  await api.buildScenes(); const after = p1();
  console.log("p1tokens: after Build All Scenes again", after.reduce((n, [, t]) => n + t.length, 0), "| Part II scenes", game.scenes.filter(s => s.flags?.[MOD]?.key).length);
  const P1 = JSON.parse(fs.readFileSync(`${ROOT}/module/data/ravenloft/scenes.json`, "utf8")).scenes;
  const diffs = P1.map(s => { const sc = game.scenes.find(x => x.flags?.[MOD]?.sourceId === s.sourceId); return sc ? `${sc.walls.size - s.walls.length}/${sc.lights.size - s.lights.length}` : "MISSING"; });
  const p1sc = game.scenes.filter(s => s.flags?.[MOD]?.part === "ravenloft");
  console.log("p1scenes:", p1sc.length, "scenes | wall/light deltas", [...new Set(diffs)].join(","), "| pins", p1sc.reduce((n, s) => n + s.notes.size, 0),
    "| walls on level", GEN < 14 || p1sc.every(s => [...s.walls.values?.() ?? s.walls].every(w => (w.levels?.length ?? w.levels?.size ?? 0) === 1)), "| journal linked", p1sc.filter(s => s.journal).length,
    "| court journal", game.journal.get(p1sc.find(s => /Court/.test(s.name))?.journal)?.name);
  const inhab = game.scenes.contents.flatMap(s => [...s.tokens.values?.() ?? s.tokens]).filter(x => x.flags?.[MOD]?.inhabitant);
  console.log("inhabitants:", inhab.length, "tokens |", game.actors.filter(a => a.flags?.[MOD]?.inhabitant).length, "monster actors imported | all hidden", inhab.every(x => x.hidden),
    "| e.g.", [...new Set(inhab.map(x => x.name))].slice(0, 6).join(", "));
  const chk = await api.art.check({ post: true }); console.log("check:", chk.total, "scenes, incomplete:", JSON.stringify(chk.incomplete));
  // simulate a world where a Part I scene lost its walls, then Build All Scenes repairs it
  const vic = p1sc.find(s => /Main Floor/.test(s.name)); await vic.deleteEmbeddedDocuments("Wall", vic.walls.map(w => w.id));
  const chk2 = await api.art.check({ post: false }); console.log("check after damage:", JSON.stringify(chk2.incomplete));
  { // a server that rejects whole batches and one bad wall: the builder falls back to one at a time and keeps the rest
    const S = P1.find(s => /Rooftops/.test(s.name)); const sc = p1sc.find(s => s.flags[MOD].sourceId === S.sourceId); const orig = sc.createEmbeddedDocuments.bind(sc); let bad = 0;
    sc.createEmbeddedDocuments = async (type, docs, o) => { if (type === "Wall" && docs.length > 1) throw new Error("batch rejected"); if (type === "Wall" && docs[0].c[0] === S.walls[5].c[0] && docs[0].c[1] === S.walls[5].c[1] && !bad++) throw new Error("bad wall"); return orig(type, docs, o); };
    const r = await api.art.p1scene(S); sc.createEmbeddedDocuments = orig; console.log("fallback:", JSON.stringify(r.walls), "of", S.walls.length); }
  await api.buildScenes(); console.log("check after rebuild:", JSON.stringify((await api.art.check({ post: false })).incomplete), "| main floor walls", vic.walls.size); }
{ // DM Control Board
  globalThis.window ??= globalThis; window.prompt ??= () => null; window.confirm ??= () => true;
  api.board.open(); const app = api.board.app; const run = (r, a = "") => app.constructor.DEFAULT_OPTIONS.actions.run.call(app, null, { dataset: { run: r, arg: String(a) } });
  const lens = [];
  for (const t of ["p1", "p2", "tools", "setup"]) { app.tab = t; const h = await app._renderHTML(); lens.push(`${t}:${h.length}${h.includes("Couldn't draw") ? "!ERR" : ""}`); if (process.env.BOARD_HTML) fs.writeFileSync(`/tmp/board-${t}.html`, h); }
  for (const [r, a] of [["stage", "bride-gauntlet"], ["bride", "volenta:destroyed"], ["finn", "sanguine"], ["finn", "self"], ["finn", "gift"], ["phase", 1], ["phase", 2], ["legres", -1], ["heart", "blood"],
    ["pressure", 1], ["arc:orcus", 1], ["res:holyWater", -1], ["prophecy", "damien"], ["restog", "silverShot"], ["coffin", -1], ["rest", "no"], ["flag", ""], ["vallaki", "warning"], ["arl", "sign"],
    ["track:defence", 1], ["evidence", "E1"], ["council:hadrik", -1], ["baldrik", "admitted"], ["hold", "low-lantern"], ["hold", "ember-baths"], ["hold", "mossbeard-remedies"], ["hold", "deep-script"], ["inh:orcus", 1]]) await run(r, a);
  const s = await game.catAndUnkindness.getState(); const L = game.settings.get(MOD, "ledger");
  console.log("board: tabs", lens.join(" "), "| stage", s.stage, "| volenta", s.brides.volenta, "finn", s.brides.finn, "| phase", s.strahdPhase, "LR", s.legendaryResistances, "| blood chain", s.heartChains.blood,
    "| orcus pressure", s.darkPowers.orcus.pressure, "att", s.arcAttention.orcus, "| holy water", s.resources.holyWater, "| prophecy", s.prophecies.damien, "| arl", s.vallaki.arlContract, "| van richten", s.vallaki.vanRichtenWarning);
  console.log("board: defence", L.defence, "accord", L.accord, "| E1", L.evidence.E1, "| hadrik", L.council.hadrik, "| hold", JSON.stringify(L.hold));
  await run("hold", "low-lantern"); console.log("board: after untick accord", game.settings.get(MOD, "ledger").accord, JSON.stringify(game.settings.get(MOD, "ledger").hold));
}
{ const ap = game.actors.find(a => a.name.startsWith("Orcus Grave Apostle")); const st = game.actors.find(a => a.name.startsWith("Strahd — Phase I:"));
  const acts = a => a.items.contents.reduce((n, i) => n + Object.keys(i.system?.activities ?? {}).length, 0);
  console.log("part I stat blocks: apostle items", ap?.items.size, "activities", acts(ap), "| strahd I items", st?.items.size, "activities", acts(st), "legact", st?.system?.resources?.legact?.max, "| actors with <3 items", game.actors.filter(a => a.getFlag(MOD, "part") === "ravenloft" && a.items.size < 3).map(a => a.name));
  await game.catAndUnkindness.setup(); console.log("part I stat blocks after re-run: apostle items", game.actors.find(a => a.name.startsWith("Orcus Grave Apostle")).items.size); }
{ const p1 = game.scenes.filter(s => s.getFlag(MOD, "part") === "ravenloft"); p1[0].padding = 0.05; const fixed = await api.art.padding(); console.log("part I padding: nonzero now", p1.filter(s => s.padding).length, "| fixed", fixed); }
if (GEN >= 14) { // tokens carry a single level id
  const sc = game.scenes.find(s => s.getFlag(MOD, "key") === "lowhearth"); const lid = sc.initialLevel?.id;
  const bad = sc.tokens.filter(t => t.level !== lid).length;
  for (const t of sc.tokens.contents.slice(0, 3)) { t.level = undefined; t._source.level = undefined; }
  console.log("token levels: wrong after build", bad, "| fixed", await api.art.tokens(), "| wrong now", sc.tokens.filter(t => t.level !== lid).length);
}
{ // The Forge without the module's art: images only load from the GitHub repository
  globalThis.Image = class { set src(u) { this._u = u; if (!u) return; setTimeout(() => (u.startsWith("https://raw.githubusercontent.com/") ? this.onload?.() : this.onerror?.()), 0); } get src() { return this._u; } };
  const n = await api.art.repair({ force: true });
  const sc = game.scenes.find(s => s.getFlag(MOD, "key") === "lowhearth");
  const all = JSON.stringify([...COLLS.Scene.contents, ...COLLS.Actor.contents, ...COLLS.Item.contents, ...COLLS.JournalEntry.contents, ...COLLS.Playlist.contents].map(d => d.toObject()));
  const plain = (all.match(/(?<!\/)modules\/unkindness-saga\/assets\//g) ?? []).length;
  const gh = (all.match(/raw\.githubusercontent\.com\/pacts-and-polyhedrals\/unkindness-saga\/v[0-9.]+\/module\/assets\//g) ?? []).length;
  console.log("forge art: updated", n, "| plain paths left", plain, "| github paths", gh, "| base", game.settings.get(MOD, "artBase"), "| lowhearth map", (sc?.initialLevel?.background?.src ?? sc?.background?.src ?? "").slice(0, 70), "| catacombs", (game.scenes.find(s => /Catacombs \(Eledryll/.test(s.name))?.initialLevel?.background?.src ?? "").slice(-40));
  const again = await api.art.repair({ force: true });
  console.log("forge art: second run updates", again);
  globalThis.Image = class { set src(u) { this._u = u; if (u) setTimeout(() => this.onload?.(), 0); } get src() { return this._u; } };
  const back = await api.art.repair({ force: true });
  const all2 = JSON.stringify([...COLLS.Scene.contents, ...COLLS.Actor.contents].map(d => d.toObject()));
  console.log("forge art: back to module folder, updated", back, "| github paths left", (all2.match(/raw\.githubusercontent/g) ?? []).length);
  delete globalThis.Image;
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
