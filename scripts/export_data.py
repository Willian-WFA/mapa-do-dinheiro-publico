import json,collections
R=json.load(open('hist_rows.json')); X=json.load(open('rtn_extra.json')); S=json.load(open('rtn_sub.json')); AG=json.load(open('agro.json'))
T50=json.load(open('top50.json')); CV=json.load(open('cvm_pos.json')); TT=json.load(open('ren_top.json'))
lab={r['label']:r for r in R['rows']}
def find(prefix):
    for l,r in lab.items():
        if l.strip().startswith(prefix): return r['data']
    raise KeyError(prefix)
def ser(key,label,unit,kind,data,note=None,fmt=None,main=False):
    return {'key':key,'label':label,'unit':unit,'kind':kind,'data':{str(k):v for k,v in data.items() if v is not None},'note':note,'fmt':fmt,'main':main}
Y=[str(y) for y in R['years']]
cards=[]
# 1 divida
ger_by_year={}
for p,v in sorted(CV.items()):
    y=p[:4]
    ger_by_year[y]=[[g,round(x/1e9,1)] for g,x in v['top'][:15]]
fundos={p[:4]:v['total']/1e9 for p,v in CV.items()}
cards.append({'id':'divida','title':'Juros da dívida, bancos e rentistas','short':'Dívida pública','color':'#b45309','icon':'₿',
 'desc':'Quanto o governo federal paga de juros, quanto rola de dívida e quem carrega os títulos em fundos de investimento.',
 'series':[
  ser('juros','Juros e encargos da dívida (orçamento, caixa)','R$ bi','val',find('Pagamento da dívida'),main=True),
  ser('jbc','Juros nominais do setor público (Banco Central)','R$ bi','val',find('juros nominais do setor'),'Competência; inclui estados, municípios e estatais.'),
  ser('refin','Rolagem: principal refinanciado','R$ bi','val',find('Rolagem da dívida'),'Troca de dívida velha por nova; não é custo.'),
  ser('resg','Principal efetivamente resgatado','R$ bi','val',find('principal efetivamente')),
  ser('jrtn','Juros nominais do Governo Central (RTN, desde 1997)','R$ bi','val',find('Juros nominais do Governo Central'),'Resultado abaixo da linha; série longa para comparação histórica.'),
  ser('fundos','Títulos públicos nas carteiras de fundos (CVM, dezembro; 2026 = ago.)','R$ bi','stock',fundos,'Recorte parcial: não inclui carteira própria de bancos, estrangeiros nem pessoas físicas diretas.'),
  ser('ngest','Gestoras (grupos) com títulos públicos em fundos','nº','n',find('Gestoras (grupos)')),
  ser('td_cad','Tesouro Direto – novos cadastros por ano de adesão','milhões','n',find('Tesouro Direto – novos cadastros'),'Códigos distintos; um investidor pode ter cadastro em mais de uma instituição.'),
  ser('td_op','Tesouro Direto – operaram nos últimos 12 meses (por ano de adesão)','mil','n',find('Tesouro Direto – desses, operaram')),
  ser('jhab','Juros da dívida por habitante','R$','pp',find('Juros da dívida (orçamento) por habitante'))],
 'lists':[{'title':'Maiores gestoras de fundos com títulos públicos (R$ bi, dezembro)','byYear':ger_by_year,'unit':'R$ bi'}],
 'notes':['"Rentistas" aqui = detentores de títulos por meio de fundos. Os nomes de pessoas físicas não são públicos.','Juros do orçamento (caixa) e do Banco Central (competência) diferem de propósito: mostramos as duas.','Fonte: Portal da Transparência (execução da despesa), Banco Central (SGS), CVM (CDA).']})
