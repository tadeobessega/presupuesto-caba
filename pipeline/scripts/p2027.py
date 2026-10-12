import json,re,pandas as pd,numpy as np,sys
sys.path.insert(0,'scripts')
from planillas import rotated,d,num,val
INC=['Personal','Bienes de consumo','Servicios no personales','Bienes de uso','Transferencias','Activos financieros','Servicio de la deuda','Otros gastos','Total']
p4,_=rotated(5); p4.columns=INC
p3,_=rotated(4); p3.columns=INC
jt=p4['Total'].drop('TOTAL')
frames=[]
for pg in [9,10,11,12]:
    df,_=rotated(pg)
    tot=df.iloc[-1]
    names=[]
    for c in df.columns:
        v=tot[c]; m=(jt-v).abs().idxmin() if (jt-v).abs().min()<1e6 else ('Total general' if abs(v-p4.loc['TOTAL','Total'])<1e6 else f'c{c}')
        names.append(m)
    df.columns=names; frames.append(df)
p8=pd.concat(frames,axis=1)
p8=p8.loc[:,~p8.columns.duplicated()]
p9,_=rotated(13)
# recursos por rubro (normal orientation): pages 15-17
rec=[]
for pg in [15,16,17]:
    it=[i for i in d[str(pg)] if i[2]==0]
    rows={}
    for i in it: rows.setdefault(round(i[6]),[]).append(i)
    for y in sorted(rows,reverse=True):
        r=sorted(rows[y],key=lambda i:i[5])
        txt=[i for i in r if not num.match(i[0])]; nums=[i for i in r if num.match(i[0])]
        if txt and nums:
            amt=[i for i in nums if i[5]>380]
            if amt: rec.append({'pag':pg,'x':txt[0][5],'rubro':' '.join(t[0] for t in txt),'importe':val(amt[0][0])})
rec=pd.DataFrame(rec)
# CAIF page 22
caif=[]
it=[i for i in d['22'] if i[2]==0]; rows={}
for i in it: rows.setdefault(round(i[6]),[]).append(i)
for y in sorted(rows,reverse=True):
    r=sorted(rows[y],key=lambda i:i[5]); txt=[i for i in r if not num.match(i[0])]; nums=[i for i in r if num.match(i[0])]
    if txt and nums: caif.append({'concepto':' '.join(t[0] for t in txt),'x':txt[0][5],'valores':[val(n[0]) for n in nums]})
caif=pd.DataFrame(caif)
pd.to_pickle({'p4':p4,'p3':p3,'p8':p8,'p9':p9,'rec':rec,'caif':caif},'p2027.pkl')
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_colwidth',70)
print(list(p8.columns)); print((p8/1e9).round(0).iloc[:,:6].to_string())
print(rec.assign(imp=(rec.importe/1e9).round(1)).drop(columns='importe').to_string())
print(caif.to_string())
