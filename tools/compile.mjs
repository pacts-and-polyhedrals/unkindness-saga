
import { compilePack } from '@foundryvtt/foundryvtt-cli';
const packs = ["journals", "actors", "items", "spells", "tables", "macros", "playlists", "cards"];
for (const p of packs) await compilePack('/home/claude/saga/il/build/packs/' + p, '/home/claude/saga/il/module/packs/' + p, { log: false });
console.log('compiled', packs.length);