# 2 inss
inss=find('INSS – benefícios'); arr=find('INSS – arrecadação')
cards.append({'id':'inss','title':'INSS (Previdência)','short':'INSS','color':'#0e7490','icon':'♥',
 'desc':'Benefícios do Regime Geral pagos pela União e quanto o próprio sistema arrecada.',
 'series':[ser('ben','Benefícios previdenciários (RGPS)','R$ bi','val',inss,main=True),
  ser('arr','Arrecadação líquida para o RGPS','R$ bi','val',arr),
  ser('def','Necessidade de financiamento (benefícios − arrecadação)','R$ bi','val',{k:inss[k]-arr[k] for k in inss if k in arr}),
  ser('ben_inss','Benefícios emitidos – total','milhões','n',find('Benefícios do INSS emitidos'),'Dezembro de cada ano (2026 = julho). Um benefício pode corresponder a uma pessoa com mais de um benefício (ex.: pensão + aposentadoria).'),
  ser('ben_rgps','Benefícios emitidos – previdenciários (RGPS)','milhões','n',find('previdenciários (RGPS)')),
  ser('ben_ass','Benefícios emitidos – assistenciais (BPC/LOAS)','milhões','n',find('assistenciais – BPC/LOAS no INSS')),
  ser('ben_ble','Benefícios emitidos – legislação especial','mil','n',find('legislação especial'))],
 'lists':[{'title':'Benefícios emitidos por espécie (julho/2026, milhões)','byYear':{'2026':[[k,round(v/1e6,2)] for k,v in json.load(open('inss_pessoas.json'))['especies_jul2026'].items()]},'unit':'milhões','cols':['Espécie','milhões']}],'notes':['2026 = janeiro a julho (RTN do Tesouro).','Quantidade de beneficiários não foi coletada nesta versão.','Fonte: Tesouro Nacional – Resultado do Tesouro Nacional (RTN).']})
# 3 poderes
cards.append({'id':'poderes','title':'Executivo e Legislativo','short':'Poderes','color':'#4338ca','icon':'⚖',
 'desc':'Folha do Executivo e gasto do Legislativo (Câmara e Senado).',
 'series':[ser('exec','Pessoal do Executivo (civil e militar)','R$ bi','val',find('Pessoal do Executivo'),main=True),
  ser('cam','Câmara dos Deputados (pago)','R$ bi','val',find('Legislativo – Câmara'),'2026 não disponível.'),
  ser('sen','Senado Federal (pago)','R$ bi','val',find('Legislativo – Senado'),'2026 até setembro.'),
  ser('cs','Câmara + Senado (TCU não incluído)','R$ bi','val',find('Câmara + Senado')),
  ser('pess','Pessoal e encargos de todos os Poderes (RTN, desde 1997)','R$ bi','val',find('Pessoal de todos os Poderes')),
  ser('s_at','Servidores civis ativos do Executivo (SIAPE)','mil','n',find('Servidores civis ativos'),'Não inclui militares nem os poderes Legislativo e Judiciário.'),
  ser('s_ap','Servidores civis aposentados','mil','n',find('Servidores civis aposentados'),'Disponível a partir de 2020.'),
  ser('s_pe','Pensionistas civis','mil','n',find('Pensionistas civis'),'Disponível a partir de 2020.'),
  ser('lj','Legislativo/Judiciário/MPU/DPU – custeio e capital (RTN)','R$ bi','val',find('Legislativo/Judiciário/MPU/DPU – custeio')),
  ser('leg','Função Legislativa – Câmara, Senado e TCU (Tesouro, 2008–2018)','R$ bi','val',find('Função Legislativa'),'Inclui o TCU; depois de 2018 só há Câmara e Senado separados.'),
  ser('pp','Câmara+Senado por parlamentar','R$ milhões/ano','pp',find('Câmara+Senado por parlamentar'))],
 'lists':[],'notes':['Parlamentares: 513 deputados e 81 senadores (594). O gasto por parlamentar está na aba Valor por pessoa.','Poderes Judiciário e Ministério Público não estão separados por falta de arquivo aberto equivalente.','Fonte: Portal da Transparência, Câmara dos Deputados, Senado Federal, Tesouro Nacional.']})
