const MODULE_ID = "unkindness-saga";
const VERSION = "2.0.0";
const CURRENT_SCHEMA = 1;
const STATE_KEY = "finaleState";
const SETUP_KEY = "ravenloftVersion";
const INTERNAL = "cuInternal";
const RETIRED_SOURCE_IDS = [{type:"Actor", sourceId:"cu.actor.oathbreaker-consort"}];

const DEFAULT_STATE = {
  stage: "wachter-cellar",
  brides: { anastrasya:"alive", volenta:"alive", ludmilla:"alive", finn:"alive" },
  finnChains: { sanguine:false, self:false, gift:false },
  restAccepted: null,
  strahdPhase: 0,
  legendaryResistances: 4,
  heartChains: { blood:true, stone:true, dominion:true },
  coffinDistance: 5,
  tatyanaAgencyHonoured: false,
  baldrikClues: { keepsake:true, plaque:false, contract:false },
  darkPowers: {
    orcus: { pressure:2, status:"active", disposition:"unset" },
    vampyr: { claim:2, status:"active", disposition:"unset" },
    vecna: { status:"departed", disposition:"distant" }
  },
  allies: { azrathox:"outside-vallaki", pitFiend:"not-free", azrathoxStrain:0, pitFiendStrain:0 },
  prophecies: { damien:false, vesper:false, bunch:false, legna:false, thorgrinn:false },
  arcAttention: { vecna:0, orcus:0, vampyr:0 },
  arcNotes: [],
  wish: {
    required:true,
    impossibleProven:false,
    edictActive:false,
    cast:false,
    source:null,
    wording:"",
    djinnOffered:false,
    djinnOutcome:"watching",
    vecnaOffered:false,
    vecnaDeal:null,
    claimClock:{active:false,power:null,round:0}
  },
  darkPowerReconstitutions: { orcus:0, vampyr:0 },
  vallaki: {
    civilWar:true,
    wachterDead:true,
    sonsDead:true,
    finnEscaped:true,
    sarapheneMet:true,
    strahdLetterOpened:false,
    shreddedDossier:true,
    arlContract:"agreed-not-signed",
    arlFreed:false,
    vanRichtenVisited:false,
    vanRichtenWarning:false,
    inheritanceWarning:false,
    realityMagicWarning:false,
    azrathoxPosition:"outside-vallaki",
    intervention:"none",
    mercyBeforeVictory:false,
    resourceCost:"",
    collapseDaysApprox:3.5
  },
  resources: { holyWater:9, diamonds300:0, diamonds500:0, silverShot:true, fireGiantPotionLegna:true, antiUndeadReagent:0 },
  notes: []
};

Hooks.once("init",()=>{
  game.settings.register(MODULE_ID,STATE_KEY,{name:"Cat and Unkindness Finale State",scope:"world",config:false,type:Object,default:foundry.utils.deepClone(DEFAULT_STATE)});
  game.settings.register(MODULE_ID,SETUP_KEY,{name:"Cat and Unkindness Installed Version",scope:"world",config:false,type:String,default:""});
  game.catAndUnkindness={setup,audit,getState,patchState,dashboard,promptMockery,promptLair,promptBride,promptFinnChain,promptPhase,promptHeart,promptCoffin,promptSunlight,promptStoryFlag,promptDarkPower,promptAlly,promptProphecy,promptArc,promptIntervention,promptPowerEnding,promptWish,promptVecnaDeal,promptReconstitution,promptVallaki,promptStage,promptArl,promptLetter,promptPrep,resetToHandoff,npcAction,openBySourceId};
});

Hooks.once("ready",()=>{
  registerDirtyHooks();
  if(!game.user.isGM) return;
  if(game.system.id!=="dnd5e") return ui.notifications.error("The Cat and the Unkindness requires dnd5e.");
  const core=Number(String(game.version??"0").split(".")[0]); const sys=Number(String(game.system.version??"0").split(".")[0]);
  if(core!==14||sys!==6) ui.notifications.warn(`Cat and Unkindness is tested on Foundry v14 / dnd5e v6. Current: ${game.version} / ${game.system.version}.`,{permanent:true});
  if(game.settings.get(MODULE_ID,SETUP_KEY)!==VERSION) ui.notifications.info("Part I (The Cat and the Unkindness) needs Set Up / Repair: open Game Settings → The Unkindness Saga Manager.",{permanent:true});
});

