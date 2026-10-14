import re,json,time,urllib.request,collections
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
B="https://portaldatransparencia.gov.br"
idx=open('raw/dl2.html',encoding='utf8',errors='ignore').read()
slugs=sorted(set(re.findall(r'href="/download-de-dados/([a-z0-9-]+)"',idx)))
out={}
for s in slugs:
    try:
        h=urllib.request.urlopen(urllib.request.Request(f"{B}/download-de-dados/{s}",headers={"User-Agent":UA}),timeout=60).read().decode('utf8','ignore')
    except Exception as e:
        out[s]={'erro':str(e)}; print(s,'ERRO',e,flush=True); time.sleep(3); continue
    if 'Human Verification' in h[:2000]: out[s]={'erro':'waf'}; print(s,'WAF',flush=True); time.sleep(10); continue
    ents=re.findall(r'arquivos\.push\(\{"ano" : "(\d+)", "mes" : "(\d*)", "dia" : "(\d*)", "origem" :\s+"([^"]*)"',h)
    title=re.search(r'<title>([^<]*)',h); 
    anos=sorted(set(re.findall(r'<option[^>]*value="(\d{4})"',h)))
    pats=sorted(set(re.findall(r"download-de-dados/%s/[^\"' ]{0,40}"%re.escape(s),h)))[:5]
    d=collections.defaultdict(list)
    for a,m,dd,o in ents: d[o].append((a,m,dd))
    out[s]={'title':(title.group(1).strip() if title else ''),'origens':{o:{'n':len(v),'ini':min(v),'fim':max(v)} for o,v in d.items()},'anos_opt':anos,'pats':pats,'len':len(h)}
    print(s,out[s]['title'][:40],'|',{o:(v['n'],v['ini'][:2],v['fim'][:2]) for o,v in out[s]['origens'].items()} or anos[:3]+anos[-2:],flush=True)
    time.sleep(3)
json.dump(out,open('disc.json','w'),ensure_ascii=False,indent=1)
