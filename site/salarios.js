(function(){
'use strict';
var S=window.SAL, $=function(s){return document.querySelector(s)};
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function n(v){return v==null?'–':Number(v).toLocaleString('pt-BR')}

function pad(m){return (m<10?'0':'')+m}
function mes(y,m){return m?pad(m)+'/'+y:'–'}
function ym(y,m){return y+pad(m)}
function lnk(u,t){return '<a href="'+u+'" target="_blank" rel="noopener">'+esc(t)+'</a>'}
function civUrl(y,m){return 'https://portaldatransparencia.gov.br/download-de-dados/servidores/'+ym(y,m)}
function judUrl(o,y,m){return 'https://dadosjusbr.org/orgao/'+o+'/'+y+'/'+m}
function verba(r){
  if(!r[8]&&!r[9])return '<span class="muted">sem detalhe</span>';
  var nm=(r[8]==null||r[8]==='0')?'verba sem descrição na fonte':r[8];
  return esc(nm)+' <b>R$ '+n(r[9])+'</b>'+(r[10]?' <span title="Uma única verba responde por mais da metade do valor do mês" style="background:#b45309;color:#fff;border-radius:999px;padding:0 .45rem;font-size:.72rem">pontual</span>':'');
}
var Y=Object.keys(S.civ).sort();
var T=['Servidor ativo (Executivo)','Servidor ativo (Banco Central)','Aposentado (Executivo)','Aposentado (Banco Central)','Pensionista (Executivo)','Pensionista (Banco Central)'];
$('#s-civ').innerHTML='<thead><tr><th>Categoria</th>'+Y.map(function(y){return '<th>'+y+(y==='2026'?'*':'')+'</th>'}).join('')+'</tr></thead><tbody>'+
 T.map(function(t){return '<tr><td>'+t+'</td>'+Y.map(function(y){return '<td>'+n(S.civ[y][t]||0)+'</td>'}).join('')+'</tr>'}).join('')+
 '<tr><td><b>Total</b></td>'+Y.map(function(y){return '<td><b>'+n(Object.keys(S.civ[y]).reduce(function(a,k){return a+S.civ[y][k]},0))+'</b></td>'}).join('')+'</tr>'+
 '<tr><td>com 6+ meses acima de R$ 50 mil</td>'+Y.map(function(y){return '<td>'+n(Object.keys(S.civ6[y]||{}).reduce(function(a,k){return a+S.civ6[y][k]},0))+'</td>'}).join('')+'</tr></tbody>';
var my=Object.keys(S.mil).sort(), all=Y.concat(my.filter(function(y){return Y.indexOf(y)<0})).sort();
var rows=[['Senado – pessoas (bruto > R$ 50 mil)',function(y){return S.sen_cnt[y]}]];
['Ativa','Reserva/Reforma','Pensionistas'].forEach(function(g){
  rows.push(['Militares – '+g+' (> R$ 50 mil)',function(y){var v=S.mil[y]&&S.mil[y][g];return v?v[0]:null}]);
  rows.push(['Militares – '+g+' (> R$ 100 mil)',function(y){var v=S.mil[y]&&S.mil[y][g];return v?v[2]:null}]);
});
$('#s-leg').innerHTML='<thead><tr><th>Grupo</th>'+all.map(function(y){return '<th>'+y+(y==='2026'?'*':'')+'</th>'}).join('')+'</tr></thead><tbody>'+
 rows.map(function(r){return '<tr><td>'+r[0]+'</td>'+all.map(function(y){return '<td>'+n(r[1](y))+'</td>'}).join('')+'</tr>'}).join('')+'</tbody>';
var RM=['Tribunais superiores e conselhos','Tribunais de Justiça (estaduais)','Justiça Militar estadual','Tribunais Regionais Federais','Tribunais do Trabalho (TRT)','Tribunais Eleitorais (TRE)','Ministério Público'];
var JY=Object.keys(S.jud.cnt).sort();
$('#s-jud').innerHTML='<thead><tr><th>Ramo</th>'+JY.map(function(y){return '<th>'+y+(y==='2026'?'*':'')+'</th>'}).join('')+'</tr></thead><tbody>'+
 RM.map(function(r){return '<tr><td>'+r+'</td>'+JY.map(function(y){return '<td>'+n(S.jud.cnt[y][r]||0)+'</td>'}).join('')+'</tr>'}).join('')+
 '<tr><td><b>Total</b></td>'+JY.map(function(y){return '<td><b>'+n(Object.keys(S.jud.cnt[y]).reduce(function(a,k){return a+S.jud.cnt[y][k]},0))+'</b></td>'}).join('')+'</tr>'+
 '<tr><td>com 6+ meses acima de R$ 50 mil</td>'+JY.map(function(y){return '<td>'+n(Object.keys(S.jud.c6[y]).reduce(function(a,k){return a+S.jud.c6[y][k]},0))+'</td>'}).join('')+'</tr>'+
 '<tr><td>com subsídio-base acima de R$ 50 mil</td>'+JY.map(function(y){return '<td>'+n(Object.keys(S.jud.sal[y]).reduce(function(a,k){return a+S.jud.sal[y][k]},0))+'</td>'}).join('')+'</tr></tbody>';
var oy=$('#s-oy'); Object.keys(S.jud_orgao).sort().reverse().forEach(function(y){var o=document.createElement('option');o.value=y;o.textContent=y;oy.appendChild(o)}); oy.value='2025';
function drawOrg(){var L=S.jud_orgao[oy.value]||[];$('#s-orgao').innerHTML='<thead><tr><th>#</th><th>Órgão</th><th>Ramo</th><th>Pessoas &gt; R$ 50 mil</th><th>Com 6+ meses</th></tr></thead><tbody>'+L.map(function(r,i){return '<tr><td>'+(i+1)+'</td><td style="text-align:left">'+esc(r[0])+'</td><td style="text-align:left">'+esc(r[1])+'</td><td>'+n(r[2])+'</td><td>'+n(r[3])+'</td></tr>'}).join('')+'</tbody>'}
oy.onchange=drawOrg; drawOrg();
var sy=$('#s-year'); Y.slice().reverse().forEach(function(y){var o=document.createElement('option');o.value=y;o.textContent=y;sy.appendChild(o)});
sy.value='2025';
function list(){
  var y=sy.value,b=$('#s-base').value,q=$('#s-q').value.toLowerCase(),h;
  if(b==='civ'){
    var L=(S.top[y]||[]).filter(function(r){return !q||r[0].toLowerCase().indexOf(q)>=0});
    h='<thead><tr><th>#</th><th>Nome</th><th>Categoria</th><th>Cargo</th><th>Órgão</th><th>Meses &gt; 50 mil</th><th>Maior mês (R$)</th><th>Mês do maior valor</th><th>Fonte</th></tr></thead><tbody>'+L.map(function(r,i){return '<tr><td>'+(i+1)+'</td><td style="text-align:left;white-space:normal">'+esc(r[0])+'</td><td style="text-align:left;white-space:normal">'+esc(r[1])+'</td><td style="text-align:left;white-space:normal">'+esc(r[2])+'</td><td style="text-align:left;white-space:normal">'+esc(r[3])+'</td><td>'+r[4]+'</td><td>'+n(r[5])+'</td><td>'+mes(y,r[6])+'</td><td>'+lnk(civUrl(y,r[6]),r[7]?ym(y,r[6])+'_'+r[7]:'Portal')+'</td></tr>'}).join('')+'</tbody>';
  }else if(b==='jud'){
    var L3=(S.jud_top[y]||[]).filter(function(r){return !q||r[0].toLowerCase().indexOf(q)>=0});
    h='<thead><tr><th>#</th><th>Nome</th><th>Ramo</th><th>Função</th><th>Órgão</th><th>Meses &gt; 50 mil</th><th>Maior mês bruto (R$)</th><th>Mês</th><th>Verba principal do mês</th><th>Fonte</th></tr></thead><tbody>'+L3.map(function(r,i){return '<tr><td>'+(i+1)+'</td><td style="text-align:left;white-space:normal">'+esc(r[0])+'</td><td style="text-align:left;white-space:normal">'+esc(r[1])+'</td><td style="text-align:left;white-space:normal">'+esc(r[2])+'</td><td>'+esc(r[3])+'</td><td>'+r[4]+'</td><td>'+n(r[5])+'</td><td>'+mes(y,r[6])+'</td><td style="text-align:left;white-space:normal">'+verba(r)+'</td><td>'+lnk(judUrl(r[3],y,r[6]),r[7]||'DadosJusBr')+'</td></tr>'}).join('')+'</tbody>';
  }else{
    var L2=(S.sen_top[y]||[]).filter(function(r){return !q||r[0].toLowerCase().indexOf(q)>=0});
    h='<thead><tr><th>#</th><th>Nome</th><th>Meses &gt; 50 mil</th><th>Maior mês bruto (R$)</th><th>Mês</th><th>Folha</th><th>Fonte</th></tr></thead><tbody>'+L2.map(function(r,i){return '<tr><td>'+(i+1)+'</td><td style="text-align:left;white-space:normal">'+esc(r[0])+'</td><td>'+r[1]+'</td><td>'+n(r[2])+'</td><td>'+mes(y,r[3])+'</td><td>'+esc(r[4])+'</td><td>'+lnk('https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/remuneracoes/'+y+'/'+r[3],'API Senado')+'</td></tr>'}).join('')+'</tbody>';
  }
  $('#s-list').className='list'; $('#s-list').innerHTML=h;
}
sy.onchange=list; $('#s-base').onchange=list; $('#s-q').oninput=list; list();
})();
