(function(){
'use strict';
var G=window.GEST, $=function(s){return document.querySelector(s)};
var el=function(t,a,h){var n=document.createElement(t);if(a)for(var k in a)n.setAttribute(k,a[k]);if(h!=null)n.innerHTML=h;return n};
var NS='http://www.w3.org/2000/svg', sv=function(t,a){var n=document.createElementNS(NS,t);if(a)for(var k in a)n.setAttribute(k,a[k]);return n};
var PAL=['#2563eb','#d97706','#059669','#db2777','#7c3aed','#0891b2','#65a30d','#e11d48','#475569','#ca8a04'];
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
var per=G.per.filter(function(p){return p.indexOf('2026')<0}), nam=G.nam;
function bi(v){return v==null?'–':(v/1e9).toLocaleString('pt-BR',{maximumFractionDigits:1})}
/* grafico */
(function(){
  var svg=$('#g-chart'),W=860,H=340,m={l:56,r:16,t:16,b:30},iw=W-m.l-m.r,ih=H-m.t-m.b,n=per.length,dx=iw/(n-1);
  var max=0; nam.forEach(function(g){per.forEach(function(p){var v=G.groups[g][p]; if(v>max)max=v})}); max=Math.ceil(max/1e11)*1e11;
  var X=function(i){return m.l+i*dx},Y=function(v){return m.t+ih-v/max*ih};
  for(var v=0;v<=max;v+=max/4){var y=Y(v); svg.appendChild(sv('line',{x1:m.l,x2:W-m.r,y1:y,y2:y,stroke:'var(--line)'})); var t=sv('text',{x:m.l-8,y:y+4,'text-anchor':'end',style:'fill:var(--muted);font-size:11px'});t.textContent=Math.round(v/1e9);svg.appendChild(t)}
  per.forEach(function(p,i){if(i%2)return;var t=sv('text',{x:X(i),y:H-10,'text-anchor':'middle',style:'fill:var(--muted);font-size:11px'});t.textContent=p.slice(0,4);svg.appendChild(t)});
  var lg=$('#g-leg');
  nam.forEach(function(g,k){
    var col=PAL[k%PAL.length],d='';
    per.forEach(function(p,i){var v=G.groups[g][p]; if(v==null)return; d+=(d?'L':'M')+X(i)+','+Y(v)});
    svg.appendChild(sv('path',{d:d,fill:'none',stroke:col,'stroke-width':g==='Sem gestor'?2.6:2,'stroke-dasharray':g==='Sem gestor'?'6 4':''}));
    lg.appendChild(el('button',{type:'button',style:'--sc:'+col},'<i></i>'+g));
  });
  var tip=$('#g-tip'),cat=sv('rect',{x:m.l,y:m.t,width:iw,height:ih,fill:'transparent'}); svg.appendChild(cat);
  cat.addEventListener('mousemove',function(e){var r=svg.getBoundingClientRect(),px=(e.clientX-r.left)/r.width*W,i=Math.max(0,Math.min(n-1,Math.round((px-m.l)/dx))),p=per[i];
    var h='<b>'+p.slice(0,4)+'</b>'; nam.forEach(function(g){h+='<div><span>'+g+'</span><span>'+bi(G.groups[g][p])+' bi</span></div>'}); tip.innerHTML=h; tip.hidden=false;
    var wr=svg.parentNode.getBoundingClientRect(),tx=e.clientX-wr.left+14; if(tx>wr.width-230)tx=e.clientX-wr.left-240; tip.style.left=tx+'px'; tip.style.top=(e.clientY-wr.top-10)+'px'});
  cat.addEventListener('mouseleave',function(){tip.hidden=true});
})();
/* tabela */
var pp=G.per;
$('#g-tab').innerHTML='<thead><tr><th>Grupo</th>'+pp.map(function(p){return '<th>'+p.slice(0,4)+(p.indexOf('2026')===0?'*':'')+'</th>'}).join('')+'</tr></thead><tbody>'+
 nam.map(function(g){return '<tr><td>'+g+'</td>'+pp.map(function(p){var v=G.groups[g][p];return '<td>'+(v==null?'–':bi(v))+'</td>'}).join('')+'</tr>'}).join('')+
 '<tr><td><b>Total</b></td>'+pp.map(function(p){return '<td><b>'+bi(G.tot[p])+'</b></td>'}).join('')+'</tr>'+
 '<tr><td>% "Sem gestor"</td>'+pp.map(function(p){var v=G.groups['Sem gestor'][p];return '<td>'+(v==null?'–':(v/G.tot[p]*100).toFixed(1)+'%')+'</td>'}).join('')+'</tr></tbody>';
$('#g-tab').insertAdjacentHTML('afterend','<p class="foot">* ago/2026 é parcial e não comparável.</p>');
/* fundos */
var sp=$('#g-per'),sg=$('#g-grp');
G.per.forEach(function(p){sp.appendChild(el('option',{value:p},p.slice(0,4)))}); sp.value='2025-12';
sg.appendChild(el('option',{value:'Sem gestor'},'Sem gestor'));
['Bradesco','Itaú Unibanco','Santander','Franklin Templeton','BTG Pactual','Safra','Funcef'].forEach(function(g){sg.appendChild(el('option',{value:g},g))});
function drawFunds(){
  var p=sp.value,g=sg.value,rows;
  if(g==='Sem gestor') rows=(G.sem[p]||[]).map(function(r){return [r[0],r[1],r[2]]});
  else rows=((G.funds[p]||{})[g]||[]).map(function(r){return [r[0],'',r[1]]});
  var note=(g!=='Sem gestor'&&!G.funds[p])?'<tr><td colspan="3">Lista por gestora disponível só para dez/2010, 2015, 2020 e 2025 (veja a planilha para todos os anos).</td></tr>':'';
  $('#g-funds').className='list'; $('#g-funds').innerHTML='<thead><tr><th>Fundo</th><th>CNPJ</th><th>R$ milhões</th></tr></thead><tbody>'+note+rows.map(function(r){return '<tr><td style="white-space:normal;text-align:left">'+esc(r[0])+'</td><td>'+esc(r[1])+'</td><td>'+(r[2]/1e6).toLocaleString('pt-BR',{maximumFractionDigits:0})+'</td></tr>'}).join('')+'</tbody>';
}
sp.onchange=drawFunds; sg.onchange=drawFunds; drawFunds();
/* lucro */
var Y=[];for(var y=2005;y<=2025;y++)Y.push(y);
$('#g-lucro').innerHTML='<thead><tr><th>Instituição</th>'+Y.map(function(y){return '<th>'+y+'</th>'}).join('')+'<th>1º sem. 2026</th></tr></thead><tbody>'+
 Object.keys(G.lucro.anual).map(function(b){return '<tr><td>'+b+'</td>'+Y.map(function(y){var v=G.lucro.anual[b][y];return '<td>'+(v==null?'–':v.toLocaleString('pt-BR',{maximumFractionDigits:1}))+'</td>'}).join('')+'<td>'+(G.lucro.h1_2026[b]==null?'–':G.lucro.h1_2026[b].toLocaleString('pt-BR',{maximumFractionDigits:1}))+'</td></tr>'}).join('')+'</tbody>';
/* donos */
$('#g-donos').innerHTML='<thead><tr><th>Grupo</th><th>Controlador / acionista</th><th>Participação</th><th>Observações</th><th>Fonte</th></tr></thead><tbody>'+
 G.donos.map(function(d){return '<tr><td>'+esc(d[0])+'</td><td style="white-space:normal;text-align:left">'+esc(d[1])+'</td><td style="white-space:normal;text-align:left">'+esc(d[2])+'</td><td style="white-space:normal;text-align:left">'+esc(d[3])+'</td><td>'+(d[4]?'<a href="'+esc(d[4])+'" target="_blank" rel="noopener">link</a>':'')+'</td></tr>'}).join('')+'</tbody>';
$('#g-patr').innerHTML='<thead><tr><th>Pessoa / família</th><th>Patrimônio informado</th><th>Fonte</th><th>Link</th></tr></thead><tbody>'+
 G.patr.map(function(d){return '<tr><td style="white-space:normal;text-align:left">'+esc(d[0])+'</td><td style="white-space:normal;text-align:left">'+esc(d[1])+'</td><td style="white-space:normal;text-align:left">'+esc(d[2])+'</td><td>'+(d[3]?'<a href="'+esc(d[3])+'" target="_blank" rel="noopener">link</a>':'')+'</td></tr>'}).join('')+'</tbody>';
})();
