import json,os,re,collections,datetime,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
X='/media/hitsuzen/Novo volume/money/arrecadacao_despesas_2019_2026.xlsx'
Y=list(range(2016,2027)); Yc=[str(y) for y in Y]
J=lambda f:json.load(open(f))
# ---------- IPCA ----------
ip=J('ipca.json'); idx=100.0; byyear=collections.defaultdict(list)
for r in ip:
    d,m,y=r['data'].split('/'); idx*=1+float(r['valor'])/100; byyear[int(y)].append(idx)
mean={y:sum(v)/len(v) for y,v in byyear.items()}
fac={y:mean[2025]/mean[y] for y in Y}
# ---------- gastos por funcao ----------
fc=J('func_cache.json'); F=collections.defaultdict(lambda:collections.defaultdict(float)); nmes=collections.defaultdict(set)
for k,v in fc.items():
    y=int(k[:4]); nmes[y].add(k[4:6])
    for f,(p,r) in v.items(): F[f][y]+=(p+r)/1e9
d2=J('desp2_cache.json'); juros=collections.defaultdict(float); refin=collections.defaultdict(float); resg=collections.defaultdict(float)
orgp=collections.defaultdict(float)
for k,v in d2.items():
    y=int(k[:4])
    for kk,x in v['enc'].items():
        if kk.startswith('Juros e Encargos da Dívida|'): juros[y]+=x/1e9
        elif kk.startswith('Amortização/Refinanciamento da Dívida|Principal Corrigido'): refin[y]+=x/1e9
        elif kk.startswith('Amortização/Refinanciamento da Dívida|Principal') and 'Resgatado' in kk: resg[y]+=x/1e9
    for kk,x in v['org'].items():
        o,g=kk.rsplit('|',1)
        if g.startswith('Pessoal'):
            orgp['total_exec']+=0; orgp[(y,'exec')]+=x/1e9
            if o=='Ministério da Defesa': orgp[(y,'defesa')]+=x/1e9
# ---------- RTN ----------
wb=openpyxl.load_workbook('raw/rtn.xlsx',data_only=True,read_only=True)
A=list(wb['2.2'].iter_rows(values_only=True)); M=list(wb['1.2'].iter_rows(values_only=True))
col={y:i for i,y in enumerate(A[4]) if isinstance(y,int)}
mcols=[(i,d) for i,d in enumerate(M[4]) if isinstance(d,datetime.datetime) and d.year==2026]
def rtn(code):
    r=next(r for r in A if r[0] and str(r[0]).split()[0]==code)
    out={y:r[col[y]]/1000 for y in col if 2016<=y<=2025}
    mr=next(r for r in M if r[0] and str(r[0]).split()[0]==code)
    out[2026]=sum(mr[i] for i,d in mcols if d.month<=7 and isinstance(mr[i],(int,float)))/1000
    return out
BPC=rtn('4.3.05'); BF=rtn('4.4.1.2'); PESS=rtn('4.2'); OUTR=rtn('4.3.12'); INSS=rtn('4.1')
SUB=J('rtn_sub.json')
agro_sub={y:sum(SUB[k].get(str(y),0) for k in ('Equalização custeio agropecuário','Equalização invest. rural e agroindustrial','Pronaf','Proagro')) for y in range(2016,2026)}
# ---------- renuncias ----------
T=J('ren_top.json'); AG=J('agro.json')
ren={y:T[str(y)]['total']/1e9 for y in range(2016,2025)}
nemp={y:T[str(y)]['n'] for y in range(2016,2025)}
agro={y:sum(g['valor'] for g in AG[str(y)]['agro'].values())/1e9 for y in range(2016,2025)}
nagro={y:sum(g['empresas'] for g in AG[str(y)]['agro'].values()) for y in range(2016,2025)}
# ---------- militares ----------
mc=J('mil_cache.json'); G={'Militares':'ativa','Reserva_Reforma_Militares':'reserva','Pensionistas_DEFESA':'pens'}
mv=collections.defaultdict(lambda:collections.defaultdict(float)); mn=collections.defaultdict(lambda:collections.defaultdict(list))
for k,v in mc.items():
    m=re.match(r'(\d{4})(\d{2})_(.+)\.zip',k); y=int(m[1]); g=G[m[3]]
    mv[g][y]+=v['bruto_total']/1e9; mn[g][y].append(v['n'])
