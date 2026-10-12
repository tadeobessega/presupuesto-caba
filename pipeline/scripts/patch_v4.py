import re
P='/home/claude/work/site/template.html'
S='/tmp/claude-0/-home-claude-presupuesto-caba/4300654a-61f3-5d7d-9a91-7d488cb58759/scratchpad/v4/'
s=open(P).read()
def rep(old,new,count=1):
    global s
    assert s.count(old)>=1, ('MISSING',old[:90])
    s=s.replace(old,new) if count==0 else s.replace(old,new,count)
def repfn(name,new):
    global s
    a=s.index('function %s(){'%name); b=s.index('\n}\n',a)+3
    s=s[:a]+new.rstrip()+'\n'+s[b:]
for n in ['ministerio','deuda','lupa','empleo']:
    repfn(n,open(S+n+'.js').read())

# ---------- tokens
rep('--proj:#ff6a3d;','--proj:#ff6a3d; --proj2:#ffb394;')
s=s.replace('--proj:#e04e1f;','--proj:#e04e1f; --proj2:#f2a07c;')

# ---------- CSS v4
css4='''/* v4 */
.nw{white-space:nowrap}
.hero{align-items:start}
.hero .kpis{margin-top:30px}
.kpi small{display:block;min-height:2.9em;line-height:1.45}
.unitnote{min-height:3.2em}
.promesas{gap:24px}
.prom{padding:26px 26px 24px;gap:14px}
@supports (grid-template-rows:subgrid){.prom{display:grid;grid-row:span 5;grid-template-rows:subgrid;row-gap:14px;align-content:start}}
.prom p{font-size:14.5px;line-height:1.6}
.prom .facts div{padding:10px 12px}
.prom .chart.mini{height:270px;margin-top:6px;align-self:end}
.bl{flex-direction:row;align-items:center;gap:14px;min-height:42px}
.blogo{height:30px;align-self:center}
.bl span{font-family:var(--font);font-weight:400;font-size:15px;letter-spacing:0}
.social a{min-height:42px;box-sizing:border-box}
.subbar{border-top:1px solid var(--line)}
.subin{max-width:1280px;margin:0 auto;padding:7px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:12.5px;color:var(--muted)}
.subin select{padding:4px 6px;font-size:12.5px}
.subin .sep{width:1px;height:18px;background:var(--line2);margin:0 4px}
.subin #pernote{flex:1;min-width:200px;text-align:right}
.card,.prom{position:relative}
.card:has(canvas) h3{padding-right:64px}
.prom q{padding-right:4px}
.dlbtn{position:absolute;top:12px;right:14px;font:600 11px var(--font);letter-spacing:.04em;background:transparent;color:var(--muted);border:1px solid var(--line2);padding:4px 7px;cursor:pointer;z-index:2}
.dlbtn:hover{color:var(--fg);border-color:var(--fg)}
.prom .dlbtn{top:auto;bottom:14px;right:16px}
#lupa-jur{font-size:12.5px}
#lupa-jur td{padding:6px 6px}
'''
rep('@media (max-width:980px){.hero', css4+'@media (max-width:980px){.hero')
rep('.bl .bsrc{font-size:12px;font-weight:400;color:#8f9bb0}\n','')
rep('<span class="bsrc">Bases: presupuesto ejecutado y sancionado (BA Data), IDECBA, Planillas Anexas 2027 · Octubre de 2026</span>','')

# ---------- subbar (period controls)
sub='''  </div>
  <div class="subbar"><div class="subin">
    <span>Período</span>
    <div class="seg" role="group" aria-label="Período"><button data-per="anual" aria-pressed="true" title="Cierre anual de cada año; 2026 con el presupuesto vigente">Año completo</button><button data-per="ytd" aria-pressed="false" title="Todos los años acumulados al mismo trimestre que el último dato de 2026">Último dato</button></div>
    <span class="sep"></span>
    <label for="yr-from">Desde</label><select id="yr-from"></select>
    <label for="yr-to">Hasta</label><select id="yr-to"></select>
    <span id="pernote"></span>
  </div></div>
</header>'''
i=s.index('<header class="top">'); j=s.index('</header>',i)
hdr=s[i:j]; k=hdr.rindex('  </div>')
s=s[:i]+hdr[:k]+sub+s[j+len('</header>'):]

