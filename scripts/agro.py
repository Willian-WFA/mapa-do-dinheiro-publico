import csv,glob,json,collections
def grp(c):
    if c[:2] in('01','02','03'): return 'Agropecuária (CNAE 01–03)'
    if c[:2] in('10','11','12'): return 'Agroindústria (alimentos, bebidas, fumo)'
    if c[:4] in('2013','2051','2831','2832','2833'): return 'Insumos e máquinas agrícolas'
    return None
res={}
for y in range(2016,2025):
    f=glob.glob(f'raw/ren/d{y}/{y}_Ren*Fiscais.csv')[0]
    tipo=collections.defaultdict(float); g=collections.defaultdict(float); gn=collections.defaultdict(set)
    emp=collections.defaultdict(lambda:collections.defaultdict(float)); nm={}
    allc=set(); tot=0
    with open(f,encoding='latin1',newline='') as fh:
        rd=csv.reader(fh,delimiter=';'); next(rd)
        for r in rd:
            v=float(r[14].replace('.','').replace(',','.') or 0)
            tot+=v; tipo[r[8]]+=v; allc.add(r[1][:8])
            k=grp(r[4])
            if k:
                g[k]+=v; gn[k].add(r[1][:8]); emp[k][r[1][:8]]+=v; nm[r[1][:8]]=r[2]
    top={k:sorted(((nm[c],v) for c,v in e.items()),key=lambda x:-x[1])[:5] for k,e in emp.items()}
    res[y]={'total':tot,'n':len(allc),'tipo':sorted(tipo.items(),key=lambda x:-x[1])[:8],
            'agro':{k:{'valor':g[k],'empresas':len(gn[k]),'top':top[k]} for k in g}}
    a=sum(g.values()); print(y,f"total {tot/1e9:.1f}  agro(total grupos) {a/1e9:.1f} bi ({a/tot*100:.1f}%)",{k[:12]:round(v/1e9,1) for k,v in g.items()})
json.dump(res,open('agro.json','w'),ensure_ascii=False)
print([ (t[0][:45],round(t[1]/1e9,1)) for t in res[2023]['tipo']])
