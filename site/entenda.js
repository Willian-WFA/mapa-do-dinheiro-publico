(function(){
'use strict';
var D=window.DATA, E=window.ENT, C=D.compare, FAC=D.fac;
var $=function(s){return document.querySelector(s)};
var COL=['#b45309','#0e7490','#4338ca','#15803d','#be123c','#1d4ed8','#334155','#9ca3af'];
function fmtR(v){return 'R$ '+Math.round(v).toLocaleString('pt-BR')}
function fmtN(n){return n>=1e6?(n/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' milhões':n>=1e3?Math.round(n/1e3).toLocaleString('pt-BR')+' mil':String(Math.round(n))}
var ys=Object.keys(E).sort(); var sel=$('#en-year');
ys.forEach(function(y){var o=document.createElement('option');o.value=y;o.textContent=y;sel.appendChild(o)});
sel.value='2023';
function G(id){return C.groups.filter(function(g){return g.id===id})[0]}
function pp(id,y){var g=G(id),r=g&&g.byYear[y]; if(!r||!r[0])return null; return {pp:r[1]*1e9/r[0]*(FAC[y]||1),n:r[0],est:r[2]===1}}
function render(){
  var y=sel.value, S=E[y], keys=Object.keys(S.itens);
  /* waffle: 100 quadrados, maior resto */
  var raw=keys.map(function(k){return S.itens[k]/S.total*100}), base=raw.map(Math.floor), left=100-base.reduce(function(a,b){return a+b},0);
  raw.map(function(v,i){return [v-Math.floor(v),i]}).sort(function(a,b){return b[0]-a[0]}).slice(0,left).forEach(function(x){base[x[1]]++});
  var w=$('#en-waffle'); w.innerHTML='';
  keys.forEach(function(k,i){for(var j=0;j<base[i];j++){var q=document.createElement('i');q.style.background=COL[i%COL.length];q.title=k;w.appendChild(q)}});
  $('#en-total').textContent='Total em '+y+': R$ '+(S.total/1000).toLocaleString('pt-BR',{maximumFractionDigits:1})+' trilhões (valores da época).';
  function sumN(ids){var t=0,ok=false;ids.forEach(function(id){var g=G(id),r=g&&g.byYear[y];if(r&&r[0]){t+=r[0];ok=true}});return ok?t:null}
  function people(k){
    var n,tx;
    if(/^Juros/.test(k))return 'pagos a quem empresta ao governo: bancos, fundos e investidores (sem contagem de pessoas)';
    if(/INSS/.test(k)){n=sumN(['inss_rgps']);tx='benefícios pagos'}
    else if(/^Sal/.test(k)){n=sumN(['mil_ativa','mil_reserva','mil_pens','civ_ativos','civ_aposent','civ_pens']);tx='pessoas (ativos, aposentados e pensionistas)'}
    else if(/^Bolsa/.test(k)){n=sumN(['bf','bpc']);tx='famílias e beneficiários'}
    else if(/^Sa/.test(k)){n=sumN(['b_sau']);tx='habitantes atendidos pelo SUS (população)'}
    else if(/^Educ/.test(k)){n=sumN(['b_edu']);tx='alunos na educação básica e superior'}
    else if(/^Segur/.test(k)){n=sumN(['b_seg']);tx='habitantes (população)'}
    else return 'varia: obras, subsídios, seguro-desemprego, transferências';
    return n?'≈ '+fmtN(n)+' '+tx:'sem contagem disponível neste ano';
  }
  $('#en-leg').innerHTML=keys.map(function(k,i){return '<div><i style="background:'+COL[i%COL.length]+'"></i><span>'+k+'<br><small class="muted">'+people(k)+'</small></span><b>R$ '+raw[i].toLocaleString('pt-BR',{maximumFractionDigits:1})+'</b></div>'}).join('');
  /* barras por mes */
  var items=[['mil_reserva','Militar da reserva ou reformado'],['civ_ativos','Servidor civil ativo (Executivo)'],['civ_aposent','Servidor civil aposentado'],['mil_pens','Pensionista militar'],['mil_ativa','Militar da ativa'],['civ_pens','Pensionista civil'],['inss_rgps','Benefício do INSS (média)'],['bpc','BPC (idosos e pessoas com deficiência)'],['bf','Família no Bolsa Família'],
    ['b_ass','Gasto federal em assistência, por beneficiário'],['b_edu','Gasto federal em educação, por aluno'],['b_sau','Gasto federal em saúde, por habitante'],['b_seg','Gasto federal em segurança, por habitante']];
  var rows=[];
  items.forEach(function(it){var d=pp(it[0],y); if(d)rows.push({id:it[0],lab:it[1],m:d.pp/12,n:d.n,est:d.est})});
  var mx=Math.max.apply(null,rows.map(function(r){return r.m}));
  $('#en-bars').innerHTML=rows.map(function(r){
    var serv=/^b_/.test(r.id), col=serv?'#0e7490':(/^mil|^civ/.test(r.id)?'#b45309':'#c2410c');
    return '<div class="b2"><div class="l"><b>'+r.lab+'</b><span>'+(r.est?'≈ ':'')+fmtN(r.n)+(serv?' pessoas atendidas':' pessoas')+'</span></div><div class="bar"><i style="width:'+Math.max(1.5,r.m/mx*100)+'%;background:'+col+'"></i><em>'+fmtR(r.m)+' por mês</em></div></div>'}).join('');
  /* chamadas */
  var al=pp('b_edu',y), sa=pp('b_sau',y), as=pp('b_ass',y), sg=pp('b_seg',y), out=[];
  [['mil_reserva','Cada militar da reserva ou reformado'],['civ_ativos','Cada servidor civil ativo do Executivo'],['mil_pens','Cada pensionista militar']].forEach(function(it){
    var a=pp(it[0],y); if(!a)return;
    var s='<b>'+it[1]+'</b> recebeu em média <b>'+fmtR(a.pp/12)+' por mês</b>. ';
    if(al)s+='É <span class="big" style="font-size:1.6rem">'+(a.pp/al.pp).toLocaleString('pt-BR',{maximumFractionDigits:0})+' vezes</span> o gasto federal por aluno ('+fmtR(al.pp/12)+' por mês). ';
    if(as)s+='E '+(a.pp/as.pp).toLocaleString('pt-BR',{maximumFractionDigits:0})+' vezes o gasto federal em assistência por beneficiário. ';
    if(al)s+='O grupo tem '+fmtN(a.n)+' pessoas; os alunos são '+fmtN(al.n)+' (cerca de '+(al.n/a.n).toLocaleString('pt-BR',{maximumFractionDigits:0})+' vezes mais).';
    out.push('<div>'+s+'</div>');
  });
  var t=G('top50').byYear[y];
  if(t&&t[0])out.push('<div><b>As 50 maiores empresas em isenção fiscal</b> deixaram de pagar, cada uma, em média <b>R$ '+(t[1]*1e9/t[0]*(FAC[y]||1)/1e6).toLocaleString('pt-BR',{maximumFractionDigits:0})+' milhões</b> em impostos em '+y+' (valor declarado). No total, R$ '+(t[1]*(FAC[y]||1)).toLocaleString('pt-BR',{maximumFractionDigits:0})+' bilhões para apenas 50 empresas.</div>');
  $('#en-call').innerHTML=out.join('')||'<div>Sem dados suficientes para este ano.</div>';
}
function esf(){
  var X=window.ENT_ESF||{}, yrs=Object.keys(X).sort(), y=sel.value;
  if(!yrs.length){$('#en-esf').innerHTML='Os dados de estados e municípios ainda estão sendo reunidos.';return}
  var use=X[y]?y:yrs.reduce(function(b,c){return Math.abs(+c-+y)<Math.abs(+b-+y)?c:b},yrs[0]);
  $('#en-esfnote').textContent=(X[y]?'':'Para '+y+' ainda não há dados completos de estados e municípios; mostrando '+use+'. ')+'Anos já disponíveis: '+yrs.join(', ')+'. Fonte: SICONFI (Tesouro Nacional), despesa paga por função, e execução da União. Pode haver pequena dupla contagem por transferências entre esferas.';
  var h='';
  Object.keys(X[use]).forEach(function(f){
    var d=X[use][f], t=d.uniao+d.est+d.mun, p=function(v){return (v/t*100)};
    h+='<div style="margin:.9rem 0"><b>'+f+'</b> <span class="muted">('+use+': R$ '+(t).toLocaleString("pt-BR",{maximumFractionDigits:0})+' bi no total)</span><div style="display:flex;height:34px;border-radius:8px;overflow:hidden;margin-top:.35rem">'+
      '<div title="União" style="width:'+p(d.uniao)+'%;background:#b45309;color:#fff;display:flex;align-items:center;padding-left:.5rem;font-size:.85rem;white-space:nowrap">União '+p(d.uniao).toFixed(0)+'%</div>'+
      '<div title="Estados" style="width:'+p(d.est)+'%;background:#0e7490;color:#fff;display:flex;align-items:center;padding-left:.5rem;font-size:.85rem;white-space:nowrap">Estados '+p(d.est).toFixed(0)+'%</div>'+
      '<div title="Municípios" style="width:'+p(d.mun)+'%;background:#4338ca;color:#fff;display:flex;align-items:center;padding-left:.5rem;font-size:.85rem;white-space:nowrap">Municípios '+p(d.mun).toFixed(0)+'%</div></div></div>';
  });
  $('#en-esf').innerHTML=h;
}
sel.onchange=function(){render();esf()}; render(); esf();
})();
