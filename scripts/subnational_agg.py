import json,collections,re
F={'10':'Saúde','12':'Educação','06':'Segurança pública','08':'Assistência social','09':'Previdência social','03':'Trabalho','04':'Administração'}
agg=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(float)))
cnt=collections.defaultdict(lambda:collections.Counter())
for l in open('siconfi_dca.jsonl'):
    r=json.loads(l)
    if r['n']<=0: cnt[r['ano']]['sem_dados']+=1; continue
    esf='M' if r['esfera']=='M' else 'E'
    cnt[r['ano']][esf]+=1
    for conta,cols in r['rows'].items():
        if conta=='TOTAL': k='Total'
        else:
            m=re.match(r'(\d{2}) - ',conta); k=F.get(m.group(1)) if m else None
        if not k: continue
        v=cols.get('Despesas Pagas')
        if v is None: v=cols.get('Despesas Liquidadas')
        if v is None: v=cols.get('Despesas Empenhadas')
        if v is not None: agg[r['ano']][esf][k]+=v
out={str(y):{e:{k:round(v/1e9,3) for k,v in d.items()} for e,d in esf.items()} for y,esf in agg.items()}
json.dump({'agg':out,'entes':{str(y):dict(c) for y,c in cnt.items()}},open('sub_year.json','w'),ensure_ascii=False)
for y in sorted(out):
    print(y,dict(cnt[int(y)]),{e:{k:round(v) for k,v in d.items() if k in('Saúde','Educação','Segurança pública','Assistência social')} for e,d in out[y].items()})