# ---------- head JS: period, range, PNG
headjs=r'''const ytBill=()=>'Billones de '+unitLabel();
// ---------- período y rango de años
let PERIOD='anual'; const YMIN=D.ymin||1995, YMAX=2027; let YF=YMIN, YT=YMAX;
const LT=D.lastT26||2, LM=D.lastM26||8;
const MESL=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
try{const p=localStorage.getItem('ceer-period'); if(p==='ytd'||p==='anual')PERIOD=p; const r=JSON.parse(localStorage.getItem('ceer-yr')||'null'); if(r&&r.length===2){YF=Math.max(YMIN,+r[0]);YT=Math.min(YMAX,+r[1]);}}catch(e){}
function applyRange(cfg){ const L=cfg.data&&cfg.data.labels; if(!L||!L.length||!cfg.options) return; if(cfg.options.indexAxis==='y') return;
  if(!L.every(l=>/^\d{4}/.test(String(l)))) return; const yr=l=>+String(l).slice(0,4);
  const a=L.findIndex(l=>yr(l)>=YF); let b=-1; L.forEach((l,i)=>{if(yr(l)<=YT)b=i;}); if(a<0||b<a) return; if(a===0&&b===L.length-1) return;
  cfg.options.scales=cfg.options.scales||{}; cfg.options.scales.x=Object.assign(cfg.options.scales.x||{},{min:a,max:b}); }
function perNote(){ const n=document.getElementById('pernote'); if(n) n.textContent=PERIOD==='ytd'?`Último dato: acumulado al ${LT}.º trimestre de cada año (recaudación: enero–${MESL[LM-1]})`:'Cierre anual; 2026 con presupuesto vigente'; }
function initPeriodUI(onChange){
  const f=document.getElementById('yr-from'), t=document.getElementById('yr-to'); if(!f) return;
  const ys=[]; for(let y=YMIN;y<=YMAX;y++) ys.push(y);
  f.innerHTML=ys.map(y=>`<option ${y===YF?'selected':''}>${y}</option>`).join(''); t.innerHTML=ys.map(y=>`<option ${y===YT?'selected':''}>${y}</option>`).join('');
  const save=()=>{try{localStorage.setItem('ceer-yr',JSON.stringify([YF,YT]));localStorage.setItem('ceer-period',PERIOD);}catch(e){}};
  f.addEventListener('change',()=>{YF=+f.value; if(YF>YT){YT=YF;t.value=YT;} save(); onChange();});
  t.addEventListener('change',()=>{YT=+t.value; if(YT<YF){YF=YT;f.value=YF;} save(); onChange();});
  document.querySelectorAll('[data-per]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.per===PERIOD); b.addEventListener('click',()=>{PERIOD=b.dataset.per; document.querySelectorAll('[data-per]').forEach(x=>x.setAttribute('aria-pressed',x===b)); save(); perNote(); onChange('per');});});
  perNote();
}
// ---------- PNG
const DEFSRC='Fuente: CEER en base a presupuesto ejecutado (BA Data), IDECBA y Planillas Anexas del Proyecto 2027.';
function wrapText(ctx,txt,maxW){ const out=[]; let line=''; (txt||'').split(/\s+/).forEach(w=>{const t=line?line+' '+w:w; if(ctx.measureText(t).width>maxW&&line){out.push(line);line=w;} else line=t;}); if(line)out.push(line); return out; }
const slug=s=>(s||'grafico').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,60)||'grafico';
async function exportPNG(box){
  const cv=box.querySelector('canvas'); const ch=charts[cv.id]; if(!ch) return;
  try{await document.fonts.ready;}catch(e){}
  const W=1200, ratio=cv.clientHeight/Math.max(cv.clientWidth,1); const CH=Math.round(Math.min(1150,Math.max(460,W*ratio)));
  const holder=document.createElement('div'); holder.style.cssText=`position:fixed;left:-99999px;top:0;width:${W}px;height:${CH}px`; const c2=document.createElement('canvas'); holder.appendChild(c2); document.body.appendChild(holder);
  const o=Object.assign({},ch.config.options,{responsive:true,maintainAspectRatio:false,animation:false,devicePixelRatio:2});
  const tmp=new Chart(c2,{type:ch.config.type,data:ch.config.data,options:o,plugins:ch.config.plugins||[]});
  const chartImg=tmp.canvas; const R=2, pad=56;
  const title=box.classList.contains('prom')?(box.querySelector('q')||{}).textContent:(box.querySelector('h3')||{}).textContent;
  const cap=box.classList.contains('prom')?(box.querySelector('.who')||{}).textContent:(box.querySelector('.cap')||{}).textContent;
  const src=((box.querySelector('.src')||{}).textContent)||DEFSRC;
  const m=document.createElement('canvas').getContext('2d'); const tw=W;
  m.font='700 34px '+css('--font'); const tl=wrapText(m,(box.classList.contains('prom')?'“'+(title||'').trim()+'”':title||'').trim(),tw);
  m.font='400 19px '+css('--font'); const cl=wrapText(m,(cap||'').trim(),tw);
  m.font='400 16px '+css('--font'); const sl=wrapText(m,src.trim(),tw);
  const unit='Montos en '+unitLabel()+(PERIOD==='ytd'?' · último dato (acumulado al '+LT+'.º trimestre)':'');
  const H=pad+44+28+tl.length*42+10+cl.length*28+18+CH+26+sl.length*22+8+22+30+pad;
  const out=document.createElement('canvas'); out.width=(W+pad*2)*R; out.height=H*R; const x=out.getContext('2d'); x.scale(R,R);
  x.fillStyle=css('--panel')||'#fff'; x.fillRect(0,0,W+pad*2,H); x.fillStyle=css('--fg'); x.fillRect(0,0,W+pad*2,6);
  let y=pad; const logo=[...document.querySelectorAll('img.logo')].find(i=>i.offsetParent!==null);
  if(logo&&logo.naturalWidth){const lh=40, lw=logo.naturalWidth*lh/logo.naturalHeight; x.drawImage(logo,pad,y,lw,lh);}
  x.fillStyle=css('--muted'); x.font='400 16px '+css('--font'); x.textAlign='right'; x.textBaseline='middle'; x.fillText('Centro de Estudios Económicos Renovación',pad+W,y+20); x.textAlign='left'; x.textBaseline='alphabetic';
  y+=44+28+30; x.fillStyle=css('--fg'); x.font='700 34px '+css('--font'); tl.forEach(l=>{x.fillText(l,pad,y);y+=42;}); y+=-12+10;
  x.fillStyle=css('--fg2'); x.font='400 19px '+css('--font'); cl.forEach(l=>{y+=28;x.fillText(l,pad,y);}); y+=18;
  x.drawImage(chartImg,pad,y,W,CH); y+=CH+26;
  x.fillStyle=css('--line2'); x.fillRect(pad,y-12,W,1);
  x.fillStyle=css('--muted'); x.font='400 16px '+css('--font'); sl.forEach(l=>{y+=22;x.fillText(l,pad,y);}); y+=8+22;
  x.fillText(unit,pad,y); x.textAlign='right'; x.font='600 16px '+css('--font'); x.fillStyle=css('--fg2'); x.fillText('@ceerenovacion · estudiosrenovacion.com',pad+W,y); x.textAlign='left';
  tmp.destroy(); holder.remove();
  out.toBlob(b=>{const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='ceer-'+slug(title)+'.png'; document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},1500);},'image/png');
}
function initPNG(){ document.querySelectorAll('.card, .prom').forEach(box=>{ if(!box.querySelector('canvas')||box.querySelector(':scope > .dlbtn')) return; const b=document.createElement('button'); b.className='dlbtn'; b.type='button'; b.textContent='PNG ↓'; b.title='Descargar el gráfico en PNG'; b.setAttribute('aria-label','Descargar el gráfico en PNG'); b.addEventListener('click',()=>exportPNG(box)); box.appendChild(b); }); }
'''
rep("const ytBill=()=>'Billones de '+unitLabel();\n", headjs)
# mk applies range
rep("function mk(id,cfg){ if(charts[id]) charts[id].destroy(); const el=document.getElementById(id); if(!el) return; charts[id]=new Chart(el,cfg); return charts[id];}",
    "function mk(id,cfg){ if(charts[id]) charts[id].destroy(); const el=document.getElementById(id); if(!el) return; applyRange(cfg); charts[id]=new Chart(el,cfg); return charts[id];}")
