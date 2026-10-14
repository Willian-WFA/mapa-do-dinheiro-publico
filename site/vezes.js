(function(){
'use strict';
var D=window.DATA, C=D.compare, $=function(s){return document.querySelector(s)};
var el=function(t,a,h){var n=document.createElement(t);if(a)for(var k in a)n.setAttribute(k,a[k]);if(h!=null)n.innerHTML=h;return n};
var NS='http://www.w3.org/2000/svg', sv=function(t,a){var n=document.createElementNS(NS,t);if(a)for(var k in a)n.setAttribute(k,a[k]);return n};
var PAL=['#2563eb','#d97706','#059669','#db2777','#7c3aed','#0891b2','#65a30d','#e11d48','#475569','#ca8a04','#0d9488','#9ca3af'];
var GROUPS=C.groups.filter(function(g){return !g.bench}), BENCH=C.groups.filter(function(g){return g.bench});
function fmtN(n){if(n>=1e6)return (n/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' milhões';if(n>=1e3)return Math.round(n/1e3).toLocaleString('pt-BR')+' mil';return Math.round(n).toLocaleString('pt-BR')}
function fmtR(v){return 'R$ '+(v>=1e9?(v/1e9).toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi':v>=1e6?(v/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' milhões':v>=1e3?(v/1e3).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mil':Math.round(v).toLocaleString('pt-BR'))}
function fmtX(x){return x>=100?Math.round(x).toLocaleString('pt-BR'):x>=10?x.toFixed(0):x.toFixed(1).replace('.',',')}
function gd(g,y){var r=g.byYear[y]; if(!r||!r[0]||r[1]==null)return null; return {n:r[0],v:r[1]*1e9,pp:r[1]*1e9/r[0],est:r[2]===1}}
var bsel=$('#vz-bench'), ysl=$('#vz-year'), on={};
BENCH.forEach(function(b){bsel.appendChild(el('option',{value:b.id},b.label))}); bsel.value='b_edu';
function B(){return BENCH.filter(function(b){return b.id===bsel.value})[0]}
function rows(y){
  var b=B(), bd=gd(b,y); if(!bd)return {b:b,bd:null,list:[]};
  var list=[]; GROUPS.forEach(function(g,i){var d=gd(g,y); if(d)list.push({g:g,d:d,r:d.pp/bd.pp,color:PAL[C.groups.indexOf(g)%11]})});
  list.sort(function(a,c){return c.r-a.r}); return {b:b,bd:bd,list:list};
}
function render(){
  var y=ysl.value; $('#vz-yearlbl').textContent=y;
  var R=rows(y), b=R.b, bd=R.bd;
  $('#vz-t1').textContent='Em '+y+': cada grupo contra o gasto '+b.per+' em '+b.label.split(' – ')[0].toLowerCase();
  if(!bd){$('#vz-top').innerHTML='<p>Sem dados da referência em '+y+'.</p>';$('#vz-bars').innerHTML='';return}
  $('#vz-explain').innerHTML='Referência: <b>'+fmtR(bd.pp)+'</b> '+b.per+' no ano, para <b>'+fmtN(bd.n)+'</b> '+b.who+'. '+(b.note||'');
  /* top 3 */
  var top=R.list.filter(function(x){return x.d.n<bd.n}).slice(0,3);
  $('#vz-top').innerHTML=top.map(function(x){
    return '<div class="vz-tile" style="--gc:'+x.color+'"><div class="vz-x">'+fmtX(x.r)+'×</div><div><b>'+(x.d.est?'≈ ':'')+fmtN(x.d.n)+'</b> '+x.g.who+' '+(x.g.verb==='tiveram isenção de'?'tiveram isenção de':'receberam')+' <b>'+fmtR(x.d.pp)+'</b> cada um no ano, '+fmtX(x.r)+' vezes o gasto '+b.per+'. O grupo era <b>'+fmtX(bd.n/x.d.n)+' vezes menor</b> que os '+fmtN(bd.n)+' '+b.who+'.</div></div>';
  }).join('');
  /* barras log */
  var mx=Math.max.apply(null,R.list.map(function(x){return x.r}).concat([10])), LM=Math.ceil(Math.log10(mx));
  $('#vz-bars').innerHTML=R.list.map(function(x){
    var w=Math.max(1,Math.min(100,(Math.log10(Math.max(x.r,1))+0.3)/(LM+0.3)*100));
    var sz=x.d.n<bd.n?fmtX(bd.n/x.d.n)+'× menor':fmtX(x.d.n/bd.n)+'× maior';
    return '<div class="vz-row"><div class="vz-lab"><b>'+x.g.label+'</b><span>'+(x.d.est?'≈ ':'')+fmtN(x.d.n)+' · '+fmtR(x.d.pp)+' '+x.g.per+' no ano · grupo '+sz+' que a referência</span></div><div class="vz-bar"><i style="width:'+w+'%;background:'+x.color+'"></i><em>'+(x.r>=1?fmtX(x.r)+'×':'0,'+Math.round(x.r*10)+'×')+'</em></div></div>';
  }).join('');
  drawLine(y); heat(); 
}
function seriesAll(){
  var b=B(), ys=C.years.map(String), out=[];
  GROUPS.forEach(function(g){var pts={}; ys.forEach(function(y){var a=gd(g,y),c=gd(b,y); if(a&&c)pts[y]=a.pp/c.pp}); if(Object.keys(pts).length)out.push({g:g,pts:pts,color:PAL[C.groups.indexOf(g)%11]})});
  return out;
}
function drawLine(sel){
  var S=seriesAll(), svg=$('#vz-line'); svg.innerHTML='';
  var lg=$('#vz-leg'); lg.innerHTML=''; S.forEach(function(s){lg.appendChild(el('button',{type:'button',style:'--sc:'+s.color},'<i></i>'+s.g.label))});
  var W=860,H=340,m={l:92,r:16,t:16,b:30},iw=W-m.l-m.r,ih=H-m.t-m.b, all=[];
  S.forEach(function(s){Object.keys(s.pts).forEach(function(y){all.push(s.pts[y])})});
  if(!all.length)return;
  var lo=Math.floor(Math.log10(Math.max(Math.min.apply(null,all),0.1))), hi=Math.max(Math.ceil(Math.log10(Math.max.apply(null,all))),lo+1);
  var yrs=C.years.map(String).filter(function(y){return S.some(function(s){return s.pts[y]!=null})}), n=yrs.length, dx=n>1?iw/(n-1):0;
  var X=function(i){return m.l+i*dx}, Y=function(v){return m.t+ih-(Math.log10(v)-lo)/(hi-lo)*ih};
  for(var e=lo;e<=hi;e++){var yy=Y(Math.pow(10,e)); svg.appendChild(sv('line',{x1:m.l,x2:W-m.r,y1:yy,y2:yy,'class':'grid'})); var t=sv('text',{x:m.l-8,y:yy+4,'text-anchor':'end'}); t.textContent=Math.pow(10,e).toLocaleString('pt-BR')+'×'; svg.appendChild(t)}
  yrs.forEach(function(y,i){var t=sv('text',{x:X(i),y:H-10,'text-anchor':'middle'});t.textContent=y;svg.appendChild(t)});
  var si=yrs.indexOf(String(sel)); if(si>=0)svg.appendChild(sv('rect',{x:X(si)-6,y:m.t,width:12,height:ih,fill:'currentColor','fill-opacity':.08}));
  S.forEach(function(s){var d='',prev=false; yrs.forEach(function(y,i){var v=s.pts[y]; if(v==null){prev=false;return} d+=(prev?'L':'M')+X(i).toFixed(1)+','+Y(v).toFixed(1); prev=true}); svg.appendChild(sv('path',{d:d,fill:'none',stroke:s.color,'stroke-width':2.2}));
    yrs.forEach(function(y,i){var v=s.pts[y]; if(v!=null)svg.appendChild(sv('circle',{cx:X(i),cy:Y(v),r:y==String(sel)?5:2.8,fill:s.color}))})});
  var tip=$('#vz-tip'), cat=sv('rect',{x:m.l-8,y:m.t,width:iw+16,height:ih,fill:'transparent'}); svg.appendChild(cat);
  cat.addEventListener('mousemove',function(ev){var r=svg.getBoundingClientRect(),px=(ev.clientX-r.left)/r.width*W,i=n>1?Math.max(0,Math.min(n-1,Math.round((px-m.l)/dx))):0,y=yrs[i];
    var h='<b>'+y+'</b>'; S.forEach(function(s){if(s.pts[y]!=null)h+='<div><span>'+s.g.label.slice(0,32)+'</span><span>'+fmtX(s.pts[y])+'×</span></div>'}); tip.innerHTML=h; tip.hidden=false;
    var wr=svg.parentNode.getBoundingClientRect(), tx=ev.clientX-wr.left+14; if(tx>wr.width-230)tx=ev.clientX-wr.left-240; tip.style.left=tx+'px'; tip.style.top=(ev.clientY-wr.top-10)+'px'});
  cat.addEventListener('mouseleave',function(){tip.hidden=true});
  cat.addEventListener('click',function(ev){var r=svg.getBoundingClientRect(),px=(ev.clientX-r.left)/r.width*W,i=n>1?Math.max(0,Math.min(n-1,Math.round((px-m.l)/dx))):0; ysl.value=yrs[i]; render()});
}
function heat(){
  var S=seriesAll(), ys=C.years.map(String).filter(function(y){return S.some(function(s){return s.pts[y]!=null})});
  var h='<thead><tr><th>Grupo</th>'+ys.map(function(y){return '<th>'+y+'</th>'}).join('')+'</tr></thead><tbody>';
  S.forEach(function(s){h+='<tr><td>'+s.g.label+'</td>'+ys.map(function(y){var v=s.pts[y]; if(v==null)return '<td class="na">–</td>'; var k=Math.max(0,Math.min(1,Math.log10(Math.max(v,1))/4)); return '<td style="background:rgba(124,58,237,'+(0.08+k*0.6).toFixed(2)+')">'+(v<1?'0,'+Math.round(v*10):fmtX(v))+'×</td>'}).join('')+'</tr>'});
  $('#vz-heat').innerHTML=h+'</tbody>';
  $('#vz-note').textContent='Razão = valor por pessoa do grupo ÷ gasto por pessoa atendida na referência, no mesmo ano. Reserva e pensionistas militares antes de 2020: quantidade estimada pela de 2020 (≈). Isenções fiscais são renúncia, não pagamento. Clique no gráfico para trocar o ano.';
}
bsel.onchange=render; ysl.oninput=render;
var timer=null; $('#vz-play').onclick=function(){
  if(timer){clearInterval(timer);timer=null;this.textContent='▶ Passar os anos';return}
  var btn=this; btn.textContent='❚❚ Pausar';
  timer=setInterval(function(){var y=+ysl.value+1; if(y>+ysl.max)y=+ysl.min; ysl.value=y; render()},1200);
};
if(location.hash){var m=location.hash.match(/(\d{4})/); if(m)ysl.value=m[1]}
render();
})();
