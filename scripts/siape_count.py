import zipfile,csv,io,glob,os,re,json,collections
R='/media/hitsuzen/Novo volume/money/dados_portal/servidores'
csv.field_size_limit(10**7)
CACHE='siape_cache.json'; cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
POL=re.compile(r'POLICIA FEDERAL|POLICIAL FEDERAL|POLICIAL RODOVIARIO|PAPILOSCOPISTA|PERITO CRIMINAL FEDERAL|AGENTE PENITENCIARIO FEDERAL|POLICIAL PENAL FEDERAL',re.I)
for p in sorted(glob.glob(R+'/*12_*_SIAPE.zip')):
    nm=os.path.basename(p)
    if nm in cache: continue
    z=zipfile.ZipFile(p); f=[n for n in z.namelist() if 'Cadastro' in n][0]
    ids=set(); org=collections.Counter(); pol=0
    with z.open(f) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        iI=h.index('Id_SERVIDOR_PORTAL'); iD=next((i for i,x in enumerate(h) if x in ('DESCRICAO_CARGO','DESCRICAO_CARGO_INSTITUIDOR_PENSAO')),iI)
        iO=next((i for i,x in enumerate(h) if x=='ORGSUP_EXERCICIO'),None)
        if iO is None: iO=next(i for i,x in enumerate(h) if x.startswith('ORGSUP_LOTACAO') and not x.startswith('COD'))
        for r in rd:
            if len(r)<=max(iI,iD,iO): continue
            if r[iI] in ids: continue
            ids.add(r[iI]); org[r[iO]]+=1
            if POL.search(r[iD]): pol+=1
    cache[nm]={'n':len(ids),'pf_prf':pol,'org':org.most_common(12)}
    json.dump(cache,open(CACHE,'w'),ensure_ascii=False); print(nm,cache[nm]['n'],pol,flush=True)
