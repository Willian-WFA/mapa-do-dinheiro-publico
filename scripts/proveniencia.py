import json, csv, io, zipfile, os, collections
csv.field_size_limit(10**7)
D = '/media/hitsuzen/Novo volume/money/dados_portal/judiciario'
rows = json.load(open('out/judic_acima50k.json'))  # [ano, orgao, nome, cargo, meses, maxbruto, maxsal, maxrem]
by = collections.defaultdict(list)
for r in rows:
    by[r[0]].append(r)
target = set()
for a, l in by.items():
    l.sort(key=lambda r: -r[5])
    for r in l[:500]:
        target.add((r[1], r[0], r[2]))
print('alvos', len(target))
best = {}
for line in open('judic_hi.jsonl'):
    o, a, m, n, f, loc, sal, ben, des, rem = json.loads(line)
    k = (o, a, n)
    if k in target:
        br = sal + ben
        if k not in best or br > best[k][0]:
            best[k] = (br, m)
print('com mes', len(best))
byzip = collections.defaultdict(list)
for (o, a, n), (br, m) in best.items():
    byzip[(o, a, m)].append((n, br))
def num(s):
    s = (s or '').strip()
    try: return float(s.replace('.', '').replace(',', '.')) if ',' in s else float(s)
    except ValueError: return 0.0
out = {}
for (o, a, m), lst in byzip.items():
    p = f'{D}/{o}/{o}-{a}-{m}.zip'
    names = {n for n, _ in lst}
    try:
        z = zipfile.ZipFile(p)
        ids = {}
        with z.open('contracheque.csv') as fh:
            for r in csv.DictReader(io.TextIOWrapper(fh, encoding='utf8', errors='replace', newline=''), delimiter=';'):
                if r['nome'] in names:
                    ids.setdefault(r['id_contracheque'], r['nome'])
        items = collections.defaultdict(list)
        if 'remuneracao.csv' in z.namelist():
            with z.open('remuneracao.csv') as fh:
                for r in csv.DictReader(io.TextIOWrapper(fh, encoding='utf8', errors='replace', newline=''), delimiter=';'):
                    i = r['id_contracheque']
                    if i in ids and r['tipo'] in ('R/B', 'R/O'):
                        v = num(r['valor'])
                        if v > 0:
                            items[ids[i]].append((v, r['item'].strip(), r['categoria']))
        for n, br in lst:
            it = sorted(items.get(n, []), reverse=True)
            # maior verba que não seja o subsídio-base
            ext = [x for x in it if x[2] != 'contracheque'] or it
            top = ext[0] if ext else None
            out[f'{o}|{a}|{n}'] = {'mes': m, 'arq': f'{o}-{a}-{m}.zip', 'bruto': round(br, 2),
                                   'verba': top[1] if top else None, 'v': round(top[0], 2) if top else None,
                                   'cat': top[2] if top else None,
                                   'pontual': bool(top and br and top[0] / br >= 0.5 and top[2] in ('direitos-eventuais', 'indenizações'))}
    except Exception as e:
        for n, br in lst:
            out[f'{o}|{a}|{n}'] = {'mes': m, 'arq': f'{o}-{a}-{m}.zip', 'bruto': round(br, 2), 'verba': None, 'v': None, 'cat': None, 'pontual': False, 'err': str(e)[:60]}
json.dump(out, open('out/prov_judic.json', 'w'), ensure_ascii=False)
print('ok', len(out), sum(1 for v in out.values() if v['pontual']), sum(1 for v in out.values() if v['verba']))
