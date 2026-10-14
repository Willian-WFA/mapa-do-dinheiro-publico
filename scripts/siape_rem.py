import zipfile,csv,io,json,os,glob
from multiprocessing import Pool
D='/media/hitsuzen/Novo volume/money/dados_portal/servidores'
CACHE='siape_rem_cache.json'; cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
NEED=['REMUNERAÇÃO BÁSICA BRUTA (R$)','ABATE-TETO (R$)','GRATIFICAÇÃO NATALINA (R$)','ABATE-TETO DA GRATIFICAÇÃO NATALINA (R$)','FÉRIAS (R$)','OUTRAS REMUNERAÇÕES EVENTUAIS (R$)']
def num(s):
    s=s.strip()
    try: return float(s.replace('.','').replace(',','.')) if s else 0.0
    except ValueError: return 0.0
def proc(p):
    z=zipfile.ZipFile(p); f=[n for n in z.namelist() if 'Remuneracao' in n][0]
    n=0; tot=0.0
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        idx=[h.index(c) for c in NEED if c in h]
        for r in rd:
            if len(r)<=max(idx): continue
            n+=1
            for i in idx: tot+=num(r[i])
    return os.path.basename(p),{'n':n,'bruto':tot}
if __name__=='__main__':
    fs=[p for p in sorted(glob.glob(D+'/*_*_SIAPE.zip')) if os.path.basename(p) not in cache and os.path.basename(p)[:4]>='2016' and os.path.basename(p)[4:6].isdigit()]
    print(len(fs),flush=True)
    with Pool(4) as pool:
        for nm,r in pool.imap_unordered(proc,fs):
            cache[nm]=r; json.dump(cache,open(CACHE,'w')); print(nm,r['n'],round(r['bruto']/1e9,2),flush=True)
