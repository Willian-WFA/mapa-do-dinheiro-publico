import zipfile,csv,io,json,os,glob,collections
D='/media/hitsuzen/Novo volume/money/dados_portal/despesas-execucao'
C='desp_cache.json'
cache=json.load(open(C)) if os.path.exists(C) else {}
ACOES={'INATIVOS MILITARES DA UNIAO':'Inativos (reserva/reforma)','ATIVOS MILITARES DA UNIAO':'Ativa','PENSOES MILITARES DA UNIAO':'Pensionistas'}
for p in sorted(glob.glob(D+'/*.zip')):
    nm=os.path.basename(p)
    if nm in cache: continue
    z=zipfile.ZipFile(p); f=z.namelist()[0]; acc=collections.defaultdict(float)
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        ia=h.index('Nome Ação'); ip=h.index('Valor Pago (R$)')
        for r in rd:
            g=ACOES.get(r[ia].strip())
            if g: acc[g]+=float(r[ip].replace('.','').replace(',','.') or 0)
    cache[nm]=acc; json.dump(cache,open(C,'w')); print(nm,{k:round(v/1e6) for k,v in acc.items()},flush=True)