# bands plugin: use chart labels
rep("const i0=x.getPixelForValue(o.labels.indexOf(String(g[0]))), i1=o.labels.indexOf(String(g[1]))>=0?x.getPixelForValue(o.labels.indexOf(String(g[1]))):ca.right; if(isNaN(i0))return;",
    "const L=ch.data.labels; const j0=L.indexOf(String(g[0])), j1=L.indexOf(String(g[1])); if(j0<0)return; const i0=Math.max(ca.left,x.getPixelForValue(j0)), i1=j1>=0?Math.min(ca.right,x.getPixelForValue(j1)):ca.right; if(i1<=i0)return;")

# ---------- tablero general: 'último dato' = T2 for all years
rep('<option value="last">Último disponible</option>','<option value="last">Último dato (T2 de cada año)</option>')
rep("const tOf=y=>tsel==='last'?lastT[y]:+tsel;","const tOf=y=>tsel==='last'?LT:+tsel;")
rep("(tsel==='last'?'Último trimestre disponible de cada año (2026: T2). ':'')","(tsel==='last'?`Último dato: todos los años acumulados al ${LT}.º trimestre, comparable con 2026. `:'')")
s=s.replace("const t=document.getElementById('tb-trim').value==='last'?lastT[y]:Math.min(+document.getElementById('tb-trim').value||4,lastT[y]);",
            "const t=document.getElementById('tb-trim').value==='last'?LT:Math.min(+document.getElementById('tb-trim').value||4,lastT[y]);")

