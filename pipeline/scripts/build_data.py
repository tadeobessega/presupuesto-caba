import pandas as pd, numpy as np, json, openpyxl, unicodedata, re
P=json.load(open('prep.json'))
norm=lambda x: re.sub(r'\s+',' ',unicodedata.normalize('NFD',str(x).lower()).encode('ascii','ignore').decode()).strip()
g=pd.read_pickle('gasto.pkl')
g['amort']=g.par_desc.fillna('').str.startswith('Amortizaci')|g.ppal_desc.fillna('').str.startswith('Disminución De Préstamos')
g.loc[g.amort,'inc_desc']='Amortización de deuda'
g['spar_desc']=g.spar_desc.fillna(g.par_desc)
for c in ['jur_desc','fin_desc','fun_desc','inc_desc','ppal_desc','par_desc','prog_desc']: g[c]=g[c].fillna('Sin dato').str.replace(r'\s+',' ',regex=True).str.strip()
# harmonize case: use latest name per normalized key
def harmon(col):
    latest=g.sort_values(['año','trim']).groupby(g[col].map(norm))[col].last()
    g[col]=g[col].map(norm).map(latest)
for c in ['jur_desc','fin_desc','fun_desc','inc_desc']: harmon(c)
V=['sancion','vigente','devengado']
for c in V: g[c]=g[c]/1e6  # millones
D={}
def cube(keys,name):
    a=g.groupby(['año','trim']+keys,as_index=False)[V].sum()
    dims={k:sorted(a[k].unique().tolist()) for k in keys}
    rows=[]
    for r in a.itertuples(index=False):
        rr=[int(r[0]),int(r[1])]+[dims[k].index(getattr(r,k)) for k in keys]+[round(float(getattr(r,v)),1) for v in V]
        rows.append(rr)
    D[name]={'keys':keys,'dims':dims,'rows':rows}
    print(name,len(rows))
cube(['jur_desc','fin_desc','fun_desc','inc_desc'],'cube')
cube(['inc_desc','ppal_desc','par_desc','spar_desc'],'objeto')
cube(['jur_desc','prog_desc'],'prog')
sub=g[g.prog_desc.str.contains('Subterraneos De Buenos Aires|Red De Subterr',case=False)]
D['subte']=[[int(a),int(t),s,round(v,1)] for (a,t,s),v in (sub.groupby(['año','trim','spar_desc']).devengado.sum()).items() if v]
# 2027 planillas
incmap={'PERSONAL':'Gastos En Personal','BIENES DE CONSUMO':'Bienes De Consumo','SERV. NO PERSONALES':'Servicios No Personales','BIENES DE USO':'Bienes De Uso','TRANSFERENCIAS':'Transferencias','FINANCIEROS ACTIVOS':'Activos Financieros','SERVICIO DE LA DEUDA':'Servicio De La Deuda Y Disminución De Otros Pasivos','OTROS GASTOS':'Otros Gastos'}
jurnames={norm(j):j for j in D['cube']['dims']['jur_desc']}
jurnames[norm('MINISTERIO DE HACIENDA y FINANZAS')]=jurnames.get(norm('Ministerio De Hacienda Y Finanzas'),'Ministerio De Hacienda Y Finanzas')
p27j={}
for j,v in P['p2027_jur_inc'].items():
    if j=='TOTAL': continue
    jn=jurnames.get(norm(j), j.title())
    p27j[jn]={incmap[k]:round(x/1e6,1) for k,x in v.items() if k in incmap}
D['p2027_jur']=p27j
funnames={norm(f):f for f in D['cube']['dims']['fun_desc']}
finset={'Administración Gubernamental','Servicios De Seguridad','Servicios Sociales','Servicios Económicos','Deuda Pública - Intereses Y Gastos'}
p27f={}; cur=None
for f,v in P['p2027_fun_inc'].items():
    if f=='TOTAL': continue
    tot=round(v['TOTAL GENERAL']/1e6,1)
    if norm(f) in [norm(x) for x in finset] or f.startswith('Deuda'):
        cur=f; p27f.setdefault('_fin',{})[f]=tot
        if f.startswith('Deuda'): p27f[f]=tot
        continue
    p27f[funnames.get(norm(f),f)]=tot
D['p2027_fun']=p27f
# CAIF, finalidad, deflators
D['caif']=P['caif']; D['defl']=P['deflator']
ws=openpyxl.load_workbook('raw/SP_GP_AX01.xlsx',data_only=True).worksheets[0]
rows=[r for r in ws.iter_rows(values_only=True)]
hdr=[str(h).replace('*','') for h in rows[1][1:] if h]
fin={}
for r in rows[2:8]:
    fin[r[0]]={hdr[i]:(r[i+1] if isinstance(r[i+1],(int,float)) else 0) for i in range(len(hdr))}
D['finalidad']=fin
# recaudación mensual
rc=pd.read_pickle('reca.pkl')
D['reca']={'cols':['total','iibb','abl','patentes','sellos','planes','publicidad','otros'],'rows':rc.round(2).values.tolist()}
ws=openpyxl.load_workbook('raw/ipcba.xlsx',data_only=True).worksheets[0]
D['ipcm']=[[r[0].year,r[0].month,round(r[1],4)] for r in ws.iter_rows(values_only=True) if hasattr(r[0],'year') and isinstance(r[1],(int,float))]
# recursos 2027 rubros
D['rec2027']=[['Ingresos Brutos',13279.892],['Sellos (incl. Fondo SUBTE)',1448.901],['ABL e Inmobiliario',1428.274],['Patentes (incl. Fondo SUBTE)',467.162],['Otros tributos propios',245.0],['Coparticipación (1,40%)',2225.985],['Transf. Nación por fallo CSJN (diferencial 1,55%)',2789.861],['Otras transferencias corrientes',227.673],['Rentas de la propiedad',951.291],['No tributarios',663.826],['Venta de bienes y servicios',365.617],['Recursos de capital',3.176]]
# stock deuda total + títulos
ws=openpyxl.load_workbook('raw/SP_SD_AX01.xlsx',data_only=True).worksheets[0]
rows=[r for r in ws.iter_rows(values_only=True)]
yrs=[str(x).replace('*','') for x in rows[1]]
tot=[r for r in rows if r[0]=='Total'][0]
D['deuda']={yrs[i]:tot[i] for i in range(1,len(yrs)) if re.match(r'^\d{4}$',yrs[i] or '') and isinstance(tot[i],(int,float))}
D['ronrop']=json.load(open('ronrop.json'))
D['logo_neg']=open('logo_neg.datauri').read(); D['logo_pos']=open('logo_pos.datauri').read()
json.dump(D,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
import os; print(os.path.getsize('data.json')/1e6,'MB'); print(D['deuda']); print(list(D['p2027_fun'].items())[:8])
