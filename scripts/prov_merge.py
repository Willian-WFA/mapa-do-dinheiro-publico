import json, collections
s = open('site/data_salarios.js').read()
d = json.loads(s[s.index('=') + 1:].rstrip().rstrip(';'))
pj = json.load(open('out/prov_judic.json'))
# civil
civ = collections.defaultdict(list)
for l in open('hi_salary_civil.jsonl'):
    r = json.loads(l)
    civ[(r['ano'], r['nome'])].append(r)
miss = 0
for y, L in d['top'].items():
    for r in L:
        c = civ.get((int(y), r[0]), [])
        # a linha de maior bruto do ano para o nome
        if c:
            b = max(c, key=lambda x: x['bruto_total'])
            r += [b['mes'], b.get('origem', ''), round(b['salario'], 2), round(b['bruto_total'], 2)]
        else:
            miss += 1; r += [None, '', None, None]
print('civil sem match', miss)
sen = collections.defaultdict(list)
for l in open('senado_pay.jsonl'):
    r = json.loads(l); sen[(r['ano'], r['nome'])].append(r)
for y, L in d['sen_top'].items():
    for r in L:
        c = sen.get((int(y), r[0]), [])
        if c:
            b = max(c, key=lambda x: x['bruto']); r += [b['mes'], b.get('tipo_folha', '')]
        else:
            r += [None, '']
mj = 0
for y, L in d['jud_top'].items():
    for r in L:
        p = pj.get(f'{r[3]}|{y}|{r[0]}')
        if p:
            r += [p['mes'], p['arq'], p['verba'], p['v'], p['pontual']]
        else:
            mj += 1; r += [None, '', None, None, False]
print('jud sem match', mj)
open('site/data_salarios.js', 'w').write('window.SAL=' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ';')
