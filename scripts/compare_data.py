import json,collections,re
J=lambda f:json.load(open(f))
H=J('hist_rows.json'); rows={r['label'].strip():{int(y):v for y,v in r['data'].items()} for r in H['rows']}
def R(prefix):
    for l,d in rows.items():
        if l.startswith(prefix): return d
    raise KeyError(prefix)
# SIAPE anual
c=J('siape_rem_cache.json'); acc=collections.defaultdict(lambda:[0,0.0,set()])
for k,v in c.items():
    y=int(k[:4]); g=k.split('_')[1]
    acc[(y,g)][0]+=v['n']; acc[(y,g)][1]+=v['bruto']; acc[(y,g)][2].add(k[4:6])
def siape(g):
    out={}
    for (y,gg),(n,t,m) in acc.items():
        if gg==g and len(m)==12 and y<=2025: out[y]=[n/12, t/1e9]
    return out
sA,sP,sN=siape('Servidores'),siape('Aposentados'),siape('Pensionistas')
# militares: valor (R$ bi) e pessoas
mil_v={'ativa':R('Militares – ativa'),'reserva':R('Militares – reserva'),'pens':R('Militares – pensionistas')}
mil_n={'ativa':R('Militares da ativa'),'reserva':R('Militares da reserva'),'pens':R('Pensionistas militares')}
inss_v=R('INSS – benefícios'); bpc_v=R('dos quais BPC'); bf_v=R('dos quais Bolsa Fam')
inss_n=R('previdenciários (RGPS) (milhões)'); ass_n=R('assistenciais – BPC/LOAS no INSS'); bf_n=R('Bolsa Família/Auxílio Brasil – famílias')
ren=R('Isenção fiscal a empresas'); nemp=R('Empresas com isenção'); agro=R('dos quais agro'); nagro=R('das quais do agro')
T=J('top50.json'); top50={int(y):sum(e['valor'] for e in v['top'])/1e9 for y,v in T.items()}
juros=R('Pagamento da dívida – juros')
Y=list(range(2006,2026))
G=[]
WHO={'mil_ativa':('militares da ativa','receberam','por militar'),'mil_reserva':('militares da reserva/reforma','receberam','por militar'),'mil_pens':('pensionistas militares','receberam','por pensionista'),'civ_ativos':('servidores civis ativos','receberam','por servidor'),'civ_aposent':('servidores civis aposentados','receberam','por aposentado'),'civ_pens':('pensionistas civis','receberam','por pensionista'),'inss_rgps':('benefícios previdenciários do INSS','pagaram','por benefício'),'bpc':('benefícios do BPC','pagaram','por benefício'),'bf':('famílias do Bolsa Família / Auxílio Brasil','receberam','por família'),'top50':('empresas entre as 50 maiores em isenção fiscal','tiveram isenção de','por empresa'),'resto_emp':('demais empresas com isenção fiscal','tiveram isenção de','por empresa'),'agro_emp':('empresas do agro com isenção fiscal','tiveram isenção de','por empresa')}
def grp(id,label,cat,color,note,fn,est=False):
    by={}
    for y in Y:
        r=fn(y)
        if r: by[str(y)]=r
    w=WHO[id]
    G.append({'id':id,'label':label,'cat':cat,'color':color,'note':note,'who':w[0],'verb':w[1],'per':w[2],'byYear':by})
def est_n(d,y,first=2020):
    if y in d: return d[y]*1e3,False
    if y<first and first in d: return d[first]*1e3,True
    return None,False
def mil(g,note):
    def f(y):
        v=mil_v[g].get(y); n,e=est_n(mil_n[g],y)
        return [n,v,1 if e else 0] if v and n else None
    return f
grp('mil_ativa','Militares da ativa','Forças Armadas','#166534','Folha bruta (remuneração + 13º + férias).',mil('ativa',''))
grp('mil_reserva','Militares da reserva/reforma','Forças Armadas','#15803d','Antes de 2020 a base não publica a quantidade; usamos a de 2020 como estimativa (≈).',mil('reserva',''))
grp('mil_pens','Pensionistas militares','Forças Armadas','#4d7c0f','Antes de 2020 a quantidade é estimada pela de 2020 (≈).',mil('pens',''))
grp('civ_ativos','Servidores civis ativos (Executivo)','Servidores civis','#4338ca','Folha bruta SIAPE; média mensal de pessoas.',lambda y:[sA[y][0],sA[y][1],0] if y in sA else None)
grp('civ_aposent','Servidores civis aposentados','Servidores civis','#6366f1','Disponível a partir de 2020.',lambda y:[sP[y][0],sP[y][1],0] if y in sP else None)
grp('civ_pens','Pensionistas civis','Servidores civis','#818cf8','Disponível a partir de 2020.',lambda y:[sN[y][0],sN[y][1],0] if y in sN else None)
grp('inss_rgps','INSS – benefícios previdenciários (RGPS)','Previdência e assistência','#0e7490','Benefícios (não pessoas); valor pago pelo Tesouro/INSS.',lambda y:[inss_n[y]*1e6,inss_v[y],0] if y in inss_n and y in inss_v else None)
grp('bpc','BPC','Previdência e assistência','#0891b2','Benefícios assistenciais (BPC/LOAS) no INSS.',lambda y:[ass_n[y]*1e6,bpc_v[y],0] if y in ass_n and y in bpc_v else None)
grp('bf','Bolsa Família / Auxílio Brasil','Previdência e assistência','#c2410c','Famílias beneficiadas em dezembro.',lambda y:[bf_n[y]*1e6,bf_v[y],0] if y in bf_n and y in bf_v else None)
grp('top50','As 50 maiores empresas em isenção','Isenção fiscal (renúncia)','#9d174d','Renúncia declarada à Receita; 2024 parcial.',lambda y:[50,top50[y],0] if y in top50 and y<=2023 else None)
grp('resto_emp','Demais empresas com isenção','Isenção fiscal (renúncia)','#be185d','Todas as outras empresas declarantes.',lambda y:[nemp[y]-50,ren[y]-top50[y],0] if y in top50 and y in nemp and y<=2023 else None)
grp('agro_emp','Empresas do agro com isenção','Isenção fiscal (renúncia)','#65a30d','Agropecuária, agroindústria e insumos (parte do total acima).',lambda y:[nagro[y],agro[y],0] if y in nagro and y in agro and y<=2023 else None)
# ---- referencias: servicos publicos (gasto federal por pessoa atendida)
edu_v=R('Educação (União)'); sau_v=R('Saúde (União)'); seg_v=R('Segurança pública (União)'); ass_v=R('Assistência social (União) – total')
pop=R('População total'); mat=R('Matrículas educação básica'); sup=R('Matrículas ensino superior'); sus=R('População sem plano')
def bench(id,label,color,note,who,per,fn):
    by={}
    for y in Y:
        r=fn(y)
        if r: by[str(y)]=r
    G.append({'id':id,'label':label,'cat':'Referência: serviços públicos','color':color,'note':note,'who':who,'verb':'tiveram de gasto federal','per':per,'bench':True,'byYear':by})
