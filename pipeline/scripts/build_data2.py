import pandas as pd, json, openpyxl, re, unicodedata
D=json.load(open('data.json'))
norm=lambda x: re.sub(r'\s+',' ',unicodedata.normalize('NFD',str(x).lower()).encode('ascii','ignore').decode()).strip()
g=pd.read_pickle('gasto.pkl')
g['amort']=g.par_desc.fillna('').str.startswith('Amortizaci')|g.ppal_desc.fillna('').str.startswith('Disminución De Préstamos')
g.loc[g.amort,'inc_desc']='Amortización de deuda'
for c in ['jur_desc','fin_desc','fun_desc','inc_desc','ppal_desc','par_desc','prog_desc','fte_desc']: g[c]=g[c].fillna('Sin dato').str.replace(r'\s+',' ',regex=True).str.strip()
def harmon(col):
    latest=g.sort_values(['año','trim']).groupby(g[col].map(norm))[col].last()
    g[col]=g[col].map(norm).map(latest)
for c in ['jur_desc','fin_desc','fun_desc','inc_desc','fte_desc','ppal_desc']: harmon(c)
V=['sancion','vigente','devengado']
for c in V: g[c]=g[c]/1e6
def cube(keys,name):
    a=g.groupby(['año','trim']+keys,as_index=False)[V].sum()
    a=a[(a[V].abs().sum(axis=1))>0.05]
    dims={k:sorted(a[k].unique().tolist()) for k in keys}
    idx={k:{v:i for i,v in enumerate(dims[k])} for k in keys}
    rows=[[int(r[0]),int(r[1])]+[idx[k][r[2+i]] for i,k in enumerate(keys)]+[round(float(x),1) for x in r[2+len(keys):]] for r in a.itertuples(index=False)]
    D[name]={'keys':keys,'dims':dims,'rows':rows}; print(name,len(rows))
cube(['jur_desc','fun_desc','inc_desc','ppal_desc','fte_desc'],'G')
cube(['jur_desc','prog_desc','inc_desc','fte_desc'],'P')
cube(['jur_desc','inc_desc','ppal_desc','par_desc','fte_desc'],'O')
D.pop('prog',None)
# ---- empleo
def tbl(f):
    ws=openpyxl.load_workbook(f,data_only=True).worksheets[0]
    return [[x for x in r] for r in ws.iter_rows(values_only=True)]
rows=[r for r in tbl('raw/seg_cargos.xlsx') if any(x is not None for x in r)]; hr=rows[1]
cargos={}
for r in rows[2:]:
    if r[0] and any(isinstance(x,(int,float)) for x in r[1:]):
        cargos[str(r[0]).strip()]={str(hr[i]):(r[i] if isinstance(r[i],(int,float)) else None) for i in range(1,len(hr)) if hr[i] is not None}
rows=tbl('raw/seg_agentes.xlsx'); hdr2=[str(x) for x in rows[1] if x is not None]
agentes={}
for r in rows[2:]:
    if r[0] and any(isinstance(x,(int,float)) for x in r[1:]): agentes[str(r[0]).strip()]={hdr2[i]:r[i] for i in range(1,len(hdr2))}
# planilla 17
txt=open('raw/planillas2027.txt').read(); pg=txt.split('=== PAGE 23')[1].split('=== PAGE 24')[0]
cols=['Autoridades superiores','Otras autoridades','Planta de gabinete','Régimen gerencial','Carrera administrativa','Carrera enfermería y técnicos de salud','Carrera profesional hospitalaria','Personal docente','Servicio penitenciario','Cuerpos transitorios','Personal transitorio (Acta 6/2014)','Residentes','Policía de la Ciudad','Total']
p17={}
for line in pg.split('\n'):
    if line.startswith('71:'):
        parts=[p.split(':',1)[1].strip() for p in line.split('\t')]
        name=re.sub(r'^\d+\s+','',parts[0]); vals=[int(x.replace('.','')) for x in parts[1:]]
        if len(vals)==14: p17[name]=dict(zip(cols,vals))
tot=[l for l in pg.split('\n') if l.startswith('231:')][0]
p17['Total']=dict(zip(cols,[int(p.split(':',1)[1].strip().replace('.','')) for p in tot.split('\t')]))
D['empleo']={'cargos':cargos,'agentes':agentes,'p17':p17}
# ---- seguridad
rows=tbl('raw/seg_hechos_tasa.xlsx'); tasa={}
for r in rows[2:]:
    if isinstance(r[0],(int,float)) or (isinstance(r[0],str) and r[0].strip().isdigit()):
        if isinstance(r[1],(int,float)): tasa[str(int(r[0]))]=[r[1],r[2]]