# ---------- otros tributos
rep("""  const ann={}; D.reca.rows.forEach(r=>{if(r[0]<2007)return; const f=facM(r[0],r[1]); const a=(ann[r[0]]=ann[r[0]]||[0,0,0,0]); a[0]+=r[4]*f;a[1]+=r[5]*f;a[2]+=r[6]*f;a[3]+=(r[7]+r[8]+r[9])*f;});
  const ay=Object.keys(ann);
  mk('ch-otros',{type:'line',data:{labels:ay.map(y=>y==='2026'?'2026*':y),""",
"""  const ytdR=PERIOD==='ytd'; const ann={}; D.reca.rows.forEach(r=>{if(r[0]<2007)return; if(ytdR?r[1]>LM:r[0]>=2026)return; const f=facM(r[0],r[1]); const a=(ann[r[0]]=ann[r[0]]||[0,0,0,0]); a[0]+=r[4]*f;a[1]+=r[5]*f;a[2]+=r[6]*f;a[3]+=(r[7]+r[8]+r[9])*f;});
  const ay=Object.keys(ann);
  document.getElementById('cap-otros').textContent=ytdR?`Enero–${MESL[LM-1]} de cada año, comparable con 2026. Miles de millones de ${unitLabel()}`:`Año completo 2007–2025. Miles de millones de ${unitLabel()}`;
  mk('ch-otros',{type:'line',data:{labels:ay,""")
