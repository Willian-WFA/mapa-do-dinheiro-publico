import json, collections, unicodedata

def norm(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()

h = json.load(open('hist_rows.json'))
FAC = h['fac']
rows = {r['label']: r['data'] for r in h['rows']}

def find(prefix):
    for k, v in rows.items():
        if k.strip().startswith(prefix):
            return v
    raise KeyError(prefix)

S = {
    'educ': find('Educação (União)'),
    'saude': find('Saúde (União)'),
    'seg': find('Segurança pública (União)'),
    'assist': find('Assistência social (União)'),
    'bpc': find('dos quais BPC'),
    'bf': find('dos quais Bolsa Família'),
    'inss': find('INSS – benefícios previdenciários'),
    'juros': find('Juros nominais do Governo Central'),
    'pessoal': find('Pessoal de todos os Poderes'),
    'isenc': find('Isenção fiscal a empresas'),
    'subs': find('Subsídios e crédito rural'),
}
POP = find('População total')  # milhões

# infraestrutura: transporte+energia+saneamento+habitação+urbanismo+comunicações (pago + restos a pagar pagos)
INF = {'TRANSPORTE', 'ENERGIA', 'SANEAMENTO', 'HABITACAO', 'URBANISMO', 'COMUNICACOES'}
tm = json.load(open('tes_mensal_func.json'))['func']
infra = {}
for y in range(2008, 2014):
    infra[str(y)] = sum(v for k, v in tm[str(y)].items() if k in INF) / 1e9
fc = json.load(open('func_cache.json'))
acc = collections.defaultdict(float); meses = collections.defaultdict(int)
for f, d in fc.items():
    y = f[:4]; meses[y] += 1
    for k, (p, r) in d.items():
        if norm(k) in INF:
            acc[y] += p + r
for y in sorted(acc):
    if meses[y] == 12:
        infra[y] = acc[y] / 1e9
S['infra'] = infra

series = {k: {y: round(v, 3) for y, v in d.items() if y in FAC} for k, d in S.items()}

GOVS = [
    ['FHC 1', 'Fernando Henrique Cardoso (1º mandato)', 1995, 1998],
    ['FHC 2', 'Fernando Henrique Cardoso (2º mandato)', 1999, 2002],
    ['Lula 1', 'Lula (1º mandato)', 2003, 2006],
    ['Lula 2', 'Lula (2º mandato)', 2007, 2010],
    ['Dilma 1', 'Dilma Rousseff (1º mandato)', 2011, 2014],
    ['Dilma 2', 'Dilma Rousseff (2º mandato, só 2015)', 2015, 2015],
    ['Temer', 'Michel Temer (2017–2018)', 2017, 2018],
    ['Bolsonaro', 'Jair Bolsonaro', 2019, 2022],
    ['Lula 3', 'Lula (3º mandato, 2023–2025)', 2023, 2025],
]

# ---------- sinais: empresas ----------
top = json.load(open('top50.json'))
yrs = sorted(top)
emp = {}
seen = {}
for i, y in enumerate(yrs):
    cur = {t['cnpj']: t for t in top[y]['top']}
    prev = {t['cnpj']: t for t in top[yrs[i - 1]]['top']} if i else {}
    lst = []
    for c, t in cur.items():
        p = prev.get(c)
        flag = None
        if i:
            if c not in seen:
                flag = 'novo'
            elif p is None:
                flag = 'volta'
            elif p['valor'] > 0 and t['valor'] >= 3 * p['valor'] and t['valor'] - p['valor'] >= 1e8:
                flag = 'salto'
        if flag:
            lst.append({'nome': t['nome'], 'cnpj': c, 'cnae': t['cnae'], 'tipo': t['tipo'], 'uf': t.get('uf'),
                        'valor': round(t['valor'] / 1e6, 1), 'prev': round(p['valor'] / 1e6, 1) if p else None, 'flag': flag})
    for c in cur:
        seen[c] = 1
    lst.sort(key=lambda x: -x['valor'])
    emp[y] = {'total': round(top[y]['total'] / 1e9, 2), 'n': top[y]['n'], 'lista': lst[:15], 'q': len(lst)}

# ---------- sinais: órgãos e pessoas ----------
civ = json.load(open('out/civil_acima50k.json'))
jud = json.load(open('out/judic_acima50k.json'))

def orgs(rows, y_ok, key_org, key_person):
    cnt = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        y = r[0]
        if y in y_ok:
            cnt[y][key_org(r)].add(key_person(r))
    return cnt

CIV_Y = set(range(2019, 2027)); JUD_Y = set(range(2019, 2027))
co = orgs(civ, CIV_Y, lambda r: r[5], lambda r: (r[2], r[3]))
jo = orgs(jud, JUD_Y, lambda r: r[1].upper(), lambda r: (r[2],))
org_out = {}
tot = {}
sis = {}
for esf, cnt, ys in (('Executivo (civil)', co, sorted(CIV_Y)), ('Judiciário e MP', jo, sorted(JUD_Y))):
    for y in ys:
        tot.setdefault(str(y), {})[esf] = sum(len(v) for v in cnt[y].values())
        if y - 1 not in cnt:
            continue
        a, b = tot[str(y)][esf], tot[str(y - 1)][esf]
        if not (0.67 <= a / b <= 1.5):
            sis.setdefault(str(y), []).append(esf)
            continue
        for o, ps in cnt[y].items():
            n = len(ps); p = len(cnt[y - 1].get(o, ()))
            if n >= 10 and (p == 0 or n >= 3 * p) and n - p >= 10:
                org_out.setdefault(str(y), []).append({'esfera': esf, 'orgao': o, 'n': n, 'prev': p})
for y in org_out:
    org_out[y].sort(key=lambda x: -(x['n'] - x['prev']))
    org_out[y] = org_out[y][:20]

# pessoas novas na lista acima de 50 mil (primeiro ano em que aparecem)
pessoas = {}
first = {}
for r in sorted(civ, key=lambda r: r[0]):
    if r[0] in CIV_Y:
        first.setdefault(('c', r[2], r[3]), r[0])
for r in sorted(jud, key=lambda r: r[0]):
    if r[0] in JUD_Y:
        first.setdefault(('j', r[2]), r[0])
cand = collections.defaultdict(list)
for r in civ:
    y = r[0]
    if y in CIV_Y and y > 2019 and first.get(('c', r[2], r[3])) == y:
        cand[y].append({'nome': r[2], 'cargo': r[4], 'orgao': r[5], 'esfera': 'Executivo (civil)', 'tipo': r[1],
                        'meses': r[7], 'total': round(r[8]), 'max': round(r[9])})
for r in jud:
    y = r[0]
    if y in JUD_Y and y > 2019 and first.get(('j', r[2])) == y:
        cand[y].append({'nome': r[2], 'cargo': r[3], 'orgao': r[1].upper(), 'esfera': 'Judiciário e MP', 'tipo': '',
                        'meses': r[4], 'total': None, 'max': round(r[5])})
ent = {}
for y, l in cand.items():
    l = [x for x in l if x['esfera'] not in sis.get(str(y), [])]
    l.sort(key=lambda x: -x['max'])
    ent[str(y)] = {'q': len(l), 'top': l[:12]}

out = {'gov': GOVS, 'series': series, 'fac': FAC, 'pop': POP, 'emp': emp, 'org': org_out, 'orgtot': tot, 'pes': ent, 'sis': sis}
open('site/data_presidentes.js', 'w').write('window.PRES=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';')
print({k: sorted(v)[:1] + sorted(v)[-1:] for k, v in series.items()})
print('emp', {y: (v['q']) for y, v in emp.items()})
print('org', {y: len(v) for y, v in org_out.items()}, tot)
print('sis',sis)
print('pes', {y: v['q'] for y, v in ent.items()})
