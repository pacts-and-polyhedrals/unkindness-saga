import sys, json, os, time
sys.path.insert(0, '/home/claude/saga/il/art')
import paintkit as K, il_maps, il_hold, edges
OUT = '/home/claude/saga/il/module/assets/maps'; PREV = '/home/claude/saga/il/art/preview'
os.makedirs(PREV, exist_ok=True)
DATA = '/home/claude/saga/il/src/scenes.json'
data = json.load(open(DATA))
which = sys.argv[1:] or il_maps.ORDER
for key in which:
    t = time.time(); m = il_maps.MAPS[key]()
    K.paint(m, f'{OUT}/{key}.webp', f'{PREV}/{key}.jpg')
    if key == 'pump-bridge':
        edges.ledge_walls(m, gaps=[(13.2,7.2,14.8,9.4),(21.2,10.6,22.8,12.8)])
    if key == 'lower-bridge':
        edges.ledge_walls(m, gaps=[(13.4,5.8,14.6,9.3),(17.4,5.8,18.6,9.3),(13.4,12.7,14.6,16.2),(17.4,12.7,18.6,16.2)])
    e = m.export(); e['lights'] = [K.darken_light(L) for L in e['lights']]
    data[key] = e
    print(key, f'{time.time()-t:.0f}s', 'walls', len(e['walls']), 'doors', sum(1 for w in e['walls'] if w['kind'] in ('door','secret')), 'lights', len(e['lights']), flush=True)
json.dump(data, open(DATA, 'w'))
