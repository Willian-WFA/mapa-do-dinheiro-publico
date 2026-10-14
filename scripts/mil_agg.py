import zipfile,csv,io,json,os,sys,glob,re
from multiprocessing import Pool
D='/media/hitsuzen/Novo volume/money/dados_portal/militares'
CACHE='mil_cache.json'
cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def num(s):
    s=s.strip()
    return float(s.replace('.','').replace(',','.')) if s else 0.0
def proc(path):
    nm=os.path.basename(path)
    z=zipfile.ZipFile(path)
    f=[n for n in z.namelist() if n.endswith('Remuneracao.csv')][0]
    n=0;tot=0.0;bas=0.0;ids=set()
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';')
        h=next(rd)
        for r in rd:
            if len(r)<16: continue
            n+=1
            bas+=num(r[5])
            tot+=num(r[5])+num(r[7])+num(r[9])+num(r[11])+num(r[13])+num(r[15])
    return nm,{'n':n,'bruto_total':tot,'basica':bas}
if __name__=='__main__':
    files=[p for p in sorted(glob.glob(D+'/*.zip')) if os.path.basename(p) not in cache]
    print(len(files),'novos')
    with Pool(4) as p:
        for nm,res in p.imap_unordered(proc,files):
            cache[nm]=res
            json.dump(cache,open(CACHE,'w'))
    print('ok',len(cache))
