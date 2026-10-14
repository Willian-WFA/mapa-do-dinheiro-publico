import zipfile,csv,io,json,os,glob,collections
from multiprocessing import Pool
D='/media/hitsuzen/Novo volume/money/dados_portal/despesas-execucao'
C='func_cache.json'
cache=json.load(open(C)) if os.path.exists(C) else {}
def proc(p):
    z=zipfile.ZipFile(p); acc=collections.defaultdict(lambda:[0.0,0.0])
    with z.open(z.namelist()[0]) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        i=h.index('Nome Função'); ip=h.index('Valor Pago (R$)'); ir=h.index('Valor Restos a Pagar Pagos (R$)')
        for r in rd:
            try:
                acc[r[i]][0]+=float(r[ip].replace('.','').replace(',','.') or 0)
                acc[r[i]][1]+=float(r[ir].replace('.','').replace(',','.') or 0)
            except ValueError: pass
    return os.path.basename(p),dict(acc)
if __name__=='__main__':
    fs=[p for p in sorted(glob.glob(D+'/*.zip')) if os.path.basename(p) not in cache]
    print(len(fs),'novos',flush=True)
    with Pool(3) as pool:
        for nm,a in pool.imap_unordered(proc,fs):
            cache[nm]=a; json.dump(cache,open(C,'w'))
    print('ok',len(cache))
