import json,collections,re,datetime,openpyxl
J=lambda f:json.load(open(f))
YA=list(range(1995,2027))
# ---------- IPCA ----------
ip=J('ipca_full.json'); idx=100.0; by=collections.defaultdict(list)
for r in ip:
    d,m,y=r['data'].split('/'); idx*=1+float(r['valor'])/100; by[int(y)].append(idx)
mean={y:sum(v)/len(v) for y,v in by.items()}
fac={y:mean[2025]/mean[y] for y in YA}
GOV={}
for y in YA:
    GOV[y]=('FHC' if y<=2002 else 'Lula 1' if y<=2006 else 'Lula 2' if y<=2010 else 'Dilma 1' if y<=2014 else 'Dilma 2' if y==2015 else 'Dilma→Temer' if y==2016 else 'Temer' if y<=2018 else 'Bolsonaro' if y<=2022 else 'Lula 3' if y<=2025 else 'Lula 3 (parcial)')
# ---------- funcao ----------
F=collections.defaultdict(lambda:collections.defaultdict(float))
for k,v in J('func_cache.json').items():
    y=int(k[:4])
    for f,(p,r) in v.items(): F[f][y]+=(p+r)/1e9
d2=J('desp2_cache.json'); juros=collections.defaultdict(float); refin=collections.defaultdict(float); resg=collections.defaultdict(float); exe=collections.defaultdict(float)
for k,v in d2.items():
    y=int(k[:4])
    for kk,x in v['enc'].items():
        if kk.startswith('Juros e Encargos da Dívida|'): juros[y]+=x/1e9
        elif kk.startswith('Amortização/Refinanciamento da Dívida|Principal Corrigido'): refin[y]+=x/1e9
        elif kk.startswith('Amortização/Refinanciamento da Dívida|Principal') and 'Resgatado' in kk: resg[y]+=x/1e9
    for kk,x in v['org'].items():
        if kk.rsplit('|',1)[1].startswith('Pessoal'): exe[y]+=x/1e9
# ---------- extensao: Tesouro mensal (2008+) e Ipea GSF (1995-2010) ----------
tes=J('tes_mensal_func.json')['func']
TMAP={'SAUDE':'Saúde','EDUCACAO':'Educação','ASSISTENCIA SOCIAL':'Assistência social','SEGURANCA PUBLICA':'Segurança pública','PREVIDENCIA SOCIAL':'Previdência social','DEFESA NACIONAL':'Defesa nacional'}
LEG={}
for y,d in tes.items():
    y=int(y)
    if y<2008 or y>2013: pass
    for k,v in d.items():
        if k in TMAP and 2008<=y<=2013: F[TMAP[k]][y]=v/1e9
        if k=='LEGISLATIVA' and y<=2018: LEG[y]=v/1e9
ipea=J('ipea_gsf.json'); IP={}
im={}
for r_ in ip:
    d_,m_,y_=r_['data'].split('/'); im[(int(y_),int(m_))]=0
_i=100.0; idxm={}
for r_ in ip:
    d_,m_,y_=r_['data'].split('/'); _i*=1+float(r_['valor'])/100; idxm[(int(y_),int(m_))]=_i
def to_nom(real,y): return real*mean[y]/idxm[(2011,12)]
for nome,k in (('Saúde','Saúde'),('Educação','Educação'),('Assistência social','Assistência Social')):
    for y,v in zip(ipea['anos'],ipea['dez2011'][k]):
        if y<2008: F[nome][y]=to_nom(v,y)
        IP.setdefault(nome,{})[y]=to_nom(v,y)
# ---------- RTN ----------
wb=openpyxl.load_workbook('raw/rtn.xlsx',data_only=True,read_only=True)
A=list(wb['2.2'].iter_rows(values_only=True)); M=list(wb['1.2'].iter_rows(values_only=True))
col={y:i for i,y in enumerate(A[4]) if isinstance(y,int)}
mc=[(i,d) for i,d in enumerate(M[4]) if isinstance(d,datetime.datetime) and d.year==2026]
def rtn(code,neg=False,drop_leading_zero=True):
    r=next(r for r in A[5:] if r[0] and (str(r[0]).split()[0]==code))
    out={y:(r[c]/1000)*(-1 if neg else 1) for y,c in col.items() if isinstance(r[c],(int,float))}
    try:
        mr=next(r for r in M[5:] if r[0] and str(r[0]).split()[0]==code)
        vs=[mr[i] for i,d in mc if d.month<=7 and isinstance(mr[i],(int,float))]
        if vs: out[2026]=sum(vs)/1000*(-1 if neg else 1)
    except StopIteration: pass
    if drop_leading_zero:
        first=min((y for y,v in out.items() if abs(v)>1e-9),default=None)
        out={y:v for y,v in out.items() if first is not None and y>=first}
    return out