rows=tbl('raw/seg_hechos_vict.xlsx'); years=[str(x) for x in rows[1][1:] if x is not None]
hv={}
for r in rows[3:]:
    if not r[0] or str(r[0]).startswith(('Nota','Fuente','1 ','2 ')): continue
    vals=r[2:2+2*len(years)]
    hv[str(r[0]).strip()]={y:(vals[2*i] if isinstance(vals[2*i],(int,float)) else None) for i,y in enumerate(years)}
rows=tbl('raw/seg_femic.xlsx'); fem={str(r[0]):r[1] for r in rows if isinstance(r[1],(int,float)) and str(r[0]).isdigit()}
rows=tbl('raw/seg_fiscalias.xlsx'); fis={str(r[0]):r[1] for r in rows if isinstance(r[1],(int,float)) and str(r[0]).isdigit()}
dl=pd.read_pickle('delitos.pkl')
meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
dl['m']=dl.mes.map(lambda x: meses.index(x)+1 if x in meses else 0)
a=dl.groupby(['anio','m','tipo','subtipo','arma','moto','comuna'],as_index=False).n.sum()
dd={k:sorted(a[k].unique().tolist()) for k in ['tipo','subtipo','arma','moto','comuna']}
D['delitos']={'dims':dd,'rows':[[int(r.anio),int(r.m)]+[dd[k].index(getattr(r,k)) for k in ['tipo','subtipo','arma','moto','comuna']]+[int(r.n)] for r in a.itertuples(index=False)]}
D['seg']={'tasa':tasa,'hv':hv,'fem':fem,'fis':fis}
print(len(D['delitos']['rows']), list(p17)[:5], p17['Total']['Total'])
json.dump(D,open('data2.json','w'),ensure_ascii=False,separators=(',',':'))
import os; print(os.path.getsize('data2.json')/1e6)
# ---- CAIF 2026 (proyecto 2026, Planilla 16)
p26={'1) Ingresos corrientes':17345060.854970,'Ingresos tributarios':14193229.980606,'Ingresos no tributarios':368094.362491,'Venta de bienes y servicios':238223.033499,'Rentas de la propiedad':551579.459778,'Transferencias corrientes':1993934.018596,
'2) Gastos corrientes':13654960.763096,'Remuneraciones al personal':7155010.416665,'Gastos de consumo':4507722.259461,'Transferencias corrientes (gasto)':1992228.086970,
'3) Resultado económico (1-2)':3690100.091874,'4) Recursos de capital':2299.507383,'Recursos propios de capital':0,'Transferencias de capital':0,'Disminución de la inversión financiera':2299.507383,
'5) Gastos de capital':3433320.695686,'Inversión real directa':3327740.781085,'Transferencias de capital (gasto)':102242.878510,'Inversión financiera':3337.036091,
'6) Recursos totales (1+4)':17347360.362353,'7) Gasto primario (2+5)':17088281.458782,'8) Resultado primario (6-7)':259078.903571,'9) Intereses de la deuda pública':253185.416377,'10) Gastos totales (7+9)':17341466.875159,'11) Resultado financiero antes de figurativas (6-10)':5893.487194}
seen_tc=0; seen_tk=0
for c in D['caif']:
    n=c['concepto'].strip(); key=None
    for k in p26:
        if k.lower().startswith(n.lower()[:18]): key=k;break
    if n.lower().startswith('transferencias corrientes'): key='Transferencias corrientes' if seen_tc==0 else 'Transferencias corrientes (gasto)'; seen_tc+=1
    if n.lower().startswith('transferencias de capital'): key='Transferencias de capital' if seen_tk==0 else 'Transferencias de capital (gasto)'; seen_tk+=1
    if n.lower().startswith(('12)','13)','14)','15)','16)','ingresos no presup','incremento','amortiz','endeud')): key=None
    c['vals']['2026P']=p26.get(key) if key else None
D['defl']['p2027']['2026P']=D['defl']['p2027']['2026']; D['defl']['hoy']['2026P']=D['defl']['hoy']['2026']
p26j=json.load(open('p2026.json'))
D['p2026_jur']={k:{kk:round(v/1e6,1) for kk,v in vals.items()} for k,vals in p26j['jur_inc'].items()}
json.dump(D,open('data2.json','w'),ensure_ascii=False,separators=(',',':'))
print('caif 2026P ok')
