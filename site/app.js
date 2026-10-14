(function(){
'use strict';
var D=window.DATA, YEARS=D.years, FAC=D.fac, real=true;
var $=function(s,r){return (r||document).querySelector(s)};
var el=function(t,a,h){var n=document.createElement(t);if(a)for(var k in a)n.setAttribute(k,a[k]);if(h!=null)n.innerHTML=h;return n};
var NS='http://www.w3.org/2000/svg';
var sv=function(t,a){var n=document.createElementNS(NS,t);if(a)for(var k in a)n.setAttribute(k,a[k]);return n};
var PAL=['#2563eb','#d97706','#059669','#db2777','#7c3aed','#0891b2','#65a30d','#e11d48','#475569','#ca8a04','#0d9488','#9333ea','#f97316'];
var GOVS=[['FHC',1995,2002],['Lula 1',2003,2006],['Lula 2',2007,2010],['Dilma 1',2011,2014],['Dilma 2',2015,2015],['Temer',2016,2018],['Bolsonaro',2019,2022],['Lula 3',2023,2025]];
function govBase(g){return g.replace(' (parcial)','')}

function money(s){return s.kind==='val'||s.kind==='stock'||(s.kind==='pp'&&/^R\$/.test(s.unit))}
function val(s,y){
  var v=s.data[y]; if(v==null)return null;
  if(real&&money(s))v=v*FAC[y];
  return v;
}
function fmt(v,s){
  if(v==null||isNaN(v))return '–';
  var a=Math.abs(v), d=a>=100?0:a>=10?1:2;
  if(s&&s.kind==='n'&&a>=100)d=0;
  if(s&&s.kind==='pct')d=0;
  var r=v.toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
  return s&&s.kind==='pct'?r+'%':r;
}
function mainSeries(c){return c.series.filter(function(s){return s.main})[0]||c.series[0]}
function pct(a,b){return (a==null||b==null||b===0)?null:(a/b-1)*100}
function delta(p){
  if(p==null)return '';
  var cls=Math.abs(p)<2?'flat':(p>0?'up':'down'), sg=p>0?'+':'';
  return '<span class="'+cls+'">'+sg+p.toFixed(0)+'%</span>';
}
function firstYear(list){
  var m=null;
  list.forEach(function(s){for(var y in s.data){var n=+y;if(s.data[y]!=null&&(m==null||n<m))m=n}});
  return m;
}
function yearsFrom(m){return YEARS.filter(function(y){return +y>=m})}

/* ---------- mapa e cards ---------- */
var mapa=$('#mapa');
(function(){
  mapa.setAttribute('viewBox','0 0 '+window.BRASIL.w+' '+window.BRASIL.h);
  mapa.appendChild(sv('path',{d:window.BRASIL.d}));
})();

function spark(c){
  var s=mainSeries(c), f=firstYear([s]), ys=yearsFrom(f), pts=ys.map(function(y){return val(s,y)}), w=200,h=34;
  var xs=pts.filter(function(v){return v!=null});
  if(xs.length<2)return '';
  var mn=Math.min.apply(null,xs), mx=Math.max.apply(null,xs), rg=(mx-mn)||1, d='';
  pts.forEach(function(v,i){if(v==null)return;var x=i*(w/(pts.length-1)),y=h-3-(v-mn)/rg*(h-8);d+=(d?'L':'M')+x.toFixed(1)+','+y.toFixed(1)});
  return '<svg class="spark" viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none" aria-hidden="true"><path d="'+d+'" fill="none" stroke="'+c.color+'" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>';
}
function renderCards(){
  var L=$('#col-left'),R=$('#col-right');L.innerHTML='';R.innerHTML='';
  D.cards.forEach(function(c,i){
    var s=mainSeries(c), hy=c.headYear||'2025', f=firstYear([s]), v=val(s,hy), v0=val(s,String(f));
    var b=el('button',{'class':'card',type:'button','data-id':c.id,style:'--c:'+c.color});
    b.innerHTML='<span class="ic" aria-hidden="true">'+c.icon+'</span>'+
      '<span><span class="t">'+c.title+'</span>'+
      '<span class="v"><b>'+fmt(v,s)+'</b><small>'+s.unit+' em '+hy+'</small>'+delta(pct(v,v0))+'<small>vs '+f+'</small></span></span>'+
      spark(c);
    b.addEventListener('click',function(){openModal(c.id)});
    (i<5?L:R).appendChild(b);
  });
}


/* ---------- pizza ---------- */
var PIEPAL=['#2563eb','#d97706','#059669','#db2777','#7c3aed','#0891b2','#65a30d','#e11d48','#475569','#ca8a04','#0d9488','#9ca3af'];
function pieSVG(host,slices,centerTxt){
  host.innerHTML='';
  var W=300,H=300,cx=150,cy=150,R=130,r=70,tot=slices.reduce(function(a,s){return a+s.value},0);
  var svg=sv('svg',{viewBox:'0 0 '+W+' '+H,'class':'pie'});
  if(!(tot>0)){var t=sv('text',{x:cx,y:cy,'text-anchor':'middle'});t.textContent='Sem dados';svg.appendChild(t);host.appendChild(svg);return}
  var a0=-Math.PI/2;
  slices.forEach(function(s,i){
    var f=s.value/tot, a1=a0+f*2*Math.PI, big=f>.5?1:0;
    if(f>=.9999){svg.appendChild(sv('circle',{cx:cx,cy:cy,r:(R+r)/2,fill:'none',stroke:s.color,'stroke-width':R-r}));a0=a1;return}
    var p=[cx+R*Math.cos(a0),cy+R*Math.sin(a0),cx+R*Math.cos(a1),cy+R*Math.sin(a1),cx+r*Math.cos(a1),cy+r*Math.sin(a1),cx+r*Math.cos(a0),cy+r*Math.sin(a0)];
    var path=sv('path',{d:'M'+p[0]+','+p[1]+'A'+R+','+R+' 0 '+big+' 1 '+p[2]+','+p[3]+'L'+p[4]+','+p[5]+'A'+r+','+r+' 0 '+big+' 0 '+p[6]+','+p[7]+'Z',fill:s.color,stroke:'var(--surface)','stroke-width':1.5});
    var tt=sv('title');tt.textContent=s.label+': '+(f*100).toFixed(1)+'%';path.appendChild(tt);svg.appendChild(path);a0=a1;
  });
  if(centerTxt){var t1=sv('text',{x:cx,y:cy-2,'text-anchor':'middle','font-size':'15','font-weight':'700',style:'fill:var(--ink)'});t1.textContent=centerTxt[0];svg.appendChild(t1);
    var t2=sv('text',{x:cx,y:cy+16,'text-anchor':'middle','font-size':'11'});t2.textContent=centerTxt[1]||'';svg.appendChild(t2)}
  host.appendChild(svg);
}
function pieLegend(host,slices,fmtv){
  var tot=slices.reduce(function(a,s){return a+s.value},0), h='';
  slices.forEach(function(s){h+='<div class="pl"><i style="background:'+s.color+'"></i><span>'+s.label+'</span><b>'+fmtv(s.value)+'</b><em>'+(tot?(s.value/tot*100).toFixed(1):'0')+'%</em></div>'});
  host.innerHTML=h;
}
function curPie(c){var arr=c.pies||(c.pie?[c.pie]:[]); var i=+($('#m-pieyear').dataset.pi||0); return arr[Math.min(i,arr.length-1)]}
function pieSlices(c,y){
  var P=curPie(c), out=[];
  function S(k){return c.series.filter(function(s){return s.key===k})[0]}
  if(P.list!=null){
    var L=c.lists[P.list], rows=(L.byYear[y]||[]).slice(0,P.top||10), totS=S(P.total), tot=totS?val(totS,y):null, sumTop=0;
    rows.forEach(function(r,i){var v=r[1]/(P.div||1000)*(real?FAC[y]:1);sumTop+=v;out.push({label:r[0],value:v,color:PIEPAL[i%11]})});
    if(tot!=null&&tot>sumTop)out.push({label:P.otherLabel||'Demais empresas',value:tot-sumTop,color:PIEPAL[11]});
  }else{
    var sum=0;
    P.keys.forEach(function(k,i){var s=S(k),v=val(s,y);if(v!=null){sum+=v;out.push({label:s.label.trim(),value:v,color:PIEPAL[i%11]})}});
    if(P.total){var t=val(S(P.total),y);if(t!=null&&t>sum)out.push({label:P.other||'Outros',value:t-sum,color:PIEPAL[11]})}
  }
  return out.filter(function(s){return s.value>0});
}
function pieYears(c,P){
  var ref=P.list!=null?Object.keys(c.lists[P.list].byYear):YEARS.filter(function(y){return P.keys.every(function(k){return c.series.some(function(s){return s.key===k&&s.data[y]!=null})})});
  return ref.filter(function(y){return +y<=2025}).sort();
}
function drawPieTab(){
  var c=cur, svgc=$('#m-chart'); svgc.innerHTML=''; svgc.style.display='none'; $('#m-legend').innerHTML='';
  var box=$('#m-pieyear'); box.hidden=false;
  if(!box.dataset.ready||box.dataset.card!==c.id){
    var arr=c.pies||[c.pie], P0=arr[0];
    var optsHtml=arr.length>1?'<label>Pizza: <select id="m-pp">'+arr.map(function(p,i){return '<option value="'+i+'">'+(p.title||'Composição')+'</option>'}).join('')+'</select></label> ':'';
    box.innerHTML=optsHtml+'<label>Ano: <select id="m-py"></select></label><div class="pierow"><div id="m-pie"></div><div id="m-pieleg" class="pleg"></div></div>';
    box.dataset.pi=0;
    var ys=pieYears(c,P0);
    var pp=$('#m-pp'); if(pp)pp.onchange=function(){box.dataset.pi=this.value;var yv=$('#m-py').value,ys2=pieYears(c,curPie(c)),s2=$('#m-py');s2.innerHTML='';ys2.forEach(function(y){s2.appendChild(el('option',{value:y},y))});s2.value=ys2.indexOf(yv)>=0?yv:ys2[ys2.length-1];drawPieTab()};
    var sel=$('#m-py'); ys.forEach(function(y){sel.appendChild(el('option',{value:y},y))});
    sel.value=ys.indexOf('2023')>=0?'2023':ys[ys.length-1]; sel.onchange=drawPieTab;
    box.dataset.ready='1'; box.dataset.card=c.id;
  }
  var y=$('#m-py').value, sl=pieSlices(c,y), tot=sl.reduce(function(a,s){return a+s.value},0), PP=curPie(c);
  var unit=PP.unit||'R$ bi';
  pieSVG($('#m-pie'),sl,[fmt(tot,{kind:'val'}),unit+' em '+y]);
  pieLegend($('#m-pieleg'),sl,function(v){return fmt(v,{kind:'val'})+(PP.unit?'':' bi')});
}

/* ---------- modal ---------- */
var modal=$('#modal'), cur=null, tab='val', hidden={};
function groupsOf(c){
  var g=[];
  if(c.series.some(function(s){return s.kind==='val'||s.kind==='stock'}))g.push(['val','Valores (R$ bi)']);
  if(c.series.some(function(s){return s.kind==='n'}))g.push(['n','Pessoas / empresas']);
  if(c.series.some(function(s){return s.kind==='pp'}))g.push(['pp','Valor por pessoa']);
  if(c.series.some(function(s){return s.kind==='pct'}))g.push(['pct','Concentração']);
  if(c.pie||c.pies)g.push(['pie','Pizza']);
  return g;
}
function seriesFor(c,t){
  return c.series.filter(function(s){
    if(t==='val')return s.kind==='val'||s.kind==='stock';
    return s.kind===t;
  });
}
function openModal(id){
  cur=D.cards.filter(function(c){return c.id===id})[0]; if(!cur)return;
  tab=groupsOf(cur)[0][0]; hidden={}; cur.series.forEach(function(s){if(s.off)hidden[s.key]=true});
  var sh=$('.sheet',modal); sh.style.setProperty('--c',cur.color);
  $('#m-icon').textContent=cur.icon; $('#m-title').textContent=cur.title; $('#m-desc').textContent=cur.desc;
  renderModal();
  modal.hidden=false; document.body.style.overflow='hidden';
  if(location.hash!=='#'+id)history.replaceState(null,'','#'+id);
  $('#m-close').focus();
}
function closeModal(){modal.hidden=true;document.body.style.overflow='';cur=null;history.replaceState(null,'',location.pathname+location.search)}
function renderModal(){
  var c=cur, s=mainSeries(c), hy=c.headYear||'2025', f=firstYear([s]);
  var k=$('#m-kpis'); k.innerHTML='';
  var p0=pct(val(s,hy),val(s,String(f)));
  var items=[[hy+(hy==='2025'?' (último ano completo)':' (último ano completo publicado)'),fmt(val(s,hy),s)+' '+s.unit],
             ['Variação '+f+' → '+hy,p0==null?'–':(p0>0?'+':'')+p0.toFixed(0)+'%']];
  var ex=c.partial||[];
  GOVS.forEach(function(g){
    var vs=[];
    for(var y=g[1];y<=g[2];y++){ if(ex.indexOf(String(y))>=0)continue; var v=val(s,String(y)); if(v!=null)vs.push(v); }
    if(vs.length>=1&&(vs.length>=2||ex.length))
      items.push(['Média anual: '+g[0]+(vs.length===1?' (só um ano)':''),fmt(vs.reduce(function(a,b){return a+b},0)/vs.length,s)+' '+s.unit]);
  });
  items.forEach(function(it){k.appendChild(el('div',{'class':'kpi'},'<span>'+it[0]+'</span><b>'+it[1]+'</b>'))});
  var T=$('#m-tabs'); T.innerHTML='';
  var gs=groupsOf(c);
  if(gs.length>1)gs.forEach(function(g){
    var b=el('button',{type:'button','class':g[0]===tab?'on':''},g[1]);
    b.onclick=function(){tab=g[0];renderModal()};T.appendChild(b);
  });
  drawChart();
  buildTable();
  var Ls=$('#m-lists'); Ls.innerHTML='';
  (c.lists||[]).forEach(function(L){
    var ys=Object.keys(L.byYear).sort();
    var wrap=el('div'); wrap.appendChild(el('h3',null,L.title));
    var box=el('div',{'class':'listsel'});
    var sel=el('select');
    ys.forEach(function(y){sel.appendChild(el('option',{value:y},y))});
    sel.value=ys.indexOf('2023')>=0?'2023':ys[ys.length-1];
    box.appendChild(el('span',null,'Ano:'));box.appendChild(sel);wrap.appendChild(box);
    var tw=el('div',{'class':'tablewrap'}); var tb=el('table'); tw.appendChild(tb); wrap.appendChild(tw);
    function draw(){
      var rows=L.byYear[sel.value]||[], cols=L.cols||['Nome','Valor'];
      var h='<thead><tr><th>#  '+cols[0]+'</th>'+cols.slice(1).map(function(x){return '<th>'+x+'</th>'}).join('')+'</tr></thead><tbody>';
      rows.forEach(function(r,i){
        h+='<tr><td>'+(i+1)+'. '+r[0]+'</td><td>'+r[1].toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'</td>'+(r.length>2?'<td style="text-align:left">'+r[2]+'</td>':'')+'</tr>';
      });
      tb.innerHTML=h+'</tbody>';
    }
    sel.onchange=draw; draw(); Ls.appendChild(wrap);
  });
  var N=$('#m-notes'); N.innerHTML='';
  (c.notes||[]).forEach(function(n){N.appendChild(el('li',null,n))});
  c.series.forEach(function(s){ if(s.note)N.appendChild(el('li',null,'<b>'+s.label.trim()+':</b> '+s.note)) });
  N.appendChild(el('li',null,real?'Valores corrigidos pelo IPCA para a média de 2025 (itens em dinheiro).':'Valores nominais, sem correção pela inflação.'));
}
function drawChart(){
  if(tab==='pie'){drawPieTab();return}
  $('#m-pieyear').hidden=true; $('#m-chart').style.display='';
  var c=cur, list=seriesFor(c,tab);
  var svg=$('#m-chart'); svg.innerHTML='';
  var lg=$('#m-legend'); lg.innerHTML='';
  var W=860,H=330,m={l:64,r:16,t:30,b:34}, iw=W-m.l-m.r, ih=H-m.t-m.b;
  var vis=list.filter(function(s){return !hidden[s.key]});
  list.forEach(function(s,i){
    var b=el('button',{type:'button','class':hidden[s.key]?'off':'',style:'--sc:'+PAL[i%PAL.length]},'<i></i>'+s.label.trim());
    b.onclick=function(){hidden[s.key]=!hidden[s.key];drawChart()};lg.appendChild(b);
  });
  var fy=firstYear(vis.length?vis:list), yrs=yearsFrom(fy==null?2016:fy), n=yrs.length;
  var all=[];vis.forEach(function(s){yrs.forEach(function(y){var v=val(s,y);if(v!=null)all.push(v)})});
  if(!all.length){var tx=sv('text',{x:W/2,y:H/2,'text-anchor':'middle'});tx.textContent='Sem dados';svg.appendChild(tx);return}
  var mx=Math.max.apply(null,all), mn=Math.min(0,Math.min.apply(null,all));
  var step=niceStep((mx-mn)/4), top=Math.ceil(mx/step)*step, bot=Math.floor(mn/step)*step;
  if(top===bot)top=bot+step;
  var span=Math.max(n-1,1), dx=iw/span;
  var X=function(i){return n===1?m.l+iw/2:m.l+i*dx}, Y=function(v){return m.t+ih-(v-bot)/(top-bot)*ih};
  var runs=[],last=null;
  yrs.forEach(function(y,i){var g=govBase(D.gov[y]);if(g!==last){runs.push([i,i,g]);last=g}else runs[runs.length-1][1]=i});
  runs.forEach(function(b,i){
    var x0=X(b[0])-(b[0]===0?0:dx/2), x1=X(b[1])+(b[1]===n-1?0:dx/2);
    svg.appendChild(sv('rect',{x:x0,y:m.t,width:x1-x0,height:ih,style:'fill:var('+(i%2?'--g3':'--g1')+');opacity:.9'}));
    if(x1-x0>46){var t=sv('text',{x:(x0+x1)/2,y:m.t-9,'text-anchor':'middle','font-size':'10'});t.textContent=b[2];svg.appendChild(t)}
  });
  for(var v=bot;v<=top+1e-9;v+=step){
    var yy=Y(v);svg.appendChild(sv('line',{x1:m.l,x2:W-m.r,y1:yy,y2:yy,'class':'grid'}));
    var t2=sv('text',{x:m.l-8,y:yy+4,'text-anchor':'end'});t2.textContent=v.toLocaleString('pt-BR',{maximumFractionDigits:step<1?1:0});svg.appendChild(t2);
  }
  var every=n>20?3:n>12?2:1;
  yrs.forEach(function(y,i){if(i!==n-1&&(i%every||(every>1&&i===n-2)))return;var t=sv('text',{x:X(i),y:H-12,'text-anchor':'middle'});t.textContent=y+(y==='2026'?'*':'');svg.appendChild(t)});
  var single=vis.length===1&&n<=16, bw=Math.min(28,dx*.6);
  var ex=(c.partial||[]).concat(['2026']);
  vis.forEach(function(s){
    var col=PAL[list.indexOf(s)%PAL.length], d='', pts=[], prev=false;
    yrs.forEach(function(y,i){
      var v=val(s,y);
      if(v==null){prev=false;return}
      var px=X(i),py=Y(v),part=ex.indexOf(y)>=0;pts.push([px,py,v,y,part]);
      if(part){prev=false;return}
      d+=(prev?'L':'M')+px.toFixed(1)+','+py.toFixed(1);prev=true;
    });
    if(single&&tab!=='pct'){
      pts.forEach(function(p){svg.appendChild(sv('rect',{x:p[0]-bw/2,y:Math.min(p[1],Y(0)),width:bw,height:Math.abs(Y(0)-p[1]),fill:col,opacity:p[4]?.35:.85,rx:3}))});
    }else{
      svg.appendChild(sv('path',{d:d,fill:'none',stroke:col,'stroke-width':2.2,'stroke-linejoin':'round'}));
      if(n<=20)pts.forEach(function(p){svg.appendChild(sv('circle',{cx:p[0],cy:p[1],r:p[4]?3:3.2,fill:col,opacity:p[4]?.4:1}))});
    }
  });
  var tip=$('#m-tip');
  var hover=sv('line',{y1:m.t,y2:m.t+ih,stroke:'currentColor','stroke-opacity':.25});hover.style.display='none';svg.appendChild(hover);
  var catcher=sv('rect',{x:m.l-10,y:m.t,width:iw+20,height:ih,fill:'transparent'});svg.appendChild(catcher);
  catcher.addEventListener('mousemove',function(e){
    var r=svg.getBoundingClientRect(), px=(e.clientX-r.left)/r.width*W;
    var i=n===1?0:Math.max(0,Math.min(n-1,Math.round((px-m.l)/dx)));
    hover.setAttribute('x1',X(i));hover.setAttribute('x2',X(i));hover.style.display='';
    var parc=(yrs[i]==='2026'||ex.indexOf(yrs[i])>=0);
    var h='<b>'+yrs[i]+(parc?' (parcial)':'')+' · '+govBase(D.gov[yrs[i]])+'</b>';
    vis.forEach(function(s){h+='<div><span>'+s.label.trim().slice(0,38)+'</span><span>'+fmt(val(s,yrs[i]),s)+'</span></div>'});
    tip.innerHTML=h;tip.hidden=false;
    var wr=svg.parentNode.getBoundingClientRect(), tx=e.clientX-wr.left+14;
    if(tx>wr.width-210)tx=e.clientX-wr.left-220;
    tip.style.left=tx+'px';tip.style.top=(e.clientY-wr.top-10)+'px';
  });
  catcher.addEventListener('mouseleave',function(){tip.hidden=true;hover.style.display='none'});
}
function niceStep(raw){
  if(!(raw>0))return 1;
  var e=Math.pow(10,Math.floor(Math.log10(raw))), f=raw/e;
  return (f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*e;
}
function buildTable(){
  var c=cur, t=$('#m-table'), fy=firstYear(c.series), ys=yearsFrom(fy);
  var h='<thead><tr><th>Item</th>'+ys.map(function(y){
    return '<th>'+y+(y==='2026'?'*':'')+'<br><span class="gh">'+govBase(D.gov[y]).replace('Dilma→Temer','Dilma/Temer')+'</span></th>';
  }).join('')+'</tr></thead><tbody>';
  c.series.forEach(function(s){
    h+='<tr><td>'+s.label.trim()+' <span class="gh">('+s.unit+')</span></td>'+ys.map(function(y){return '<td>'+fmt(val(s,y),s)+'</td>'}).join('')+'</tr>';
  });
  t.innerHTML=h+'</tbody>';
}
function csv(){
  var c=cur, ys=yearsFrom(firstYear(c.series)), rows=[['Item','Unidade'].concat(ys)];
  c.series.forEach(function(s){rows.push([s.label.trim(),s.unit].concat(ys.map(function(y){var v=val(s,y);return v==null?'':String(v).replace('.',',')})))});
  var txt=rows.map(function(r){return r.map(function(x){return '"'+String(x).replace(/"/g,'""')+'"'}).join(';')}).join('\n');
  var a=el('a',{href:URL.createObjectURL(new Blob(['﻿'+txt],{type:'text/csv;charset=utf-8'})),download:c.id+'.csv'});
  document.body.appendChild(a);a.click();a.remove();
}


/* ---------- comparar quem recebe ---------- */
var cmpEl=$('#cmp'), cmpOn={}, cmpInit=false;
function fmtN(n){if(n==null)return 'n/d';if(n>=1e6)return (n/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' milhões';if(n>=1e3)return Math.round(n/1e3).toLocaleString('pt-BR')+' mil';return Math.round(n).toLocaleString('pt-BR')}
function fmtR(v){return 'R$ '+(v>=1e9?(v/1e9).toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi':v>=1e6?(v/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' milhões':v>=1e3?(v/1e3).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mil':Math.round(v).toLocaleString('pt-BR'))}
function gdata(g,y){
  var r=g.byYear[y]; if(!r||!r[0]||r[1]==null)return null;
  var v=r[1]*(real?FAC[y]:1);
  return {n:r[0],v:v,pp:v*1e9/r[0],est:r[2]===1};
}
function openCmp(){
  var C=D.compare;
  if(!cmpInit){
    cmpInit=true;
    var ys=$('#cmp-year'); C.years.forEach(function(y){ys.appendChild(el('option',{value:y},y))}); ys.value='2016';
    var gl=$('#cmp-groups');
    C.groups.forEach(function(g){
      cmpOn[g.id]=!(g.id==='agro_emp'||g.id==='inss_rgps'||g.bench);
      if(g.bench)return;
      var lb=el('label',null,'<input type="checkbox" '+(cmpOn[g.id]?'checked':'')+' data-g="'+g.id+'"> '+g.label);
      lb.firstChild.onchange=function(){cmpOn[g.id]=this.checked;renderCmp()};
      gl.appendChild(lb);
    });
    ['#cmp-a','#cmp-b'].forEach(function(s){C.groups.forEach(function(g){$(s).appendChild(el('option',{value:g.id},g.label))})});
    $('#cmp-a').value='mil_reserva'; $('#cmp-b').value='bf';
    var bs=$('#cmp-bench'); C.groups.filter(function(g){return g.bench}).forEach(function(g){bs.appendChild(el('option',{value:g.id},g.label))}); bs.value='b_edu';
    $('#cmp-year').value='2016'; bs.onchange=renderCmp;
    ys.onchange=renderCmp; $('#cmp-a').onchange=renderCmp; $('#cmp-b').onchange=renderCmp;
  }
  renderCmp(); cmpEl.hidden=false; document.body.style.overflow='hidden';
}
function closeCmp(){cmpEl.hidden=true;document.body.style.overflow=''}
function renderCmp(){
  var C=D.compare, y=$('#cmp-year').value, G=C.groups, rows=[];
  G.forEach(function(g,i){var d=gdata(g,y); if(d)rows.push({g:g,d:d,color:PIEPAL[i%11]})});
  rows=rows.filter(function(r){return !r.g.bench||true});
  var sel=rows.filter(function(r){return cmpOn[r.g.id]});
  var totV=sel.reduce(function(a,r){return a+r.d.v},0), totN=sel.reduce(function(a,r){return a+r.d.n},0);
  pieSVG($('#cmp-pie-v'),sel.map(function(r){return {label:r.g.label,value:r.d.v,color:r.color}}),[totV.toLocaleString('pt-BR',{maximumFractionDigits:0}),'R$ bi em '+y]);
  pieLegend($('#cmp-leg-v'),sel.map(function(r){return {label:r.g.label,value:r.d.v,color:r.color}}),function(v){return v.toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi'});
  pieSVG($('#cmp-pie-n'),sel.map(function(r){return {label:r.g.label,value:r.d.n,color:r.color}}),[fmtN(totN),'pessoas/empresas']);
  pieLegend($('#cmp-leg-n'),sel.map(function(r){return {label:r.g.label,value:r.d.n,color:r.color}}),function(v){return fmtN(v)});
  /* comparação A x B */
  var A=rows.filter(function(r){return r.g.id===$('#cmp-a').value})[0], B=rows.filter(function(r){return r.g.id===$('#cmp-b').value})[0], s=$('#cmp-sentence');
  if(A&&B){
    var ratio=A.d.pp/B.d.pp, maior=ratio>=1?A:B, menor=ratio>=1?B:A, r2=ratio>=1?ratio:1/ratio;
    function part(X){return '<b>'+(X.d.est?'≈ ':'')+fmtN(X.d.n)+'</b> '+X.g.who+' '+X.g.verb+' <b>R$ '+X.d.v.toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi</b> (R$ '+Math.round(X.d.pp).toLocaleString('pt-BR')+' '+X.g.per+' no ano)'}
    s.innerHTML='Em <b>'+y+'</b>, '+part(A)+'. '+part(B)+'. Em média, cada um dos <b>'+maior.g.who+'</b> '+(maior.g.verb==='tiveram isenção de'?'teve':maior.g.verb==='pagaram'?'recebeu':'recebeu')+' <b>'+r2.toLocaleString('pt-BR',{maximumFractionDigits:r2>=10?0:1})+' vezes</b> mais que cada um dos '+menor.g.who+
      (maior.d.n<menor.d.n?', mesmo sendo um grupo <b>'+(menor.d.n/maior.d.n).toLocaleString('pt-BR',{maximumFractionDigits:0})+' vezes menor</b>.':'.');
  }else s.textContent='Não há dados de um dos grupos neste ano (veja a tabela).';
  /* contrastes */
  var cand=[];
  rows.forEach(function(a){rows.forEach(function(b){
    if(a===b||!(a.d.n<b.d.n)||!(a.d.pp>b.d.pp)||b.d.n/a.d.n<3)return;
    cand.push({a:a,b:b,ratio:a.d.pp/b.d.pp});
  })});
  cand.sort(function(p,q){return q.ratio-p.ratio});
  var used={},out=[]; cand.forEach(function(c){if(out.length<6&&!used[c.a.g.id]){used[c.a.g.id]=1;out.push(c)}});
  $('#cmp-high').innerHTML=out.map(function(c){
    return '<li><b>'+(c.a.d.est?'≈ ':'')+fmtN(c.a.d.n)+'</b> '+c.a.g.who+' ('+c.a.g.verb+' R$ '+c.a.d.v.toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi): <b>'+c.ratio.toLocaleString('pt-BR',{maximumFractionDigits:0})+' vezes</b> mais por pessoa que os <b>'+fmtN(c.b.d.n)+'</b> '+c.b.g.who+' ('+c.b.g.verb+' R$ '+c.b.d.v.toLocaleString('pt-BR',{maximumFractionDigits:1})+' bi).</li>';
  }).join('')||'<li>Sem contrastes calculáveis neste ano.</li>';
  /* tabela */
  var h='<thead><tr><th>Grupo</th><th>Pessoas</th><th>Recebeu (R$ bi)</th><th>R$ por pessoa/ano</th><th>R$ por pessoa/mês</th><th>% do dinheiro</th><th>% das pessoas</th><th>Índice</th></tr></thead><tbody>';
  rows.forEach(function(r){
    var on=cmpOn[r.g.id], pv=on&&totV?r.d.v/totV*100:null, pn=on&&totN?r.d.n/totN*100:null;
    h+='<tr style="opacity:'+(on?1:.45)+'"><td>'+r.g.label+' <span class="gh">'+r.g.cat+'</span></td><td class="'+(r.d.est?'est':'')+'">'+fmtN(r.d.n)+'</td><td>'+r.d.v.toLocaleString('pt-BR',{maximumFractionDigits:1})+'</td><td>'+Math.round(r.d.pp).toLocaleString('pt-BR')+'</td><td>'+Math.round(r.d.pp/12).toLocaleString('pt-BR')+'</td><td>'+(pv==null?'–':pv.toFixed(1)+'%')+'</td><td>'+(pn==null?'–':pn.toFixed(2)+'%')+'</td><td>'+(pv&&pn?(pv/pn).toFixed(1)+'×':'–')+'</td></tr>';
  });
  $('#cmp-table').innerHTML=h+'</tbody>';
  var N=$('#cmp-notes'); N.innerHTML='';
  var seen={}; G.forEach(function(g){if(g.note&&!seen[g.note]){seen[g.note]=1;N.appendChild(el('li',null,'<b>'+g.label+':</b> '+g.note))}});
  renderRatios();
  N.appendChild(el('li',null,'Índice = % do dinheiro ÷ % das pessoas (acima de 1× o grupo recebe mais que sua parte numérica). '+(real?'Valores em R$ de 2025.':'Valores nominais.')));
}

/* ---------- quantas vezes mais (ano a ano) ---------- */
function benchOf(){var id=$('#cmp-bench').value;return D.compare.groups.filter(function(g){return g.id===id})[0]}
function fmtX(x){return x>=100?Math.round(x).toLocaleString('pt-BR'):x>=10?x.toFixed(0):x.toFixed(1).replace('.',',')}
function renderRatios(){
  var C=D.compare, B=benchOf(), Y=C.years.map(String), groups=C.groups.filter(function(g){return !g.bench&&cmpOn[g.id]});
  var series=[];
  groups.forEach(function(g,i){
    var pts={};
    Y.forEach(function(y){var a=gdata(g,y),b=gdata(B,y); if(a&&b&&b.pp>0)pts[y]={r:a.pp/b.pp,a:a,b:b}});
    series.push({g:g,color:PIEPAL[C.groups.indexOf(g)%11],pts:pts});
  });
  /* legenda */
  var lg=$('#cmp-ratio-leg'); lg.innerHTML=''; 
  series.forEach(function(s){var b=el('button',{type:'button',style:'--sc:'+s.color},'<i></i>'+s.g.label); lg.appendChild(b)});
  /* gráfico log */
  var svg=$('#cmp-ratio'); svg.innerHTML='';
  var W=860,H=340,m={l:92,r:16,t:16,b:30},iw=W-m.l-m.r,ih=H-m.t-m.b;
  var all=[]; series.forEach(function(s){Object.keys(s.pts).forEach(function(y){all.push(s.pts[y].r)})});
  if(!all.length){var t=sv('text',{x:W/2,y:H/2,'text-anchor':'middle'});t.textContent='Sem dados para esta comparação';svg.appendChild(t);}
  else{
    var lo=Math.floor(Math.log10(Math.max(Math.min.apply(null,all),0.1))), hi=Math.ceil(Math.log10(Math.max.apply(null,all)));
    if(hi<=lo)hi=lo+1;
    var yrs=Y.filter(function(y){return series.some(function(s){return s.pts[y]})}), n=yrs.length, dx=n>1?iw/(n-1):0;
    var X=function(i){return n>1?m.l+i*dx:m.l+iw/2}, Yf=function(v){return m.t+ih-(Math.log10(v)-lo)/(hi-lo)*ih};
    for(var e=lo;e<=hi;e++){var yy=Yf(Math.pow(10,e)); svg.appendChild(sv('line',{x1:m.l,x2:W-m.r,y1:yy,y2:yy,'class':'grid'}));var tt=sv('text',{x:m.l-8,y:yy+4,'text-anchor':'end'});tt.textContent=(Math.pow(10,e)).toLocaleString('pt-BR')+'×';svg.appendChild(tt)}
    var y1=Yf(1); if(lo<=0&&hi>=0){svg.appendChild(sv('line',{x1:m.l,x2:W-m.r,y1:y1,y2:y1,stroke:'currentColor','stroke-opacity':.45,'stroke-dasharray':'4 3'}))}
    yrs.forEach(function(y,i){var t=sv('text',{x:X(i),y:H-10,'text-anchor':'middle'});t.textContent=y;svg.appendChild(t)});
    series.forEach(function(s){
      var d='',prev=false;
      yrs.forEach(function(y,i){var p=s.pts[y]; if(!p){prev=false;return} d+=(prev?'L':'M')+X(i).toFixed(1)+','+Yf(p.r).toFixed(1); prev=true});
      svg.appendChild(sv('path',{d:d,fill:'none',stroke:s.color,'stroke-width':2.2,'stroke-linejoin':'round'}));
      yrs.forEach(function(y,i){var p=s.pts[y]; if(p)svg.appendChild(sv('circle',{cx:X(i),cy:Yf(p.r),r:3,fill:s.color}))});
    });
    var tip=$('#cmp-ratio-tip'), hov=sv('line',{y1:m.t,y2:m.t+ih,stroke:'currentColor','stroke-opacity':.25}); hov.style.display='none'; svg.appendChild(hov);
    var cat=sv('rect',{x:m.l-10,y:m.t,width:iw+20,height:ih,fill:'transparent'}); svg.appendChild(cat);
    cat.addEventListener('mousemove',function(ev){
      var r=svg.getBoundingClientRect(),px=(ev.clientX-r.left)/r.width*W,i=n>1?Math.max(0,Math.min(n-1,Math.round((px-m.l)/dx))):0,y=yrs[i];
      hov.setAttribute('x1',X(i));hov.setAttribute('x2',X(i));hov.style.display='';
      var h='<b>'+y+'</b>'; series.forEach(function(s){var p=s.pts[y]; if(p)h+='<div><span>'+s.g.label.slice(0,34)+'</span><span>'+fmtX(p.r)+'×</span></div>'});
      tip.innerHTML=h; tip.hidden=false; var wr=svg.parentNode.getBoundingClientRect(), tx=ev.clientX-wr.left+14; if(tx>wr.width-230)tx=ev.clientX-wr.left-240; tip.style.left=tx+'px'; tip.style.top=(ev.clientY-wr.top-10)+'px';
    });
    cat.addEventListener('mouseleave',function(){tip.hidden=true;hov.style.display='none'});
  }
  /* mapa de calor */
  var allY=Y.filter(function(y){return series.some(function(s){return s.pts[y]})});
  var h='<thead><tr><th>Grupo (por pessoa)</th>'+allY.map(function(y){return '<th>'+y+'</th>'}).join('')+'</tr></thead><tbody>';
  series.forEach(function(s){
    h+='<tr><td>'+s.g.label+'</td>';
    allY.forEach(function(y){
      var p=s.pts[y];
      if(!p){h+='<td class="na">–</td>';return}
      var k=Math.max(0,Math.min(1,(Math.log10(Math.max(p.r,1))/4))), bg='rgba(124,58,237,'+(0.08+k*0.6).toFixed(2)+')';
      h+='<td style="background:'+bg+'" title="'+s.g.who+': '+fmtN(p.a.n)+' (R$ '+Math.round(p.a.pp).toLocaleString('pt-BR')+' por pessoa/ano) · referência: '+fmtN(p.b.n)+' (R$ '+Math.round(p.b.pp).toLocaleString('pt-BR')+')">'+(p.r<1?'0,'+Math.round(p.r*10):fmtX(p.r))+'×</td>';
    });
    h+='</tr>';
  });
  h+='<tr><td><i>Tamanho do grupo de referência ('+B.who+')</i></td>'+allY.map(function(y){var b=gdata(B,y);return '<td class="na">'+(b?fmtN(b.n):'–')+'</td>'}).join('')+'</tr>';
  $('#cmp-heat').className='heat'; $('#cmp-heat').innerHTML=h+'</tbody>';
  /* cartões do ano selecionado */
  var y=$('#cmp-year').value; $('#cmp-yr-title').textContent='Em '+y+': cada grupo contra '+B.label.split(' – ')[0].toLowerCase()+' ('+B.per+')';
  var b=gdata(B,y), ul=$('#cmp-cards'); ul.innerHTML='';
  if(!b){ul.innerHTML='<li>Sem dados da referência em '+y+'.</li>';return}
  series.map(function(s){return {s:s,d:gdata(s.g,y)}}).filter(function(x){return x.d}).sort(function(p,q){return q.d.pp-p.d.pp}).forEach(function(x){
    var r=x.d.pp/b.pp, size=x.d.n<b.n?(b.n/x.d.n):(x.d.n/b.n), sizeTxt=x.d.n<b.n?'menor':'maior';
    var li=el('li',null,'<span class="big">'+(r>=1?fmtX(r)+'×':'0,'+Math.round(r*10)+'×')+'</span> — cada um dos <b>'+(x.d.est?'≈ ':'')+fmtN(x.d.n)+'</b> '+x.s.g.who+' '+(x.s.g.verb==='tiveram isenção de'?'teve isenção de':'recebeu')+' <b>'+fmtR(x.d.pp)+'</b> no ano, '+(r>=1?'<b>'+fmtX(r)+' vezes mais</b>':'<b>'+fmtX(1/r)+' vezes menos</b>')+' que o gasto federal '+B.per+' ('+fmtR(b.pp)+'). O grupo era <b>'+fmtX(size)+' vezes '+sizeTxt+'</b> que os '+fmtN(b.n)+' '+B.who+'.');
    li.style.setProperty('--gc',x.s.color); ul.appendChild(li);
  });
}

$('#btn-cmp').onclick=openCmp; $('#cmp-close').onclick=closeCmp;
cmpEl.addEventListener('click',function(e){if(e.target===cmpEl)closeCmp()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!cmpEl.hidden)closeCmp()});

$('#m-close').onclick=closeModal;
modal.addEventListener('click',function(e){if(e.target===modal)closeModal()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!modal.hidden)closeModal()});
$('#m-csv').onclick=csv;
function setReal(v){real=v;$('#btn-real').classList.toggle('on',v);$('#btn-nom').classList.toggle('on',!v);renderCards();if(cur)renderModal();if(!cmpEl.hidden)renderCmp()}
$('#btn-real').onclick=function(){setReal(true)};
$('#btn-nom').onclick=function(){setReal(false)};
renderCards();
if(location.hash==='#comparar'){openCmp()}else if(location.hash.length>1){var hs=location.hash.slice(1).split(':');openModal(hs[0]);if(hs[1]&&cur){tab=hs[1];renderModal()}}
})();
