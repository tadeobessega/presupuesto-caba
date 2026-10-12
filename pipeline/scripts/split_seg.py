import re
s=open('site/template.html').read()
lines=s.split('\n')
# pieces
btn=[l for l in lines if 'tabbtn-sg' in l][0]
i=s.index('<div class="tab" id="tab-sg"'); j=s.index('<section id="metodo">')
sg_html=s[i:j]
a=s.index('// ======== Seguridad'); b=s.index('// ---------- tabs')
sg_js=s[a:b]
# ---- main template without seguridad
m=s.replace(btn+'\n','').replace(sg_html,'').replace(sg_js,'')
m=m.replace("if(TAB==='sg'){seguridad();} ","").replace(" else if(h==='seguridad')TAB='sg';","")
m=m.replace("['p27','ej','tb','sg'].forEach","['p27','ej','tb'].forEach")
m=m.replace("try{const h=location.hash.replace('#',''); const st=localStorage.getItem('ceer-tab');","try{const h=location.hash.replace('#',''); let st=localStorage.getItem('ceer-tab'); if(st==='sg')st='p27';")
open('site/template_main.html','w').write(m)
# ---- seguridad page
style=s[:s.index('</style>')+8]
style=style.replace('<title>Presupuesto CABA 2027 en perspectiva</title>','<title>Seguridad en la Ciudad</title>')
header=s[s.index('<header class="top">'):s.index('</header>')+9]
header=re.sub(r'<nav class="tabs".*?</nav>','<nav class="tabs" aria-label="Secciones"><span class="pagename">Seguridad en la Ciudad de Buenos Aires</span></nav>',header,flags=re.S)
footer=s[s.index('<footer class="banner">'):s.index('</footer>')+9]
body=sg_html.replace(' hidden>','>',1)
metodo='''<section id="metodo">
  <h2><span class="tag">Metodología</span>Fuentes y notas</h2>
  <div class="method"><p><b>Delito registrado.</b> IDECBA sobre datos del Ministerio de Seguridad (nacional hasta 2016, de la Ciudad desde 2017). La tasa se calcula cada 10.000 habitantes. Hay años sin dato.</p><p><b>Mapa del Delito.</b> Registros georreferenciados del Ministerio de Seguridad de la Ciudad publicados en BA Data, 2016–2025. Para 2016, 2020 y 2025 se usaron las versiones en Excel porque los CSV publicados están dañados.</p><p><b>Homicidios y femicidios.</b> IDECBA; femicidios según la Oficina de la Mujer de la Corte Suprema.</p><p><b>Gasto.</b> Función Seguridad del presupuesto ejecutado (BA Data) y Planilla 3 del Proyecto 2027. Pesos de 2027: IPCBA a septiembre de 2026, 2% mensual de octubre a diciembre y 18% de inflación 2027 según la pauta del proyecto.</p></div>
</section>'''
script_all=s[s.index('<script src="https://cdnjs'):]
head_js=s[s.index('(function(){'):s.index('// ---------- KPIs + conclusions')]
opts_fn=[l for l in lines if l.startswith('function opts(')][0]
sjs=sg_js
assert 'SGG' in sjs
tail='''
function renderAll(){ themeChart(); seguridad(); const n=document.getElementById('unitnote'); if(n) n.textContent='';}
initPeriodUI(()=>renderAll()); initPNG();
document.querySelectorAll('[data-u]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.u===U); b.addEventListener('click',()=>{U=b.dataset.u; try{localStorage.setItem('ceer-unit',U);}catch(e){} document.querySelectorAll('[data-u]').forEach(x=>x.setAttribute('aria-pressed',x===b)); renderAll();});});
document.getElementById('themebtn').addEventListener('click',()=>{const r=document.documentElement; const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'); r.setAttribute('data-theme',cur==='dark'?'light':'dark'); renderAll();});
matchMedia('(prefers-color-scheme: light)').addEventListener('change',renderAll);
document.documentElement.lang='es';
renderAll();
})();
'''
page=style+'\n<style>.pagename{font-weight:600;font-size:14px;color:var(--fg);padding:10px 4px}</style>\n'+header+'\n<main>\n'+body+metodo+'\n</main>\n'+footer+'\n<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>\n<script id="data" type="application/json">__DATA__</script>\n<script>\n'+head_js+'\n'+opts_fn+'\n'+sjs+tail+'</script>\n'
open('site/template_seg.html','w').write(page)
print(len(m), len(page))
