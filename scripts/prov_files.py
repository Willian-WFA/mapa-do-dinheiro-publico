import json, csv, collections, openpyxl
P = '/media/hitsuzen/Novo volume/money/planilhas/'
pj = json.load(open('out/prov_judic.json'))
# --- judiciario
best = {}
for line in open('judic_hi.jsonl'):
    o, a, m, n, f, loc, sal, ben, des, rem = json.loads(line)
    br = sal + ben
    k = (a, o, n)
    if k not in best or br > best[k][0]:
        best[k] = (br, m)
src = P + 'judiciario_mp_acima_50mil.csv'
rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))
hdr = rows[0] + ['mes_maior_valor', 'arquivo_fonte', 'url_fonte_dadosjusbr', 'verba_principal', 'valor_verba_principal', 'verba_pontual']
out = [hdr]
for r in rows[1:]:
    a, o, n = int(r[0]), r[2], r[3]
    b = best.get((a, o, n))
    p = pj.get(f'{o}|{a}|{n}')
    if b:
        m = b[1]
        r += [m, f'{o}-{a}-{m}.zip', f'https://dadosjusbr.org/orgao/{o}/{a}/{m}']
    else:
        r += ['', '', '']
    if p:
        r += [p['verba'] or '', p['v'] if p['v'] is not None else '', 'sim' if p['pontual'] else 'nao']
    else:
        r += ['', '', '']
    out.append(r)
with open(src, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f, delimiter=';').writerows(out)
print('judic csv', len(out))
# xlsx
wb = openpyxl.load_workbook(P + 'judiciario_mp_acima_50mil.xlsx')
ws = wb['Maiores por ano (top 500)']
if ws.cell(1, 10).value is None:
    for j, t in enumerate(['Mês do maior valor', 'Arquivo de origem', 'Verba principal do mês', 'Valor da verba (R$)', 'Verba pontual?', 'Link da fonte'], 10):
        ws.cell(1, j, t)
        ws.cell(1, j).font = ws.cell(1, 1).font.copy()
    for i in range(2, ws.max_row + 1):
        a, o, n = ws.cell(i, 1).value, ws.cell(i, 3).value, ws.cell(i, 4).value
        p = pj.get(f'{o}|{a}|{n}')
        if p:
            ws.cell(i, 10, p['mes']); ws.cell(i, 11, p['arq']); ws.cell(i, 12, p['verba']); ws.cell(i, 13, p['v'])
            ws.cell(i, 14, 'sim' if p['pontual'] else 'não')
            ws.cell(i, 15, f"https://dadosjusbr.org/orgao/{o}/{a}/{p['mes']}")
    for c, w in zip('JKLMNO', (10, 22, 46, 16, 12, 48)):
        ws.column_dimensions[c].width = w
r = wb['Resumo']
mx = r.max_row + 2
r.cell(mx, 1, 'Colunas de origem (aba "Maiores por ano"): mês do maior valor, arquivo DadosJusBr de origem, verba principal do mês (maior parcela além do subsídio-base) e se ela é pontual (sozinha > 50% do valor do mês). Valores acima de R$ 1 milhão num mês podem ser erro de registro do tribunal; confira na fonte.')
wb.save(P + 'judiciario_mp_acima_50mil.xlsx')
# --- executivo
civ = {}
for l in open('hi_salary_civil.jsonl'):
    r = json.loads(l); k = (r['ano'], r['nome'], r['cpf'])
    if k not in civ or r['bruto_total'] > civ[k]['bruto_total']:
        civ[k] = r
src = P + 'executivo_acima_50mil.csv'
rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))
out = [rows[0] + ['mes_maior_valor', 'arquivo_fonte', 'url_fonte_portal']]
miss = 0
for r in rows[1:]:
    c = civ.get((int(r[0]), r[2], r[3]))
    if c:
        ym = f"{c['ano']}{c['mes']:02d}"
        r += [c['mes'], f"{ym}_{c['origem']}.zip", f'https://portaldatransparencia.gov.br/download-de-dados/servidores/{ym}']
    else:
        miss += 1; r += ['', '', '']
    out.append(r)
with open(src, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f, delimiter=';').writerows(out)
print('exec', len(out), 'sem match', miss)
# --- senado
sen = {}
for l in open('senado_pay.jsonl'):
    r = json.loads(l); k = (r['ano'], r['nome'])
    if k not in sen or r['bruto'] > sen[k]['bruto']:
        sen[k] = r
src = P + 'senado_acima_50mil.csv'
rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))
out = [rows[0] + ['mes_maior_valor', 'tipo_folha', 'url_fonte_api_senado']]
for r in rows[1:]:
    c = sen.get((int(r[0]), r[1]))
    r += [c['mes'], c.get('tipo_folha', ''), f"https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/remuneracoes/{r[0]}/{c['mes']}"] if c else ['', '', '']
    out.append(r)
with open(src, 'w', encoding='utf-8-sig', newline='') as f:
    csv.writer(f, delimiter=';').writerows(out)
print('senado', len(out))