rep('<p class="cap">ABL, Patentes, Sellos y resto, por año</p><div class="chart"><canvas id="ch-otros" aria-label="Otros tributos"></canvas></div><p class="src">2026: enero a agosto.</p>',
    '<p class="cap" id="cap-otros">ABL, Patentes, Sellos y resto, por año</p><div class="chart"><canvas id="ch-otros" aria-label="Otros tributos"></canvas></div><p class="src">Fuente: IDECBA sobre datos de AGIP. Deflactado con IPCBA mensual.</p>')

# ---------- gasto inciso / jurisdicción ytd
rep("""  const y=2025; const rows=CB.rows.filter(r=>r[0]===y&&r[1]===4&&r[5]!==AMORT);
  const m={}; rows.forEach(r=>{const k=dims.inc_desc[r[5]]; m[k]=(m[k]||0)+r[8];});
  const r26=CB.rows.filter(r=>r[0]===2026&&r[1]===2&&r[5]!==AMORT); const m26={}; r26.forEach(r=>{const k=dims.inc_desc[r[5]]; m26[k]=(m26[k]||0)+r[7];});
  const p=p27By('inc');""",
"""  const y=2025; const gy=PERIOD==='ytd'; const rows=CB.rows.filter(r=>r[0]===y&&r[1]===(gy?LT:4)&&r[5]!==AMORT);
  const m={}; rows.forEach(r=>{const k=dims.inc_desc[r[5]]; m[k]=(m[k]||0)+r[8];});
  const r26=CB.rows.filter(r=>r[0]===2026&&r[1]===LT&&r[5]!==AMORT); const m26={}; r26.forEach(r=>{const k=dims.inc_desc[r[5]]; m26[k]=(m26[k]||0)+r[gy?8:7];});
  const f25=gy?fac(2025,LT):fac(2025), f26=gy?fac(2026,LT):fac(2026); const L25=gy?`Devengado ene–jun 2025`:'Ejecutado 2025', L26=gy?'Devengado ene–jun 2026':'Vigente 2026';
  const p=p27By('inc');""")
rep("""datasets:[{label:'Ejecutado 2025',data:ks.map(k=>m[k]*fac(2025)),backgroundColor:H1()},{label:'Vigente 2026',data:ks.map(k=>(m26[k]||0)*fac(2026)),backgroundColor:H2()},{label:'Proyecto 2027',data:ks.map(k=>(p[k]||0)*fac('2027P')),backgroundColor:PJ()}]}""",
    """datasets:[{label:L25,data:ks.map(k=>m[k]*f25),backgroundColor:H1()},{label:L26,data:ks.map(k=>(m26[k]||0)*f26),backgroundColor:H2()},...(gy?[]:[{label:'Proyecto 2027',data:ks.map(k=>(p[k]||0)*fac('2027P')),backgroundColor:PJ()}])]}""")
rep("document.getElementById('cap-inc').textContent='Ejecutado 2025, vigente 2026 (2.º trimestre) y proyecto 2027, billones de '+unitLabel();",
    "document.getElementById('cap-inc').textContent=(gy?`Último dato: devengado acumulado al ${LT}.º trimestre de 2025 y de 2026`:'Ejecutado 2025, vigente 2026 (2.º trimestre) y proyecto 2027')+', billones de '+unitLabel();")
rep("const mj={}; rows.forEach(r=>{const k=dims.jur_desc[r[2]]; mj[k]=(mj[k]||0)+r[8];}); const mj26={}; r26.forEach(r=>{const k=dims.jur_desc[r[2]]; mj26[k]=(mj26[k]||0)+r[7];});",
    "const mj={}; rows.forEach(r=>{const k=dims.jur_desc[r[2]]; mj[k]=(mj[k]||0)+r[8];}); const mj26={}; r26.forEach(r=>{const k=dims.jur_desc[r[2]]; mj26[k]=(mj26[k]||0)+r[gy?8:7];});")
