import json,urllib.request,urllib.parse,time,re,os,sys,threading,collections
from concurrent.futures import ThreadPoolExecutor
B="https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
entes=json.load(open('entes.json'))['items']
YEARS=[int(y) for y in (sys.argv[1].split(',') if len(sys.argv)>1 else ['2022'])]
OUT='siconfi_dca.jsonl'
done=set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: r=json.loads(l); done.add((r['ano'],r['ente']))
        except: pass
lock=threading.Lock(); fh=open(OUT,'a')
FUN=re.compile(r'^(\d{2}) - ')
def fetch(ano,e):
    q=urllib.parse.urlencode({'an_exercicio':ano,'no_anexo':'DCA-Anexo I-E','id_ente':e['cod_ibge']})
    for t in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(B+'?'+q,headers={'User-Agent':'Mozilla/5.0'}),timeout=90))
            rows={}
            for it in d.get('items',[]):
                m=FUN.match(it['conta'])
                if m and it['coluna'] in ('Despesas Pagas','Despesas Empenhadas','Despesas Liquidadas'):
                    rows.setdefault(it['conta'],{})[it['coluna']]=it['valor']
                if it['cod_conta']=='TotalDespesas' and it['coluna'] in ('Despesas Pagas','Despesas Empenhadas','Despesas Liquidadas'):
                    rows.setdefault('TOTAL',{})[it['coluna']]=it['valor']
            return {'ano':ano,'ente':e['cod_ibge'],'esfera':e['esfera'],'uf':e['uf'],'pop':e.get('populacao'),'rows':rows,'n':len(d.get('items',[]))}
        except Exception as ex:
            time.sleep(2+t*3)
    return {'ano':ano,'ente':e['cod_ibge'],'esfera':e['esfera'],'uf':e['uf'],'pop':e.get('populacao'),'rows':{},'n':-1}
jobs=[(a,e) for a in YEARS for e in entes if (a,e['cod_ibge']) not in done and e['esfera'] in ('E','M','D')]
print(len(jobs),'chamadas',flush=True)
t0=time.time(); cnt=0
def work(j):
    global cnt
    r=fetch(*j)
    with lock:
        fh.write(json.dumps(r,ensure_ascii=False)+'\n'); fh.flush(); cnt+=1
        if cnt%200==0: print(cnt,round(time.time()-t0),'s',flush=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(work,jobs))
print('fim',round(time.time()-t0),flush=True)
