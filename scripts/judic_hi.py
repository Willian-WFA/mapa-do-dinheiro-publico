import zipfile,csv,io,json,os,glob,sys
from multiprocessing import Pool
csv.field_size_limit(10**7)
D='/media/hitsuzen/Novo volume/money/dados_portal/judiciario'
OUT='judic_hi.jsonl'
def num(s):
    s=(s or '').strip()
    try: return float(s.replace('.','').replace(',','.')) if ',' in s else float(s)
    except ValueError: return 0.0
def proc(p):
    nm=os.path.basename(p)
    try:
        z=zipfile.ZipFile(p)
        with z.open('contracheque.csv') as fh:
            rd=csv.reader(io.TextIOWrapper(fh,encoding='utf8',errors='replace',newline=''),delimiter=';'); h=next(rd)
            io_=h.index('orgao'); im=h.index('mes'); ia=h.index('ano'); inm=h.index('nome'); ifu=h.index('funcao'); il=h.index('local_trabalho'); isa=h.index('salario'); ibe=h.index('beneficios'); ide=h.index('descontos'); ire=h.index('remuneracao')
            n=0; rows=[]
            for r in rd:
                if len(r)<=ire: continue
                n+=1
                sal=num(r[isa]); ben=num(r[ibe]); br=sal+ben
                if br>50000 or sal>50000:
                    rows.append([r[io_],int(r[ia]),int(r[im]),r[inm],r[ifu],r[il],round(sal,2),round(ben,2),round(num(r[ide]),2),round(num(r[ire]),2)])
        return nm,n,rows
    except Exception as e:
        return nm,-1,[]
if __name__=='__main__':
    done=set(open(OUT+'.done').read().split()) if os.path.exists(OUT+'.done') else set()
    files=[p for p in sorted(glob.glob(D+'/*/*.zip')) if os.path.basename(p) not in done]
    print(len(files),flush=True)
    with Pool(10) as pool, open(OUT,'a') as fo, open(OUT+'.done','a') as fd:
        k=0
        for nm,n,rows in pool.imap_unordered(proc,files,chunksize=4):
            if n>=0:
                for r in rows: fo.write(json.dumps(r,ensure_ascii=False)+'\n')
                fd.write(nm+'\n')
            k+=1
            if k%500==0: print(k,flush=True); fo.flush(); fd.flush()
