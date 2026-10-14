import csv,glob,json,collections,sys
res={}
for y in range(2016,2025):
    f=glob.glob(f'raw/ren/d{y}/{y}_Ren*Benef*.csv')[0]
    tot=0; by=collections.defaultdict(float); nm={}; big={}
    with open(f,encoding='latin1',newline='') as fh:
        rd=csv.reader(fh,delimiter=';')
        h=next(rd)
        for r in rd:
            v=float(r[8].replace('.','').replace(',','.') or 0)
            k=r[1][:8]; tot+=v; by[k]+=v
            if v>big.get(k,-1): big[k]=v; nm[k]=r[2]
    top=sorted(by.items(),key=lambda x:-x[1])[:15]
    # concentração
    res[y]={'total':tot,'n':len(by),'top':[(nm[k],k,v) for k,v in top],'top15sum':sum(v for _,v in top)}
    print(y,f"total {tot/1e9:.1f} bi  empresas {len(by)}  top15 {res[y]['top15sum']/1e9:.1f} bi")
json.dump(res,open('ren_top.json','w'),ensure_ascii=False)
for y in (2019,2023,2024):
    print(y)
    for n,k,v in res[y]['top']: print(f"  {n[:50]:50} {k} {v/1e9:6.2f}")
