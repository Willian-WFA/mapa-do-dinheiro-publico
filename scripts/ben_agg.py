import zipfile,csv,io,json,os,glob,re,collections
R='/media/hitsuzen/Novo volume/money/dados_portal'
C='ben_cache.json'; cache=json.load(open(C)) if os.path.exists(C) else {}
def num(s):
    try: return float(s.replace('.','').replace(',','.'))
    except: return 0.0
def proc(p):
    z=zipfile.ZipFile(p); f=z.namelist()[0]
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        hu=[x.upper() for x in h]
        idc=next((i for i,x in enumerate(hu) if 'NÚMERO BENEFÍCIO' in x),None)
        if idc is None: idc=next((i for i,x in enumerate(hu) if x.startswith('NIS') and ('FAVORECIDO' in x or 'BENEFICI' in x)),None)
        if idc is None: idc=next((i for i,x in enumerate(hu) if 'NIS' in x),0)
        vc=next((i for i,x in enumerate(hu) if 'VALOR' in x),None)
        ids=set(); rows=0; tot=0.0
        for r in rd:
            if len(r)<=idc: continue
            rows+=1; ids.add(r[idc])
            if vc is not None and len(r)>vc: tot+=num(r[vc])
    return {'rows':rows,'unicos':len(ids),'valor':tot,'col':h[idc]}
for ds in ('bpc','bolsa-familia-pagamentos','auxilio-brasil','novo-bolsa-familia','auxilio-emergencial'):
    for p in sorted(glob.glob(f'{R}/{ds}/*.zip')):
        k=ds+'/'+os.path.basename(p)
        if k not in cache:
            cache[k]=proc(p); json.dump(cache,open(C,'w')); print(k,cache[k],flush=True)
ben={'bpc':{},'bf':{}}
for k,v in cache.items():
    ds,fn=k.split('/'); ym=fn[:6]; y=int(ym[:4])
    if ds=='bpc' and ym.endswith('12'): ben['bpc'][str(y)]=v['unicos']
    if ds=='bolsa-familia-pagamentos' and (ym.endswith('12') or ym=='202111'): ben['bf'].setdefault(str(y),v['unicos'])
    if ds in('auxilio-brasil','novo-bolsa-familia') and ym.endswith('12'): ben['bf'][str(y)]=v['unicos']
json.dump(ben,open('ben.json','w')); print(ben)
