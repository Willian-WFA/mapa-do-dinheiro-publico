import zipfile,glob,os,json,re,sys,subprocess
sys.path.insert(0,'.')
from xl_head import head
res=json.load(open('inep_basica.json')) if os.path.exists('inep_basica.json') else {}
for y in range(2016,2026):
    if str(y) in res: continue
    z=f'raw/inep2/b{y}.zip'
    if not os.path.exists(z) or os.path.getsize(z)<1e6: continue
    try:
        zz=zipfile.ZipFile(z)
        xl=[n for n in zz.namelist() if n.lower().endswith('.xlsx')][0]
        out=f'raw/inep2/x{y}'; os.makedirs(out,exist_ok=True)
        p=zz.extract(xl,out)
        names,_=head(p,0,maxrows=1,maxss=10)
        cand=[i for i,n in enumerate(names) if re.search(r'1\.1\b',n)]
        found=None
        for i in cand[:3]:
            _,rows=head(p,i,maxrows=40,maxss=20000)  # strings nao necessarios: numeros sao valores diretos
            for r in rows:
                if r and r[0].strip().startswith('Brasil') or (r and len(r)>4 and 'Brasil' in str(r[0])):
                    nums=[x for x in r if re.fullmatch(r'\d+(\.\d+)?',str(x))]
                    if nums: found=int(float(nums[0])); break
            if found: break
        res[str(y)]=found; print(y,names[cand[0]] if cand else None,found,flush=True)
        json.dump(res,open('inep_basica.json','w'))
        os.remove(p)
    except Exception as e: print(y,'erro',e,flush=True)
