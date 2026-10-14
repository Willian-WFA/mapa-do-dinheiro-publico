import json,re
H=json.load(open('hist_rows.json')); rows={r['label'].strip():{int(y):v for y,v in r['data'].items()} for r in H['rows']}
U={'Saúde':rows['Saúde (União)'],'Educação':rows['Educação (União)'],'Segurança pública':rows['Segurança pública (União)'],'Assistência social':rows['Assistência social (União) – total']}
sub=json.load(open('sub_year.json'))
ok=[y for y,c in sub['entes'].items() if c.get('M',0)>=5000 and c.get('E',0)>=26]
out={}
for y in sorted(ok):
    a=sub['agg'].get(y,{}); d={}
    for f,uv in U.items():
        e=a.get('E',{}).get(f); m=a.get('M',{}).get(f); u=uv.get(int(y))
        if e and m and u: d[f]={'uniao':round(u,1),'est':round(e,1),'mun':round(m,1)}
    if d: out[y]=d
open('site/data_entenda_esf.js','w').write('window.ENT_ESF='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';')
print({y:{f:round(v['uniao']/(v['uniao']+v['est']+v['mun'])*100) for f,v in d.items()} for y,d in out.items()})
