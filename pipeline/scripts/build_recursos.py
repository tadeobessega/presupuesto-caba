import openpyxl, pandas as pd, numpy as np, re
MES={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'setiembre':9,'octubre':10,'noviembre':11,'diciembre':12}
def num(v):
    if v is None: return np.nan
    if isinstance(v,(int,float)): return float(v)
    s=str(v).strip()
    return 0.0 if s in ('-','–','') else pd.to_numeric(s.replace(',','.'),errors='coerce')
def parse(f, kind):
    ws=openpyxl.load_workbook(f,data_only=True).worksheets[0]
    rows=list(ws.iter_rows(values_only=True))
    hdr=None
    for r in rows:
        if r[0] in ('Período','Periodo'): hdr=[str(x).strip() if x else '' for x in r]; break
    out=[]; y=None
    for r in rows:
        a=r[0]
        if isinstance(a,(int,float)) and 1990<a<2100 and all(x is None for x in r[1:4]): y=int(a); continue
        if isinstance(a,str) and y:
            t=re.sub(r'[\d\*]+$','',a.strip().lower().replace('*','')).strip()
            if kind=='m':
                k=MES.get(t.split()[0] if t else '')
            else:
                m=re.match(r'(\d)',a.strip()); k=int(m.group(1)) if m and 'trim' in t else None
            if k: out.append([y,k]+[num(x) for x in r[1:len(hdr)]])
    cols=['año','mes' if kind=='m' else 'trim']+[h if h else f'c{i}' for i,h in enumerate(hdr[1:],1)]
    df=pd.DataFrame(out,columns=cols[:len(out[0])]).dropna(axis=1,how='all')
    return df
R='raw/recursos/'
reca=parse(R+'SP_IP_Reca_concepto.xlsx','m')
reca.columns=['año','mes','Total','IIBB','ABL','Patentes','Sellos','Planes de facilidades','Publicidad','Gravámenes varios'][:len(reca.columns)]
reca['trim']=(reca.mes-1)//3+1
files={'NT':'SP_IP_No_Tribut','K':'SP_IP_Recursos_Capital','RP':'SP_IP_Rentas_Propiedad','TC':'SP_IP_Transf_Corrientes','VByS':'SP_IP_Ventas_BB_y_SS','Derechos':'SP_IP_Derechos','Multas':'SP_IP_Multas','OtrosNT':'SP_IP_Otros_Ingr_NT'}
acc={k:parse(R+v+'.xlsx','q').groupby(['año','trim'],as_index=False).first() for k,v in files.items()}
def flows(df):
    df=df.sort_values(['año','trim']).copy(); vc=[c for c in df.columns if c not in('año','trim')]
    f=df.copy()
    f[vc]=df.groupby('año')[vc].diff().fillna(df[vc])
    return f
fl={k:flows(v) for k,v in acc.items()}
rq=reca.groupby(['año','trim']).agg(n=('mes','size'),T=('Total','sum')).reset_index(); rq=rq[rq.n==3]
q=rq[['año','trim','T']].rename(columns={'T':'Recaudación propia'})
for k in ['NT','K','RP','TC','VByS']:
    q=q.merge(fl[k][['año','trim',fl[k].columns[2]]].rename(columns={fl[k].columns[2]:k}),on=['año','trim'],how='outer')
q=q.sort_values(['año','trim'])
q.columns=['año','trim','Recaudación propia','No tributarios','Recursos de capital','Rentas de la propiedad','Transferencias corrientes','Venta de bienes y servicios']
q['Total propio (sin RON)']=q.iloc[:,2:8].sum(axis=1,min_count=1)
q['periodo']=q.año.astype(str)+'-T'+q.trim.astype(str)
pd.to_pickle({'reca':reca,'acc':acc,'fl':fl,'q':q},'recursos.pkl')
print(reca.tail(3).to_string()); print(q[q.año>=2024].to_string())
for k,v in acc.items(): print(k, list(v.columns), v.año.min(), v.año.max())