rep("""datasets:[{label:'Ejecutado 2025',data:all.map(k=>(mj[k]||0)*fac(2025)),backgroundColor:H1()},{label:'Vigente 2026',data:all.map(k=>(mj26[k]||0)*fac(2026)),backgroundColor:H2()},{label:'Proyecto 2027',data:all.map(k=>(pj[k]||0)*fac('2027P')),backgroundColor:PJ()}]}""",
    """datasets:[{label:L25,data:all.map(k=>(mj[k]||0)*f25),backgroundColor:H1()},{label:L26,data:all.map(k=>(mj26[k]||0)*f26),backgroundColor:H2()},...(gy?[]:[{label:'Proyecto 2027',data:all.map(k=>(pj[k]||0)*fac('2027P')),backgroundColor:PJ()}])]}""")
rep("document.getElementById('cap-jur').textContent='Ejecutado 2025, vigente 2026 y proyecto 2027, billones de '+unitLabel()+",
    "document.getElementById('cap-jur').textContent=(gy?`Último dato: devengado acumulado al ${LT}.º trimestre de 2025 y de 2026`:'Ejecutado 2025, vigente 2026 y proyecto 2027')+', billones de '+unitLabel()+")

# ---------- subte
a=s.index('  // subte\n'); b=s.index("  charts['ch-subte'].options.scales.x.stacked=true;",a); b=s.index('\n',b)+1
subte=r'''  // subte
  const sty=PERIOD==='ytd'; const SB=D.subte.filter(r=>sty?r[1]===LT:(r[1]===4&&r[0]<2026)); const sy=[...new Set(SB.map(r=>r[0]))].sort();
  const cats={}; SB.forEach(r=>{let c=r[2]; if(/Fondo Subte|Contrato|Operaci/i.test(c))c='Operación (Fondo Subte / contrato)'; else if(/Expansi|Ampliaci|Obra/i.test(c))c='Ampliación de la red'; else if(/Vigilancia|Seguridad/i.test(c))c='Seguridad'; else c='Resto'; (cats[c]=cats[c]||{})[r[0]]=(cats[c][r[0]]||0)+r[3];});
  const ck=['Operación (Fondo Subte / contrato)','Ampliación de la red','Seguridad','Resto'].filter(k=>cats[k]);
  const SBC=[H1(),H3(),css('--m5'),css('--c8')]; const tail=sty?[]:[null,null,null]; const fs=y=>sty?fac(y,LT):fac(y);
  const ds=ck.map((k,i)=>({label:k,data:[...sy.map(y=>(cats[k][y]||0)*fs(y)),...tail],backgroundColor:SBC[i],stack:'s'}));
  if(!sty){ const sp=PG.dims.prog_desc.map((p,i)=>/subterr/i.test(p)?i:-1).filter(i=>i>=0); let s26=0,v26=0; PG.rows.forEach(r=>{if(r[0]===2026&&r[1]===LT&&sp.includes(r[3])){s26+=r[6];v26+=r[7];}});
    ds.push({label:'Presupuesto 2026',data:[...sy.map(()=>null),s26*fac(2026),v26*fac(2026),null],backgroundColor:H2(),stack:'s'});
    ds.push({label:'Inversión anunciada 2027',data:[...sy.map(()=>null),null,null,917000*fac('2027P')],backgroundColor:PJ(),stack:'s'}); }
  mk('ch-subte',{type:'bar',data:{labels:sty?sy.map(y=>y+' T'+LT):[...sy.map(String),'2026 Sanc.','2026 Vig.','2027 P'],datasets:ds},options:baseOpts({div:1e3,ytitle:'Miles de millones de '+unitLabel()})});
  document.getElementById('cap-subte').textContent=sty?`Último dato: devengado acumulado al ${LT}.º trimestre de cada año, por destino. Miles de millones de ${unitLabel()}.`:`Programas Subterráneos de Buenos Aires y Obras en la red: devengado anual por destino 2019–2025, crédito 2026 (sancionado y vigente al ${LT}.º trimestre) e inversión anunciada para 2027 ($917.000 millones nominales). Miles de millones de ${unitLabel()}.`;
  charts['ch-subte'].options.scales.x.stacked=true;charts['ch-subte'].options.scales.y.stacked=true;charts['ch-subte'].update();
'''
s=s[:a]+subte+s[b:]
rep('<h3>El subte</h3><p class="cap">Programas Subterráneos de Buenos Aires y Obras en la red, devengado anual por destino. 2027: inversión anunciada en la red ($917.000 millones nominales)</p>','<h3>El subte</h3><p class="cap" id="cap-subte"></p>')

