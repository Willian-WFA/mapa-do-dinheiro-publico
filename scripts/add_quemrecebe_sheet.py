import json,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
X='/media/hitsuzen/Novo volume/money/arrecadacao_despesas_2019_2026.xlsx'
C=json.load(open('compare.json')); H=json.load(open('hist_rows.json')); fac={int(k):v for k,v in H['fac'].items()}
wb=openpyxl.load_workbook(X)
if 'Quem recebe' in wb.sheetnames: del wb['Quem recebe']
ws=wb.create_sheet('Quem recebe',2)
hdr=PatternFill('solid',fgColor='1F3864'); grp=PatternFill('solid',fgColor='D9E1F2')
ws['A1']='Quem recebe: pessoas, valor recebido e valor por pessoa, por grupo e ano'; ws['A1'].font=Font(bold=True,size=14)
ws['A2']='Valores em R$ de 2025 (IPCA) na primeira tabela e nominais na segunda. ≈ = quantidade estimada pela de 2020 (a base só passa a existir nesse ano). Isenções fiscais são renúncia, não pagamento.'; ws['A2'].font=Font(italic=True,size=9)
Y=C['years']
def block(r,title,fn,fmt):
    ws.cell(row=r,column=1,value=title).font=Font(bold=True)
    for c in range(1,len(Y)+3): ws.cell(row=r,column=c).fill=grp
    r+=1
    ws.cell(row=r,column=1,value='Grupo').font=Font(bold=True,color='FFFFFF'); ws.cell(row=r,column=1).fill=hdr
    for j,y in enumerate(Y):
        x=ws.cell(row=r,column=2+j,value=y); x.font=Font(bold=True,color='FFFFFF'); x.fill=hdr; x.alignment=Alignment(horizontal='center')
    r+=1
    for g in C['groups']:
        ws.cell(row=r,column=1,value=g['label'])
        for j,y in enumerate(Y):
            d=g['byYear'].get(str(y))
            if d:
                v=fn(d,y)
                if v is not None:
                    c=ws.cell(row=r,column=2+j,value=v); c.number_format=fmt
        r+=1
    return r+1
r=4
r=block(r,'PESSOAS / EMPRESAS / BENEFÍCIOS NO GRUPO',lambda d,y:round(d[0]),'#,##0')
r=block(r,'RECEBEU (R$ bi, valores reais de 2025)',lambda d,y:round(d[1]*fac[y],2),'#,##0.0')
r=block(r,'POR PESSOA NO ANO (R$ de 2025)',lambda d,y:round(d[1]*fac[y]*1e9/d[0]),'#,##0')
r=block(r,'POR PESSOA NO MÊS (R$ de 2025)',lambda d,y:round(d[1]*fac[y]*1e9/d[0]/12),'#,##0')
r=block(r,'RECEBEU (R$ bi nominais)',lambda d,y:round(d[1],2),'#,##0.0')
# razoes vs bolsa familia
ws.cell(row=r,column=1,value='QUANTAS VEZES O VALOR POR PESSOA DO GRUPO É O DO BOLSA FAMÍLIA').font=Font(bold=True)
for c in range(1,len(Y)+3): ws.cell(row=r,column=c).fill=grp
r+=1
bf=[g for g in C['groups'] if g['id']=='bf'][0]
for g in C['groups']:
    if g['id']=='bf': continue
    ws.cell(row=r,column=1,value=g['label'])
    for j,y in enumerate(Y):
        a=g['byYear'].get(str(y)); b=bf['byYear'].get(str(y))
        if a and b: ws.cell(row=r,column=2+j,value=round((a[1]/a[0])/(b[1]/b[0]),1)).number_format='#,##0.0'
    r+=1
ws.column_dimensions['A'].width=54
for j in range(len(Y)): ws.column_dimensions[openpyxl.utils.get_column_letter(2+j)].width=13
ws.freeze_panes='B4'
wb.save(X); print('ok')
