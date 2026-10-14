import zipfile,csv,io,json,collections,re,os
D='/media/hitsuzen/Novo volume/money/dados_portal/cvm'
csv.field_size_limit(10**7)
dg=lambda s:re.sub(r'\D','',s or '')
cad={}; adm={}
with open(D+'/cad_fi.csv',encoding='latin1',newline='') as f:
    for r in csv.DictReader(f,delimiter=';'):
        k=dg(r['CNPJ_FUNDO']); cad[k]=(r.get('GESTOR') or '').strip(); adm[k]=(r.get('ADMIN') or '').strip()
zr=zipfile.ZipFile(D+'/registro.zip'); gest={}; admn={}
with zr.open('registro_fundo.csv') as fh:
    for r in csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'):
        gest[r['ID_Registro_Fundo']]=(r.get('Gestor') or '').strip(); admn[r['ID_Registro_Fundo']]=(r.get('Administrador') or '').strip()
with zr.open('registro_classe.csv') as fh:
    for r in csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'):
        k=dg(r['CNPJ_Classe'])
        if k:
            if gest.get(r['ID_Registro_Fundo']): cad[k]=gest[r['ID_Registro_Fundo']]
            if admn.get(r['ID_Registro_Fundo']): adm[k]=admn[r['ID_Registro_Fundo']]
GR=[('ITAU','Itaú Unibanco'),('KINEA','Itaú Unibanco'),('ARX ','Itaú Unibanco'),('BRADESCO','Bradesco'),('BRAM','Bradesco'),('BB GESTAO','Banco do Brasil'),('BB DTVM','Banco do Brasil'),('BANCO DO BRASIL','Banco do Brasil'),('BB ASSET','Banco do Brasil'),
 ('FUNCEF','Funcef'),('CAIXA','Caixa Econômica'),('SANTANDER','Santander'),('FRANKLIN','Franklin Templeton'),('TEMPLETON','Franklin Templeton'),('BTG','BTG Pactual'),('SAFRA','Safra'),('XP ','XP'),('XP.','XP'),
 ('VOTORANTIM','Votorantim/BV'),('BV ','Votorantim/BV'),('SICREDI','Sicredi'),('SICOOB','Sicoob'),('GENIAL','Genial'),('VINCI','Vinci'),('INTER ','Inter'),('MODAL','Modal'),('VERDE','Verde'),('GALAPAGOS','Galapagos'),('JGP','JGP'),
 ('WESTERN','Western Asset'),('CLARITAS','Claritas'),('SPARTA','Sparta'),('PORTO','Porto Seguro'),('SULAMERICA','SulAmérica'),('MAPFRE','Mapfre'),('HSBC','HSBC'),('CITIBANK','Citi'),('JP MORGAN','JP Morgan'),('BNP','BNP Paribas'),('ICATU','Icatu'),('PREVI','Previ'),('PETROS','Petros'),('BRADESCO','Bradesco')]
def grupo(n):
    if not n: return 'Sem gestor'
    u=n.upper()+' '
    for k,g in GR:
        if k in u: return g
    return n.title()[:40]
res={}
def proc(zpath,mf):
    z=zipfile.ZipFile(zpath); nm=[n for n in z.namelist() if 'BLC_1' in n][0]
    by=collections.defaultdict(float); semg=collections.defaultdict(float); funds=collections.defaultdict(lambda:collections.defaultdict(float)); semadm={}
    with z.open(nm) as fh:
        rd=csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';')
        for r in rd:
            if not r['DT_COMPTC'].startswith(mf) or r['TP_APLIC']!='Títulos Públicos': continue
            try: v=float(r['VL_MERC_POS_FINAL'] or 0)
            except ValueError: continue
            k=dg(r.get('CNPJ_FUNDO') or r.get('CNPJ_FUNDO_CLASSE'))
            g=grupo(cad.get(k,''))
            by[g]+=v
            den=r.get('DENOM_SOCIAL','')
            if g=='Sem gestor':
                semg[(k,den)]+=v; semadm[k]=adm.get(k,'')
            elif g in ('Bradesco','Itaú Unibanco','Santander','Franklin Templeton','BTG Pactual','Safra','Funcef'):
                funds[g][den]+=v
    return {'groups':dict(by),'sem_gestor':[[d,k,v,semadm.get(k,'')] for (k,d),v in sorted(semg.items(),key=lambda x:-x[1])[:40]],'funds':{g:sorted(d.items(),key=lambda x:-x[1])[:12] for g,d in funds.items()}}
for y in range(2005,2023):
    p=f'{D}/hist_{y}.zip'
    if os.path.exists(p): res[f'{y}-12']=proc(p,f'{y}-12'); print(y,round(sum(res[f'{y}-12']['groups'].values())/1e9),flush=True)
for m,mf in (('202312','2023-12'),('202412','2024-12'),('202512','2025-12'),('202608','2026-08')):
    p=f'{D}/m_{m}.zip'
    if os.path.exists(p): res[mf]=proc(p,mf); print(mf,round(sum(res[mf]['groups'].values())/1e9),flush=True)
json.dump(res,open('cvm_groups.json','w'),ensure_ascii=False)
