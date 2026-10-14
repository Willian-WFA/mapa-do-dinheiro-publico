(function(){
'use strict';
var D=window.DON, FAC=D.fac, GOV=D.gov;
var $=function(s){return document.querySelector(s)};
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function f(v,d){return v==null?'–':Number(v).toLocaleString('pt-BR',{maximumFractionDigits:d==null?1:d})}
var E=D.emp, se=$('#d-emp'), sa=$('#d-ano');
E.forEach(function(e,i){var o=document.createElement('option');o.value=i;o.textContent=(e.banco?'[banco] ':'')+e.nome;se.appendChild(o)});
function cur(){return E[+se.value]}
function fillYears(){
  var ys=Object.keys(cur().acion).sort().reverse(); sa.innerHTML='';
  ys.forEach(function(y){var o=document.createElement('option');o.value=y;o.textContent=y;sa.appendChild(o)});
}
function acion(){
  var e=cur(), L=(e.acion[sa.value]||[]);
  var direct=L.filter(function(a){return !a.via}), chain=L.filter(function(a){return a.via});
  $('#d-anote').textContent='Participações ≥ 5% das ações em circulação ou controladores, conforme o Formulário de Referência de '+sa.value+'. Linhas "dentro de" mostram quem participa do controlador (percentual dentro dele, não da empresa).';
  function row(a,ind){return '<tr><td style="'+(ind?'padding-left:1.6rem':'')+'"><b>'+esc(a.n)+'</b>'+(a.via?'<br><span class="muted">dentro de '+esc(a.via)+'</span>':'')+'</td><td>'+(a.pf?'pessoa física':'pessoa jurídica')+(a.pais?' · '+esc(a.pais):'')+'</td><td class="r">'+f(a.pct,2)+'%</td><td>'+(a.ctrl?'<span class="tag">controlador</span>':'')+'</td></tr>'}
  var seen={};
  var h='<thead><tr><th>Acionista</th><th>Tipo</th><th class="r">% das ações</th><th></th></tr></thead><tbody>';
  direct.forEach(function(a){h+=row(a,false)});
  chain.forEach(function(a){var k=a.n+'|'+a.via+'|'+a.pct; if(seen[k])return; seen[k]=1; h+=row(a,true)});
  $('#d-acion').innerHTML=h+(L.length?'':'<tr><td class="muted" colspan="4">Sem dados para este ano.</td></tr>')+'</tbody>';
}
function rem(){
  var e=cur(), ys=Object.keys(e.rem).sort();
  var h='<thead><tr><th>Exercício</th><th class="r">Conselho: total (R$ mi)</th><th class="r">membros</th><th class="r">média por membro (R$ mi, 2025)</th><th class="r">Diretoria: total (R$ mi)</th><th class="r">membros</th><th class="r">média por membro (R$ mi, 2025)</th></tr></thead><tbody>';
  ys.forEach(function(y){
    var c=e.rem[y]['Conselho de Administração'], d=e.rem[y]['Diretoria Estatutária'], k=FAC[y]||1;
    h+='<tr><td>'+y+'</td><td class="r">'+(c?f(c[0],1):'–')+'</td><td class="r">'+(c?f(c[1],1):'–')+'</td><td class="r">'+(c?f(c[2]*k,2):'–')+'</td><td class="r">'+(d?f(d[0],1):'–')+'</td><td class="r">'+(d?f(d[1],1):'–')+'</td><td class="r">'+(d?f(d[2]*k,2):'–')+'</td></tr>';
  });
  $('#d-rem').innerHTML=h+(ys.length?'':'<tr><td class="muted" colspan="7">Remuneração não informada nesta base.</td></tr>')+'</tbody>';
}
function fin(){
  var e=cur(), ys={}; Object.keys(e.isenc).forEach(function(y){ys[y]=1}); Object.keys(e.lucro).forEach(function(y){ys[y]=1});
  var Y=Object.keys(ys).sort();
  var h='<thead><tr><th>Ano</th><th class="r">Isenção declarada (R$ mi, 2025)</th><th class="r">Lucro líquido (R$ bi, 2025)</th></tr></thead><tbody>';
  Y.forEach(function(y){var k=FAC[y]||1;h+='<tr><td>'+y+'</td><td class="r">'+(e.isenc[y]!=null?f(e.isenc[y]*k,0):'–')+'</td><td class="r">'+(e.lucro[y]!=null?f(e.lucro[y]*k,1):'–')+'</td></tr>'});
  $('#d-fin').innerHTML=h+(Y.length?'':'<tr><td class="muted" colspan="3">Sem isenção no top 50 nem lucro bancário nesta base.</td></tr>')+'</tbody>';
  $('#d-fnote').textContent=e.banco?'Lucro do conglomerado prudencial (Banco Central, IF.data). Bancos não aparecem entre as 50 maiores em isenção declarada.':'Isenção: apenas anos em que a empresa esteve entre as 50 maiores beneficiárias (2015–2024).';
}
function gov(){
  var e=cur();
  var gs=[['FHC 1',1995,1998],['FHC 2',1999,2002],['Lula 1',2003,2006],['Lula 2',2007,2010],['Dilma 1',2011,2014],['Dilma 2',2015,2015],['Temer',2017,2018],['Bolsonaro',2019,2022],['Lula 3',2023,2025]];
  function avg(map,a,b,mul){var s=0,n=0;for(var y=a;y<=b;y++){var v=map[y];if(v!=null){s+=v*(FAC[y]||1)*(mul||1);n++}}return n?s/n:null}
  var remAvg={}; Object.keys(e.rem).forEach(function(y){var d=e.rem[y]['Diretoria Estatutária'];if(d)remAvg[y]=d[2]});
  var h='<thead><tr><th>Mandato</th><th class="r">Diretoria: média por membro (R$ mi/ano)</th><th class="r">Isenção declarada (R$ mi/ano)</th><th class="r">Lucro líquido (R$ bi/ano)</th></tr></thead><tbody>';
  gs.forEach(function(g){
    h+='<tr><td><b>'+g[0]+'</b> <span class="muted">'+g[1]+(g[2]>g[1]?'–'+g[2]:'')+'</span></td><td class="r">'+f(avg(remAvg,g[1],g[2]),2)+'</td><td class="r">'+f(avg(e.isenc,g[1],g[2]),0)+'</td><td class="r">'+f(avg(e.lucro,g[1],g[2]),1)+'</td></tr>'});
  $('#d-gov').innerHTML=h+'</tbody>';
}
function all(){acion();rem();fin();gov()}
se.onchange=function(){fillYears();all()}; sa.onchange=acion;
fillYears(); all();
})();