R={}
R['inss']=rtn('4.1'); R['arr']=rtn('1.3'); R['pess']=rtn('4.2'); R['legjud']=rtn('4.3.12'); R['bpc']=rtn('4.3.05'); R['bf']=rtn('4.4.1.2')
R['sub']=rtn('4.3.15'); R['pronaf']=rtn('4.3.15.1.4'); R['proagro']=rtn('4.3.15.2'); R['eqc']=rtn('4.3.15.1.1'); R['psi']=rtn('4.3.15.1.14')
R['saude_ob']=rtn('4.4.1.3'); R['saude_d']=rtn('4.4.2.1'); R['educ_ob']=rtn('4.4.1.4'); R['educ_d']=rtn('4.4.2.2'); R['seg_d']=rtn('4.4.2.7'); R['ass_d']=rtn('4.4.2.8'); R['def_d']=rtn('4.4.2.3')
R['fundeb']=rtn('4.3.10'); R['jur']=rtn('9.',neg=True)
def add(a,b): return {y:a.get(y,0)+b.get(y,0) for y in set(a)|set(b)}
R['saude']=add(R['saude_ob'],R['saude_d']); R['educ']=add(R['educ_ob'],R['educ_d'])
# ---------- outros ----------
ext=J('hist_ext.json'); jbc={int(y):v for y,v in ext['jbc'].items()}
for y,v in J('rows_dump.json') and []: pass
old=J('rows_dump.json'); orows={r['label']:{int(y):v for y,v in r['data'].items()} for r in old['rows']}
def O(prefix):
    for l,d in orows.items():
        if l.strip().startswith(prefix): return dict(d)
    raise KeyError(prefix)
jbc_all=dict(jbc); jbc_all[2026]=O('juros nominais do setor')[2026]
pop={int(y):v for y,v in ext['pop'].items()}
ks=sorted(pop)
for y in range(ks[0],ks[-1]+1):
    if y not in pop:
        lo=max(k for k in pop if k<y); hi=min(k for k in pop if k>y)
        pop[y]=pop[lo]+(pop[hi]-pop[lo])*(y-lo)/(hi-lo)
wbk={n:{int(y):v for y,v in d.items()} for n,d in ext['wb'].items()}
inep=J('inep_basica.json'); inep={int(y):v for y,v in inep.items() if v}
mat={}
for y in YA:
    if y in inep: mat[y]=inep[y]/1e6
    elif y in wbk['prim'] and y in wbk['sec']: mat[y]=(wbk['prim'][y]+wbk['sec'][y]+wbk['pre'].get(y,0))/1e6
sup_wb={y:v/1e6 for y,v in wbk['sup'].items()}
sup_ap={int(y):v/1e6 for y,v in J('inep_sup.json').items()}
sup={**sup_wb,**{y:v for y,v in sup_ap.items() if y>2018}}
planos={2016:47.7,2017:47.3,2018:47.3,2019:47.1,2020:47.6,2021:49.1,2022:50.5,2023:51.0,2024:52.1,2025:53.1}
sus={y:pop[y]/1e6-planos[y] for y in planos if y in pop}
# renuncias
rt=J('ren_top.json'); ag=J('agro.json')
ren={int(y):v['total']/1e9 for y,v in rt.items()}; nemp={int(y):v['n'] for y,v in rt.items()}
agro={int(y):sum(g['valor'] for g in v['agro'].values())/1e9 for y,v in ag.items()}
nagro={int(y):sum(g['empresas'] for g in v['agro'].values()) for y,v in ag.items()}
# militares
mc_=J('mil_cache.json'); G={'Militares':'ativa','Reserva_Reforma_Militares':'reserva','Pensionistas_DEFESA':'pens'}
mv=collections.defaultdict(lambda:collections.defaultdict(float)); mn=collections.defaultdict(lambda:collections.defaultdict(list))
for k,v in mc_.items():
    m=re.match(r'(\d{4})(\d{2})_(.+)\.zip',k); y=int(m[1]); g=G[m[3]]
    mv[g][y]+=v['bruto_total']/1e9; mn[g][y].append(v['n'])