# ---------- empleo HTML
a=s.index('  <div class="grid">\n    <div class="card span7"><h3>Cargos por planta, 2002–2021</h3>'); b=s.index('</section>',a)
emp='''  <div class="grid">
    <div class="card span7"><h3>Cargos totales</h3><p class="cap" id="cap-emp-total"></p><div class="chart"><canvas id="ch-emp-total" aria-label="Cargos totales"></canvas></div><p class="src">Fuente: IDECBA (2002–2021) y Planilla 17 de los Proyectos 2026 y 2027.</p></div>
    <div class="card span5"><h3>Por carrera o planta, 2026 vs. 2027</h3><p class="cap">Dotación prevista en cada proyecto de presupuesto</p><div class="tablewrap"><table id="emp-car-table"></table></div><p class="src">Fuente: Planilla 17, Proyectos 2026 y 2027.</p></div>
    <div class="card span7"><h3>Cargos por planta, 2002–2021</h3><p class="cap">Administración central, a diciembre de cada año</p><div class="chart"><canvas id="ch-emp-cargos" aria-label="Cargos por planta"></canvas></div><p class="src">Fuente: IDECBA sobre datos de la Dirección General de Planeamiento de Recursos Humanos. La serie se discontinuó en 2021.</p></div>
    <div class="card span5"><h3>Dotación por jurisdicción</h3><p class="cap" id="cap-emp27">Cargos previstos en los proyectos 2026 y 2027</p><div class="tablewrap" style="max-height:360px;overflow-y:auto"><table id="emp27-table"></table></div><p class="src">Fuente: Planilla 17. Poder Ejecutivo; no incluye Legislatura, Justicia ni organismos de control.</p></div>
    <div class="card span6"><h3>Dotación por carrera, 2026 vs. 2027</h3><p class="cap">Docentes, policías y salud explican cuatro de cada cinco cargos</p><div class="chart"><canvas id="ch-emp27" aria-label="Dotación por carrera 2026 y 2027"></canvas></div><p class="src">Fuente: Planilla 17, Proyectos 2026 y 2027.</p></div>
    <div class="card span6"><h3>Gasto en personal</h3><p class="cap" id="cap-emp-gasto">Inciso 1, devengado anual y proyecto 2027</p><div class="chart"><canvas id="ch-emp-gasto" aria-label="Gasto en personal"></canvas></div><p class="src">Fuente: presupuesto ejecutado (BA Data) y Planilla 4.</p></div>
  </div>
'''
s=s[:a]+emp+s[b:]

# ---------- lupa layout
rep('<p class="lupatxt" id="lupa-txt"></p><div class="chart"><canvas id="ch-lupa"','<p class="lupatxt" id="lupa-txt"></p><div class="chart tall"><canvas id="ch-lupa"')