dc=J('desp_cache.json'); DM={'Ativa':'ativa','Inativos (reserva/reforma)':'reserva','Pensionistas':'pens'}
for k,v in dc.items():
    y=int(k[:4])
    for g,x in v.items():
        if y<2020 and DM[g]!='ativa': mv[DM[g]][y]+=x/1e9
mil_val={g:{y:mv[g][y] for y in Y if mv[g].get(y)} for g in ('ativa','reserva','pens')}
mil_n={g:{y:sum(l)/len(l) for y,l in mn[g].items()} for g in ('ativa','reserva','pens')}
# ---------- juros BC ----------
L=lambda s:{r['data'][3:]:float(r['valor']) for r in J(f'sgs_{s}.json')}
nom,pri,pib=L(5727),L(5793),L(4382)
jbc={}
for y in range(2016,2026):
    k=f'12/{y}'; jbc[y]=(nom[k]-pri[k])/100*pib[k]/1000
last=sorted((k for k in nom if k.endswith('/2026')),key=lambda s:int(s[:2]))[-1]
jbc[2026]=(nom[last]-pri[last])/100*pib[last]/1000
# ---------- pessoas ----------
ben=J('ben.json'); wbk=J('wb_enrl.json')
inep=J('inep_basica.json') if os.path.exists('inep_basica.json') else {}
pop={2016:206081432,2017:207660929,2018:208494900,2019:210147125,2020:211755692,2021:213317639,2024:212583750,2025:213421037}
pop[2022]=pop[2021]+(pop[2024]-pop[2021])/3; pop[2023]=pop[2021]+2*(pop[2024]-pop[2021])/3; pop[2026]=pop[2025]*1.004
planos={2016:47.7,2017:47.3,2018:47.3,2019:47.1,2020:47.6,2021:49.1,2022:50.5,2023:51.0,2024:52.1,2025:53.1}
mat={y:inep.get(str(y)) for y in Y}
for y in Y:
    if not mat.get(y):
        a=wbk['Fundamental I (primário)'].get(str(y)); b=wbk['Fund. II + Médio (secundário)'].get(str(y)); p=wbk['Pré-escola'].get(str(y))
        mat[y]=(a+b+(p or 4.9e6))*0+ (a+b) if (a and b) else None  # fallback: so fund+medio (nao inclui infantil)
