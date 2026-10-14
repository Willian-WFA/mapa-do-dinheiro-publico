import zipfile, csv, io, json, re, collections, glob, os
csv.field_size_limit(10**8)
D = '/media/hitsuzen/Novo volume/money/dados_portal/cvm_fre/'
top = json.load(open('top50.json'))
isenc = collections.defaultdict(dict)   # raiz -> ano -> valor
nomes_top = {}
for y, v in top.items():
    for t in v['top']:
        isenc[t['cnpj']][y] = isenc[t['cnpj']].get(y, 0) + t['valor']
        nomes_top[t['cnpj']] = t['nome']
BANCOS = {'60872504': 'Itaú Unibanco Holding', '60746948': 'Bradesco', '90400888': 'Santander Brasil', '30306294': 'BTG Pactual',
          '00000000': 'Banco do Brasil', '58160789': 'Banco Safra', '00416968': 'Banco Inter', '92702067': 'Banrisul',
          '61532644': 'Itaúsa', '07526557': 'Banco Daycoval', '33657248': 'BNDES', '60701190': 'Itaú Unibanco S.A.'}
def raiz(c):
    return re.sub(r'\D', '', c)[:8]
pos = collections.defaultdict(dict)   # raiz -> data_ref -> versao,rows
rem = collections.defaultdict(dict)
nome = {}
def keep(r):
    return None
for f in sorted(glob.glob(D + 'fre_20*.zip')):
    y = f[-8:-4]
    z = zipfile.ZipFile(f)
    with z.open(f'fre_cia_aberta_posicao_acionaria_{y}.csv') as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding='latin1', newline=''), delimiter=';')
        for r in rd:
            rz = raiz(r['CNPJ_Companhia'])
            if rz in BANCOS or rz in isenc:
                nome[rz] = r['Nome_Companhia']
                dr = r['Data_Referencia'][:4]; v = int(r['Versao'] or 0)
                cur = pos[rz].get(dr)
                if cur is None or v > cur[0]:
                    pos[rz][dr] = [v, []]
                    cur = pos[rz][dr]
                if v == cur[0]:
                    cur[1].append(r)
    with z.open(f'fre_cia_aberta_remuneracao_total_orgao_{y}.csv') as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding='latin1', newline=''), delimiter=';')
        for r in rd:
            rz = raiz(r['CNPJ_Companhia'])
            if rz in BANCOS or rz in isenc:
                dr = r['Data_Referencia'][:4]; v = int(r['Versao'] or 0)
                cur = rem[rz].get(dr)
                if cur is None or v > cur[0]:
                    rem[rz][dr] = [v, []]; cur = rem[rz][dr]
                if v == cur[0]:
                    cur[1].append({k: r[k] for k in ('Data_Fim_Exercicio_Social', 'Orgao_Administracao', 'Numero_Membros_Remunerados', 'Total_Remuneracao_Orgao', 'Numero_Membros')})
def fl(s):
    try: return float(s)
    except: return 0.0
out = {}
for rz in set(pos) | set(rem):
    e = {'nome': nome.get(rz, BANCOS.get(rz, '')), 'raiz': rz, 'banco': rz in BANCOS, 'isenc': {y: round(v / 1e6, 1) for y, v in isenc.get(rz, {}).items()},
         'acion': {}, 'rem': {}}
    for dr, (v, rows) in pos[rz].items():
        L = []
        for r in rows:
            pct = fl(r['Percentual_Total_Acoes_Circulacao'])
            ctrl = r['Acionista_Controlador'] == 'S'
            if (pct >= 5 or ctrl) and r['Acionista'] not in ('Ações Tesouraria', 'Outros'):
                L.append({'n': r['Acionista'], 'pf': r['Tipo_Pessoa_Acionista'] == 'PF', 'pct': round(pct, 2), 'ctrl': ctrl,
                          'via': r['Acionista_Relacionado'] or '', 'pais': r['Nacionalidade']})
        L.sort(key=lambda x: (-x['pct']))
        e['acion'][dr] = L[:25]
    for dr, (v, rows) in rem[rz].items():
        for r in rows:
            ex = r['Data_Fim_Exercicio_Social'][:4]
            o = r['Orgao_Administracao']
            n = fl(r['Numero_Membros_Remunerados']); t = fl(r['Total_Remuneracao_Orgao'])
            if n > 0 and o in ('Conselho de Administração', 'Diretoria Estatutária'):
                e['rem'].setdefault(ex, {})[o] = [round(t / 1e6, 2), n, round(t / n / 1e6, 2)]
    out[rz] = e
json.dump(out, open('out/fre_donos.json', 'w'), ensure_ascii=False)
print(len(out), 'empresas;', sum(1 for e in out.values() if e['banco']), 'bancos')
for rz in ('60872504', '60746948', '90400888', '30306294'):
    e = out.get(rz)
    if e: print(e['nome'], sorted(e['acion'])[-1:], [ (a['n'],a['pct'],a['ctrl']) for a in e['acion'][sorted(e['acion'])[-1]][:6]], {y:v for y,v in sorted(e['rem'].items())[-2:]})
print({e['nome'][:30] for e in out.values() if e['isenc']} and len([1 for e in out.values() if e['isenc']]), 'listadas no top50 isenção')
