import openpyxl, datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
src=openpyxl.load_workbook('raw/rtn.xlsx',data_only=True,read_only=True)
A=list(src['2.2'].iter_rows(values_only=True))
M=list(src['1.2'].iter_rows(values_only=True))
yrs=A[4]; ycol={y:i for i,y in enumerate(yrs) if isinstance(y,int)}
mh=M[4]
mcols={i:d for i,d in enumerate(mh) if isinstance(d,datetime.datetime)}
def find(rows,prefix,nth=0):
    k=0
    for r in rows:
        if r[0] and str(r[0]).strip().startswith(prefix):
            if k==nth: return r
            k+=1
    raise KeyError(prefix)
def ann(prefix,nth=0,neg=False):
    r=find(A,prefix,nth); s=-1 if neg else 1
    return {y:s*r[c]/1000 for y,c in ycol.items() if 2016<=y<=2025}
def ytd(prefix,nth=0,neg=False,upto=7):
    r=find(M,prefix,nth); s=-1 if neg else 1
    tot=0;n=0
    for i,d in mcols.items():
        if d.year==2026 and d.month<=upto and isinstance(r[i],(int,float)): tot+=r[i];n+=1
    return s*tot/1000 if n else None
def add(a,b): return {y:a[y]+b[y] for y in a}
rows=[]
def R(label,prefix,nth=0,neg=False,group=''):
    d=ann(prefix,nth,neg); d[2026]=ytd(prefix,nth,neg); rows.append((group,label,d))
def Rsum(label,pairs,group=''):
    d=None; y26=0
    for p,n in pairs:
        a=ann(p,n); d=a if d is None else add(d,a); y26+=ytd(p,n)
    d[2026]=y26; rows.append((group,label,d))
R('Receita total do Governo Central (caixa)','1. RECEITA TOTAL',group='ARRECADAÇÃO (União)')
R('  Receita administrada pela Receita Federal (impostos e contribuições)','1.1 -  Receita Administrada')
R('  Arrecadação líquida para o RGPS (contribuições INSS)','1.3 -  Arrecadação Líquida')
R('  Receitas não administradas (royalties, dividendos, concessões)','1.4 -  Receitas Não Adm')
R('Repasses a estados e municípios (FPE/FPM/IPI-EE etc.)','2. TRANSF.',group='REPARTIÇÃO')
R('DESPESA TOTAL do Governo Central (valor pago)','4. DESPESA TOTAL',group='DESPESA DA UNIÃO')
R('Juros nominais da dívida – Governo Central (Banco Central)','9. JUROS',neg=True,group='DÍVIDA PÚBLICA')
R('Resultado nominal (déficit incl. juros)','10. RESULTADO NOMINAL',neg=True)
R('INSS – benefícios previdenciários (RGPS)','4.1  Benef',group='PREVIDÊNCIA')
R('Pessoal e encargos sociais (Executivo+Legislativo+Judiciário+MPU, inclui militares ativa/reserva/pensões)','4.2  Pessoal',group='PESSOAL')
R('Legislativo/Judiciário/MPU/DPU – custeio e capital (não é pessoal)','4.3.12',group='')
R('BPC / LOAS','4.3.05 ',group='ASSISTÊNCIA SOCIAL')
R('Bolsa Família / Auxílio Brasil','4.4.1.2')
R('Assistência social – discricionárias','4.4.2.8')
Rsum('Saúde (obrigatórias + discricionárias)',[('4.4.1.3',0),('4.4.2.1',0)],group='ÁREAS')
Rsum('Educação MEC (obrigatórias + discricionárias)',[('4.4.1.4',0),('4.4.2.2',0)])
R('  Complementação da União ao Fundeb (adicional à educação)','4.3.10')
R('Defesa – despesas discricionárias (sem pessoal)','4.4.2.3')
R('Segurança pública – discricionárias (sem pessoal PF/PRF)','4.4.2.7')

hdrfill=PatternFill('solid',fgColor='1F3864'); grpfill=PatternFill('solid',fgColor='D9E1F2')
thin=Side(style='thin',color='BBBBBB')
wb=openpyxl.Workbook()
def sheet(title,years,note):
    ws=wb.create_sheet(title)
    ws['A1']=title+' — valores em R$ bilhões correntes'; ws['A1'].font=Font(bold=True,size=13)
    ws['A2']=note; ws['A2'].font=Font(italic=True,size=9)
    h=['Grupo','Item']+[('2026 (jan–jul)' if y==2026 else str(y)) for y in years]
    for c,t in enumerate(h,1):
        x=ws.cell(row=4,column=c,value=t); x.font=Font(bold=True,color='FFFFFF'); x.fill=hdrfill; x.alignment=Alignment(horizontal='center',wrap_text=True)
    r=5
    for g,l,d in rows:
        if g: 
            ws.cell(row=r,column=1,value=g).font=Font(bold=True)
            for c in range(1,len(h)+1): ws.cell(row=r,column=c).fill=grpfill
        ws.cell(row=r,column=2,value=l)
        for j,y in enumerate(years):
            v=d.get(y); c=ws.cell(row=r,column=3+j,value=None if v is None else round(v,1))
            c.number_format='#,##0.0'
        r+=1
    ws.column_dimensions['A'].width=24; ws.column_dimensions['B'].width=78
    for j in range(len(years)): ws.column_dimensions[openpyxl.utils.get_column_letter(3+j)].width=15
    ws.freeze_panes='C5'
    return ws,r