function registerDirtyHooks(){
 const mark=async(doc,options={})=>{if(options?.[INTERNAL])return; const target=doc?.documentName==="JournalEntryPage"?doc.parent:(doc?.parent?.documentName==="Actor"?doc.parent:doc); if(!target?.getFlag?.(MODULE_ID,"managed")||target.getFlag(MODULE_ID,"part")!=="ravenloft"||target.getFlag(MODULE_ID,"dirty"))return; try{await target.update({[`flags.${MODULE_ID}.dirty`]:true},{[INTERNAL]:true});}catch(_){}};
 for(const hook of ["updateJournalEntry","updateJournalEntryPage","updateActor","updateItem","updateMacro"]) Hooks.on(hook,(d,c,o)=>mark(d,o));
}
async function loadJSON(file){const r=await fetch(`modules/${MODULE_ID}/data/ravenloft/${file}`); if(!r.ok)throw new Error(`Could not load ${file}`); return r.json();}
async function getState(){const s=game.settings.get(MODULE_ID,STATE_KEY)??{}; return foundry.utils.mergeObject(foundry.utils.deepClone(DEFAULT_STATE),s,{inplace:false,insertKeys:true,overwrite:true});}
async function patchState(p){if(!game.user.isGM)throw new Error("GM only."); const s=await getState(); const n=foundry.utils.mergeObject(s,p,{inplace:false,insertKeys:true,overwrite:true}); await game.settings.set(MODULE_ID,STATE_KEY,n); return n;}
const COLLECTIONS={JournalEntry:"journal",Actor:"actors",Item:"items",Macro:"macros",Scene:"scenes"};
function collectionFor(t){return game[COLLECTIONS[t]];} function classFor(t){return CONFIG[t]?.documentClass??globalThis[t];}
function ownership(obs){return {default:obs?CONST.DOCUMENT_OWNERSHIP_LEVELS.OBSERVER:CONST.DOCUMENT_OWNERSHIP_LEVELS.NONE};}
async function ensureFolderPath(type,path){let parent=null;if(!path)return null;for(const name of path.split("/").map(s=>s.trim()).filter(Boolean)){let f=game.folders.find(x=>x.type===type&&x.name===name&&(x.folder?.id??x.folder??null)===(parent?.id??null));if(!f)f=await Folder.create({name,type,folder:parent?.id??null,sorting:"a"},{[INTERNAL]:true});parent=f;}return parent;}
async function recoveryFolder(type){return ensureFolderPath(type,"The Cat and the Unkindness/99 — Recovery Copies");}
function sourceDoc(t,sid){return collectionFor(t)?.find(d=>d.getFlag(MODULE_ID,"sourceId")===sid);} function stripIds(o){if(Array.isArray(o))return o.map(stripIds);if(o&&typeof o==="object"){const n={};for(const[k,v]of Object.entries(o)){if(k==="_id"||k==="id")continue;n[k]=stripIds(v);}return n;}return o;}
async function recover(doc){const folder=await recoveryFolder(doc.documentName);const data=stripIds(doc.toObject());data.name=`${doc.name} — RECOVERY ${new Date().toISOString().slice(0,19).replaceAll(":","-")}`;data.folder=folder?.id??null;data.flags??={};data.flags[MODULE_ID]={managed:false,recoveryOf:doc.getFlag(MODULE_ID,"sourceId")};return classFor(doc.documentName).create(data,{[INTERNAL]:true});}
function mergedSystem(type,subtype,system){const base=foundry.utils.deepClone(game.system?.model?.[type]?.[subtype]??{});return foundry.utils.mergeObject(base,system??{},{inplace:false,insertKeys:true,overwrite:true});}
function flags(src){return {[MODULE_ID]:{sourceId:src.sourceId,managed:true,schemaVersion:CURRENT_SCHEMA,lastSourceHash:src.sourceHash,lastImportedVersion:VERSION,dirty:false,part:"ravenloft",...(src.flags??{})}};}
async function upsertSimple(type,src){const folder=await ensureFolderPath(type,src.folder);let doc=sourceDoc(type,src.sourceId);if(doc&&doc.getFlag(MODULE_ID,"lastSourceHash")===src.sourceHash)return{status:"unchanged",doc};if(doc?.getFlag(MODULE_ID,"dirty"))await recover(doc);const data={name:src.name,folder:folder?.id??null,img:src.img,ownership:ownership(src.ownership==="observer"),flags:flags(src)};if(type==="Actor"){data.type=src.type;if(src.token)data.prototypeToken={texture:{src:src.token},ring:{enabled:false}};data.system=mergedSystem("Actor",src.type,src.system);data.flags[MODULE_ID].actions=src.actions??[];}if(type==="Item"){data.type=src.type;data.system=mergedSystem("Item",src.type,src.system);}if(type==="Macro"){data.type=src.type;data.command=src.command;}if(!doc){doc=await classFor(type).create(data,{[INTERNAL]:true});return{status:"created",doc};}await doc.update(data,{[INTERNAL]:true});return{status:"updated",doc};}
async function reconcileFeatures(actor,src){for(const[i,f]of(src.features??[]).entries()){const sid=`${src.sourceId}.feature.${i+1}`;let item=actor.items.find(x=>x.getFlag(MODULE_ID,"sourceId")===sid);const data={name:f.name,type:"feat",system:mergedSystem("Item","feat",{description:{value:`<section class="cat-unkindness cu-slab cu-blood"><p>${f.description}</p></section>`}}),flags:{[MODULE_ID]:{sourceId:sid,managed:true}}};if(item)await item.update(data,{[INTERNAL]:true});else await actor.createEmbeddedDocuments("Item",[data],{[INTERNAL]:true});}}
async function upsertJournal(src){const folder=await ensureFolderPath("JournalEntry",src.folder);let doc=sourceDoc("JournalEntry",src.sourceId);if(doc&&doc.getFlag(MODULE_ID,"lastSourceHash")===src.sourceHash)return{status:"unchanged",doc};if(doc?.getFlag(MODULE_ID,"dirty"))await recover(doc);const data={name:src.name,folder:folder?.id??null,img:src.img,ownership:ownership(src.ownership==="observer"),flags:flags(src)};if(!doc)doc=await JournalEntry.create(data,{[INTERNAL]:true});else await doc.update(data,{[INTERNAL]:true});for(const p of src.pages??[]){let ep=doc.pages.find(x=>x.getFlag(MODULE_ID,"sourcePageId")===p.sourcePageId);const pd={name:p.name,type:"text",sort:p.sort??0,text:{content:p.html,format:CONST.JOURNAL_ENTRY_PAGE_FORMATS.HTML},flags:{[MODULE_ID]:{sourcePageId:p.sourcePageId,managed:true}}};if(ep)await ep.update(pd,{[INTERNAL]:true});else await doc.createEmbeddedDocuments("JournalEntryPage",[pd],{[INTERNAL]:true});}await doc.update({[`flags.${MODULE_ID}.dirty`]:false},{[INTERNAL]:true});return{status:"updated",doc};}
async function retireManagedSources(){for(const r of RETIRED_SOURCE_IDS){const doc=sourceDoc(r.type,r.sourceId);if(!doc)continue;if(doc.getFlag(MODULE_ID,"dirty"))await recover(doc);await doc.delete({[INTERNAL]:true});}}

function sceneChildren(src){const tag={[MODULE_ID]:{managed:true,part:"ravenloft"}};return{walls:(src.walls??[]).map(w=>({c:w.c,move:w.move,sight:w.sight,light:w.light,sound:w.sound,door:w.door,ds:w.ds,dir:w.dir??0,flags:tag})),lights:(src.lights??[]).map(l=>({...l,flags:tag}))};}
async function setSceneBackground(scene,src){const lvl=scene.initialLevel??scene.levels?.contents?.[0];if(lvl){if(lvl.background?.src!==src)await lvl.update({"background.src":src},{[INTERNAL]:true});return;}if(scene.background?.src!==src)await scene.update({"background.src":src},{[INTERNAL]:true});}
async function upsertScene(src){const folder=await ensureFolderPath("Scene",src.folder);let doc=sourceDoc("Scene",src.sourceId);if(doc&&doc.getFlag(MODULE_ID,"lastSourceHash")===src.sourceHash)return{status:"unchanged",doc};
 const base={name:src.name,folder:folder?.id??null,width:src.width,height:src.height,padding:0.05,backgroundColor:"#050306",grid:{type:CONST.GRID_TYPES.SQUARE,size:src.gridSize,distance:5,units:"ft"},tokenVision:true,environment:{darknessLevel:src.darkness??0.6,globalLight:{enabled:false}},flags:flags(src)};
 const kids=sceneChildren(src);let status="updated";
 if(!doc){status="created";doc=await Scene.create({...base,levels:[{name:"Ground",background:{src:src.img}}],sort:src.sort??0},{[INTERNAL]:true});}
 else{await doc.update(base,{[INTERNAL]:true});const oldW=doc.walls.filter(w=>w.getFlag(MODULE_ID,"managed")).map(w=>w.id);const oldL=doc.lights.filter(l=>l.getFlag(MODULE_ID,"managed")).map(l=>l.id);if(oldW.length)await doc.deleteEmbeddedDocuments("Wall",oldW,{[INTERNAL]:true});if(oldL.length)await doc.deleteEmbeddedDocuments("AmbientLight",oldL,{[INTERNAL]:true});}
 await setSceneBackground(doc,src.img);
 if(kids.walls.length)await doc.createEmbeddedDocuments("Wall",kids.walls,{[INTERNAL]:true});
 if(kids.lights.length)await doc.createEmbeddedDocuments("AmbientLight",kids.lights,{[INTERNAL]:true});
 try{const t=await doc.createThumbnail({img:src.img});if(t?.thumb)await doc.update({thumb:t.thumb},{[INTERNAL]:true});}catch(e){console.warn(MODULE_ID,"thumbnail",src.sourceId,e);}
 return{status,doc};}
