import json, pathlib, sys
root=pathlib.Path(__file__).resolve().parents[1]
files=['module.json','data/actors.json','data/items.json','data/journals.json','data/macros.json']
for f in files:
    json.loads((root/f).read_text(encoding='utf-8'))
ids=[]
for f,key in [('data/actors.json','actors'),('data/items.json','items'),('data/journals.json','journals'),('data/macros.json','macros')]:
    for o in json.loads((root/f).read_text(encoding='utf-8'))[key]: ids.append(o['sourceId'])
assert len(ids)==len(set(ids)), 'duplicate sourceId'
print(f'OK: {len(ids)} managed source documents; JSON valid; source IDs unique.')