DM={'Ativa':'ativa','Inativos (reserva/reforma)':'reserva','Pensionistas':'pens'}
dc=collections.defaultdict(lambda:collections.defaultdict(float))
for k,v in J('desp_cache.json').items():
    y=int(k[:4])
    for g,x in v.items(): dc[DM[g]][y]+=x/1e9
for g in ('ativa','reserva','pens'):
    for y,x in dc[g].items():
        if (y<2020 and g!='ativa') or (y<2016 and g=='ativa'): mv[g][y]=x
mil_val={g:{y:v for y,v in mv[g].items() if v} for g in mv}
mil_n={g:{y:sum(l)/len(l)/1e3 for y,l in mn[g].items()} for g in mn}
for y,n in J('mil_dec_old.json').items(): mil_n['ativa'][int(y)]=n/1e3
# legislativo
cam=O('Legislativo – Câmara'); cam[2015]=4.951
sen=O('Legislativo – Senado'); sen.update({2013:3.32,2014:3.45,2015:3.69})
ben=J('ben.json'); nbpc={int(y):v/1e6 for y,v in ben['bpc'].items()}; nbf={int(y):v/1e6 for y,v in ben['bf'].items()}
cv=J('cvm_pos.json'); fundos={int(p[:4]):v['total']/1e9 for p,v in cv.items()}
# ---------- linhas ----------
rows=[]
def row(sec,label,kind,d): rows.append({'sec':sec,'label':label,'kind':kind,'data':{str(y):v for y,v in sorted(d.items()) if v is not None}})
S1='1) QUANTO FOI DESTINADO (R$ bilhões)'; S2='2) QUANTAS PESSOAS / EMPRESAS'; S3='3) VALOR POR PESSOA / EMPRESA'
def mer(a,b): return {**b,**a}   # a tem prioridade
row(S1,'Educação (União)','val',F['Educação'])
row(S1,'Saúde (União)','val',F['Saúde'])
row(S1,'Segurança pública (União)','val',F['Segurança pública'])
row(S1,'Assistência social (União) – total','val',F['Assistência social'])
row(S1,'Função Legislativa – Câmara, Senado e TCU (Tesouro, até 2018)','val',LEG)
row(S1,'   dos quais BPC','val',R['bpc'])
row(S1,'   dos quais Bolsa Família / Auxílio Brasil','val',R['bf'])
row(S1,'Isenção fiscal a empresas (renúncia declarada, todos setores)','val',ren)
row(S1,'   dos quais agro (agropecuária + agroindústria + insumos)','val',agro)
row(S1,'Subsídios e crédito rural no orçamento (Pronaf, Proagro, equalização)','val',{y:R['pronaf'].get(y,0)+R['proagro'].get(y,0)+R['eqc'].get(y,0)+(J('rtn_sub.json')['Equalização invest. rural e agroindustrial'].get(str(y),0)) for y in R['pronaf'] if y<=2025})
row(S1,'Pagamento da dívida – juros e encargos (orçamento, caixa)','val',juros)
row(S1,'   juros nominais do setor público (Banco Central, competência)','val',jbc_all)
row(S1,'Rolagem da dívida – principal refinanciado','val',refin)
row(S1,'   principal efetivamente resgatado (pago)','val',resg)
row(S1,'Pessoal do Executivo civil e militar (orçamento)','val',{y:v for y,v in exe.items() if y<=2026})
row(S1,'Pessoal de todos os Poderes (RTN)','val',R['pess'])
row(S1,'Legislativo/Judiciário/MPU/DPU – custeio e capital (RTN)','val',R['legjud'])
row(S1,'Legislativo – Câmara dos Deputados (pago; 2026 n/d)','val',cam)
row(S1,'Legislativo – Senado Federal (pago; 2026 até set.)','val',sen)
row(S1,'   Câmara + Senado (TCU não incluído)','val',{y:cam[y]+sen[y] for y in cam if y in sen})
row(S1,'Militares – ativa','val',mil_val.get('ativa',{}))
row(S1,'Militares – reserva/reforma','val',mil_val.get('reserva',{}))
row(S1,'Militares – pensionistas','val',mil_val.get('pens',{}))
row(S1,'INSS – benefícios previdenciários (RGPS)','val',R['inss'])
row(S1,'INSS – arrecadação líquida do RGPS','val',R['arr'])
row(S1,'Juros nominais do Governo Central (RTN, abaixo da linha)','val',R['jur'])
row(S1,'Subsídios, subvenções e Proagro (RTN, total)','val',R['sub'])
row(S1,'Saúde – RTN (obrigatórias + discricionárias, sem pessoal)','val',R['saude'])
row(S1,'Educação – RTN (obrigatórias + discricionárias, sem pessoal)','val',R['educ'])
row(S1,'Segurança – RTN (discricionárias, sem pessoal)','val',R['seg_d'])
row(S1,'Assistência – RTN (discricionárias, sem BPC/BF)','val',R['ass_d'])
row(S1,'Complementação da União ao Fundeb (RTN)','val',R['fundeb'])
row(S1,'Títulos públicos nas carteiras de fundos (CVM, dezembro)','stock',fundos)
row(S1,'Pronaf (equalização, RTN)','val',R['pronaf'])
row(S1,'Proagro (RTN)','val',R['proagro'])
row(S1,'Equalização de custeio agropecuário (RTN)','val',R['eqc'])
row(S1,'Equalização de investimento rural (RTN)','val',rtn('4.1.15.1.2'))
row(S2,'Matrículas educação básica (milhões; INEP 2016+, Banco Mundial antes)','n',mat)
row(S2,'Matrículas ensino superior (milhões)','n',sup)
row(S2,'População sem plano de saúde – dependente do SUS (milhões, estimativa)','n',sus)
row(S2,'População total (milhões)','n',{y:v/1e6 for y,v in pop.items()})
row(S2,'BPC – benefícios em dezembro (milhões)','n',nbpc)
row(S2,'Bolsa Família/Auxílio Brasil – famílias em dezembro (milhões)','n',nbf)
row(S2,'Empresas com isenção fiscal declarada (nº)','n',nemp)
row(S2,'   das quais do agro (nº, 3 grupos)','n',nagro)
row(S2,'Militares da ativa (média mensal, mil)','n',mil_n.get('ativa',{}))
row(S2,'Militares da reserva/reforma (mil)','n',mil_n.get('reserva',{}))
row(S2,'Pensionistas militares (mil)','n',mil_n.get('pens',{}))
row(S2,'Parlamentares (deputados + senadores, nº)','n',{y:594 for y in range(2013,2026)})
dg=J('dgt_series.json')
row(S1,'Gastos tributários – Receita Federal (bases efetivas)','val',{int(y):v for y,v in dg['total'].items()})
row(S1,'Gastos tributários – projeção (edição DGT 2023)','val',{int(y):v for y,v in dg['proj'].items()})
row(S1,'Gastos tributários – previsão da PLOA do ano','val',{int(y):v for y,v in dg['ploa_total'].items()})
for nm in ('Agricultura','Saúde','Educação','Assistência Social','Trabalho','Indústria','Comércio e Serviço'):
    row(S1,'Gasto tributário – função '+nm,'val',{int(y):v for y,v in dg['fun'].get(nm,{}).items()})