# 4 militares
cards.append({'id':'militares','title':'Militares: ativa, reserva e pensionistas','short':'Militares','color':'#166534','icon':'★',
 'desc':'Folha das Forças Armadas por grupo, com quantidade de pessoas e valor médio por pessoa.',
 'series':[ser('at','Ativa','R$ bi','val',find('Militares – ativa'),main=True),
  ser('re','Reserva/reforma','R$ bi','val',find('Militares – reserva')),
  ser('pe','Pensionistas','R$ bi','val',find('Militares – pensionistas')),
  ser('nat','Pessoas na ativa (média mensal)','mil','n',find('Militares da ativa')),
  ser('nre','Pessoas na reserva/reforma','mil','n',find('Militares da reserva'),'Quantidade só a partir de 2020.'),
  ser('npe','Pensionistas','mil','n',find('Pensionistas militares'),'Quantidade só a partir de 2020.'),
  ser('pat','Média por militar da ativa','R$/ano','pp',find('Militar da ativa')),
  ser('pre','Média por militar da reserva','R$/ano','pp',find('Militar reserva')),
  ser('ppe','Média por pensionista','R$/ano','pp',find('Pensionista militar'))],
 'lists':[],'notes':['Valor bruto (antes de IR e contribuições). 2016–2019 de reserva e pensionistas vêm da despesa do orçamento; 2020 em diante da folha de pagamento.','Fonte: Portal da Transparência (servidores e despesas).']})
# 5 isencao
top_by_year={y:[[e['nome'].title()[:42],round(e['valor']/1e6,1),e['cnae'][:40]] for e in T50[y]['top']] for y in T50}
conc={y:sum(e['valor'] for e in T50[y]['top'])/T50[y]['total']*100 for y in T50}
cards.append({'id':'isencao','headYear':'2023','partial':['2024'],'title':'Isenção fiscal às empresas','short':'Isenção empresas','color':'#9d174d','icon':'%',
 'desc':'Renúncia fiscal declarada pelas empresas e as 50 maiores beneficiárias de cada ano.',
 'series':[ser('ren','Renúncia total declarada','R$ bi','val',find('Isenção fiscal a empresas'),main=True,note='2024 é parcial; 2025–2026 ainda não publicados.'),
  ser('gt','Gastos tributários oficiais (Receita Federal, bases efetivas)','R$ bi','val',find('Gastos tributários – Receita Federal'),'Medida oficial da Receita; inclui Simples, Zona Franca, saúde e outros. Maior que a renúncia declarada pelas empresas.'),
  ser('gtp','   projeção das edições do DGT (2024–2026)','R$ bi','val',find('Gastos tributários – projeção')),
  ser('gtploa','   previsão do DGT anexo à PLOA de cada ano','R$ bi','val',find('Gastos tributários – previsão da PLOA')),
  ser('nemp','Empresas beneficiárias','nº','n',find('Empresas com isenção')),
  ser('pemp','Isenção média por empresa','R$ mil/ano','pp',find('Isenção por empresa beneficiada')),
  ser('conc','Parcela das 50 maiores no total','%','pct',conc)],
 'lists':[{'title':'50 maiores beneficiárias (R$ milhões)','byYear':top_by_year,'unit':'R$ mi','cols':['Empresa','R$ mi','Setor']}],
 'notes':['Valores declarados à Receita (CGU/Receita Federal). Não equivalem aos gastos tributários oficiais, que são maiores.','Matriz e filiais somadas pela raiz do CNPJ.','Fonte: Portal da Transparência – Renúncias Fiscais.']})
# 6 agro
def agro_grp(k): return {y:AG[y]['agro'].get(k,{}).get('valor',0)/1e9 for y in AG}
ag_top={}
for y in AG:
    items=[]
    for g,v in AG[y]['agro'].items():
        for n,val in v['top']: items.append([n.title()[:42],round(val/1e6,1),g.split(' (')[0]])
    ag_top[y]=sorted(items,key=lambda z:-z[1])[:15]