async function setup(){if(!game.user.isGM)return ui.notifications.error("GM only.");await retireManagedSources();const[j,a,i,m,sc]=await Promise.all([loadJSON("journals.json"),loadJSON("actors.json"),loadJSON("items.json"),loadJSON("macros.json"),loadJSON("scenes.json")]);const rep={created:0,updated:0,unchanged:0,errors:[]};const run=async(fn,s)=>{try{const x=await fn(s);rep[x.status]=(rep[x.status]??0)+1;if(x.doc?.documentName==="Actor")await reconcileFeatures(x.doc,s);}catch(e){console.error(MODULE_ID,s.sourceId,e);rep.errors.push(`${s.sourceId}: ${e.message}`);}};for(const s of j.journals)await run(upsertJournal,s);for(const s of a.actors)await run(x=>upsertSimple("Actor",x),s);for(const s of i.items)await run(x=>upsertSimple("Item",x),s);for(const s of m.macros)await run(x=>upsertSimple("Macro",x),s);for(const s of sc.scenes)await run(upsertScene,s);await game.settings.set(MODULE_ID,SETUP_KEY,VERSION);ui.notifications.info(`Cat and Unkindness ${VERSION}: ${rep.created} created, ${rep.updated} updated, ${rep.unchanged} unchanged, ${rep.errors.length} errors.`,{permanent:!!rep.errors.length});return rep;}
async function audit(){const files=["journals.json","actors.json","items.json","macros.json","scenes.json"];let expected=[];for(const f of files){const d=await loadJSON(f);expected.push(...Object.values(d)[0].map(x=>x.sourceId));}const all=[...game.journal,...game.actors,...game.items,...game.macros,...game.scenes];return{expected:expected.length,missing:expected.filter(s=>!all.some(d=>d.getFlag?.(MODULE_ID,"sourceId")===s))};}
async function enrich(c){const ed=foundry?.applications?.ux?.TextEditor?.implementation??globalThis.TextEditor;return ed?.enrichHTML?ed.enrichHTML(c,{async:true}):c;}
async function post(title,body,whisper=true){return ChatMessage.create({speaker:ChatMessage.getSpeaker({user:game.user}),content:await enrich(`<section class="cu-chat"><header>${title}</header><div>${body}</div></section>`),whisper:whisper?ChatMessage.getWhisperRecipients("GM").map(u=>u.id):[]});}
async function dashboard(){
 const s=await getState();
 const b=Object.entries(s.brides).map(([k,v])=>`<span class="cu-pill">${k}: ${v}</span>`).join(" ");
 const f=Object.entries(s.finnChains).map(([k,v])=>`<span class="cu-pill ${v?"on":""}">${k}: ${v?"broken":"bound"}</span>`).join(" ");
 const h=Object.entries(s.heartChains).map(([k,v])=>`<span class="cu-pill ${!v?"on":""}">${k}: ${v?"active":"destroyed"}</span>`).join(" ");
 const dp=s.darkPowers??{}, aa=s.arcAttention??{}, al=s.allies??{}, pr=s.prophecies??{}, v=s.vallaki??{}, r=s.resources??{};
 const props=Object.entries(pr).map(([k,v])=>`<span class="cu-pill ${v?"on":""}">${k}: ${v?"fulfilled":"open"}</span>`).join(" ");
 return post("RAVENLOFT FINALE — STATE",`<p><b>CURRENT STAGE:</b> ${s.stage}</p><p><b>Wachter House:</b> Wachter/sons dead ✓ | Finn escaped ✓ | Arl contract <b>${v.arlContract??"unset"}</b> | Arl freed ${v.arlFreed?"✓":"—"} | Strahd letter ${v.strahdLetterOpened?"OPEN":"sealed"}</p><p><b>Next prep:</b> Van Richten ${v.vanRichtenVisited?"visited":"NOT YET"} | Azrathox ${v.azrathoxPosition??al.azrathox??"outside-vallaki"} | Vallaki intervention <b>${v.intervention??"none"}</b></p><p><b>Resources:</b> Holy water ${r.holyWater??9} | 300gp diamonds ${r.diamonds300??0} | 500gp diamonds ${r.diamonds500??0} | anti-undead reagent ${r.antiUndeadReagent??0} | silver shot ${r.silverShot?"✓":"—"} | fire-giant potion (Legna) ${r.fireGiantPotionLegna?"✓":"—"}</p><p><b>Strahd:</b> Phase ${s.strahdPhase} | Legendary Resistances ${s.legendaryResistances} | Coffin Distance ${s.coffinDistance}</p><p><b>Brides/Finn:</b> ${b}</p><p><b>Finn Chains:</b> ${f}</p><p><b>Heart Chains:</b> ${h}</p><p><b>Dark Powers:</b> Orcus Pressure ${dp.orcus?.pressure??2}; Vampyr Claim ${dp.vampyr?.claim??2}; Vecna ${dp.vecna?.status??"departed"}</p><p><b>Allies:</b> Azrathox → ${al.azrathox??"outside-vallaki"}; Arl/Pit Fiend → ${al.pitFiend??"not-free"}</p><p><b>Prophecies:</b> ${props}</p><p><b>Arc Attention:</b> Vecna ${aa.vecna??0} | Orcus ${aa.orcus??0} | Vampyr ${aa.vampyr??0}</p><p><b>Wish:</b> ${s.wish?.edictActive?"EDICT ACTIVE":"not active"} | source ${s.wish?.source??"—"} | impossible proven ${s.wish?.impossibleProven?"yes":"no"}</p><p><b>Tatyana agency:</b> ${s.tatyanaAgencyHonoured?"honoured":"open"} | <b>Strahd rest:</b> ${s.restAccepted===true?"accepted":s.restAccepted===false?"refused":"unset"}</p><p><b>Ironfist:</b> Baldrik keepsake ${s.baldrikClues?.keepsake?"✓":"—"}</p>`,true);
}
const MOCKERY={general:["There you are. I was beginning to think you had mistaken surviving for arriving.","An Unkindness of ravens. You circle death so faithfully.","You have killed me before. Usually you don't remember.","The book told you? How terribly rude."],damien:["How many voices have you collected, Damien? I wonder which one answers when nobody else is listening.","You drank monstrosity rather than die. Do stop pretending we have nothing in common."],vesper:["Hold your little sun higher, Vesper. Ravenloft has swallowed dawn before."],bunch:["You are the one I find genuinely perplexing. Everyone else brings scars. You keep bringing hope."],legna:["Your Queen keeps returning you. Mine never learned to let go either.","Finn is here, you know. You did say you wanted to save him."],thorgrinn:["Your brother mourned you.","What will he call you when he sees you again? Brother? Machine? Miracle?","Your brother left you a box. He expected you to understand the lock."]};
async function promptMockery(){const who=(window.prompt("Target: general / damien / vesper / bunch / legna / thorgrinn","general")||"general").toLowerCase();const a=MOCKERY[who]??MOCKERY.general;const line=a[Math.floor(Math.random()*a.length)];return post("STRAHD",`<blockquote>“${line}”</blockquote>`,false);}
const LAIR=["The House Moves — DC 17 Dexterity or Strahd moves the creature up to 15 feet.","The Curtains Reach — DC 17 Strength or Dexterity or Restrained until an action is used to escape.","Blackout — extinguish all mundane and non-artifact magical light.","The Master's Courtesy — one bride moves half speed without provoking and may end Grappled/Restrained.","The Organ Plays — DC 17 Constitution; 14 thunder + 14 psychic and push 10 feet, half and no push on success.","A Word in the Ear — DC 17 Wisdom; disadvantage on next attack or save. Immunity after first successful save."];
async function promptLair(){const line=LAIR[Math.floor(Math.random()*LAIR.length)];return post("RAVENLOFT LAIR ACTION",`<p>${line}</p>`,false);}
async function promptBride(){const who=(window.prompt("Bride/Finn: anastrasya / volenta / ludmilla / finn","anastrasya")||"").toLowerCase();if(!["anastrasya","volenta","ludmilla","finn"].includes(who))return;const state=(window.prompt("State: alive / mist / destroyed / saved","destroyed")||"").toLowerCase();const s=await getState();const brides={...s.brides,[who]:state};await patchState({brides});return dashboard();}
async function promptFinnChain(){const key=(window.prompt("Finn chain: sanguine / self / gift","sanguine")||"").toLowerCase();if(!["sanguine","self","gift"].includes(key))return;const s=await getState();const finnChains={...s.finnChains,[key]:!s.finnChains[key]};await patchState({finnChains});if(Object.values(finnChains).every(Boolean)){const brides={...s.brides,finn:"saved"};await patchState({brides});}return dashboard();}
async function promptPhase(){const p=Math.max(0,Math.min(3,Number(window.prompt("Strahd phase: 0 / 1 / 2 / 3",String((await getState()).strahdPhase||1)))||0));const s=await getState();let legendary=s.legendaryResistances??4;if(p>(s.strahdPhase??0)&&p>1)legendary=Math.min(4,legendary+1);await patchState({strahdPhase:p,stage:p?`strahd-phase-${p}`:s.stage,legendaryResistances:legendary});return dashboard();}
async function promptHeart(){const key=(window.prompt("Heart Chain: blood / stone / dominion","blood")||"").toLowerCase();if(!["blood","stone","dominion"].includes(key))return;const s=await getState();const heartChains={...s.heartChains,[key]:!s.heartChains[key]};await patchState({heartChains});return dashboard();}
async function promptCoffin(){const s=await getState();const delta=Number(window.prompt("Change coffin Distance by (-2,-1,1,2)","-1"));if(!Number.isFinite(delta))return;await patchState({coffinDistance:Math.max(0,s.coffinDistance+delta)});return dashboard();}
async function promptSunlight(){const token=canvas.tokens?.controlled?.[0];const name=token?.name??"Selected vampire";return post("ARTIFACT SUNLIGHT",`<p><b>${name}</b>: at the start of its turn in artifact sunlight take <b>15 radiant</b>; no regeneration, mist-form escape, or Ravenloft wall-phasing until the beginning of its next turn.</p>`,false);}
async function promptStoryFlag(){
  const key=(window.prompt("Story flag: tatyana / rest / keepsake / contract","tatyana")||"").toLowerCase();
  const s=await getState();
  if(key==="tatyana"){await patchState({tatyanaAgencyHonoured:!s.tatyanaAgencyHonoured});return dashboard();}
  if(key==="rest"){const raw=(window.prompt("Strahd's rest offer: yes / no / unset",s.restAccepted===true?"yes":s.restAccepted===false?"no":"unset")||"unset").toLowerCase();const value=raw==="yes"?true:raw==="no"?false:null;await patchState({restAccepted:value});return dashboard();}
  if(key==="keepsake"||key==="plaque"||key==="contract"){const useKey=key==="plaque"?"keepsake":key;const baldrikClues={...s.baldrikClues,[useKey]:!s.baldrikClues?.[useKey]};await patchState({baldrikClues});return dashboard();}
}

