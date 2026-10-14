import zipfile,csv,io,json,collections,glob,os
D='/media/hitsuzen/Novo volume/money/dados_portal/orcamento-despesa'
def num(s):
    try: return float(s.replace('.','').replace(',','.'))
    except ValueError: return 0.0
def poder(n):
    n=n.lower()
    if any(k in n for k in ('câmara dos deputados','senado federal','tribunal de contas da união')): return 'Legislativo'
    if n.startswith('justiça') or any(k in n for k in ('supremo tribunal','superior tribunal','conselho nacional de justiça','tribunal','conselho da justiça')): return 'Judiciário'
    if any(k in n for k in ('ministério público','defensoria')): return 'MPU/DPU'
    return 'Executivo'
out={}
for p in sorted(glob.glob(D+'/*.zip')):
    y=os.path.basename(p)[:4]; z=zipfile.ZipFile(p); acc=collections.defaultdict(float)
    with z.open(z.namelist()[0]) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        io_=h.index('NOME ÓRGÃO SUPERIOR'); ig=h.index('NOME GRUPO DE DESPESA'); ir=h.index('ORÇAMENTO REALIZADO (R$)'); ifn=h.index('NOME FUNÇÃO')
        for r in rd:
            v=num(r[ir]); P=poder(r[io_])
            acc[P+'|total']+=v
            if r[ig].startswith('Pessoal'): acc[P+'|pessoal']+=v
            if r[io_]=='Ministério da Defesa' and r[ig].startswith('Pessoal'): acc['Defesa|pessoal']+=v
    out[y]=dict(acc); print(y,{k:round(v/1e9,1) for k,v in acc.items()})
json.dump(out,open('orc_poder.json','w'))
