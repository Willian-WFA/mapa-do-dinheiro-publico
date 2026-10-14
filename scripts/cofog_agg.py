import csv,glob,collections,json,re
D='/media/hitsuzen/Novo volume/money/dados_portal/tesouro/cofog'
out=collections.defaultdict(lambda:collections.defaultdict(float))
for f in sorted(glob.glob(D+'/dados-abertos-cofog-gc-*.csv')):
    with open(f,encoding='latin1',newline='') as fh:
        rd=csv.DictReader(fh,delimiter=';')
        for r in rd:
            try: v=float(r['VALOR (R$)'].replace('.','').replace(',','.'))
            except: continue
            d=r['CLASSIFICACAO COFOG DESCRICAO'].split(' - ')[0].strip()
            out[int(r['ANO'])][d]+=v
    print(f[-8:-4],round(sum(out[int(f[-8:-4])].values())/1e9),flush=True)
json.dump({y:dict(d) for y,d in out.items()},open('cofog_year.json','w'),ensure_ascii=False)
for y in (2010,2015,2023): print(y,{k[:28]:round(v/1e9) for k,v in sorted(out[y].items(),key=lambda x:-x[1])[:8]})
