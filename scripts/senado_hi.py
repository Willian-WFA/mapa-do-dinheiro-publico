import urllib.request,json,os,time
OUT='senado_pay.jsonl'
def num(s):
    try: return float(str(s).replace('.','').replace(',','.'))
    except: return 0.0
done=set()
if os.path.exists(OUT+'.done'): done=set(open(OUT+'.done').read().split())
fo=open(OUT,'a'); fd=open(OUT+'.done','a')
for y in range(2016,2027):
    for m in range(1,13):
        k=f'{y}{m:02d}'
        if k in done or (y==2026 and m>9): continue
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/remuneracoes/{y}/{m}',headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'}),timeout=180))
        except Exception as e:
            print(k,'erro',str(e)[:60],flush=True); continue
        n=0; hi=0
        for r in d:
            n+=1
            tot=num(r.get('remuneracao_basica'))+num(r.get('vantagens_pessoais'))+num(r.get('funcao_comissionada'))+num(r.get('horas_extras'))+num(r.get('outras_eventuais'))+num(r.get('abono_permanencia'))
            rev=num(r.get('reversao_teto_constitucional'))
            # remuneracao bruta menos teto: usar campo se existir
            liq=tot-rev
            if tot>50000 or liq>50000:
                hi+=1; fo.write(json.dumps({'ano':y,'mes':m,'nome':r.get('nome'),'tipo_folha':r.get('tipo_folha'),'bruto':round(tot,2),'liquido_teto':round(liq,2),'cargo':r.get('cargo') or r.get('funcao') or '', 'lotacao':r.get('lotacao') or r.get('situacao') or '', 'raw_keys':list(r.keys())[:40] if hi==1 else None},ensure_ascii=False)+'\n')
        fo.flush(); fd.write(k+'\n'); fd.flush(); print(k,n,hi,flush=True)
