import pandas as pd, numpy as np, json, openpyxl
P=json.load(open('prep.json')); D=P['deflator']
ipcm={}
ws=openpyxl.load_workbook('raw/ipcba.xlsx',data_only=True).worksheets[0]
for r in ws.iter_rows(values_only=True):
    if hasattr(r[0],'year') and isinstance(r[1],(int,float)): ipcm[(r[0].year,r[0].month)]=r[1]
avg26=np.mean([ipcm.get((2026,k), ipcm[(2026,9)]*1.02**(k-9)) for k in range(1,13)])
def to27_m(y,m): return avg26/ipcm[(y,m)]*1.18
rc=pd.read_pickle('reca.pkl')
rc=rc[rc.año>=2013].copy()
for c in ['total','iibb','abl','patentes','sellos']: rc[c+'_27']=rc.apply(lambda r: r[c]*to27_m(int(r.año),int(r.mes)),axis=1)
ytd=rc[rc.mes<=8].groupby('año')[[c+'_27' for c in ['total','iibb','abl','patentes','sellos']]].sum()/1e6
full=rc.groupby('año')[[c+'_27' for c in ['total','iibb','abl','patentes','sellos']]].sum()/1e6
print('YTD ene-ago, billones pesos 2027\n',ytd.round(2).tail(8))
print('Anual\n',full.round(2).tail(8))
# 2026 full-year estimate: YTD 2026 real * (full/ytd ratio 2025)
ratio=full.loc[2025]/ytd.loc[2025]; est26=ytd.loc[2026]*ratio
print('est 2026 real (pesos 2027):\n',est26.round(3))
p27={'iibb':13.2799,'abl_inm':1.4549,'patentes':0.4672,'sellos':1.4489}
print('2027P IIBB vs est26', p27['iibb']/est26['iibb_27']-1, ' vs 2025', p27['iibb']/full.loc[2025,'iibb_27']-1, 'vs 2023',p27['iibb']/full.loc[2023,'iibb_27']-1)
print('2027P patentes vs est26', p27['patentes']/est26['patentes_27']-1, 'vs 2025',p27['patentes']/full.loc[2025,'patentes_27']-1)
print('2027P sellos vs est26', p27['sellos']/est26['sellos_27']-1)
print('2027P ABL+inmob vs est26', p27['abl_inm']/est26['abl_27']-1)
# nominal patentes 2026 estimate
nom=rc.groupby('año')[['patentes','iibb']].sum()/1e6; nytd=rc[rc.mes<=8].groupby('año')[['patentes','iibb']].sum()/1e6
print('patentes nominal 2025', nom.loc[2025,'patentes'], ' 2026 ytd', nytd.loc[2026,'patentes'], ' est', nytd.loc[2026,'patentes']*nom.loc[2025,'patentes']/nytd.loc[2025,'patentes'])
# CAIF ratios
caif={c['concepto']:c['vals'] for c in P['caif']}
ys=[str(y) for y in range(1995,2026)]
def s(name): return pd.Series({y:caif[name].get(y) for y in ys+['2027P']},dtype=float)
gk=s('5) Gastos de capital'); gt=s('10) Gastos totales (7+9)'); rem=s('Remuneraciones al personal'); intr=s('9) Intereses de la deuda pública'); rt=s('6) Recursos totales (1+4)')
sh=(gk/gt*100).round(1); print('capital share\n', sh.to_dict())
print('avg 2006-2025', sh.loc[[str(y) for y in range(2006,2026)]].mean(), 'avg 2005-2024', sh.loc[[str(y) for y in range(2005,2025)]].mean())
print('remun share', (rem/gt*100).round(1).to_dict())
print('intereses/recursos', (intr/rt*100).round(2).to_dict())
prim=s('8) Resultado primario (6-7)'); fin=s('11) Resultado financiero antes de figurativas (6-10)')
print('primario %rec', (prim/rt*100).round(1).to_dict())