wb.remove(wb.active)
ws0,r0=sheet('2016-2018',[2016,2017,2018],'Fonte: Tesouro Nacional – RTN Série Histórica (jul/2026), tabela 2.2. Valores sujeitos a revisão. 2016–2018 não têm complementos de fontes secundárias.')
ws1,r1=sheet('2019-2022',[2019,2020,2021,2022],'Fonte: Tesouro Nacional – Resultado do Tesouro Nacional, Série Histórica (jul/2026), tabela 2.2. Valores sujeitos a revisão.')
ws2,r2=sheet('2023-2026',[2023,2024,2025,2026],'Fonte: Tesouro Nacional – RTN Série Histórica (jul/2026), tabelas 2.2 (anual) e 1.2 (mensal, 2026 = jan–jul; juros 2026 = jan–jun, último mês divulgado).')

# complementary non-official items
def extra(ws,r,items,years):
    ws.cell(row=r+1,column=1,value='COMPLEMENTOS (fontes secundárias – conferir)').font=Font(bold=True)
    for c in range(1,len(years)+3): ws.cell(row=r+1,column=c).fill=grpfill
    rr=r+2
    for label,vals in items:
        ws.cell(row=rr,column=2,value=label)
        for j,y in enumerate(years):
            v=vals.get(y)
            if v is not None:
                c=ws.cell(row=rr,column=3+j,value=v); c.number_format='#,##0.0'
        rr+=1
extra(ws0,r0,[
 ('Renúncia fiscal total declarada – Portal da Transparência (por beneficiário)',{2016:78.3,2017:70.6,2018:100.2}),
],[2016,2017,2018])
extra(ws1,r1,[
 ('Renúncia fiscal total declarada – Portal da Transparência (por beneficiário)',{2019:119.4,2020:159.4,2021:204.7,2022:194.7}),
 ('Estados – todos os tributos estaduais (Confaz). 2022 derivado: 776,2 bi de 2023 era -1% sobre 2022',{2022:784.0}),
 ('Juros + amortização/rolagem – Tesouro "Transações da Dívida" via Auditoria Cidadã (NÃO oficial)',{2022:772.0}),
 ('Gastos tributários / renúncia – Portal da Transparência (2021) e Unafisco (2022, inclui outras renúncias)',{2021:215.0,2022:525.0}),
 ('Militares – inativos (Jovem Pan/Portal da Transparência)',{2019:26.0}),
 ('Militares – pensionistas (idem)',{2019:23.8}),
],[2019,2020,2021,2022])
extra(ws2,r2,[
 ('Renúncia fiscal total declarada – Portal da Transparência (2024 PARCIAL)',{2023:179.4,2024:70.6}),
 ('Estados – todos os tributos estaduais (Confaz). 2024 derivado: +6% sobre 2023',{2023:776.2,2024:823.0}),
 ('Juros + amortização/rolagem – Auditoria Cidadã (NÃO oficial)',{2023:1890.0,2025:2135.0}),
 ('Juros do setor público consolidado – Banco Central (12 meses até jun/2026 = 1.160)',{2024:950.4,2025:1008.0,2026:1160.0}),
 ('Gastos tributários / renúncia – Unafisco 2023 (inclui outras) e Receita/DGT 2025',{2023:641.0,2025:544.5}),
 ('Militares – ativa (Folha / Portal da Transparência)',{2023:32.4}),
 ('Militares – inativos',{2023:31.2}),
 ('Militares – pensionistas',{2023:25.7}),
 ('Militares – total pessoal (ativa+reserva+pensões, Centro de Liderança Pública; recorte diferente de 2023)',{2024:77.4}),
 ('Segurança pública – despesa total da União (PF 10,4; PRF 6,8; FNSP 2,2)',{2025:18.09}),
],[2023,2024,2025,2026])