# ---------- seguridad gasto (precomputed, with ytd) + delitos labels
rep("""  const fi=GD.fun_desc.indexOf('Seguridad interior'); const dv={}; let v26=0;
  G.rows.forEach(r=>{if(r[3]!==fi||r[4]===GAM)return; if(r[1]===4) dv[r[0]]=(dv[r[0]]||0)+r[9]*fac(r[0]); if(r[0]===2026&&r[1]===lastT[2026]) v26+=r[8]*fac(2026);});
  const ys=Object.keys(dv).map(Number).sort(); const p27=(D.p2027_fun['Seguridad interior']||D.p2027_fun['Seguridad']||0)*fac('2027P');
  const c5=mk('ch-sg-gasto',{type:'bar',data:{labels:[...ys.map(String),'2026 Vig.','2027 P'],datasets:[{label:'Seguridad',data:[...ys.map(y=>dv[y]),v26,p27],backgroundColor:[...ys.map(()=>H1()),H2(),PJ()]}]},options:baseOpts({ytitle:ytBill()})}); c5.options.plugins.legend.display=false; c5.update();
  document.getElementById('sg-gcap').textContent='Función Seguridad (policía, prevención y emergencias), billones de '+unitLabel()+'. Devengado 2019–2025, vigente 2026 y proyecto 2027.';""",
"""  const SGG=D.seggasto; const dv={}; Object.entries(SGG.dev).forEach(([y,v])=>{if(+y<2026)dv[y]=v*fac(+y);}); const v26=SGG.v26*fac(2026), s26=(SGG.s26||0)*fac(2026);
  const ys=Object.keys(dv).map(Number).sort(); const p27=(D.p2027_fun['Seguridad interior']||D.p2027_fun['Seguridad']||0)*fac('2027P'); const gyt=PERIOD==='ytd';
  const yt2=Object.keys(SGG.dev_t2||{}).map(Number).sort();
  const c5=gyt?mk('ch-sg-gasto',{type:'bar',data:{labels:yt2.map(y=>y+' T'+LT),datasets:[{label:'Seguridad',data:yt2.map(y=>SGG.dev_t2[y]*fac(y,LT)),backgroundColor:yt2.map((y,i)=>i===yt2.length-1?H2():H1())}]},options:baseOpts({ytitle:ytBill()})})
    :mk('ch-sg-gasto',{type:'bar',data:{labels:[...ys.map(String),'2026 Sanc.','2026 Vig.','2027 P'],datasets:[{label:'Seguridad',data:[...ys.map(y=>dv[y]),s26,v26,p27],backgroundColor:[...ys.map(()=>H1()),H2(),H2(),PJ()]}]},options:baseOpts({ytitle:ytBill()})}); c5.options.plugins.legend.display=false; c5.update();
  document.getElementById('sg-gcap').textContent='Función Seguridad (policía, prevención y emergencias), billones de '+unitLabel()+'. '+(gyt?`Último dato: devengado acumulado al ${LT}.º trimestre de cada año, comparable con 2026.`:'Devengado 2019–2025, sancionado y vigente 2026 y proyecto 2027.');""")
rep("ys.forEach(y=>{for(let m=1;m<=12;m++){labs.push(MES[m-1]+' '+String(y).slice(2)); vals.push(mon[y+'-'+m]||0);}});",
    "ys.forEach(y=>{for(let m=1;m<=12;m++){labs.push(y+'-'+String(m).padStart(2,'0')); vals.push(mon[y+'-'+m]||0);}});")

# ---------- render hooks
rep("document.querySelectorAll('[data-u]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.u===U);",
    "initPeriodUI(k=>{ if(k==='per'){const t=document.getElementById('tb-trim'); if(t) t.value=PERIOD==='ytd'?'last':'4';} renderAll(); }); initPNG();\nif(PERIOD==='ytd'){const t=document.getElementById('tb-trim'); if(t) t.value='last';}\ndocument.querySelectorAll('[data-u]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.u===U);")
open(P,'w').write(s); print('ok',len(s))
