(function(){
var F=window.FONTES, PL=window.PLAN||[], $=function(s){return document.querySelector(s)};
var base=localStorage.getItem('dd-base')||''; $('#dd-base').value=base;
function join(b,p){if(!b)return '';return b.replace(/\/+$/,'')+'/'+p.replace(/^\/+/,'')}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function render(){
  base=$('#dd-base').value.trim(); localStorage.setItem('dd-base',base);
  var q=$('#dd-q').value.toLowerCase();
  $('#dd-plan').innerHTML='<thead><tr><th>Arquivo</th><th>MB</th><th>Neste site</th><th>Sua cópia</th></tr></thead><tbody>'+PL.filter(function(p){return !q||p.arq.toLowerCase().indexOf(q)>=0}).map(function(p){
    var c=join(base,p.arq); return '<tr><td>'+esc(p.arq)+'</td><td>'+p.mb+'</td><td><a href="'+esc(p.arq)+'">abrir</a></td><td>'+(c?'<a href="'+esc(c)+'">link</a>':'—')+'</td></tr>'}).join('')+'</tbody>';
  var rows=F.filter(function(f){return !q||(f.fonte+' '+f.conteudo+' '+f.local+' '+f.obs).toLowerCase().indexOf(q)>=0});
  $('#dd-src').innerHTML='<thead><tr><th>Fonte</th><th>Conteúdo</th><th>Arquivos</th><th>MB</th><th>Pasta local</th><th>Fonte oficial</th><th>Sua cópia</th></tr></thead><tbody>'+rows.map(function(f){
    var c=f.local?join(base,f.local):'';
    return '<tr><td>'+esc(f.fonte)+'</td><td style="white-space:normal">'+esc(f.conteudo)+(f.obs?' <span class="gh">'+esc(f.obs)+'</span>':'')+'</td><td>'+(f.n||'')+'</td><td>'+(f.mb||'')+'</td><td style="text-align:left;white-space:normal"><code>'+esc(f.local)+'</code></td><td>'+(f.link?'<a href="'+esc(f.link)+'" target="_blank" rel="noopener">oficial</a>':'')+'</td><td>'+(c?'<a href="'+esc(c)+'">link</a>':'—')+'</td></tr>'}).join('')+'</tbody>';
}
$('#dd-base').oninput=render; $('#dd-q').oninput=render; render();
})();