bench('b_edu','Educação – gasto federal por aluno','#1d4ed8','Gasto da União em educação ÷ matrículas (básica + superior, todas as redes). Estados e municípios não incluídos.','alunos matriculados','por aluno',lambda y:[(mat[y]+sup.get(y,0))*1e6,edu_v[y],0] if y in mat and y in edu_v else None)
bench('b_sau','Saúde – gasto federal por habitante','#be123c','Gasto da União em saúde ÷ população total (o SUS é universal).','habitantes (saúde)','por habitante',lambda y:[pop[y]*1e6,sau_v[y],0] if y in pop and y in sau_v else None)
bench('b_sus','Saúde – gasto federal por dependente do SUS','#e11d48','Gasto da União em saúde ÷ população sem plano de saúde (estimativa).','dependentes do SUS','por dependente',lambda y:[sus[y]*1e6,sau_v[y],0] if y in sus and y in sau_v else None)
bench('b_ass','Assistência social – gasto federal por beneficiário (BPC + Bolsa Família)','#c2410c','Gasto da União na função assistência social ÷ (benefícios BPC + famílias do Bolsa Família).','beneficiários da assistência (BPC + Bolsa Família)','por beneficiário',lambda y:[(ass_n[y]+bf_n[y])*1e6,ass_v[y],0] if y in ass_n and y in bf_n and y in ass_v else None)
bench('b_seg','Segurança – gasto federal por habitante','#334155','Gasto da União em segurança pública ÷ população total.','habitantes (segurança)','por habitante',lambda y:[pop[y]*1e6,seg_v[y],0] if y in pop and y in seg_v else None)
import os
if os.path.exists('sub_year.json'):
    sub=J('sub_year.json'); okY=[int(y) for y,cc in sub['entes'].items() if cc.get('M',0)>=5000 and cc.get('E',0)>=26]
    def tri(nome,y):
        a=sub['agg'].get(str(y),{}); return (a.get('E',{}).get(nome,0)+a.get('M',{}).get(nome,0))
    def bench3(id,label,color,note,who,per,nome,uv,den,fac=1):
        by={}
        for y in okY:
            if y in Y and y in uv and y in den: by[str(y)]=[den[y]*fac,uv[y]+tri(nome,y),0]
        if by: G.append({'id':id,'label':label,'cat':'Referência: serviços públicos (3 esferas)','color':color,'note':note,'who':who,'verb':'tiveram de gasto público','per':per,'bench':True,'byYear':by})
    mat_t={y:(mat[y]+sup.get(y,0))*1e6 for y in mat}
    popA={y:v*1e6 for y,v in pop.items()}
    bench3('b_edu3','Educação – gasto das 3 esferas por aluno','#1e40af','União + estados + municípios (SICONFI) ÷ matrículas (básica + superior).','alunos matriculados','por aluno','Educação',edu_v,mat_t)
    bench3('b_sau3','Saúde – gasto das 3 esferas por habitante','#9f1239','União + estados + municípios (SICONFI) ÷ população.','habitantes (saúde)','por habitante','Saúde',sau_v,popA)
    bench3('b_seg3','Segurança – gasto das 3 esferas por habitante','#1e293b','União + estados + municípios (SICONFI) ÷ população.','habitantes (segurança)','por habitante','Segurança pública',seg_v,popA)
    bench3('b_ass3','Assistência – gasto das 3 esferas por habitante','#9a3412','União + estados + municípios (SICONFI) ÷ população.','habitantes (assistência)','por habitante','Assistência social',ass_v,popA)
json.dump({'years':Y,'groups':G},open('compare.json','w'),ensure_ascii=False)
for g in G:
    r=g['byYear'].get('2016'); r2=g['byYear'].get('2023')
    print(g['label'][:40].ljust(40),[ (round(x/1e3) if i==0 else round(x,1)) for i,x in enumerate(r[:2])] if r else None, [ (round(x/1e3) if i==0 else round(x,1)) for i,x in enumerate(r2[:2])] if r2 else None)