# companies
import json
T=json.load(open('ren_top.json'))
ws=wb.create_sheet('Top15 isenção')
ws['A1']='15 empresas com maior renúncia fiscal por ano (Portal da Transparência – Renúncias Fiscais por Beneficiário; grupo = raiz do CNPJ, soma matriz+filiais) – R$ bilhões'; ws['A1'].font=Font(bold=True,size=12)
ws['A2']='Fonte: CGU/Receita Federal, arquivos "RenúnciasFiscaisPorBeneficiário" 2016–2024. 2024 é PARCIAL (só ~10 mil beneficiários declarados). Inclui IRPJ/CSLL/PIS/Cofins/II/IPI etc.; dados autodeclarados.'; ws['A2'].font=Font(italic=True,size=9)
years=list(range(2016,2025))
ws.cell(row=4,column=1,value='#').font=Font(bold=True)
for j,y in enumerate(years):
    c0=2+j*2
    ws.cell(row=3,column=c0,value=str(y)+(' (parcial)' if y==2024 else '')).font=Font(bold=True,color='FFFFFF')
    ws.merge_cells(start_row=3,start_column=c0,end_row=3,end_column=c0+1)
    for c in (c0,c0+1): ws.cell(row=3,column=c).fill=hdrfill
    ws.cell(row=4,column=c0,value='Empresa').font=Font(bold=True)
    ws.cell(row=4,column=c0+1,value='R$ bi').font=Font(bold=True)
    for k,(n,cnpj,v) in enumerate(T[str(y)]['top']):
        ws.cell(row=5+k,column=1,value=k+1)
        ws.cell(row=5+k,column=c0,value=n.title()[:38])
        x=ws.cell(row=5+k,column=c0+1,value=round(v/1e9,2)); x.number_format='0.00'
    base=21
    lab=[('Soma top 15',T[str(y)]['top15sum']/1e9),('Total renúncia declarada',T[str(y)]['total']/1e9),('% do total no top 15',T[str(y)]['top15sum']/T[str(y)]['total']*100),('Nº de beneficiários',T[str(y)]['n'])]
    for k,(l,v) in enumerate(lab):
        ws.cell(row=base+k,column=c0,value=l).font=Font(bold=True)
        x=ws.cell(row=base+k,column=c0+1,value=round(v,1)); x.number_format='#,##0.0'
    ws.column_dimensions[openpyxl.utils.get_column_letter(c0)].width=34
    ws.column_dimensions[openpyxl.utils.get_column_letter(c0+1)].width=8
ws.column_dimensions['A'].width=4
ws.freeze_panes='B5'

# notes
ws=wb.create_sheet('Notas e lacunas')
notes=[
'NOTAS METODOLÓGICAS',
'1. Escopo: "Governo Central" (Tesouro + Previdência + Banco Central). Despesas por valor pago; receitas por regime de caixa. Valores correntes (nominais), sem correção pela inflação.',
'2. 2020 está distorcido pela pandemia (créditos extraordinários de R$ 429,6 bi, Auxílio Emergencial). 2023 inclui precatórios elevados.',
'3. Pessoal e encargos (4.2) é o total do Governo Central: Executivo, Legislativo, Judiciário, MPU e militares (ativa, reserva e pensionistas). O RTN não separa Executivo x Legislativo nem militares.',
'4. Juros: o RTN traz os juros nominais do Governo Central (Banco Central). O Setor Público Consolidado (inclui estados, municípios e estatais) é maior. Não há "rolagem" no RTN — ela está nas operações de financiamento; os números de juros+amortização citados são da Auditoria Cidadã (não oficiais).',
'5. Saúde = obrigatórias com controle de fluxo + discricionárias (exclui pessoal). Educação MEC idem; Fundeb mostrado à parte. Defesa e Segurança aqui são só discricionárias — pessoal está em 4.2.',
'6. Isenção/renúncia: o Portal da Transparência (2016–2024, por beneficiário) soma o que as empresas declararam à Receita; Receita (DGT) e Unafisco usam outras metodologias e não são comparáveis. 2024 do Portal é parcial; 2025–2026 não disponíveis.',
'7. 2026: acumulado jan–jul (receita, despesas) e jan–jun (juros nominais). Não comparar diretamente com ano cheio.',
'8. Estados: o boletim do Confaz não traz arquivo para download (2024/2025 "em breve"); valores aproximados vêm de reportagens.',
'LACUNAS AINDA ABERTAS: militares por categoria (Portal bloqueou download automatizado com verificação humana – WAF); renúncia 2025–2026; tributos estaduais 2016–2022 e 2024–2026; rolagem oficial da dívida.',
'FONTES: Tesouro Transparente (ckan: resultado-do-tesouro-nacional), Confaz, Receita Federal, Portal da Transparência, Auditoria Cidadã, Unafisco, Banco Central.']
for i,t in enumerate(notes,1):
    c=ws.cell(row=i,column=1,value=t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if t.isupper() or t.startswith('NOTAS') or t.startswith('LACUNAS') or t.startswith('FONTES'): c.font=Font(bold=True)
ws.column_dimensions['A'].width=140
wb.move_sheet('2016-2018',offset=0)
out='/media/hitsuzen/Novo volume/money/arrecadacao_despesas_2019_2026.xlsx'
wb.save(out); print('saved',out)
for g,l,d in rows: print(l[:50].ljust(50),[None if d.get(y) is None else round(d[y],1) for y in (2016,2017,2018)])