const ORCUS_INTERVENTIONS=[
 "Bone Rain — DC 18 Dexterity; 4d8 piercing/necrotic, half on success.",
 "Denied Death — a corpse, crypt or destroyed undead becomes a 20-foot necrotic hazard until initiative 20 next round.",
 "Soul Hook — target a resurrected creature or soul-coin vessel; DC 18 Charisma or Restrained by a 20 HP hook.",
 "Death Knell — Strahd cannot regenerate until initiative 20 next round. Deliberately benefiting from this may add Orcus Attention.",
 "Infernal Challenge — Orcus collides with the contracted pit fiend. If the fiend is not on Orcus, increase Orcus Pressure by 1.",
 "The Horseman Looks Back — Orcus recognizes Thorgrinn and advances the Black Road prophecy scene."
];
const VAMPYR_INTERVENTIONS=[
 "Blood Tide — a 20-foot zone becomes difficult terrain; DC 18 Constitution on entry or 3d8 necrotic.",
 "Black Sun — non-artifact light fails; artifact sunlight remains as a blade through the dark.",
 "Covenant Hook — attach a tether to Strahd or another vampiric story target; three Hooks threaten a rebind.",
 "Metal Dwarf — Vampyr targets Thorgrinn with First Thirst, drinking soul resonance rather than blood.",
 "Possess the Wound — a destroyed bride's mist or blood becomes a 30 HP Blood Heart unless artifact sunlight prevents it.",
 "Night Without Stars — trigger Legna's Raven prophecy and reveal the hidden Blood Heart if he follows the silent feather."
];
const VECNA_INTERVENTIONS=[
 "A sentence appears in the Tome that was not there before: ‘This is not a creature. It is a rule.’",
 "One character hears: ‘You may keep your secret, or you may keep your life. I am curious which you value.’",
 "An impossible eye appears in a reflection, watches one failed roll, and closes. Offer a bargain only if the player is truly cornered.",
 "Vesper hears: ‘You asked who writes the future. Now ask who edits it.’",
 "Thorgrinn hears: ‘A soul in a coin is still a secret in a box.’",
 "Damien hears the djinn’s bond flare—and beneath it, much farther away, Vecna quietly says: ‘I can do it without begging.’"
];
async function promptDarkPower(){
 const power=(window.prompt("Power: orcus / vampyr","orcus")||"").toLowerCase(); if(!["orcus","vampyr"].includes(power))return;
 const s=await getState(); const darkPowers=foundry.utils.deepClone(s.darkPowers??DEFAULT_STATE.darkPowers); const d=darkPowers[power];
 const op=(window.prompt(power==="orcus"?"Operation: +pressure / -pressure / status":"Operation: +claim / -claim / status",power==="orcus"?"+pressure":"+claim")||"").toLowerCase();
 if(op==="status"){d.status=(window.prompt("Status: active / contained / banished / spared / bargained / withdrawn",d.status||"active")||d.status);}
 else {const delta=op.startsWith("-")?-1:1; const key=power==="orcus"?"pressure":"claim"; d[key]=Math.max(0,Math.min(6,Number(d[key]??2)+delta));}
 await patchState({darkPowers}); return dashboard();
}
async function promptAlly(){
 const ally=(window.prompt("Ally: azrathox / pitfiend","azrathox")||"").toLowerCase(); if(!["azrathox","pitfiend"].includes(ally))return;
 const s=await getState(); if(ally==="pitfiend"&&!s.vallaki?.arlFreed)return ui.notifications.warn("Arl is still trapped beneath Wachter House. Sign and release him first.");
 const target=(window.prompt("Deploy to: orcus / vampyr / ravenloft / unassigned",ally==="pitfiend"?"orcus":"vampyr")||"unassigned").toLowerCase();
 const allies={...s.allies}; if(ally==="pitfiend")allies.pitFiend=target; else allies.azrathox=target; await patchState({allies});
 return post("ALLY DEPLOYMENT",`<p><b>${ally==="pitfiend"?"Arl — Contracted Pit Fiend":"Azrathox"}</b> → <b>${target}</b></p>`,false).then(()=>dashboard());
}
async function promptProphecy(){
 const who=(window.prompt("Prophecy: damien / vesper / bunch / legna / thorgrinn","damien")||"").toLowerCase(); if(!["damien","vesper","bunch","legna","thorgrinn"].includes(who))return;
 const s=await getState(); const prophecies={...s.prophecies,[who]:!s.prophecies?.[who]}; await patchState({prophecies});
 const lines={damien:"The Healer — mercy becomes action.",vesper:"The Diviner — the author behind the truth is revealed.",bunch:"The Traitor — loyalty is chosen instead of sacrificial arithmetic.",legna:"The Raven — the silent wing is followed through the dark.",thorgrinn:"The Horseman — the road and the ending are chosen."};
 await post("MADAM EVA — PROPHECY",`<p><b>${lines[who]}</b></p>`,false); return dashboard();
}
async function promptArc(){
 const power=(window.prompt("Attention: vecna / orcus / vampyr","orcus")||"").toLowerCase(); if(!["vecna","orcus","vampyr"].includes(power))return;
 const delta=Number(window.prompt("Change attention by", "1")); if(!Number.isFinite(delta))return;
 const reason=window.prompt("Reason (optional)","")||""; const s=await getState(); const arcAttention={...s.arcAttention,[power]:Math.max(0,Number(s.arcAttention?.[power]??0)+delta)}; const arcNotes=[...(s.arcNotes??[])]; if(reason)arcNotes.push(`${power} ${delta>=0?"+":""}${delta}: ${reason}`); await patchState({arcAttention,arcNotes});
 const high=Math.max(...Object.values(arcAttention)); const leaders=Object.entries(arcAttention).filter(([,v])=>v===high).map(([k])=>k); await post("DARK POWER ATTENTION",`<p>${power}: ${arcAttention[power]}</p><p>Current leader${leaders.length>1?"s":""}: <b>${leaders.join(" + ")}</b></p>`,true); return dashboard();
}
async function promptIntervention(){
 const power=(window.prompt("Intervention: orcus / vampyr / vecna","orcus")||"").toLowerCase(); if(!["orcus","vampyr","vecna"].includes(power))return; const list=power==="vampyr"?VAMPYR_INTERVENTIONS:power==="vecna"?VECNA_INTERVENTIONS:ORCUS_INTERVENTIONS; const line=list[Math.floor(Math.random()*list.length)]; return post(`${power.toUpperCase()} — INTERVENTION`,`<p>${line}</p>`,false);
}
async function promptPowerEnding(){
 const power=(window.prompt("Power: orcus / vampyr","orcus")||"").toLowerCase(); if(!["orcus","vampyr"].includes(power))return;
 const s=await getState();
 if(!s.wish?.edictActive){
   await post("THE DARK POWER DOES NOT END",`<p><b>${power.toUpperCase()}</b> cannot be given a final banish/spare/bargain result while the old metaphysical rule still exists.</p><p>Damage can break the manifestation. Only <b>Wish</b> can make the break final. Trigger <b>Dark Power — Reconstitution</b> or <b>Final Wish — Crisis / Cast</b>.</p>`,false);
   return dashboard();
 }
 const choice=(window.prompt("Ending: banish / spare / bargain","banish")||"banish").toLowerCase(); if(!["banish","spare","bargain"].includes(choice))return;
 const darkPowers=foundry.utils.deepClone(s.darkPowers??DEFAULT_STATE.darkPowers); const arcAttention={...s.arcAttention};
 const cfg={banish:{status:"banished",disposition:"vengeful",add:2},spare:{status:"withdrawn",disposition:power==="orcus"?"indebted/curious":"obsessed",add:1},bargain:{status:"bargained",disposition:"claimant",add:3}}[choice];
 darkPowers[power].status=cfg.status; darkPowers[power].disposition=cfg.disposition; arcAttention[power]=Number(arcAttention[power]??0)+cfg.add; await patchState({darkPowers,arcAttention});
 await post("DARK POWER — FINAL CHOICE",`<p><b>${power.toUpperCase()}</b>: ${choice}. Future disposition: <b>${cfg.disposition}</b>. Attention +${cfg.add}.</p>`,false); return dashboard();
}
async function promptReconstitution(){
 const power=(window.prompt("Dark Power reduced to 0: orcus / vampyr","orcus")||"").toLowerCase(); if(!["orcus","vampyr"].includes(power))return;
 const s=await getState();
 if(s.wish?.edictActive){
   await post("THE EDICT HOLDS",`<p><b>${power.toUpperCase()}</b> reaches 0 HP—and this time reality does not put it back.</p><p>The manifestation is now eligible for <b>Banish / Spare / Bargain</b>.</p>`,false);
   return dashboard();
 }
 const rec={...(s.darkPowerReconstitutions??{orcus:0,vampyr:0})}; rec[power]=Number(rec[power]??0)+1;
 const darkPowers=foundry.utils.deepClone(s.darkPowers??DEFAULT_STATE.darkPowers);
 const key=power==="orcus"?"pressure":"claim"; darkPowers[power][key]=Math.min(6,Number(darkPowers[power][key]??2)+1);
 const wish=foundry.utils.deepClone(s.wish??DEFAULT_STATE.wish); wish.impossibleProven=true; wish.djinnOffered=true; wish.vecnaOffered=true;
 await patchState({darkPowerReconstitutions:rec,darkPowers,wish});
 const hp=power==="orcus"?115:103;
 await post("THE DARK POWER REASSERTS ITSELF",`<p>The ${power.toUpperCase()} manifestation reaches 0 HP.</p><p>For one heartbeat, it is gone.</p><p>Then it <b>re-forms at approximately ${hp} HP</b>. This is not healing. Barovia is reasserting a Dark Power that still has permission to exist here.</p><p><b>${power==="orcus"?"Orcus Pressure":"Vampyr Claim"} +1.</b></p><p>The table now knows the truth: <b>ordinary victory is impossible until Wish changes the law.</b></p>`,false);
 return dashboard();
}

