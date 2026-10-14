import zipfile,csv,io,json,collections
D='/media/hitsuzen/Novo volume/money/dados_portal/renuncias'
res={}
for y in range(2016,2025):
    z=zipfile.ZipFile(f'{D}/{y}.zip')
    nm=[n for n in z.namelist() if n.endswith('RenúnciasFiscais.csv') or ('Fiscais' in n and 'Benef' not in n and 'Habil' not in n and 'Imunes' not in n)][0]
    tot=collections.defaultdict(float); tipo=collections.defaultdict(lambda:collections.defaultdict(float))
    nome={}; cnae={}; uf={}; big=collections.defaultdict(float); alltot=0.0
    with z.open(nm) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); next(rd)
        for r in rd:
            try: v=float(r[14].replace('.','').replace(',','.') or 0)
            except ValueError: continue
            k=r[1][:8]; alltot+=v; tot[k]+=v; tipo[k][r[8]]+=v
            if v>big[k]: big[k]=v; nome[k]=r[2]; cnae[k]=r[5]; uf[k]=r[7]
    top=sorted(tot.items(),key=lambda x:-x[1])[:50]
    res[y]={'total':alltot,'n':len(tot),'top':[{'cnpj':k,'nome':nome[k],'cnae':cnae[k],'uf':uf[k],'valor':v,'tipo':max(tipo[k].items(),key=lambda z:z[1])[0],'tipo_pct':max(tipo[k].values())/v if v else 0} for k,v in top]}
    print(y,round(alltot/1e9,1),len(tot),round(sum(v for _,v in top)/1e9,1),flush=True)
json.dump(res,open('top50.json','w'),ensure_ascii=False)