# ---------- pessoas por beneficio / grupo ----------
ip_=J('inss_pessoas.json'); sc=J('siape_cache.json'); cp=J('count_progs.json'); tdu=J('td_uniq.json'); bc=J('ben_cache.json')
inssp={int(y):v for y,v in ip_['inss'].items()}
row(S2,'Benefícios do INSS emitidos – total (milhões; dez., 2026 = jul.)','n',{y:v[0]/1e6 for y,v in inssp.items()})
row(S2,'   previdenciários (RGPS) (milhões)','n',{y:v[1]/1e6 for y,v in inssp.items()})
row(S2,'   assistenciais – BPC/LOAS no INSS (milhões)','n',{y:v[2]/1e6 for y,v in inssp.items()})
row(S2,'   legislação especial (mil)','n',{y:v[3]/1e3 for y,v in inssp.items()})
def siape(kind):
    out={}
    for k,v in sc.items():
        if kind in k: out[int(k[:4])]=v['n']/1e3
    return out
def siape_org(kind,org):
    out={}
    for k,v in sc.items():
        if kind in k:
            for o,n in v['org']:
                if o==org: out[int(k[:4])]=n/1e3
    return out
row(S2,'Servidores civis ativos – SIAPE (mil, dezembro)','n',siape('Servidores_SIAPE'))
row(S2,'Servidores civis aposentados (mil, dezembro)','n',siape('Aposentados_SIAPE'))
row(S2,'Pensionistas civis (mil, dezembro)','n',siape('Pensionistas_SIAPE'))
row(S2,'   servidores ativos no Ministério da Educação (mil)','n',siape_org('Servidores_SIAPE','Ministério da Educação'))
ben_bc={}
for k,v in bc.items():
    ds,fn=k.split('/'); ym=fn[:6]
    if ds=='auxilio-brasil' and ym.endswith('12'): ben_bc[('ab',int(ym[:4]))]=v['unicos']
    if ds=='auxilio-emergencial': ben_bc[('ae',int(ym[:4]))]=v['unicos']