const VECNA_DEALS={
 damien:{line:"You have already become a monster once to save them. Why become precious now?",price:"Give Vecna the memory of why Damien first chose monstrosity to save the others."},
 vesper:{line:"You were told to ask who writes the future. You looked. I noticed.",price:"Accept the Whispered Eye whenever Vesper looks beyond written fate."},
 bunch:{line:"Loyalty is simply a secret you have decided not to sell. Shall we test the price?",price:"Give Vecna one true secret Bunch has protected out of loyalty."},
 legna:{line:"Your Queen collects endings. I collect what endings conceal.",price:"Give Vecna the first true name or title by which the Raven Queen recognized Legna."},
 thorgrinn:{line:"A soul in a coin is still a secret in a box. I know something of boxes.",price:"Allow Vecna to read the construction and inscriptions of Thorgrinn's soul coin."}
};
async function promptVecnaDeal(){
 const who=(window.prompt("Vecna targets: damien / vesper / bunch / legna / thorgrinn","vesper")||"").toLowerCase(); if(!VECNA_DEALS[who])return;
 const kind=(window.prompt("Deal: minor / wish / refuse","minor")||"minor").toLowerCase(); if(!["minor","wish","refuse"].includes(kind))return;
 const cfg=VECNA_DEALS[who]; const s=await getState(); const wish=foundry.utils.deepClone(s.wish??DEFAULT_STATE.wish); const arcAttention={...s.arcAttention}; wish.vecnaOffered=true;
 if(kind==="refuse"){
   const fascinates=(window.prompt("Does the refusal itself increase Vecna Attention? yes / no","no")||"no").toLowerCase()==="yes";
   if(fascinates)arcAttention.vecna=Number(arcAttention.vecna??0)+1;
   await patchState({wish,arcAttention}); await post("VECNA — REFUSED",`<blockquote>“${cfg.line}”</blockquote><p>The offer is refused. Vecna does not force it.</p>`,false); return dashboard();
 }
 const benefit=kind==="wish"?"The Borrowed Ending — one Wish-equivalent intervention.":(window.prompt("Minor benefit: Refuse Death / Unwritten Step / Remembered Power / See the Author","Refuse Death")||"Refuse Death");
 const price=(window.prompt("Price (edit if desired)",cfg.price)||cfg.price);
 wish.vecnaDeal={target:who,kind,benefit,price,accepted:true}; arcAttention.vecna=Number(arcAttention.vecna??0)+1;
 await patchState({wish,arcAttention});
 await post("VECNA — A BARGAIN IS ACCEPTED",`<blockquote>“${cfg.line}”</blockquote><p><b>Benefit:</b> ${benefit}</p><p><b>Price:</b> ${price}</p><p><b>Vecna Attention +1.</b>${kind==="wish"?" The Wish itself adds a further +2 when cast.":""}</p>`,false); return dashboard();
}

