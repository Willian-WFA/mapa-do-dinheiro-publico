(function(){
'use strict';
var P=window.PRES, FAC=P.fac, G=P.gov;
var $=function(s){return document.querySelector(s)};
var AREAS=[
 ['saude','Saúde (União)'],['educ','Educação (União)'],['seg','Segurança pública (União)'],['assist','Assistência social (total)'],
 ['bpc','BPC'],['bf','Bolsa Família / Auxílio Brasil'],['inss','INSS (benefícios previdenciários)'],['infra','Infraestrutura'],
 ['juros','Juros da dívida (Governo Central)'],['pessoal','Pessoal de todos os Poderes'],['isenc','Isenção fiscal a empresas (declarada)'],['subs','Subsídios e crédito rural']];
var LAB={}; AREAS.forEach(function(a){LAB[a[0]]=a[1]});
function fmt(v,d){return v==null?'n/d':v.toLocaleString('pt-BR',{maximumFractionDigits:d==null?1:d})}
function real(a,y){var v=P.series[a][y]; return v==null?null:v*FAC[y]}
function gYears(g){var r=[];for(var y=g[2];y<=g[3];y++)r.push(String(y));return r}
function avg(a,g){
  var ys=gYears(g),s=0;
  for(var i=0;i<ys.length;i++){var v=real(a,ys[i]); if(v==null)return null; s+=v}
  return s/ys.length;
}
function perCap(a,g){
  var ys=gYears(g),s=0;
  for(var i=0;i<ys.length;i++){var v=real(a,ys[i]),p=P.pop[ys[i]]; if(v==null||!p)return null; s+=v*1e9/(p*1e6)}
  return s/ys.length;
}
function ends(a,g){var ys=gYears(g),f=real(a,ys[0]),l=real(a,ys[ys.length-1]); if(f==null||l==null||ys.length<2)return null; return (l/f-1)*100}
function prevAvg(a,i){ // média do mandato imediatamente anterior
  return i>0?avg(a,G[i-1]):null;
}
function varPrev(a,i){var c=avg(a,G[i]),p=prevAvg(a,i); return (c==null||p==null||p===0)?null:(c/p-1)*100}
function val(a,i,m){
  if(m==='media')return avg(a,G[i]);
  if(m==='hab')return perCap(a,G[i]);
  if(m==='var')return varPrev(a,i);
  return ends(a,G[i]);
}
var UN={media:' bi',hab:' R$/hab',var:' %',fim:' %'};
function show(v,m){
  if(v==null)return 'n/d';
  if(m==='media')return 'R$ '+fmt(v,1)+' bi';
  if(m==='hab')return 'R$ '+fmt(v,0);
  return (v>0?'+':'')+fmt(v,1)+'%';
}
(function init(){
  var s=$('#p-area'); AREAS.forEach(function(a){var o=document.createElement('option');o.value=a[0];o.textContent=a[1];s.appendChild(o)});
  var ys=Object.keys(P.emp).filter(function(y){return P.emp[y].q>0});
  var set={}; ys.concat(Object.keys(P.org),Object.keys(P.pes)).forEach(function(y){set[y]=1});
  var all=Object.keys(set).sort().reverse(), sa=$('#p-ano');
  all.forEach(function(y){var o=document.createElement('option');o.value=y;o.textContent=y;sa.appendChild(o)});
  s.onchange=render; $('#p-met').onchange=render; sa.onchange=sinais;
})();
function bars(el,area,m){
  var rows=G.map(function(g,i){return {g:g,v:val(area,i,m)}});
  var mx=Math.max.apply(null,rows.map(function(r){return r.v==null?0:Math.abs(r.v)}))||1;
  var best=null; rows.forEach(function(r){if(r.v!=null&&(best==null||r.v>best.v))best=r});
  el.innerHTML=rows.map(function(r){
    var w=r.v==null?0:Math.max(1.5,Math.abs(r.v)/mx*100);
    var cls=r.v==null?'':(r.v<0?'neg':(best&&r===best?'top':''));
    return '<div class="b2"><div class="l"><b>'+r.g[0]+'</b><span>'+r.g[2]+(r.g[3]>r.g[2]?'–'+r.g[3]:'')+'</span></div><div class="bar"><i class="'+cls+'" style="width:'+w+'%"></i><em>'+show(r.v,m)+'</em></div></div>';
  }).join('');
  return rows;
}
function render(){
  var a=$('#p-area').value, m=$('#p-met').value;
  var rows=bars($('#p-bars'),a,m);
  var ok=rows.filter(function(r){return r.v!=null});
  var out=[];
  if(ok.length){
    var hi=ok.slice().sort(function(x,y){return y.v-x.v})[0], lo=ok.slice().sort(function(x,y){return x.v-y.v})[0];
    var lbl={media:'maior média anual',hab:'maior valor por habitante',var:'maior aumento frente ao mandato anterior',fim:'maior crescimento no mandato'}[m];
    out.push('<div><b>'+LAB[a]+':</b> '+lbl+' em <b>'+hi.g[1]+'</b> ('+show(hi.v,m)+'). '+(lo.v<0&&(m==='var'||m==='fim')?'Maior redução: <b>'+lo.g[1]+'</b> ('+show(lo.v,m)+').':'Menor valor: <b>'+lo.g[1]+'</b> ('+show(lo.v,m)+').')+'</div>');
  }
  var cuts=[]; G.forEach(function(g,i){var v=varPrev(a,i); if(v!=null&&v<-0.5)cuts.push(g[0]+' ('+fmt(v,1)+'%)')});
  out.push('<div>'+(cuts.length?'Mandatos em que a média anual real <b>diminuiu</b> frente ao anterior: '+cuts.join(', ')+'.':'Nenhum mandato teve média anual real menor que a do anterior nesta área.')+'</div>');
  $('#p-call').innerHTML=out.join('');
  var ys=Object.keys(P.series[a]).sort();
  $('#p-note').textContent='Dados de '+ys[0]+' a '+ys[ys.length-1]+'. Mandatos sem série completa aparecem como n/d. Valores em reais de 2025 (IPCA).';
  matriz();
}
function matriz(){
  var h='<thead><tr><th>Mandato</th>'+AREAS.map(function(a){return '<th>'+a[1].replace(' (União)','').replace(' (benefícios previdenciários)','').replace(' (declarada)','')+'</th>'}).join('')+'</tr></thead><tbody>';
  G.forEach(function(g,i){
    h+='<tr><td><b>'+g[0]+'</b><small class="muted">'+g[2]+(g[3]>g[2]?'–'+g[3]:'')+'</small></td>';
    AREAS.forEach(function(a){
      var v=avg(a[0],g), d=varPrev(a[0],i);
      h+='<td>'+(v==null?'n/d':fmt(v,1))+(d==null?'':'<small class="'+(d>=0?'up':'dn')+'">'+(d>0?'+':'')+fmt(d,0)+'%</small>')+'</td>';
    });
    h+='</tr>';
  });
  $('#p-matriz').innerHTML=h+'</tbody>';
}
function sinais(){
  var y=$('#p-ano').value, sis=P.sis[y]||[];
  $('#p-anonote').textContent=sis.length?'Aviso: em '+y+' a lista de '+sis.join(' e ')+' mudou muito de tamanho em relação ao ano anterior (provável mudança de cobertura da base); sinais dessa lista foram omitidos.':'';
  var E=P.emp[y];
  var tag={novo:'<span class="tag">novo no top 50</span>',volta:'<span class="tag v">voltou ao top 50</span>',salto:'<span class="tag s">≥ 3× o ano anterior</span>'};
  var el=$('#p-emp');
  el.innerHTML=E&&E.lista.length?'<thead><tr><th>Empresa</th><th>Atividade</th><th>Sinal</th><th class="r">Isenção no ano (R$ mi)</th><th class="r">Ano anterior (R$ mi)</th></tr></thead><tbody>'+E.lista.map(function(r){
    return '<tr><td><b>'+r.nome+'</b><br><span class="muted">CNPJ raiz '+r.cnpj+(r.uf?' · '+r.uf:'')+'</span></td><td>'+(r.cnae||'')+'</td><td>'+tag[r.flag]+'</td><td class="r">'+fmt(r.valor,0)+'</td><td class="r">'+(r.prev==null?'fora do top 50':fmt(r.prev,0))+'</td></tr>'}).join('')+'</tbody>':'<tbody><tr><td class="muted">Sem sinais calculados para este ano (a base de isenção começa em 2015 e vai até 2024).</td></tr></tbody>';
  var O=P.org[y]||[];
  $('#p-org').innerHTML=O.length?'<thead><tr><th>Órgão</th><th>Poder</th><th class="r">Pessoas acima de R$ 50 mil no ano</th><th class="r">Ano anterior</th></tr></thead><tbody>'+O.map(function(r){
    return '<tr><td><b>'+r.orgao+'</b></td><td>'+r.esfera+'</td><td class="r">'+r.n+'</td><td class="r">'+r.prev+'</td></tr>'}).join('')+'</tbody>':'<tbody><tr><td class="muted">Nenhum órgão com salto acentuado neste ano, ou ano excluído por mudança geral de cobertura.</td></tr></tbody>';
  var Pp=P.pes[y];
  $('#p-pes').innerHTML=Pp&&Pp.top.length?'<thead><tr><th>Nome</th><th>Órgão e cargo</th><th class="r">Maior mês (R$)</th><th class="r">Meses acima de 50 mil</th></tr></thead><tbody>'+Pp.top.map(function(r){
    return '<tr><td><b>'+r.nome+'</b></td><td>'+r.orgao+'<br><span class="muted">'+(r.cargo||'')+'</span></td><td class="r">'+fmt(r.max,0)+'</td><td class="r">'+(r.meses||'')+'</td></tr>'}).join('')+'</tbody>':'<tbody><tr><td class="muted">Sem dados para este ano.</td></tr></tbody>';
  $('#p-pnote').textContent=Pp?'No ano de '+y+', '+Pp.q.toLocaleString('pt-BR')+' pessoas apareceram pela primeira vez acima de R$ 50 mil na base (mostramos as 12 de maior mês). Quase sempre é pagamento retroativo, promoção, cargo novo ou mudança de cadastro; os dados são públicos e oficiais, mas isso não indica irregularidade.':'';
}
function infra(){
  var m='media', rows=bars($('#p-infra'),'infra','media');
}
render(); infra(); sinais();
})();
