import pandas as pd, json, glob, re, io
D=json.load(open('raw/gasto/dicts.json'))
import re as _re
D={f:{l:{'|'.join(_re.sub(r'\.0$','',p.strip()) for p in k.split('|')):v for k,v in dd_.items()} for l,dd_ in lv.items()} for f,lv in D.items()}
ordmap={'primer':1,'segundo':2,'tercer':3,'cuarto':4}
frames=[]
for f in sorted(glob.glob('raw/gasto/presupuesto-ejecutado-*.txt')):
    name=f.split('/')[-1]
    m=re.search(r'(\d{4})-(\d)\.txt',name)
    if m: y,q=int(m.group(1)),int(m.group(2))
    else:
        m=re.search(r'(\d{4})-(\w+)-trimestre',name); y,q=int(m.group(1)),ordmap[m.group(2)]
    meta,csv=open(f).read().split('\n@@\n')
    df=pd.read_csv(io.StringIO(csv),sep='|',dtype=str)
    vc=df.columns[10:]
    df=df.rename(columns=dict(zip(vc,['sancion','vigente','definitivo','devengado'])))
    for c in ['sancion','vigente','definitivo','devengado']: df[c]=pd.to_numeric(df[c])
    df=df[df.iloc[:,:10].fillna('').apply(lambda r: ''.join(r),axis=1).str.strip()!='']
    df['año']=y; df['trim']=q; df['fuente_dato']='CDN trimestral'
    frames.append(df)
g=pd.concat(frames,ignore_index=True)
g.columns=['car','jur','prog','fin','fun','inc','ppal','par','spar','fte','sancion','vigente','definitivo','devengado','año','trim','fuente_dato']
# Sheet1 annual for 2020, 2021 (Q4)
s=pd.read_pickle('sheet1.pkl')
s=s[s['año'].isin([2020,2021])]
s=s.rename(columns={'sanción':'sancion'})
for c in ['car','jur','prog','fin','fun','inc','ppal','par','spar','fte']: s[c]=s[c].astype(str)
sa=s.groupby(['año','car','jur','prog','fin','fun','inc','ppal','par','spar','fte'],as_index=False)[['sancion','vigente','definitivo','devengado']].sum()
sa['trim']=4; sa['fuente_dato']='Base propia (Sheet1) anual'
# drop CDN rows for 2020Q4/2021Q4 if any (none)
g=pd.concat([g,sa],ignore_index=True)
for c in ['car','jur','prog','fin','fun','inc','ppal','par','spar','fte']: g[c]=g[c].astype(str).str.strip().str.replace(r'\.0$','',regex=True).replace({'nan':'','None':''})
# descriptions: hierarchical; prefer latest file, fall back to Sheet1
def build(level,keyf):
    d={}
    for k in D: 
        for kk,v in D[k][level].items():
            if v: d.setdefault(kk,v)  # earliest
    # override with latest
    for k in sorted(D, key=lambda n: (re.search(r'(\d{4})',n).group(1), n)):
        for kk,v in D[k][level].items():
            if v: d[kk]=v
    return d
dd={l:build(l,None) for l in ['car','jur','prog','fin','fun','inc','ppal','par','spar','fte']}
# sheet1 descs
s1=pd.read_pickle('sheet1.pkl')
for c in ['car','jur','prog','fin','fun','inc','ppal','par','spar','fte']: s1[c]=s1[c].astype(str)
def add(level,cols,desc):
    for row in s1[cols+[desc]].drop_duplicates(cols).itertuples(index=False):
        k='|'.join(row[:-1]); dd[level].setdefault(k,row[-1])
add('car',['car'],'car_desc');add('jur',['jur'],'jur_desc');add('prog',['jur','prog'],'prog_desc');add('fin',['fin'],'fin_desc');add('fun',['fin','fun'],'fun_desc')
add('inc',['inc'],'inc_desc');add('ppal',['inc','ppal'],'ppal_desc');add('par',['inc','ppal','par'],'par_desc');add('spar',['inc','ppal','par','spar'],'spar_desc');add('fte',['fte'],'fte_desc')
g['car_desc']=g.car.map(dd['car']); g['jur_desc']=g.jur.map(dd['jur'])
g['prog_desc']=(g.jur+'|'+g.prog).map(dd['prog']); g['fin_desc']=g.fin.map(dd['fin']); g['fun_desc']=(g.fin+'|'+g.fun).map(dd['fun'])
g['inc_desc']=g.inc.map(dd['inc']); g['ppal_desc']=(g.inc+'|'+g.ppal).map(dd['ppal']); g['par_desc']=(g.inc+'|'+g.ppal+'|'+g.par).map(dd['par']); g['spar_desc']=(g.inc+'|'+g.ppal+'|'+g.par+'|'+g.spar).map(dd['spar']); g['fte_desc']=g.fte.map(dd['fte'])
print(g.isna().sum()[g.isna().sum()>0])
g.to_pickle('gasto.pkl')
t=g.groupby(['año','trim'])[['sancion','vigente','definitivo','devengado']].sum()/1e9
print(t.round(1))
