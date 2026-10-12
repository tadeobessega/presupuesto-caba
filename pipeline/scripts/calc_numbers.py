import json, pandas as pd, numpy as np
D=json.load(open('data.json')); F=D['defl']; p27=F['p2027']; hoy=F['hoy']
caif={c['concepto']:c['vals'] for c in D['caif']}
def c27(name,y): v=caif[name].get(y); return None if v is None else v*p27[y if y!='2027P' else '2027P']/1e6
N={}
for k in ['6) Recursos totales (1+4)','10) Gastos totales (7+9)','7) Gasto primario (2+5)','5) Gastos de capital','Remuneraciones al personal','9) Intereses de la deuda pública','Ingresos tributarios','Transferencias corrientes','8) Resultado primario (6-7)','11) Resultado financiero antes de figurativas (6-10)']:
    N[k]={y:round(c27(k,y),2) for y in ['2015','2017','2018','2019','2022','2023','2024','2025','2027P'] if caif[k].get(y) is not None}
for k,v in N.items(): print(k[:40].ljust(40), v)
# max historic recursos/gasto constant
for k in ['6) Recursos totales (1+4)','10) Gastos totales (7+9)']:
    s={y:caif[k][y]*p27[y]/1e6 for y in caif[k] if y!='2027P' and caif[k][y]}
    m=max(s,key=s.get); print(k,'max',m,round(s[m],2), '2027P',round(caif[k]['2027P']/1e6,2))
# cube: totals by year (Q4) devengado excl amort, 2026 sanc/vig, 2027
cb=D['cube']; dims=cb['dims']; inc=dims['inc_desc']; ai=inc.index('Amortización de deuda')
df=pd.DataFrame(cb['rows'],columns=['y','t','jur','fin','fun','inc','s','v','d'])
df=df[df.inc!=ai]
tot=df.groupby(['y','t'])[['s','v','d']].sum()/1e6
print(tot.tail(8).round(2))
# bienes de uso execution ratio
bu=inc.index('Bienes De Uso')
x=df[(df.inc==bu)&(df.t==4)].groupby('y')[['s','v','d']].sum()
print('Bienes de uso dev/sanc', (x.d/x.s).round(2).to_dict(), 'dev/vig',(x.d/x.v).round(2).to_dict())
# function shares devengado Q4 and 2027
fun=dims['fun_desc']
q4=df[df.t==4].groupby(['y','fun']).d.sum().unstack().fillna(0)
sh=(q4.div(q4.sum(1),axis=0)*100)
for f in ['Educación','Salud','Seguridad interior','Promoción y acción social','Transporte','Vivienda y Urbanismo','Deuda Pública - Intereses y Gastos','Servicios Urbanos']:
    print(f, sh[fun.index(f)].round(1).to_dict())
# 2026 vig by function
v26=df[(df.y==2026)&(df.t==2)].groupby('fun').v.sum()
print('2026 vig shares', {fun[i]:round(v/ v26.sum()*100,1) for i,v in v26.items()})
