import zipfile,csv,io,json,collections,re,sys,os
sys.argv=['x']
exec(open('cvm_agg.py').read().split("res={}")[0])   # cad, grupo, proc preparados (sem re-executar)
exec("def proc"+open('cvm_agg.py').read().split("def proc",1)[1].split("for y in range")[0])
res=json.load(open('cvm_pos.json'))
for y in range(2005,2016):
    p=f'{D}/hist_{y}.zip'
    if not os.path.exists(p): continue
    try:
        zipfile.ZipFile(p).testzip()
        res[f'{y}-12']=proc(p,f'{y}-12'); print(y,round(res[f'{y}-12']['total']/1e9),flush=True)
    except Exception as e: print(y,'erro',repr(e)[:80])
json.dump(res,open('cvm_pos.json','w'),ensure_ascii=False)
