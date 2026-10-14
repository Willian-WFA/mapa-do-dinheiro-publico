import zipfile,csv,io,json,collections,re,os,sys
D='/media/hitsuzen/Novo volume/money/dados_portal/cvm'
csv.field_size_limit(10**7)
dg=lambda s:re.sub(r'\D','',s or '')
cad={}
with open(D+'/cad_fi.csv',encoding='latin1',newline='') as f:
    for r in csv.DictReader(f,delimiter=';'):
        cad[dg(r['CNPJ_FUNDO'])]=(r.get('GESTOR') or '').strip() or (r.get('ADMIN') or '').strip()
zr=zipfile.ZipFile(D+'/registro.zip')
gest={}
with zr.open('registro_fundo.csv') as fh:
    for r in csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'):
        gest[r['ID_Registro_Fundo']]=(r.get('Gestor') or '').strip() or (r.get('Administrador') or '').strip()
with zr.open('registro_classe.csv') as fh:
    for r in csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';'):
        k=dg(r['CNPJ_Classe'])
        if k and gest.get(r['ID_Registro_Fundo']): cad[k]=gest[r['ID_Registro_Fundo']]
GR=[('ITAU','Itaú Unibanco'),('KINEA','Itaú Unibanco'),('BRADESCO','Bradesco'),('BRAM','Bradesco'),('BB GESTAO','Banco do Brasil'),('BB DTVM','Banco do Brasil'),('BANCO DO BRASIL','Banco do Brasil'),('BB ASSET','Banco do Brasil'),
    ('CAIXA','Caixa Econômica'),('SANTANDER','Santander'),('BTG','BTG Pactual'),('XP ','XP'),('XP.','XP'),('SAFRA','Safra'),('VOTORANTIM','Votorantim/BV'),('BV ','Votorantim/BV'),
    ('SICREDI','Sicredi'),('SICOOB','Sicoob'),('GENIAL','Genial'),('VINCI','Vinci'),('INTER ','Inter'),('MODAL','Modal'),('ARX','Itaú Unibanco'),('VERDE','Verde'),('GALAPAGOS','Galapagos'),('JGP','JGP'),('ASA ','ASA'),
    ('WESTERN','Western Asset'),('CLARITAS','Claritas'),('SPARTA','Sparta'),('PORTO','Porto Seguro'),('SULAMERICA','SulAmérica'),('MAPFRE','Mapfre'),('HSBC','HSBC'),('CITIBANK','Citi'),('JP MORGAN','JP Morgan'),('BNP','BNP Paribas'),('ICATU','Icatu'),('PREVI','Previ/fundos de pensão'),('FUNCEF','Funcef'),('PETROS','Petros')]
def grupo(n):
    u=(n or 'SEM GESTOR').upper()+' '
    for k,g in GR:
        if k in u: return g
    return n.title()[:38] if n else 'Sem gestor'
res={}
def proc(zpath,mfilter):
    z=zipfile.ZipFile(zpath); nm=[n for n in z.namelist() if 'BLC_1' in n][0]
    by=collections.defaultdict(float); tipo=collections.defaultdict(float); comp=0.0; tot=0.0
    with z.open(nm) as fh:
        rd=csv.DictReader(io.TextIOWrapper(fh,encoding='latin1',newline=''),delimiter=';')
        for r in rd:
            if not r['DT_COMPTC'].startswith(mfilter): continue
            try: v=float(r['VL_MERC_POS_FINAL'] or 0)
            except ValueError: continue
            if r['TP_APLIC']=='Títulos Públicos':
                g=grupo(cad.get(dg(r.get('CNPJ_FUNDO') or r.get('CNPJ_FUNDO_CLASSE')),''))
                by[g]+=v; tot+=v; tipo[r['TP_TITPUB'][:40]]+=v
            else: comp+=v
    top=sorted(by.items(),key=lambda x:-x[1])[:15]
    return {'total':tot,'compromissadas':comp,'top':top,'tipo':sorted(tipo.items(),key=lambda x:-x[1])[:6],'n_gestores':len(by)}
for y in range(2016,2023):
    res[f'{y}-12']=proc(f'{D}/hist_{y}.zip',f'{y}-12'); print(y,round(res[f'{y}-12']['total']/1e9),flush=True)
for m,mf in (('202312','2023-12'),('202412','2024-12'),('202512','2025-12'),('202608','2026-08')):
    res[mf]=proc(f'{D}/m_{m}.zip',mf); print(mf,round(res[mf]['total']/1e9),flush=True)
json.dump(res,open('cvm_pos.json','w'),ensure_ascii=False)
for k in ('2019-12','2025-12'):
    print(k,[(g,round(v/1e9)) for g,v in res[k]['top'][:8]])