sup=J('inep_sup.json') if os.path.exists('inep_sup.json') else {}
# ---------- governos ----------
gov={2016:'Dilma→Temer',2017:'Temer',2018:'Temer',2019:'Bolsonaro',2020:'Bolsonaro',2021:'Bolsonaro',2022:'Bolsonaro',2023:'Lula 3',2024:'Lula 3',2025:'Lula 3',2026:'Lula 3 (parcial)'}
ROWS=[]  # (secao,label,{y:valor_nominal_bi},tipo) tipo: 'val' (deflaciona) | 'n' | 'pp'
def add(sec,label,d,kind='val',fmt='#,##0.0',bold=False): ROWS.append((sec,label,d,kind,fmt,bold))
S1='1) QUANTO FOI DESTINADO (R$ bilhões)'
add(S1,'Educação (União)',F['Educação'],bold=True)
add(S1,'Saúde (União)',F['Saúde'],bold=True)
add(S1,'Segurança pública (União)',F['Segurança pública'],bold=True)
add(S1,'Assistência social (União) – total',F['Assistência social'],bold=True)
add(S1,'   dos quais BPC',BPC)
add(S1,'   dos quais Bolsa Família / Auxílio Brasil',BF)
add(S1,'Isenção fiscal a empresas (renúncia declarada, todos setores)',ren,bold=True)
add(S1,'   dos quais agro (agropecuária + agroindústria + insumos)',agro)
add(S1,'Subsídios e crédito rural no orçamento (Pronaf, Proagro, equalização)',agro_sub)
add(S1,'Pagamento da dívida – juros e encargos (orçamento, caixa)',juros,bold=True)
add(S1,'   juros nominais do setor público (Banco Central, competência)',jbc)
add(S1,'Rolagem da dívida – principal refinanciado',refin,bold=True)
add(S1,'   principal efetivamente resgatado (pago)',resg)
exec_p={y:orgp[(y,'exec')] for y in Y if (y,'exec') in orgp}
add(S1,'Pessoal do Executivo civil e militar (orçamento)',exec_p,bold=True)
add(S1,'Pessoal de Legislativo+Judiciário+MPU+DPU (RTN total menos Executivo)',{y:PESS[y]-exec_p[y] for y in exec_p if y in PESS})
add(S1,'Legislativo/Judiciário/MPU/DPU – custeio e capital (RTN)',OUTR)
cam={2016:5.198,2017:5.336,2018:5.442,2019:5.778,2020:5.677,2021:5.697,2022:5.724,2023:6.100,2024:6.504,2025:7.014}
sen={2016:3.84,2017:4.06,2018:4.11,2019:4.32,2020:4.29,2021:4.33,2022:4.34,2023:4.61,2024:5.28,2025:5.86,2026:4.55}
add(S1,'Legislativo – Câmara dos Deputados (pago; 2026 n/d)',cam,bold=True)
add(S1,'Legislativo – Senado Federal (pago; 2026 até set.)',sen,bold=True)
add(S1,'   Câmara + Senado (TCU não incluído)',{y:cam[y]+sen[y] for y in cam})
add(S1,'Militares – ativa',mil_val['ativa'],bold=True)
add(S1,'Militares – reserva/reforma',mil_val['reserva'],bold=True)
add(S1,'Militares – pensionistas',mil_val['pens'],bold=True)
add(S1,'INSS – benefícios previdenciários (RGPS)',INSS)
S2='2) QUANTAS PESSOAS / EMPRESAS'
add(S2,'Matrículas educação básica (milhões, todas as redes; INEP, 2023 aprox.)',{y:(mat[y]/1e6 if mat.get(y) else None) for y in Y},'n','#,##0.0')
add(S2,'Matrículas ensino superior (milhões; aprox., conferir no INEP)',{y:sup.get(str(y))/1e6 for y in Y if sup.get(str(y))},'n','#,##0.0')
add(S2,'População sem plano de saúde – dependente do SUS (milhões, estimativa)',{y:pop[y]/1e6-planos[y] for y in Y if y in planos},'n','#,##0.0')
add(S2,'População total (milhões)',{y:pop[y]/1e6 for y in Y},'n','#,##0.0')
add(S2,'BPC – benefícios em dezembro (milhões)',{y:ben['bpc'][str(y)]/1e6 for y in Y if str(y) in ben['bpc']},'n','#,##0.00')
add(S2,'Bolsa Família/Auxílio Brasil – famílias em dezembro (milhões)',{y:ben['bf'][str(y)]/1e6 for y in Y if str(y) in ben['bf']},'n','#,##0.00')
add(S2,'Empresas com isenção fiscal declarada (nº)',nemp,'n','#,##0')
add(S2,'   das quais do agro (nº, 3 grupos)',nagro,'n','#,##0')
add(S2,'Militares da ativa (média mensal, mil)',{y:v/1e3 for y,v in mil_n['ativa'].items()},'n','#,##0.0')
add(S2,'Militares da reserva/reforma (mil)',{y:v/1e3 for y,v in mil_n['reserva'].items()},'n','#,##0.0')
add(S2,'Pensionistas militares (mil)',{y:v/1e3 for y,v in mil_n['pens'].items()},'n','#,##0.0')
add(S2,'Parlamentares (deputados + senadores, nº)',{y:594 for y in range(2016,2026)},'n','#,##0')
S3='3) VALOR POR PESSOA / EMPRESA (R$ por ano; reais de 2025 na aba real)'
def div(num,den,mult=1e9): return {y:num[y]*mult/den[y] for y in num if y in den and den[y]}
R=lambda lab: next(r for r in ROWS if r[1]==lab)[2]
mat_b={y:mat[y] for y in Y if mat.get(y)}
add(S3,'Educação federal por matrícula básica (R$/aluno) – ref. apenas',div(F['Educação'],mat_b),'pp','#,##0')
sus={y:(pop[y]-planos[y]*1e6) for y in Y if y in planos}
add(S3,'Saúde federal por dependente do SUS (R$/pessoa)',div(F['Saúde'],sus),'pp','#,##0')
add(S3,'Segurança federal por habitante (R$)',div(F['Segurança pública'],pop),'pp','#,##0')
add(S3,'BPC por benefício (R$/ano)',div(BPC,{y:ben['bpc'][str(y)] for y in range(2019,2026)}),'pp','#,##0')
add(S3,'Bolsa Família por família (R$/ano)',div(BF,{y:ben['bf'][str(y)] for y in range(2016,2026)}),'pp','#,##0')
add(S3,'Isenção por empresa beneficiada (R$ mil/ano)',div(ren,nemp,1e6),'pp','#,##0')
add(S3,'Isenção agro por empresa do agro (R$ mil/ano)',div(agro,nagro,1e6),'pp','#,##0')
add(S3,'Militar da ativa – média por pessoa (R$/ano)',div(mil_val['ativa'],mil_n['ativa']),'pp','#,##0')
add(S3,'Militar reserva/reforma – média por pessoa (R$/ano)',div(mil_val['reserva'],mil_n['reserva']),'pp','#,##0')
add(S3,'Pensionista militar – média por pessoa (R$/ano)',div(mil_val['pens'],mil_n['pens']),'pp','#,##0')
add(S3,'Câmara+Senado por parlamentar (R$ milhões/ano)',div({y:cam[y]+sen[y] for y in cam},{y:594 for y in cam},1e3),'pp','#,##0.0')
add(S3,'Juros da dívida (orçamento) por habitante (R$)',div(juros,pop),'pp','#,##0')
# ---------- escrever ----------
hdr=PatternFill('solid',fgColor='1F3864'); grp=PatternFill('solid',fgColor='D9E1F2'); gfill={'Dilma→Temer':'F8CBAD','Temer':'F8CBAD','Bolsonaro':'FFE699','Lula 3':'C6E0B4','Lula 3 (parcial)':'C6E0B4'}
wbk2=openpyxl.load_workbook(X)
for n in ('Mapa por governo','Resumo por governo','Mapa nominal'):
    if n in wbk2.sheetnames: del wbk2[n]
