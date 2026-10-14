import zipfile,csv,io,json,os,glob,collections
from multiprocessing import Pool
D='/media/hitsuzen/Novo volume/money/dados_portal/despesas-execucao'
C='desp2_cache.json'
cache=json.load(open(C)) if os.path.exists(C) else {}
def num(s):
    try: return float(s.replace('.','').replace(',','.'))
    except ValueError: return 0.0
def proc(p):
    z=zipfile.ZipFile(p); a=collections.defaultdict(float); b=collections.defaultdict(float)
    with z.open(z.namelist()[0]) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        iF=h.index('Nome Função'); iG=h.index('Nome Grupo de Despesa'); iE=h.index('Nome Elemento de Despesa'); iO=h.index('Nome Órgão Superior')
        iP=h.index('Valor Pago (R$)'); iR=h.index('Valor Restos a Pagar Pagos (R$)')
        for r in rd:
            v=num(r[iP])+num(r[iR])
            if not v: continue
            if r[iF]=='Encargos especiais': a[r[iG]+'|'+r[iE]]+=v
            b[r[iO]+'|'+r[iG]]+=v
    return os.path.basename(p),{'enc':dict(a),'org':dict(b)}
if __name__=='__main__':
    fs=[p for p in sorted(glob.glob(D+'/*.zip')) if os.path.basename(p) not in cache]
    print(len(fs),flush=True)
    with Pool(3) as pool:
        for nm,r in pool.imap_unordered(proc,fs):
            cache[nm]=r; json.dump(cache,open(C,'w'))
    print('ok',len(cache))
