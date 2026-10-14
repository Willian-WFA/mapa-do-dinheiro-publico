import json
d = json.load(open('out/fre_donos.json'))
g = open('site/data_gestoras.js').read(); G = json.loads(g[g.index('=') + 1:].rstrip().rstrip(';'))
LUC = {'60746948': 'Bradesco', '60872504': 'Itaú Unibanco', '90400888': 'Santander Brasil', '30306294': 'BTG Pactual', '58160789': 'Safra'}
P = json.loads(open('site/data.js').read()[len('window.DATA='):].rstrip().rstrip(';'))
out = {'fac': P['fac'], 'gov': P['gov'], 'emp': []}
for rz, e in d.items():
    e['lucro'] = {y: round(v, 2) for y, v in G['lucro']['anual'].get(LUC.get(rz), {}).items()}
    out['emp'].append(e)
out['emp'].sort(key=lambda e: (not e['banco'], e['nome']))
open('site/data_donos.js', 'w').write('window.DON=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';')
