import json,glob,re,io,pandas as pd
rows=[];dicts={}
ordmap={'primer':1,'segundo':2,'tercer':3,'cuarto':4}
for f in sorted(glob.glob('raw/gasto/*.txt')):
    meta,csv=open(f).read().split('\n@@\n')
    meta=json.loads(meta)
    nm=f.split('/')[-1]
    m=re.search(r'(\d{4})-(\d)\.txt',nm) or re.search(r'(\d{4})-(\w+)-trimestre',nm)
    y=int(m.group(1)); q=m.group(2); q=int(q) if q.isdigit() else ordmap[q]
    df=pd.read_csv(io.StringIO(csv),sep='|',dtype=str)
    keys=list(df.columns[:10]); vals=list(df.columns[10:])
    df=df.rename(columns=dict(zip(vals,['sancion','vigente','definitivo','devengado'][:len(vals)])))
    for c in ['sancion','vigente','definitivo','devengado']:
        df[c]=pd.to_numeric(df.get(c),errors='coerce').fillna(0)
    df['año']=y; df['trim']=q
    rows.append(df)
    for k,d in meta['dict'].items():
        for code,desc in d.items():
            dicts.setdefault(k,{}).setdefault(code,{})[y*10+q]=desc
    print(y,q,len(df),vals, (df[['sancion','vigente','definitivo','devengado']].sum()/1e6).round(0).tolist())
g=pd.concat(rows,ignore_index=True)
g.to_pickle('gasto_trim.pkl')
json.dump({k:{c:v[max(v)] for c,v in d.items()} for k,d in dicts.items()},open('dicts_latest.json','w'),ensure_ascii=False)
json.dump({k:{c:{str(p):s for p,s in v.items()} for c,v in d.items()} for k,d in dicts.items()},open('dicts_all.json','w'),ensure_ascii=False)