async function promptWish(){
 const op=(window.prompt("Final Wish: crisis / djinn / vecna / cast / claim / reset","crisis")||"").toLowerCase();
 const s=await getState(); const wish=foundry.utils.deepClone(s.wish??DEFAULT_STATE.wish); const arcAttention={...s.arcAttention};
 if(op==="crisis"){
   wish.impossibleProven=true; wish.djinnOffered=true; wish.vecnaOffered=true; await patchState({wish});
   await post("THE IMPOSSIBLE MOMENT",`<p>Damage has stopped being a solution. A Dark Power is reasserting itself or reaching for Strahd's ending.</p><p>Damien feels the old djinn bond flare. Somewhere impossibly far away, Vecna notices the same problem.</p><p><b>Two routes to Wish are now available.</b></p>`,false); return dashboard();
 }
 if(op==="djinn"){
   wish.djinnOffered=true; await patchState({wish});
   await post("DAMIEN'S DJINN — ONE MORE",`<blockquote>“No. Absolutely not. I already paid that debt.<br><br>…Unfortunately, if that thing inherits this place, I suspect technicalities will cease to matter.<br><br>One. More. Wish. Then we are finished.”</blockquote><p>The djinn offers one final Wish only because the alternative threatens its own survival. If used, it survives, loses the ability to grant another Wish through this bond, and regards the extraordinary debt as settled.</p>`,false); return dashboard();
 }
 if(op==="vecna"){
   wish.vecnaOffered=true; await patchState({wish});
   await post("VECNA — THE BORROWED ENDING",`<blockquote>“This is not a creature you can kill. It is a sentence reality continues to repeat.<br><br>I can give you another ending.”</blockquote><p>Use <b>Vecna — Offer Bargain</b> to set the target and explicit price.</p>`,false); return dashboard();
 }
 if(op==="claim"){
   const power=(window.prompt("Claiming power: orcus / vampyr",wish.claimClock?.power??"vampyr")||"").toLowerCase(); if(!["orcus","vampyr"].includes(power))return;
   const round=Number(window.prompt("Claim round: 0=off, 1, 2, or 3",String(wish.claimClock?.round??1))); wish.claimClock={active:round>0,power:round>0?power:null,round:Math.max(0,Math.min(3,round||0))}; await patchState({wish});
   if(round>0)await post("STRAHD'S ENDING IS BEING CLAIMED",`<p><b>${power.toUpperCase()}</b> Claim Clock: <b>${round}/3</b>.</p><p>At 3 without Wish, Strahd dies but Barovia gains a new supernatural anchor instead of freedom.</p>`,false); return dashboard();
 }
 if(op==="reset"){
   const next=foundry.utils.deepClone(DEFAULT_STATE.wish); await patchState({wish:next}); return dashboard();
 }
 if(op==="cast"){
   const source=(window.prompt("Wish source: djinn / vecna / other",wish.vecnaDeal?.kind==="wish"?"vecna":"djinn")||"").toLowerCase(); if(!["djinn","vecna","other"].includes(source))return;
   if(source==="vecna" && wish.vecnaDeal?.kind!=="wish"){
     const ok=window.confirm("No accepted Vecna Wish bargain is recorded. Cast through Vecna anyway and record an unspecified price?"); if(!ok)return; wish.vecnaDeal={target:"unspecified",kind:"wish",benefit:"Borrowed Ending",price:"GM and player must define the explicit price",accepted:true}; arcAttention.vecna=Number(arcAttention.vecna??0)+1;
   }
   const defaultWording="I wish that, until Barovia passes from existence, no Dark Power released from the Amber Temple may anchor itself here, inherit Strahd's prison, or return from destruction within this domain.";
   const wording=window.prompt("Wish wording",defaultWording)||defaultWording;
   wish.cast=true; wish.edictActive=true; wish.source=source; wish.wording=wording; wish.claimClock={active:false,power:null,round:0};
   if(source==="djinn")wish.djinnOutcome="survived-free-diminished";
   if(source==="vecna")arcAttention.vecna=Number(arcAttention.vecna??0)+2;
   await patchState({wish,arcAttention});
   await post("WISH — THE EDICT OF FINALITY",`<blockquote>“${wording}”</blockquote><p>Reality changes.</p><ul><li>Orcus and Vampyr lose Dark Power Reconstitution.</li><li>Destroyed Grave Horns and Blood Hearts stay destroyed.</li><li>No Dark Power can inherit Strahd's prison through his death.</li><li>At 0 HP a manifestation can now receive a final Banish / Spare / Bargain result.</li></ul><p><b>Source:</b> ${source}.${source==="vecna"?" Vecna Attention +2 for using the Borrowed Ending.":source==="djinn"?" The djinn survives, but this bond cannot grant another Wish.":""}</p>`,false); return dashboard();
 }
}