cards.append({'id':'agro','headYear':'2025','partial':['2024'],'title':'Plano Safra e agro','short':'Plano Safra','color':'#65a30d','icon':'🌾',
 'desc':'Subsídios do orçamento ao crédito rural e isenções fiscais declaradas pelo agro.',
 'series':[ser('sub','Subsídios e crédito rural (Pronaf, Proagro, equalização)','R$ bi','val',find('Subsídios e crédito rural no orçamento'),main=True,note='2026 não disponível.'),
  ser('pronaf','Pronaf (equalização)','R$ bi','val',S['Pronaf']),
  ser('proagro','Proagro','R$ bi','val',S['Proagro']),
  dict(off=True,**ser('eqc','Equalização de custeio agropecuário','R$ bi','val',S['Equalização custeio agropecuário'])),
  dict(off=True,**ser('eqi','Equalização de investimento rural','R$ bi','val',S['Equalização invest. rural e agroindustrial'])),
  ser('ren','Isenção declarada: agro total','R$ bi','val',find('dos quais agro')),
  dict(off=True,**ser('ren1','   Agropecuária (produtor)','R$ bi','val',agro_grp('Agropecuária (CNAE 01–03)'))),
  dict(off=True,**ser('ren2','   Agroindústria','R$ bi','val',agro_grp('Agroindústria (alimentos, bebidas, fumo)'))),
  dict(off=True,**ser('ren3','   Insumos e máquinas agrícolas','R$ bi','val',agro_grp('Insumos e máquinas agrícolas'))),
  ser('nag','Empresas do agro com isenção','nº','n',find('das quais do agro')),
  ser('gtagr','Gasto tributário oficial – função Agricultura (Receita)','R$ bi','val',find('Gasto tributário – função Agricultura'),'Inclui desoneração da cesta básica, defensivos, exportação rural, Funrural etc.'),
  ser('pag','Isenção média por empresa do agro','R$ mil/ano','pp',find('Isenção agro por empresa'))],
 'lists':[{'title':'Maiores beneficiárias do agro (R$ milhões)','byYear':ag_top,'unit':'R$ mi','cols':['Empresa','R$ mi','Grupo']}],
 'notes':['O valor do Plano Safra anunciado (crédito liberado) não está nesta base: aqui aparece o custo do subsídio no orçamento.','O agro está subestimado nas isenções (IRPF rural, Funrural e parte do Simples não aparecem na base).','Fonte: Tesouro Nacional (RTN), Portal da Transparência – Renúncias Fiscais.']})
# 7 educacao
cards.append({'id':'educacao','title':'Educação','short':'Educação','color':'#1d4ed8','icon':'✎',
 'desc':'Gasto federal em educação e número de matrículas no país.',
 'series':[ser('g','Gasto da União em educação','R$ bi','val',find('Educação (União)'),'2014+: Portal da Transparência (despesa paga por função, Executivo e Poderes); 2008–2013: Tesouro (despesa paga por função); 1995–2007: Ipea/Disoc (gasto social federal, conceito próprio, em R$ de dez/2011 convertido para nominal).',main=True),
  ser('rtn','Educação – RTN, obrigatórias+discricionárias sem pessoal (desde 2008)','R$ bi','val',find('Educação – RTN')),
  ser('fundeb','Complementação da União ao Fundeb (RTN)','R$ bi','val',find('Complementação da União ao Fundeb')),
  ser('mb','Matrículas na educação básica (todas as redes)','milhões','n',find('Matrículas educação básica'),'INEP desde 2016 (2023 aproximado); antes, Banco Mundial/UNESCO (fund.+médio+pré).'),
  ser('pdm','Pé-de-Meia – estudantes pagos no mês','milhões','n',find('Pé-de-Meia'),'Dezembro de cada ano (2026 = junho).'),
  ser('smec','Servidores ativos no Ministério da Educação','mil','n',find('servidores ativos no Ministério da Educação'),'Universidades e institutos federais.'),
  ser('ms','Matrículas no ensino superior','milhões','n',find('Matrículas ensino superior'),'Banco Mundial/UNESCO até 2018; 2019–2024 aproximados (conferir no INEP).'),
  ser('gtedu','Gasto tributário oficial – função Educação (Receita)','R$ bi','val',find('Gasto tributário – função Educação')),
  ser('pm','Gasto federal por matrícula básica (referência)','R$','pp',find('Educação federal por matrícula'),'Inclui gasto com universidades federais.')],
 'lists':[],'notes':['Só a União. A educação básica é financiada majoritariamente por estados e municípios.','Fonte: Portal da Transparência (despesas por função), INEP.']})