def write(ws,real):
    ws['A1']='Mapa ano a ano: quanto cada governo destinou e a quantas pessoas/empresas'; ws['A1'].font=Font(bold=True,size=14)
    ws['A2']=('Valores '+('REAIS, corrigidos pelo IPCA para a média de 2025' if real else 'NOMINAIS')+'. Só gastos da União (estados e municípios não incluídos). '
              '2026 = parcial (despesas jan–out; BPC/Bolsa Família jan–jul; isenções 2025–2026 ainda não publicadas). Brancos = dado não disponível.')
    ws['A2'].font=Font(italic=True,size=9); ws['A2'].alignment=Alignment(wrap_text=True); ws.row_dimensions[2].height=32
    ws.cell(row=4,column=1,value='Governo').font=Font(bold=True)
    for j,y in enumerate(Y):
        c=ws.cell(row=4,column=2+j,value=gov[y]); c.fill=PatternFill('solid',fgColor=gfill[gov[y]]); c.font=Font(bold=True,size=9); c.alignment=Alignment(horizontal='center',wrap_text=True)
        c=ws.cell(row=5,column=2+j,value=str(y)+(' *' if y==2026 else '')); c.fill=hdr; c.font=Font(bold=True,color='FFFFFF'); c.alignment=Alignment(horizontal='center')
    ws.cell(row=5,column=1,value='Item').fill=hdr; ws.cell(row=5,column=1).font=Font(bold=True,color='FFFFFF')
    r=6; cur=None
    for sec,lab,d,kind,fmt,bold in ROWS:
        if sec!=cur:
            cur=sec; ws.cell(row=r,column=1,value=sec).font=Font(bold=True)
            for c in range(1,len(Y)+2): ws.cell(row=r,column=c).fill=grp
            r+=1
        ws.cell(row=r,column=1,value=lab).font=Font(bold=bold)
        for j,y in enumerate(Y):
            v=d.get(y)
            if v is None: continue
            if kind in ('val','pp') and real: v=v*fac[y]
            if kind=='pp' and not real:
                pass
            c=ws.cell(row=r,column=2+j,value=round(v,2)); c.number_format=fmt
        r+=1
    ws.column_dimensions['A'].width=70
    for j in range(len(Y)): ws.column_dimensions[openpyxl.utils.get_column_letter(2+j)].width=12
    ws.freeze_panes='B6'
