import zipfile,csv,io,json,os,glob,sys
from multiprocessing import Pool
csv.field_size_limit(10**7)
D='/media/hitsuzen/Novo volume/money/dados_portal/servidores'
OUT=sys.argv[1] if len(sys.argv)>1 else 'hi_salary_civil.jsonl'
PAT=sys.argv[2] if len(sys.argv)>2 else '*_Servidores_SIAPE.zip,*_Servidores_BACEN.zip,*_Aposentados_SIAPE.zip,*_Pensionistas_SIAPE.zip,*_Aposentados_BACEN.zip,*_Pensionistas_BACEN.zip'
LIM=50000.0
def num(s):
    s=s.strip()
    try: return float(s.replace('.','').replace(',','.')) if s else 0.0
    except ValueError: return 0.0
def proc(p):
    nm=os.path.basename(p); ym=nm[:6]; origem=nm[7:-4]
    if int(ym[:4])<2016: return nm,[],0,0
    z=zipfile.ZipFile(p); fr=[n for n in z.namelist() if 'Remuneracao' in n]; fc=[n for n in z.namelist() if 'Cadastro' in n]
    if not fr: return nm,[],0,0
    hi={}; n=0; n50=0
    with z.open(fr[0]) as fh:
        rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
        ib=h.index('REMUNERAÇÃO BÁSICA BRUTA (R$)'); ia=h.index('ABATE-TETO (R$)'); io_=h.index('OUTRAS REMUNERAÇÕES EVENTUAIS (R$)')
        inat=h.index('GRATIFICAÇÃO NATALINA (R$)'); iab=h.index('ABATE-TETO DA GRATIFICAÇÃO NATALINA (R$)'); ife=h.index('FÉRIAS (R$)')
        iid=h.index('Id_SERVIDOR_PORTAL'); inm=h.index('NOME'); icpf=h.index('CPF')
        for r in rd:
            if len(r)<=io_: continue
            n+=1
            sal=num(r[ib])+num(r[ia])+num(r[io_])
            if sal>LIM:
                tot=sal+num(r[inat])+num(r[iab])+num(r[ife])
                hi[r[iid]]=[r[inm],r[icpf],round(sal,2),round(tot,2)]
    n50=len(hi)
    if hi and fc:
        with z.open(fc[0]) as fh:
            rd=csv.reader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'); h=next(rd)
            iid=h.index('Id_SERVIDOR_PORTAL')
            ic=next((i for i,x in enumerate(h) if x.startswith('DESCRICAO_CARGO')),None)
            io2=next((i for i,x in enumerate(h) if x=='ORGSUP_EXERCICIO'),None)
            if io2 is None: io2=next((i for i,x in enumerate(h) if x.startswith('ORGSUP_LOTACAO')),None)
            ig=next((i for i,x in enumerate(h) if x=='ORG_EXERCICIO'),None)
            if ig is None: ig=next((i for i,x in enumerate(h) if x.startswith('ORG_LOTACAO')),None)
            for r in rd:
                if len(r)>iid and r[iid] in hi:
                    v=hi[r[iid]]
                    v+= [r[ic] if ic is not None and len(r)>ic else '', r[io2] if io2 is not None and len(r)>io2 else '', r[ig] if ig is not None and len(r)>ig else '']
    rows=[]
    for k,v in hi.items():
        v=v+['','','']*(1 if len(v)<7 else 0)
        rows.append({'ano':int(ym[:4]),'mes':int(ym[4:]),'origem':origem,'id':k,'nome':v[0],'cpf':v[1],'salario':v[2],'bruto_total':v[3],'cargo':v[4] if len(v)>4 else '','orgsup':v[5] if len(v)>5 else '','org':v[6] if len(v)>6 else ''})
    return nm,rows,n,n50
if __name__=='__main__':
    files=[]
    for pat in PAT.split(','): files+=glob.glob(D+'/'+pat)
    done=set()
    if os.path.exists(OUT+'.done'): done=set(open(OUT+'.done').read().split())
    files=[f for f in sorted(files) if os.path.basename(f) not in done]
    print(len(files),'arquivos',flush=True)
    with Pool(4) as pool, open(OUT,'a') as fo, open(OUT+'.done','a') as fd:
        for nm,rows,n,n50 in pool.imap_unordered(proc,files):
            for r in rows: fo.write(json.dumps(r,ensure_ascii=False)+'\n')
            fo.flush(); fd.write(nm+'\n'); fd.flush(); print(nm,n,n50,flush=True)