# 8 saude
cards.append({'id':'saude','title':'Saúde','short':'Saúde','color':'#be123c','icon':'✚',
 'desc':'Gasto federal em saúde e população que depende do SUS.',
 'series':[ser('g','Gasto da União em saúde','R$ bi','val',find('Saúde (União)'),'2014+: Portal da Transparência (despesa paga por função, Executivo e Poderes); 2008–2013: Tesouro (despesa paga por função); 1995–2007: Ipea/Disoc (gasto social federal, conceito próprio, em R$ de dez/2011 convertido para nominal).',main=True),
  ser('rtn','Saúde – RTN, sem pessoal (desde 2008)','R$ bi','val',find('Saúde – RTN')),
  ser('plano','Com plano de saúde (beneficiários, aprox.)','milhões','n',{y:find('População total')[y]-find('População sem plano')[y] for y in find('População sem plano') if y in find('População total')}),
  ser('sus','População sem plano (dependente do SUS, estimativa)','milhões','n',find('População sem plano')),
  ser('pop','População total','milhões','n',find('População total')),
  ser('gtsau','Gasto tributário oficial – função Saúde (Receita)','R$ bi','val',find('Gasto tributário – função Saúde'),'Inclui dedução de despesas médicas no IR, planos de saúde e entidades filantrópicas.'),
  ser('pp','Gasto federal por dependente do SUS','R$','pp',find('Saúde federal por dependente'))],
 'lists':[],'notes':['Só a União, inclui repasses a estados e municípios.','Número de planos de saúde são aproximados (ANS).','Fonte: Portal da Transparência (despesas por função), IBGE, ANS.']})
# 9 seguranca
cards.append({'id':'seguranca','title':'Segurança pública','short':'Segurança','color':'#334155','icon':'⛨',
 'desc':'Gasto federal com segurança pública (PF, PRF, fundos e sistema penitenciário federal).',
 'series':[ser('g','Gasto da União em segurança pública','R$ bi','val',find('Segurança pública (União)'),'Desde 2008 (Tesouro/Portal). Antes disso não há série aberta por função.',main=True),
  ser('rtn','Segurança – RTN, discricionárias sem pessoal (desde 2008)','R$ bi','val',find('Segurança – RTN')),
  ser('hab','Gasto federal por habitante','R$','pp',find('Segurança federal por habitante'))],
 'lists':[],'notes':['A maior parte do gasto nacional com segurança é estadual.','Fonte: Portal da Transparência (despesas por função).']})
# 10 assistencia
cards.append({'id':'assistencia','title':'Assistência social: BPC e Bolsa Família','short':'Assistência','color':'#c2410c','icon':'♡',
 'desc':'Transferências de renda e quantas pessoas e famílias recebem.',
 'series':[ser('tot','Assistência social – total','R$ bi','val',find('Assistência social (União)'),'2020 inclui o Auxílio Emergencial. '+'2014+: Portal da Transparência (despesa paga por função, Executivo e Poderes); 2008–2013: Tesouro (despesa paga por função); 1995–2007: Ipea/Disoc (gasto social federal, conceito próprio, em R$ de dez/2011 convertido para nominal).',main=True),
  ser('bpc','BPC','R$ bi','val',find('dos quais BPC')),
  ser('bf','Bolsa Família / Auxílio Brasil','R$ bi','val',find('dos quais Bolsa Família'),'2026 = janeiro a julho.'),
  ser('rtn','Assistência – RTN, discricionárias (sem BPC/BF)','R$ bi','val',find('Assistência – RTN')),
  ser('gtass','Gasto tributário oficial – função Assistência Social (Receita)','R$ bi','val',find('Gasto tributário – função Assistência Social')),
  ser('nbpc','BPC – benefícios em dezembro','milhões','n',find('BPC – benefícios')),
  ser('nbf','Bolsa Família – famílias em dezembro','milhões','n',find('Bolsa Família/Auxílio')),
  ser('nab','Auxílio Brasil – famílias em dezembro','milhões','n',find('Auxílio Brasil – famílias')),
  ser('nae','Auxílio Emergencial – pessoas em dez./2020','milhões','n',find('Auxílio Emergencial – pessoas')),
  ser('ngas','Gás do Povo – famílias no mês','milhões','n',find('Gás do Povo')),
  ser('pbpc','BPC por benefício','R$/ano','pp',find('BPC por benefício')),
  ser('pbf','Bolsa Família por família','R$/ano','pp',find('Bolsa Família por família'))],
 'lists':[],'notes':['BPC só a partir de 2019 no portal.','Fonte: Tesouro Nacional (RTN), Portal da Transparência (pagamentos).']})
