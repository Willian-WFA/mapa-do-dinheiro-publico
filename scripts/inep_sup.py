import zipfile,os,json,re,sys,shutil
sys.path.insert(0,'.')
from xl_head import head
res=json.load(open('inep_sup.json')) if os.path.exists('inep_sup.json') else {}
for y in range(2016,2025):
    if str(y) in res: continue
    z=f'raw/inep2/s{y}.zip'
    if not os.path.exists(z): continue
    try:
        zz=zipfile.ZipFile(z); zz.testzip()
        xl=[n for n in zz.namelist() if 'Municipio' in n and n.lower().endswith('.xlsx')][0]
        p=zz.extract(xl,'raw/inep2/xs')
        names,_=head(p,0,maxrows=1,maxss=5)
        i=names.index('5.1') if '5.1' in names else next(k for k,n in enumerate(names) if n.startswith('5.1'))
        _,rows=head(p,i,maxrows=40,maxss=30000)
        tot=None
        for r in rows:
            if r and str(r[0]).strip().startswith('Brasil'):
                nums=[x for x in r[1:] if re.fullmatch(r'\d+',str(x))]
                if nums: tot=int(nums[0]); break
        print(y,names[i],tot,flush=True)
        if tot: res[str(y)]=tot; json.dump(res,open('inep_sup.json','w'))
        os.remove(p)
    except Exception as e: print(y,'erro',repr(e)[:100],flush=True)