row(S2,'Auxílio Brasil – famílias em dezembro (milhões)','n',{y:v/1e6 for (t,y),v in ben_bc.items() if t=='ab'})
row(S2,'Auxílio Emergencial – pessoas em dez./2020 (milhões)','n',{y:v/1e6 for (t,y),v in ben_bc.items() if t=='ae'})
pdm={}
for ym,v in cp['pe_de_meia'].items():
    y=int(ym[:4])
    if ym.endswith('12') or ym==max(k for k in cp['pe_de_meia'] if k[:4]==ym[:4]): pdm[y]=v['unicos']/1e6
row(S2,'Pé-de-Meia – estudantes pagos no mês (milhões; dez., 2026 = jun.)','n',pdm)
gas={}
for ym,v in cp['gas'].items():
    y=int(ym[:4]); gas[y]=v['unicos']/1e6 if ym==max(k for k in cp['gas'] if k[:4]==ym[:4]) else gas.get(y)
row(S2,'Gás do Povo – famílias no mês (milhões; último mês do ano)','n',gas)
tdn={int(y):v['cadastrados']/1e6 for y,v in tdu.items() if y.isdigit()}
row(S2,'Tesouro Direto – novos cadastros por ano de adesão (milhões; códigos distintos)','n',tdn)
row(S2,'Tesouro Direto – desses, ainda ativos hoje (milhões)','n',{int(y):v['ativos']/1e6 for y,v in tdu.items() if y.isdigit()})
row(S2,'Tesouro Direto – desses, operaram nos últimos 12 meses (mil)','n',{int(y):v['operou12m']/1e3 for y,v in tdu.items() if y.isdigit()})
row(S2,'Gestoras (grupos) com títulos públicos em fundos (nº, dezembro)','n',{int(p[:4]):v['n_gestores'] for p,v in cv.items()})

D={r['label']:{int(y):v for y,v in r['data'].items()} for r in rows}
def div(a,b,m=1e9): return {y:a[y]*m/b[y] for y in a if y in b and b[y]}
pop_abs=pop
row(S3,'Educação federal por matrícula básica (R$/aluno) – ref. apenas','pp',div(F['Educação'],{y:v*1e6 for y,v in mat.items()}))
row(S3,'Saúde federal por dependente do SUS (R$/pessoa)','pp',div(F['Saúde'],{y:(pop[y]-planos[y]*1e6) for y in planos if y in pop}))
row(S3,'Segurança federal por habitante (R$)','pp',div(F['Segurança pública'],pop))
row(S3,'BPC por benefício (R$/ano)','pp',div(R['bpc'],{y:v*1e6 for y,v in nbpc.items()}))
row(S3,'Bolsa Família por família (R$/ano)','pp',div(R['bf'],{y:v*1e6 for y,v in nbf.items()}))
row(S3,'Isenção por empresa beneficiada (R$ mil/ano)','pp',div(ren,nemp,1e6))
row(S3,'Isenção agro por empresa do agro (R$ mil/ano)','pp',div(agro,nagro,1e6))
row(S3,'Militar da ativa – média por pessoa (R$/ano)','pp',div(mil_val.get('ativa',{}),{y:v*1e3 for y,v in mil_n.get('ativa',{}).items()}))
row(S3,'Militar reserva/reforma – média por pessoa (R$/ano)','pp',div(mil_val.get('reserva',{}),{y:v*1e3 for y,v in mil_n.get('reserva',{}).items() if y>=2020}))
row(S3,'Pensionista militar – média por pessoa (R$/ano)','pp',div(mil_val.get('pens',{}),{y:v*1e3 for y,v in mil_n.get('pens',{}).items() if y>=2020}))
row(S3,'Câmara+Senado por parlamentar (R$ milhões/ano)','pp',div({y:cam[y]+sen[y] for y in cam if y in sen},{y:594 for y in cam},1e3))
row(S3,'Juros da dívida (orçamento) por habitante (R$)','pp',div(juros,pop))
json.dump({'rows':rows,'fac':{str(y):fac[y] for y in YA},'gov':{str(y):GOV[y] for y in YA},'years':YA},open('hist_rows.json','w'),ensure_ascii=False)
print('ok',len(rows))
for r in rows[:6]+rows[22:26]: ys=sorted(map(int,r['data'])); print(r['label'][:60].ljust(60),ys[0],ys[-1],len(ys))
