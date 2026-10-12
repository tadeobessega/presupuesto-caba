import pandas as pd, numpy as np, json, unicodedata, re, sys
sys.path.insert(0,'scripts')
from deflators import A, Q, ipc, ann
b=pd.read_pickle('base_gasto.pkl'); P=pd.read_pickle('p2027.pkl'); caif=pd.read_pickle('caif.pkl'); R=pd.read_pickle('recursos.pkl')
def norm(s): s=unicodedata.normalize('NFD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'[^a-z ]','',s.replace('–','-')).strip()
FUN={ # canonical: (finalidad, función)
 'legislativa':('Administración gubernamental','Legislativa'),'judicial':('Administración gubernamental','Judicial'),
 'direccion ejecutiva':('Administración gubernamental','Dirección ejecutiva'),'administracion fiscal':('Administración gubernamental','Administración fiscal'),
 'control de la gestion':('Administración gubernamental','Control de la gestión'),'seguridad interior':('Seguridad','Seguridad interior'),
 'interior seguridad':('Seguridad','Seguridad interior'),'sistema penal':('Seguridad','Sistema penal'),'salud':('Servicios sociales','Salud'),
 'promocion y accion social':('Servicios sociales','Promoción y acción social'),'educacion':('Servicios sociales','Educación'),'cultura':('Servicios sociales','Cultura'),
 'trabajo':('Servicios sociales','Trabajo'),'vivienda':('Servicios sociales','Vivienda y urbanismo'),'vivienda y urbanismo':('Servicios sociales','Vivienda y urbanismo'),
 'agua potable y alcantarillado':('Servicios sociales','Agua potable y alcantarillado'),'servicios urbanos':('Servicios sociales','Servicios urbanos'),
 'transporte':('Servicios económicos','Transporte'),'ecologia':('Servicios económicos','Ecología'),'turismo':('Servicios económicos','Turismo'),
 'industria y comercio':('Servicios económicos','Industria y comercio'),'deuda publica  intereses y gastos':('Deuda pública','Intereses y gastos'),
 'deuda publica - intereses y gastos':('Deuda pública','Intereses y gastos'),'gastos no clasificados':('Gastos no clasificados','Gastos no clasificados')}
def fun_of(s):
    n=norm(s); n2=n.replace('  ',' ')
    for k,v in FUN.items():
        if norm(k)==n or norm(k).replace(' ','')==n.replace(' ',''): return v
    raise KeyError(s)
INC={'1':'Personal','2':'Bienes de consumo','3':'Servicios no personales','4':'Bienes de uso','5':'Transferencias','6':'Activos financieros','7':'Servicio de la deuda','8':'Otros gastos'}
b['F']=b.fun_desc.map(lambda s: fun_of(s)[1]); b['FIN']=b.fun_desc.map(lambda s: fun_of(s)[0])
b['I']=b.inc.map(INC)
# snapshots: for each year: sanción (from latest period), vigente & devengado at Q4 (or latest)
last=b.groupby('año').trim.max()
snap=b[b.trim==b.año.map(last)].copy()
snap['per']=snap.año.astype(str)
# jurisdiction label per year (title case)
def jlab(s): 
    s=str(s).strip(); s=re.sub(r'\s+',' ',s); return s.title().replace(' De ',' de ').replace(' Del ',' del ').replace(' La ',' la ').replace(' Y ',' y ').replace(' E ',' e ').replace(' A ',' a ')
snap['J']=snap.jur_desc.map(jlab)
# ---- cube 1: año x J x FIN x F x I x fte : sancion, vigente, devengado (millones)
fteM={'11':'Tesoro','12':'Recursos propios','13':'Afectados','14':'Transferencias afectadas','15':'Transferencias internas','22':'Financiamiento externo','21':'Financiamiento interno'}
snap['FTE']=snap.fte.map(lambda f: fteM.get(str(f),'Otras'))
c1=snap.groupby(['año','J','FIN','F','I','FTE'],as_index=False)[['sancion','vigente','devengado']].sum()
for c in ['sancion','vigente','devengado']: c1[c]=(c1[c]/1e6).round(1)
# 2027 proyecto: fun x inc (P3), jur x inc (P4)
p3=P['p3'].copy(); p4=P['p4'].copy()
INCN=['Personal','Bienes de consumo','Servicios no personales','Bienes de uso','Transferencias','Activos financieros','Servicio de la deuda','Otros gastos']
fin_rows={'Administración Gubernamental','Servicios de Seguridad','Servicios Sociales','Servicios Económicos','TOTAL'}
pf=[]; seen=set()
for lab,row in p3.iterrows():
    if lab in fin_rows: continue
    if 'Deuda' in lab:
        if 'deuda' in seen: continue
        seen.add('deuda')
    fin,fn=fun_of(lab)
    for i in INCN:
        if row[i]: pf.append({'FIN':fin,'F':fn,'I':i,'proyecto':round(row[i]/1e6,1)})
pf=pd.DataFrame(pf)
pj=[]
for lab,row in p4.iterrows():
    if lab=='TOTAL': continue
    for i in INCN:
        if row[i]: pj.append({'J':jlab(lab),'I':i,'proyecto':round(row[i]/1e6,1)})
pj=pd.DataFrame(pj)
# ---- cube 2: objeto detail: año x jur label x inc x ppal x par x spar (sancion, vigente, devengado)
snap['P']=snap.ppal_desc.fillna('s/d'); snap['PA']=snap.par_desc.fillna('s/d'); snap['SP']=snap.spar_desc.fillna('s/d')
c2=snap.groupby(['año','J','I','P','PA','SP'],as_index=False)[['sancion','vigente','devengado']].sum()
for c in ['sancion','vigente','devengado']: c2[c]=(c2[c]/1e6).round(1)
# ---- programs: año x J x prog
snap['PR']=snap.prog.astype(str)+' · '+snap.prog_desc.fillna('').str.strip()
c3=snap.groupby(['año','J','PR'],as_index=False)[['sancion','vigente','devengado']].sum()
for c in ['sancion','vigente','devengado']: c3[c]=(c3[c]/1e6).round(1)
c3=c3[(c3.sancion.abs()+c3.devengado.abs())>0.5]
# ---- quarterly execution by F
tq=b.groupby(['año','trim','FIN','F'],as_index=False)[['sancion','vigente','devengado']].sum()
for c in ['sancion','vigente','devengado']: tq[c]=(tq[c]/1e6).round(1)
# ---- CAIF
import openpyxl
_ws=openpyxl.load_workbook('raw/SP_Fi_AX01.xlsx',data_only=True).worksheets[0]; _rows=list(_ws.iter_rows(values_only=True))
CK=['IC','IT','INT','VBS','RP','TCI','GC','REM','GCO','OP','IMP','TCG','RE','RK','RPK','TKI','DIF','GK','IRD','TKG','IF','RT','GP','RPRIM','INTD','GT','RFAF','CF','GF','RF','FF','FF_DIF','FF_END','FF_INP','AF','AF_INC','AF_AMO']
_yrs=[int(str(y).replace('*','')) for y in _rows[1][1:32]]
caif_out={'years':_yrs,'labels':{},'rows':{}}
for k,r in zip(CK,_rows[2:39]):
    caif_out['labels'][k]=r[0].strip(); caif_out['rows'][k]=[0.0 if v in ('-',None) else round(float(v),1) for v in r[1:32]]
K27=['IC','IT','INT','VBS','RP','TCI','GC','REM','GCO','TCG','REP','RK','RPK','TKI','DIF','GK','IRD','TKG','IF','RT','GP','RPRIM','INTD','GT','RF','FF','FF_DIF','FF_END','AF','AF_INC','AF_AMO']
cp=P['caif']; assert len(cp)==len(K27); caif27={k:round(v[0]/1e6,1) for k,v in zip(K27,cp.valores)}
# ---- recursos
reca=R['reca'].copy(); reca=reca[['año','mes','Total','IIBB','ABL','Patentes','Sellos','Planes de facilidades','Publicidad','Gravámenes varios']]
recaL=reca.round(1).values.tolist()
q=R['q']; qrec=q.round(1).where(pd.notna(q),None).values.tolist()
rub=P['rec'][['x','rubro','importe']].copy(); rub['importe']=(rub.importe/1e6).round(1)
# deflators
Ad={int(k):float(v) for k,v in A.items()}
Qd={f'{k[0]}-{k[1]}':float(v) for k,v in Q.items()}
M={f'{d.year}-{d.month:02d}':float(v/ann[2026]) for d,v in ipc.items()}
data={'meta':{'generado':'2026-10-12','ipc_hasta':'2026-09','supuesto_oct_dic_2026':0.02,'supuesto_dic_dic_2027':0.18,'infl_prom_2027':float(ann[2027]/ann[2026]-1)},
 'A':Ad,'Q':Qd,'M':M,
 'c1':{'cols':list(c1.columns),'rows':c1.values.tolist()},
 'p27f':pf.values.tolist(),'p27j':pj.values.tolist(),
 'c2':{'cols':list(c2.columns),'rows':c2.values.tolist()},
 'c3':{'cols':list(c3.columns),'rows':c3.values.tolist()},
 'tq':{'cols':list(tq.columns),'rows':tq.values.tolist()},
 'caif':caif_out,'caif27':caif27,
 'reca':{'cols':list(reca.columns),'rows':recaL},
 'qrec':{'cols':list(q.columns),'rows':qrec},
 'rub27':rub.values.tolist(),
 'periodos':sorted(b.periodo.unique().tolist()),
 'lastper':{int(k):int(v) for k,v in last.items()}}
s=json.dumps(data,ensure_ascii=False,separators=(',',':'),default=lambda o: o.item() if hasattr(o,'item') else str(o))
open('data.json','w').write(s)
print(len(s)/1e6,'MB', {k:len(v['rows']) if isinstance(v,dict) and 'rows' in v else '' for k,v in data.items()})
# ---- compact encoding: string columns -> dictionary indices
def enc(cube):
    cols=cube['cols']; rows=cube['rows']; dicts={}
    out=[list(r) for r in rows]
    for j,c in enumerate(cols):
        if rows and isinstance(rows[0][j],str):
            vals=sorted(set(r[j] for r in rows)); ix={v:i for i,v in enumerate(vals)}; dicts[c]=vals
            for r in out: r[j]=ix[r[j]]
    return {'cols':cols,'dict':dicts,'rows':out}
for k in ['c1','c2','c3','tq']: data[k]=enc(data[k])
s=json.dumps(data,ensure_ascii=False,separators=(',',':'),default=lambda o: o.item() if hasattr(o,'item') else str(o))
open('data.json','w').write(s); print('encoded',len(s)/1e6,'MB')