ws=wbk2.create_sheet('Mapa por governo',0); write(ws,True)
ws=wbk2.create_sheet('Mapa nominal',1); write(ws,False)
# ---------- resumo por governo ----------
ws=wbk2.create_sheet('Resumo por governo',1)
ws['A1']='Média anual por governo (R$ bilhões de 2025) – anos completos'; ws['A1'].font=Font(bold=True,size=14)
ws['A2']='Temer = 2016–2018 (2016 inclui jan–mai de Dilma); Bolsonaro = 2019–2022; Lula 3 = 2023–2025 (2026 parcial, fora da média). Isenções: 2024 é parcial e 2025 não foi publicada, então a média de Lula 3 usa só 2023.'; ws['A2'].font=Font(italic=True,size=9)
G=[('Temer (2016–18)',[2016,2017,2018]),('Bolsonaro (2019–22)',[2019,2020,2021,2022]),('Lula 3 (2023–25)',[2023,2024,2025])]
for c,v in enumerate(['Item']+[g[0] for g in G]+['Lula vs Bolsonaro','Bolsonaro vs Temer'],1):
    x=ws.cell(row=4,column=c,value=v); x.fill=hdr; x.font=Font(bold=True,color='FFFFFF'); x.alignment=Alignment(horizontal='center',wrap_text=True)
r=5; cur=None
for sec,lab,d,kind,fmt,bold in ROWS:
    if sec!=cur:
        cur=sec; ws.cell(row=r,column=1,value=sec).font=Font(bold=True)
        for c in range(1,7): ws.cell(row=r,column=c).fill=grp
        r+=1
    avgs=[]
    for g,ys in G:
        partial=any(k in lab for k in ('Isenção','isenção','agro','Empresas com'))
        vals=[(d[y]*(fac[y] if kind in ('val','pp') else 1)) for y in ys if d.get(y) is not None and not (partial and y>=2024)]
        avgs.append(sum(vals)/len(vals) if len(vals)>=1 and (len(vals)>=2 or partial) else None)
    ws.cell(row=r,column=1,value=lab).font=Font(bold=bold)
    for j,v in enumerate(avgs):
        if v is not None: ws.cell(row=r,column=2+j,value=round(v,2)).number_format=fmt
    if avgs[2] is not None and avgs[1]: 
        c=ws.cell(row=r,column=5,value=avgs[2]/avgs[1]-1); c.number_format='+0%;-0%'
    if avgs[1] is not None and avgs[0]:
        c=ws.cell(row=r,column=6,value=avgs[1]/avgs[0]-1); c.number_format='+0%;-0%'
    r+=1
ws.column_dimensions['A'].width=70
for c in 'BCDEF': ws.column_dimensions[c].width=18
wbk2.save(X); print('ok')
for sec,lab,d,kind,fmt,bold in ROWS[:6]: print(lab,[round(d[y]*fac[y]) if d.get(y) is not None else None for y in Y])
json.dump({'rows':[{'sec':s,'label':l,'kind':k,'data':{str(y):v for y,v in d.items() if v is not None}} for s,l,d,k,f,b in ROWS],'fac':{str(y):fac[y] for y in Y},'gov':{str(y):gov[y] for y in Y}},open('rows_dump.json','w'),ensure_ascii=False)
print('dump ok')