async function promptVallaki(){
 const op=(window.prompt("Vallaki: warning / vampyr / orcus / evacuate / both / leave / reset","warning")||"").toLowerCase();
 const s=await getState(); const vallaki=foundry.utils.deepClone(s.vallaki??DEFAULT_STATE.vallaki); const darkPowers=foundry.utils.deepClone(s.darkPowers??DEFAULT_STATE.darkPowers);
 if(op==="warning"){
   vallaki.vanRichtenVisited=true; vallaki.vanRichtenWarning=true; vallaki.inheritanceWarning=true; vallaki.realityMagicWarning=true; const resources={...(s.resources??DEFAULT_STATE.resources)}; if((resources.diamonds300??0)===0){resources.diamonds300=3;resources.diamonds500=1;resources.antiUndeadReagent=2;} await patchState({vallaki,resources,stage:"van-richten-briefing"});
   await post("VAN RICHTEN — THE LOCKS ARE OPEN",`<blockquote>“You broke the locks. I am not telling you that was wrong. But locks do not distinguish between Strahd and the things imprisoned beside him.”</blockquote><p><b>Do not let Orcus or Vampyr own Strahd's final heartbeat.</b> If a Dark Power is destroyed and reality simply puts it back, Van Richten suspects magic on the scale of <b>Wish</b> may be required to revoke its claim.</p>`,false); return dashboard();
 }
 if(op==="reset"){vallaki.intervention="none";vallaki.mercyBeforeVictory=false;vallaki.resourceCost="";await patchState({vallaki});return dashboard();}
 if(op==="leave"){vallaki.intervention="leave";await patchState({vallaki});await post("VALLAKI — PRESERVE STRENGTH",`<p>The Unkindness leaves the civil war unresolved and preserves its resources for Ravenloft. No Pressure / Claim change.</p>`,false);return dashboard();}
 if(op==="evacuate"){vallaki.intervention="evacuate";vallaki.mercyBeforeVictory=true;await patchState({vallaki});await post("VALLAKI — MERCY BEFORE VICTORY",`<p>The Unkindness chooses civilians over strategic advantage. No Pressure / Claim change. Mark <b>Mercy Before Victory</b>; it can support Damien's Healer prophecy when the final heartbeat choice arrives.</p>`,false);return dashboard();}
 if(op==="vampyr"){vallaki.intervention="break-vampyr-rite";darkPowers.vampyr.claim=Math.max(0,Number(darkPowers.vampyr.claim??2)-1);darkPowers.orcus.pressure=Math.min(6,Number(darkPowers.orcus.pressure??2)+1);await patchState({vallaki,darkPowers});await post("VALLAKI — BLOOD RITE BROKEN",`<p>Vampyr Claim −1. Orcus Pressure +1 as the grave cult exploits the opening.</p>`,false);return dashboard();}
 if(op==="orcus"){vallaki.intervention="break-orcus-reliquary";darkPowers.orcus.pressure=Math.max(0,Number(darkPowers.orcus.pressure??2)-1);darkPowers.vampyr.claim=Math.min(6,Number(darkPowers.vampyr.claim??2)+1);await patchState({vallaki,darkPowers});await post("VALLAKI — GRAVE RELIQUARY DESTROYED",`<p>Orcus Pressure −1. Vampyr Claim +1 as the blood cult exploits the opening.</p>`,false);return dashboard();}
 if(op==="both"){const cost=window.prompt("Record the real resource cost paid to strike both rituals (spell slots, consumables, injury, exhaustion, etc.)","significant resources")||"significant resources";vallaki.intervention="strike-both";vallaki.resourceCost=cost;darkPowers.orcus.pressure=Math.max(0,Number(darkPowers.orcus.pressure??2)-1);darkPowers.vampyr.claim=Math.max(0,Number(darkPowers.vampyr.claim??2)-1);await patchState({vallaki,darkPowers});await post("VALLAKI — BOTH RITUALS BROKEN",`<p>Orcus Pressure −1. Vampyr Claim −1.</p><p><b>Cost recorded:</b> ${cost}</p>`,false);return dashboard();}
}


async function resetToHandoff(){
 if(!game.user.isGM)throw new Error("GM only.");
 if(!window.confirm("Reset finale state to the exact Nov 8 Wachter House cliffhanger? This resets finale tracking but does not delete world documents."))return;
 const next=foundry.utils.deepClone(DEFAULT_STATE);
 await game.settings.set(MODULE_ID,STATE_KEY,next);
 await post("FINALE STATE RESET",`<p>State restored to the Nov 8 cliffhanger: Wachter House cellar, Arl terms agreed but unsigned/unreleased, Strahd letter sealed, Van Richten unvisited, Azrathox outside Vallaki, 9 holy waters, and no finale prophecies/Wish outcomes resolved yet.</p>`,false);
 return dashboard();
}

