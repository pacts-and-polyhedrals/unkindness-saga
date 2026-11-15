// The Cat and the Unkindness: artwork refresh for GM-managed world Actors/Items/Journals and placed tokens.
// Safe to run repeatedly. Only touches known module source IDs (or exact named scene tokens linked to them).
const MODULE_ID = 'unkindness-saga';
const INTERNAL = 'cuInternal';
const FILE_PATH = `modules/${MODULE_ID}/assets/ravenloft/art/art-map.json`;
export async function applyArtToWorld({includeAllScenes=true}={}) {
  if(!game.user?.isGM) throw new Error('GM only: artwork refresh');
  const res=await fetch(FILE_PATH,{cache:'no-store'});
  if(!res.ok) throw new Error('Artwork mapping not installed: '+FILE_PATH);
  const data=await res.json();
  const summary={actors:0,items:0,journals:0,tokens:0,scenes:0,errors:[]};
  const sourceId=(d)=>d.getFlag?.(MODULE_ID,'sourceId')??null;
  const srcToActor=new Map();
  const actorImageById=new Map();
  for(const a of game.actors.contents){
    const sid=sourceId(a), image=data.actors?.[sid];
    if(!image)continue;
    srcToActor.set(sid,a);
    actorImageById.set(a.id,image.token);
    const update={};
    if(a.img!==image.portrait)update.img=image.portrait;
    if(a.prototypeToken?.texture?.src!==image.token)update['prototypeToken.texture.src']=image.token;
    if(Object.keys(update).length){try{await a.update(update,{[INTERNAL]:true});summary.actors++;}catch(e){summary.errors.push('Actor '+a.name+': '+e.message);}}
  }
  for(const it of game.items.contents){
    const p=data.items?.[sourceId(it)];
    if(p&&it.img!==p){try{await it.update({img:p},{[INTERNAL]:true});summary.items++;}catch(e){summary.errors.push('Item '+it.name+': '+e.message);}}
  }
  for(const j of game.journal.contents){
    const p=data.journals?.[sourceId(j)];
    if(p&&j.img!==p){try{await j.update({img:p},{[INTERNAL]:true});summary.journals++;}catch(e){summary.errors.push('Journal '+j.name+': '+e.message);}}
  }
  // Update tokens on existing scenes, not just new prototype tokens.
  const scenes=includeAllScenes?game.scenes.contents:[canvas.scene].filter(Boolean);
  for(const scene of scenes){
    const changes=[];
    for(const t of scene.tokens.contents){
      let p=actorImageById.get(t.actorId);
      // v14 scene-local module tokens may be unlinked; match only exact known module actor names.
      if(!p){
        const tokenSourceId=t.getFlag?.(MODULE_ID,'actorSourceId')??t.getFlag?.(MODULE_ID,'sourceActorId');
        p=data.actors?.[tokenSourceId]?.token;
      }
      if(!p||t.texture?.src===p)continue;
      changes.push({_id:t.id,'texture.src':p});
    }
    if(!changes.length)continue;
    try{await scene.updateEmbeddedDocuments('Token',changes);summary.tokens+=changes.length;summary.scenes++;}
    catch(e){summary.errors.push('Scene '+scene.name+': '+e.message);}
  }
  console.info('Cat and Unkindness: artwork refresh',summary);
  ui.notifications.info(`Ravenloft art refreshed: ${summary.actors} actors, ${summary.items} items, ${summary.journals} journals, ${summary.tokens} scene tokens.${summary.errors.length?' '+summary.errors.length+' errors.':''}`);
  return summary;
}
