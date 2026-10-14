import re,json,time,urllib.request
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
B="https://portaldatransparencia.gov.br"
idx=open('raw/dl2.html',encoding='utf8',errors='ignore').read()
slugs=sorted(set(re.findall(r'href="/download-de-dados/([a-z0-9-]+)"',idx)))
cat={}
for s in slugs:
    try: h=urllib.request.urlopen(urllib.request.Request(f"{B}/download-de-dados/{s}",headers={"User-Agent":UA}),timeout=60).read().decode('utf8','ignore')
    except Exception as e: print(s,'ERRO',e); time.sleep(5); continue
    if 'Human Verification' in h[:2000]: print(s,'WAF'); time.sleep(20); continue
    ents=re.findall(r'arquivos\.push\(\{"ano" : "(\d+)", "mes" : "(\d*)", "dia" : "(\d*)", "origem" :\s+"([^"]*)"',h)
    ctor=re.search(r'new DownloadPlanilhas\(([^;]{0,300})\)',h)
    init=re.findall(r'download\.(criarLinksIniciais\w*)\(',h)
    cat[s]={'ctor':ctor.group(1) if ctor else None,'init':sorted(set(init)),'arquivos':ents}
    print(s,cat[s]['init'],'|',(cat[s]['ctor'] or '')[:150].replace('\n',' '),flush=True)
    time.sleep(3)
json.dump(cat,open('catalogo.json','w'),ensure_ascii=False)
