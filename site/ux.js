(function(){
'use strict';
var P=location.pathname.split('/').pop()||'index.html';
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var th=ls('ux-theme'); if(th)document.documentElement.setAttribute('data-theme',th);
var head=document.head;
function meta(n,c){var m=document.createElement('meta');m.name=n;m.content=c;head.appendChild(m)}
meta('theme-color','#0e1116'); meta('mobile-web-app-capable','yes'); meta('apple-mobile-web-app-capable','yes');
var l=document.createElement('link');l.rel='manifest';l.href='manifest.webmanifest';head.appendChild(l);
var IC={
 home:'<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
 book:'<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 21V5"/>',
 scale:'<path d="M12 3v18"/><path d="M5 7h14"/><path d="M5 7l-3 7a4 4 0 006 0z"/><path d="M19 7l-3 7a4 4 0 006 0z"/>',
 flag:'<path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/>',
 dots:'<circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>',
 up:'<path d="M6 14l6-6 6 6"/>'
};
function svg(k){return '<svg viewBox="0 0 24 24" aria-hidden="true">'+IC[k]+'</svg>'}
var MAIN=[['index.html','Início','home'],['entenda.html','Entenda','book'],['vezes.html','Vezes mais','scale'],['presidentes.html','Governos','flag']];
var MORE=[['donos.html','Donos e executivos','Quem controla bancos e grandes empresas'],['gestoras.html','Gestoras e donos','Rentistas, fundos e lucro dos bancos'],['salarios.html','Altos salários','Quem recebe acima de R$ 50 mil'],['dados.html','Dados e fontes','Planilhas, arquivos e links oficiais'],['metodologia.html','Metodologia e limites','O que é estimativa e o que falta']];
function cur(h){return (P===h||(P===''&&h==='index.html'))?' aria-current="page"':''}
var bar=document.createElement('nav');bar.className='ux-tabbar';bar.setAttribute('aria-label','Navegação principal');
bar.innerHTML=MAIN.map(function(m){return '<a href="'+m[0]+'"'+cur(m[0])+'>'+svg(m[2])+'<span>'+m[1]+'</span></a>'}).join('')+
  '<button type="button" id="ux-more-btn" aria-haspopup="dialog"'+(MORE.some(function(m){return m[0]===P})?' aria-current="page"':'')+'>'+svg('dots')+'<span>Mais</span></button>';
var scrim=document.createElement('div');scrim.className='ux-scrim';
var more=document.createElement('div');more.className='ux-more';more.setAttribute('role','dialog');more.setAttribute('aria-label','Mais páginas');
more.innerHTML='<h3>Mais páginas</h3>'+MORE.map(function(m){return '<a href="'+m[0]+'"'+cur(m[0])+'><span>'+m[1]+'<small>'+m[2]+'</small></span></a>'}).join('')+
  '<h3 style="margin-top:1rem">Ajustes</h3><button class="row" type="button" id="ux-theme">Alternar tema claro/escuro</button>'+(navigator.share?'<button class="row" type="button" id="ux-share">Compartilhar esta página</button>':'');
var fab=document.createElement('button');fab.className='ux-fab';fab.type='button';fab.setAttribute('aria-label','Voltar ao topo');fab.innerHTML=svg('up');
document.body.appendChild(bar);document.body.appendChild(scrim);document.body.appendChild(more);document.body.appendChild(fab);
function open(o){document.body.classList.toggle('ux-more-open',o)}
document.getElementById('ux-more-btn').onclick=function(){open(!document.body.classList.contains('ux-more-open'))};
scrim.onclick=function(){open(false)};
document.addEventListener('keydown',function(e){if(e.key==='Escape')open(false)});
document.getElementById('ux-theme').onclick=function(){
  var r=document.documentElement,d=r.getAttribute('data-theme');
  var dark=d?d==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;
  var n=dark?'light':'dark'; r.setAttribute('data-theme',n); ls('ux-theme',n); open(false);
};
var sh=document.getElementById('ux-share'); if(sh)sh.onclick=function(){navigator.share({title:document.title,url:location.href}).catch(function(){})};
fab.onclick=function(){window.scrollTo({top:0})};
var tick=false;window.addEventListener('scroll',function(){if(tick)return;tick=true;requestAnimationFrame(function(){fab.classList.toggle('on',window.scrollY>700);tick=false})},{passive:true});
/* modais: trava rolagem do fundo e botão voltar do celular fecha o modal */
function watch(m){
  var was=!m.hidden;
  new MutationObserver(function(){
    var now=!m.hidden;
    if(now===was)return; was=now;
    var any=[].some.call(document.querySelectorAll('.modal'),function(x){return !x.hidden});
    document.body.classList.toggle('ux-lock',any);
    if(now){try{history.pushState({ux:1},'')}catch(e){}}
  }).observe(m,{attributes:true,attributeFilter:['hidden']});
}
[].forEach.call(document.querySelectorAll('.modal'),watch);
window.addEventListener('popstate',function(){
  [].forEach.call(document.querySelectorAll('.modal'),function(m){if(!m.hidden)m.hidden=true});
});
})();
