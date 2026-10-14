import json,collections,re
def ramo(o):
    if o.startswith('mp'): return 'Ministério Público'
    if o in ('tjmmg','tjmrs','tjmsp'): return 'Justiça Militar estadual'
    if o.startswith('tj'): return 'Tribunais de Justiça (estaduais)'
    if o.startswith('trf'): return 'Tribunais Regionais Federais'
    if o.startswith('trt'): return 'Tribunais do Trabalho (TRT)'
    if o.startswith('tre'): return 'Tribunais Eleitorais (TRE)'
    if o in ('stf','stj','tst','tse','stm','cnj','csjt','cjf','cnmp'): return 'Tribunais superiores e conselhos'
    return 'Outros'
P={}
for l in open('judic_hi.jsonl'):
    o,a,m,n,f,loc,sal,ben,des,rem=json.loads(l)
    k=(a,o,n); p=P.get(k)
    if p is None: p=P[k]=[f,set(),0.0,0.0,0.0]
    br=sal+ben
    if br>50000: p[1].add(m)
    p[2]=max(p[2],br); p[3]=max(p[3],sal); p[4]=max(p[4],rem)
cnt=collections.defaultdict(lambda:collections.Counter()); c6=collections.defaultdict(lambda:collections.Counter()); csal=collections.defaultdict(lambda:collections.Counter())
rows=[]
for (a,o,n),(f,ms,mb,ms2,mr) in P.items():
    r=ramo(o)
    if ms: cnt[a][r]+=1
    if len(ms)>=6: c6[a][r]+=1
    if ms2>50000: csal[a][r]+=1
    if ms: rows.append([a,o,n,f,len(ms),round(mb,2),round(ms2,2),round(mr,2)])
print('pessoas-ano',len(rows))
for a in sorted(cnt): print(a,sum(cnt[a].values()),'6+m:',sum(c6[a].values()),'sal-base>50k:',sum(csal[a].values()),dict(cnt[a]))
json.dump(rows,open('out/judic_acima50k.json','w'),ensure_ascii=False)
json.dump({'cnt':{str(a):dict(c) for a,c in cnt.items()},'c6':{str(a):dict(c) for a,c in c6.items()},'sal':{str(a):dict(c) for a,c in csal.items()}},open('out/judic_counts.json','w'),ensure_ascii=False)