data={'years':Y,'fac':R['fac'],'gov':R['gov'],'cards':cards,'generated':'2026-10-14'}
import os
data['compare']=json.load(open('compare.json'))
if os.path.exists('sub_year.json'):
    sub=json.load(open('sub_year.json')); okY=[y for y,c in sub['entes'].items() if c.get('M',0)>=5000 and c.get('E',0)>=26]
    SF={'saude':('Saúde','g'),'educacao':('Educação','g'),'seguranca':('Segurança pública','g'),'assistencia':('Assistência social','tot')}
    for c in data['cards']:
        if c['id'] in SF and okY:
            nome,ukey=SF[c['id']]; U=[s for s in c['series'] if s['key']==ukey][0]
            est={y:sub['agg'][y]['E'].get(nome) for y in okY if sub['agg'][y].get('E',{}).get(nome)}
            mun={y:sub['agg'][y]['M'].get(nome) for y in okY if sub['agg'][y].get('M',{}).get(nome)}
            c['series'].insert(1,ser('est','Gasto dos estados e DF (SICONFI, despesa paga)','R$ bi','val',est,'Fonte: SICONFI/DCA, anexo I-E, despesa paga por função.'))
            c['series'].insert(2,ser('mun','Gasto dos municípios (SICONFI, despesa paga)','R$ bi','val',mun,'Fonte: SICONFI/DCA, anexo I-E, despesa paga por função (soma de ~5,5 mil municípios).'))
            c['series'].insert(3,ser('g3','Gasto das três esferas (União + estados + municípios)','R$ bi','val',{y:U['data'][y]+est.get(y,0)+mun.get(y,0) for y in est if y in U['data'] and y in mun},'Soma simples; transferências entre esferas podem gerar dupla contagem.'))
            base=c.get('pie'); c['pies']=[{'title':'Por esfera de governo','keys':['g' if ukey=='g' else ukey,'est','mun'],'unit':'R$ bi'}]+([dict(base,title='Outra composição')] if base else [])
open('site/data.js','w')
PIES={'divida':{'list':0,'div':1,'total':'fundos','otherLabel':'Demais gestoras','top':10},'inss':{'keys':['ben_rgps','ben_ass'],'total':'ben_inss','other':'Legislação especial','unit':'milhões de benefícios'},'educacao':{'keys':['mb','ms'],'unit':'milhões de matrículas'},'saude':{'keys':['sus','plano'],'unit':'milhões de pessoas'},'militares':{'keys':['at','re','pe']},'assistencia':{'keys':['bpc','bf'],'total':'tot','other':'Outros programas'},'poderes':{'keys':['exec','cs','lj']},'agro':{'keys':['ren1','ren2','ren3']},'isencao':{'list':0,'top':10,'total':'ren'}}
for c in data['cards']:
    if c['id'] in PIES: c['pie']=PIES[c['id']]
open('site/data.js','w').write('window.DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
print('ok',len(json.dumps(data))//1024,'KB')
