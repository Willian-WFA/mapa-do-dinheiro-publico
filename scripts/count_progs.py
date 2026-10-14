import zipfile,csv,io,json,glob,os,collections,re
R='/media/hitsuzen/Novo volume/money/dados_portal'
out={'pe_de_meia':{},'gas':{},'td':{}}
csv.field_size_limit(10**7)
def uniq(path,pred=None):
    z=zipfile.ZipFile(path); f=z.namelist()[0]; n=0; ids=set(); val=0.0
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        hu=[x.upper() for x in h]
        ic=next((i for i,x in enumerate(hu) if 'CPF' in x or 'NIS' in x),0)
        iv=next((i for i,x in enumerate(hu) if 'VALOR' in x),None)
        for r in rd:
            if len(r)<=ic: continue
            n+=1; ids.add(r[ic])
            if iv is not None and len(r)>iv:
                try: val+=float(r[iv].replace('.','').replace(',','.'))
                except: pass
    return {'rows':n,'unicos':len(ids),'valor':val,'col':h[ic]}
for ds,key in (('pe-de-meia','pe_de_meia'),('gas-do-povo','gas')):
    for p in sorted(glob.glob(f'{R}/{ds}/*.zip')):
        ym=os.path.basename(p)[:6]; out[key][ym]=uniq(p); print(ds,ym,out[key][ym],flush=True)
# Tesouro Direto
for p in sorted(glob.glob(f'{R}/tesouro/investidores-do-tesouro-direto/*.csv')):
    nm=os.path.basename(p); n=0; ativos=0; op=0
    with open(p,encoding='latin1',newline='') as fh:
        rd=csv.reader(fh,delimiter=';'); h=next(rd)
        iS=next(i for i,x in enumerate(h) if x.startswith('Situacao')); iO=next(i for i,x in enumerate(h) if x.startswith('Operou'))
        for r in rd:
            n+=1
            if len(r)>iS and r[iS]=='A': ativos+=1
            if len(r)>iO and r[iO]=='S': op+=1
    out['td'][nm]={'total':n,'ativos':ativos,'operou12m':op}; print(nm,out['td'][nm],flush=True)
json.dump(out,open('count_progs.json','w'))
