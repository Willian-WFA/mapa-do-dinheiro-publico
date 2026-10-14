import zipfile,csv,io,json,collections
D='/media/hitsuzen/Novo volume/money/dados_portal/renuncias'
def grp(c):
    if c[:2] in('01','02','03'): return 'Agropecuária (CNAE 01–03)'
    if c[:2] in('10','11','12'): return 'Agroindústria (alimentos, bebidas, fumo)'
    if c[:4] in('2013','2051','2831','2832','2833'): return 'Insumos e máquinas agrícolas'
    return None
top50={};agro={};rt={}
for y in range(2015,2025):
    z=zipfile.ZipFile(f'{D}/{y}.zip')
    nm=[n for n in z.namelist() if 'Fiscais' in n and 'Benef' not in n and 'Habil' not in n and 'Imunes' not in n][0]
    tot=collections.defaultdict(float); tipo=collections.defaultdict(lambda:collections.defaultdict(float))
    nome={};cnae={};uf={};big=collections.defaultdict(float);alltot=0.0
    g=collections.defaultdict(float);gn=collections.defaultdict(set);emp=collections.defaultdict(lambda:collections.defaultdict(float));tp=collections.defaultdict(float)
    with z.open(nm) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); next(rd)
        for r in rd:
            try: v=float(r[14].replace('.','').replace(',','.') or 0)
            except ValueError: continue
            k=r[1][:8]; alltot+=v; tot[k]+=v; tipo[k][r[8]]+=v; tp[r[8]]+=v
            if v>big[k]: big[k]=v; nome[k]=r[2]; cnae[k]=r[5]; uf[k]=r[7]
            a=grp(r[4])
            if a: g[a]+=v; gn[a].add(k); emp[a][k]+=v
    top=sorted(tot.items(),key=lambda x:-x[1])[:50]
    top50[str(y)]={'total':alltot,'n':len(tot),'top':[{'cnpj':k,'nome':nome[k],'cnae':cnae[k],'uf':uf[k],'valor':v,'tipo':max(tipo[k].items(),key=lambda z:z[1])[0],'tipo_pct':max(tipo[k].values())/v if v else 0} for k,v in top]}
    agro[str(y)]={'total':alltot,'n':len(tot),'tipo':sorted(tp.items(),key=lambda x:-x[1])[:8],
        'agro':{k:{'valor':g[k],'empresas':len(gn[k]),'top':sorted(((nome[c],v) for c,v in emp[k].items()),key=lambda x:-x[1])[:5]} for k in g}}
    rt[str(y)]={'total':alltot,'n':len(tot),'top15sum':sum(v for _,v in top[:15]),'top':[(nome[k],k,v) for k,v in top[:15]]}
    print(y,round(alltot/1e9,1),len(tot),flush=True)
json.dump(top50,open('top50.json','w'),ensure_ascii=False);json.dump(agro,open('agro.json','w'),ensure_ascii=False);json.dump(rt,open('ren_top.json','w'),ensure_ascii=False)