const STAGES=["wachter-cellar","arl-released","van-richten-route","van-richten-briefing","vallaki-exit","azrathox-rendezvous","war-of-broken-gods","bride-gauntlet","finn-tatyana","strahd-phase-1","strahd-phase-2","wish-crisis","strahd-phase-3","coffin-chase","barovia-collapse","campaign-ended"];
async function promptStage(){const s=await getState();const val=window.prompt(`Stage:\n${STAGES.join("\n")}`,s.stage??STAGES[0]);if(!val||!STAGES.includes(val))return;await patchState({stage:val});return dashboard();}
async function promptArl(){
 const op=(window.prompt("Arl: terms / sign / free / breach / reset","terms")||"").toLowerCase(); const s=await getState(); const vallaki=foundry.utils.deepClone(s.vallaki??DEFAULT_STATE.vallaki); const allies={...s.allies};
 if(op==="terms")return post("ARL — AGREED TERMS",`<ol><li>Free Arl from the circle and Wachter control.</li><li>Mutual non-harm during the Ravenloft undertaking.</li><li>Arl materially assists against Ravenloft/Strahd.</li><li>No future service, souls or unspecified favours.</li><li>Truthful recognition of Arl's assistance if he materially aids Strahd's defeat.</li></ol>`,false);
 if(op==="sign"){vallaki.arlContract="signed";await patchState({vallaki});await post("INFERNAL CONTRACT — SIGNED",`<p>The agreed terms are now binding. Arl is still inside the circle until someone deliberately releases him.</p>`,false);return dashboard();}
 if(op==="free"){if(vallaki.arlContract!=="signed"&&!window.confirm("No signed contract is recorded. Release Arl anyway?"))return;vallaki.arlFreed=true;vallaki.arlContract=vallaki.arlContract==="signed"?"signed-and-active":"released-without-recorded-signature";allies.pitFiend="ravenloft";await patchState({vallaki,allies,stage:"van-richten-route"});await post("ARL — RELEASED",`<p>The summoning circle burns out from the inside. Arl proceeds toward Castle Ravenloft to fulfil the bargain.</p><p>When Orcus manifests, his natural priority becomes <b>Orcus</b>.</p>`,false);return dashboard();}
 if(op==="breach"){vallaki.arlContract="breached";await patchState({vallaki});await post("ARL CONTRACT — BREACH",`<p>A deliberate breach has occurred. Resolve the exact consequence from the wording actually signed; do not invent a soul-forfeit that was never agreed.</p>`,false);return dashboard();}
 if(op==="reset"){vallaki.arlContract="agreed-not-signed";vallaki.arlFreed=false;allies.pitFiend="not-free";await patchState({vallaki,allies,stage:"wachter-cellar"});return dashboard();}
}
async function promptLetter(){const op=(window.prompt("Strahd letter: open / show / reset","open")||"").toLowerCase();const s=await getState();const vallaki=foundry.utils.deepClone(s.vallaki??DEFAULT_STATE.vallaki);if(op==="reset"){vallaki.strahdLetterOpened=false;await patchState({vallaki});return dashboard();}if(op==="show"&&!vallaki.strahdLetterOpened)return ui.notifications.warn("The letter is still sealed.");if(op==="open")vallaki.strahdLetterOpened=true;await patchState({vallaki});return post("STRAHD'S INVITATION",`<blockquote>To the Unkindness,<br><br>You have broken my temple, murdered those I named family, stolen the dead from their endings, and convinced yourselves that this constitutes victory.<br><br>I will indulge the misunderstanding once more.<br><br>The gates of Ravenloft stand open. Enter as guests, and you may yet receive the courtesy you refused before. Enter as prey, and the castle shall entertain itself.<br><br>Finn has returned to me. Tatyana remains under my protection. My household is divided, my servants frightened, and the dead beneath my floors have begun whispering names that even I did not invite.<br><br>You wanted an ending.<br><br>Come before lesser things decide it for us.<br><br><b>— Strahd von Zarovich</b></blockquote>`,false).then(()=>dashboard());}
async function promptPrep(){const op=(window.prompt("Preparation: holywater / diamonds / reagent / azrathox / summary","summary")||"").toLowerCase();const s=await getState();const resources={...(s.resources??DEFAULT_STATE.resources)},vallaki=foundry.utils.deepClone(s.vallaki??DEFAULT_STATE.vallaki),allies={...s.allies};if(op==="holywater"){resources.holyWater=Math.max(0,Number(window.prompt("Holy water flasks",String(resources.holyWater??9)))||0);}else if(op==="diamonds"){resources.diamonds300=Math.max(0,Number(window.prompt("300gp diamonds",String(resources.diamonds300??0)))||0);resources.diamonds500=Math.max(0,Number(window.prompt("500gp diamonds",String(resources.diamonds500??0)))||0);}else if(op==="reagent"){resources.antiUndeadReagent=Math.max(0,Number(window.prompt("Anti-undead reagent doses",String(resources.antiUndeadReagent??0)))||0);}else if(op==="azrathox"){const p=window.prompt("Azrathox position: outside-vallaki / with-party / deployed","outside-vallaki")||"outside-vallaki";vallaki.azrathoxPosition=p;allies.azrathox=p;}await patchState({resources,vallaki,allies});return dashboard();}

function critFormula(f){return String(f).replace(/(\d+)d(\d+)/gi,(m,n,d)=>`${Number(n)*2}d${d}`);}
async function npcAction(){const token=canvas.tokens?.controlled?.[0];const actor=token?.actor;if(!actor)return ui.notifications.warn("Select a Cat and Unkindness actor token.");const actions=actor.getFlag(MODULE_ID,"actions")??[];if(!actions.length)return ui.notifications.warn("No source actions on this actor.");const idx=Number(window.prompt(actions.map((a,i)=>`${i+1}. ${a.name}`).join("\n"),"1"))-1;const a=actions[idx];if(!a)return;if(a.type==="utility")return post(`${actor.name} — ${a.name}`,`<p>${a.description}</p>`,false);if(a.type==="save")return post(`${actor.name} — ${a.name}`,`<p>${a.description??""}</p><p>[[/save ${a.ability} dc=${a.dc}]]</p>${a.damage?`<p>Damage: <b>${a.damage} ${a.damageType??""}</b></p>`:""}`,false);const rows=[];for(let i=0;i<Number(a.attacks??1);i++){const r=await(new Roll(`1d20 + ${Number(a.bonus??0)}`)).evaluate();const nat=Number(r.dice?.[0]?.total??0);const d=await(new Roll(nat===20?critFormula(a.damage):a.damage)).evaluate();rows.push(`<li>Attack ${i+1}: <b>${r.total}</b>${nat===20?" critical":""}; damage <b>${d.total} ${a.damageType??""}</b></li>`);}return post(`${actor.name} — ${a.name}`,`<ul>${rows.join("")}</ul><p>${a.description??""}</p>`,false);}
async function openBySourceId(sid){const d=[...game.journal,...game.actors,...game.items,...game.macros,...game.scenes].find(x=>x.getFlag?.(MODULE_ID,"sourceId")===sid);if(!d)return ui.notifications.warn(`No managed document ${sid}.`);return d.sheet.render(true);}
