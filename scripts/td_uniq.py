import csv,glob,os,json,re
D='/media/hitsuzen/Novo volume/money/dados_portal/tesouro/investidores-do-tesouro-direto'
out={}
for p in sorted(glob.glob(D+'/*.csv')):
    nm=os.path.basename(p); tot=set(); at=set(); op=set()
    with open(p,encoding='latin1',newline='') as fh:
        rd=csv.reader(fh,delimiter=';'); h=next(rd)
        iS=next(i for i,x in enumerate(h) if x.startswith('Situacao')); iO=next(i for i,x in enumerate(h) if x.startswith('Operou'))
        for r in rd:
            c=r[0]; tot.add(c)
            if r[iS]=='A': at.add(c)
            if r[iO]=='S': op.add(c)
    m=re.search(r'(\d{4})\.csv',nm); key='ate2017' if 'ate2017' in nm else m.group(1)
    out[key]={'cadastrados':len(tot),'ativos':len(at),'operou12m':len(op)}; print(key,out[key],flush=True)
json.dump(out,open('td_uniq.json','w'))
