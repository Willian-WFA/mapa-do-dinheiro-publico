import openpyxl,glob,re,json,os,collections
D='/media/hitsuzen/Novo volume/money/dados_portal/dgt'
def rows(ws): return [[c for c in r if c is not None] for r in ws.iter_rows(values_only=True)]
tot={}      # ano -> (valor, fonte, efetivo?)
fun={}      # (ano,funcao) -> (valor, fonte)
pib={}
files=sorted(glob.glob(D+'/efetivas_dgt-bases-efetivas-*-quadros.xlsx'))
for f in files:
    ed=int(re.search(r'efetivas-(\d{4})-serie',f).group(1)); nm=os.path.basename(f)
    wb=openpyxl.load_workbook(f,data_only=True,read_only=True)
    # --- Q XXVI total por ano
    ws=wb['Q XXVI'] if 'Q XXVI' in wb.sheetnames else wb['QXXVI']; R=[r for r in rows(ws) if r]
    hdr=None
    for i,r in enumerate(R):
        if len(r)>=4 and all(re.fullmatch(r'20\d\d',str(x)) for x in r): hdr=[int(x) for x in r]; hi=i; break
    nef=None
    for r in R[:hi]:
        if r and str(r[0]).upper().startswith('TRIBUTO'):
            # colunas EFETIVO / PROJEÇÃO: contar anos efetivos pelo cabeçalho (heurística: ate ed)
            pass
    for r in R[hi:]:
        if str(r[0]).strip().upper()=='TOTAL' and len(r)==len(hdr)+1:
            for y,v in zip(hdr,r[1:]):
                efet=y<=ed
                tot[(ed,y)]=(float(v)/1e9,nm,efet)
        if str(r[0]).strip().upper()=='PIB' and len(r)==len(hdr)+1:
            for y,v in zip(hdr,r[1:]): pib[y]=float(v)
    # --- por função: Q V (ano base)
    names=set()
    ws=wb['Q V']
    for r in rows(ws):
        if len(r)>=2 and isinstance(r[1],(int,float)) and isinstance(r[0],str) and r[0].upper()!='FUNÇÃO ORÇAMENTÁRIA':
            fun[(ed,ed,r[0].strip())]=float(r[1])/1e9; names.add(r[0].strip())
    # --- Q XXVII.. por ano (regionalizado, coluna TOTAL = ultima)
    for sn in wb.sheetnames:
        if not re.match(r'Q (XXVI[I]|XXI[X]|XXX)',sn): continue
        R=rows(wb[sn]); t=' '.join(str(c) for r in R[:6] for c in r)
        m=re.search(r'(20\d\d)',t.split('BASES EFETIVAS')[-1] if 'BASES EFETIVAS' in t else t)
        yrs=re.findall(r'\b(20\d\d)\b',' '.join(str(c) for r in R[:5] for c in r))
        if not yrs: continue
        y=int(yrs[-1])
        for r in R:
            if r and isinstance(r[0],str) and r[0].strip() in names and len(r)>=7 and isinstance(r[-1],(int,float)):
                fun[(ed,y,r[0].strip())]=float(r[-1])/1e9
# ---- consolidar: ultima edicao em que o ano e efetivo
T={}
for (ed,y),(v,nm,efet) in sorted(tot.items()):
    if efet: T[y]=(v,ed)
Pr={}
for (ed,y),(v,nm,efet) in sorted(tot.items()):
    if not efet: Pr[y]=(v,ed)   # projecao da edicao mais recente
F=collections.defaultdict(dict)
for (ed,y,n),v in sorted(fun.items()):
    if y<=ed: F[n][y]=v
print('TOTAL efetivo:',{y:round(v[0],1) for y,v in sorted(T.items())})
print('projecao:',{y:round(v[0],1) for y,v in sorted(Pr.items()) if y not in T})
for n in ('Agricultura','Saúde','Educação','Assistência Social','Comércio e Serviço','Indústria','Trabalho'):
    print(n,{y:round(v,1) for y,v in sorted(F[n].items())})
json.dump({'total':{y:v[0] for y,v in T.items()},'proj':{y:v[0] for y,v in Pr.items() if y not in T},'fun':F,'pib':pib},open('dgt_series.json','w'),ensure_ascii=False)
